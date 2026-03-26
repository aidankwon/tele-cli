from unittest.mock import MagicMock
from datetime import datetime
from tele_cli.utils.fmt import _format_message_to_str

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
