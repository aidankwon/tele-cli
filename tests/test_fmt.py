import json
from unittest.mock import MagicMock
from datetime import datetime
from tele_cli.types import OutputFormat
from tele_cli.utils.fmt import _format_message_to_str, format_attachment_list, attachment_type

def test_format_message_to_str_with_attachment():
    # Setup mock message
    msg = MagicMock()
    msg.id = 123
    msg.date = datetime(2025, 1, 1, 12, 0)
    msg.out = True
    msg.message = ""
    
    # Setup mock file
    msg.file = MagicMock()
    msg.file.name = "test_image.png"
    msg.file.size = 1024
    msg.file.ext = ".png"
    
    result = _format_message_to_str(msg, relative_time=False)
    
    assert "test_image.png" in result
    assert "1024" in result
    assert "📎 Attachment: name='test_image.png', size=1024" in result

def test_format_message_to_str_with_text_and_attachment():
    msg = MagicMock()
    msg.id = 124
    msg.date = datetime(2025, 1, 1, 12, 0)
    msg.out = True
    msg.message = "Check out this file"
    
    msg.file = MagicMock()
    msg.file.name = None
    msg.file.size = 2048
    msg.file.ext = ".pdf"
    
    result = _format_message_to_str(msg, relative_time=False)
    
    assert "Check out this file" in result
    assert "📎 Attachment: ext='.pdf', size=2048" in result

def test_format_message_to_str_no_attachment():
    # Setup mock message
    msg = MagicMock()
    msg.id = 125
    msg.date = datetime(2025, 1, 1, 12, 0)
    msg.out = True
    msg.message = "Hello World"
    
    # No file
    del msg.file
    # Wait, telethon Message without a file either returns None or doesn't have it in MagicMock if we don't mock it.
    # MagicMock creates it automatically if accessed, unless we delete it or set it to None. 
    # The actual implementation calls getattr(msg, "file", None), so we should make it return None
    msg.file = None
    
    result = _format_message_to_str(msg, relative_time=False)

    assert "Hello World" in result
    assert "📎 Attachment" not in result


def _make_attachment_msg(msg_id, name, ext, mime, size, kind="document"):
    msg = MagicMock()
    msg.id = msg_id
    msg.date = datetime(2025, 1, 1, 12, 0)
    # only the chosen kind should be truthy for attachment_type detection
    for attr in ("photo", "video_note", "video", "voice", "audio", "gif", "sticker", "contact", "geo", "document"):
        setattr(msg, attr, None)
    setattr(msg, kind, MagicMock())
    msg.file = MagicMock()
    msg.file.name = name
    msg.file.ext = ext
    msg.file.mime_type = mime
    msg.file.size = size
    return msg


def test_attachment_type_prefers_specific_kind():
    photo = _make_attachment_msg(1, None, ".jpg", "image/jpeg", 100, kind="photo")
    assert attachment_type(photo) == "photo"

    doc = _make_attachment_msg(2, "a.pdf", ".pdf", "application/pdf", 200, kind="document")
    assert attachment_type(doc) == "document"


def test_format_attachment_list_text():
    msgs = [_make_attachment_msg(123, "report.pdf", ".pdf", "application/pdf", 2048, kind="document")]
    result = format_attachment_list(msgs, OutputFormat.text)
    assert "* 123" in result
    assert "[document]" in result
    assert "name='report.pdf'" in result
    assert "size=2048" in result


def test_format_attachment_list_json():
    msgs = [_make_attachment_msg(124, "clip.mp4", ".mp4", "video/mp4", 4096, kind="video")]
    result = format_attachment_list(msgs, OutputFormat.json)
    data = json.loads(result)
    assert data[0]["message_id"] == 124
    assert data[0]["type"] == "video"
    assert data[0]["name"] == "clip.mp4"
    assert data[0]["size"] == 4096


def test_format_attachment_list_document_attribute_fallback():
    msg = MagicMock()
    msg.id = 125
    msg.date = datetime(2025, 1, 1, 12, 0)
    msg.file = MagicMock()
    msg.file.name = None
    msg.file.ext = None
    msg.file.mime_type = "application/pdf"
    msg.file.size = 5000

    doc_attr = MagicMock(spec=["file_name"])
    # DocumentAttributeFilename check
    from telethon.types import DocumentAttributeFilename
    doc_attr = DocumentAttributeFilename(file_name="fallback_doc.pdf")

    doc = MagicMock()
    doc.attributes = [doc_attr]
    doc.mime_type = "application/pdf"
    doc.size = 5000
    msg.document = doc

    result = format_attachment_list([msg], OutputFormat.json)
    data = json.loads(result)
    assert data[0]["name"] == "fallback_doc.pdf"
    assert data[0]["ext"] == ".pdf"
    assert data[0]["mime_type"] == "application/pdf"
    assert data[0]["size"] == 5000


def test_format_attachment_list_synthetic_filename_fallback():
    photo_msg = _make_attachment_msg(9184, None, ".jpg", "image/jpeg", 1024, kind="photo")
    result = format_attachment_list([photo_msg], OutputFormat.json)
    data = json.loads(result)
    assert data[0]["name"] == "photo_9184.jpg"

    no_ext_msg = _make_attachment_msg(47117, None, None, "application/octet-stream", 2048, kind="document")
    no_ext_msg.document.file_name = None
    no_ext_msg.document.attributes = []
    result_no_ext = format_attachment_list([no_ext_msg], OutputFormat.json)
    data_no_ext = json.loads(result_no_ext)
    assert data_no_ext[0]["name"] == "document_47117"


