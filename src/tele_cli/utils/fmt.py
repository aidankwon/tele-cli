from datetime import datetime
import json

import telethon
from telethon.custom import Message
import toon_format
from telethon.tl.tlobject import _json_default

from tele_cli.types import OutputFormat, get_dialog_type
from tele_cli.types.session import SessionInfo
import arrow

from .output import get_str_len_for_int


def json_default_callback(value):
    return _json_default(value)


def format_me(me: telethon.types.User, fmt: None | OutputFormat = None) -> str:
    output_fmt = fmt or OutputFormat.text
    match output_fmt:
        case OutputFormat.text:
            return telethon.utils.get_display_name(me)
        case OutputFormat.json:
            return json.dumps(me.to_json(), ensure_ascii=False)
        case OutputFormat.toon:
            return toon_format.encode(me.to_dict())


def _format_dialog_to_str(x: telethon.custom.Dialog, unread_count_len: int, peer_id_len: int) -> str:
    """
    format: "[<Dialog Type>.<UI State>.<Dialog State>] <Unread Count> <Name> [entity id]"
    """

    have_unread: bool = x.unread_count > 0
    unread_color = "red" if have_unread else "not"
    _color = "white" if x.archived else "not"

    state = "-"
    if x.pinned:
        state = "P"
    if x.archived:
        state = "A"

    dialog_type = str(get_dialog_type(x))

    mute_until = x.dialog.notify_settings.mute_until
    is_mute = mute_until is not None and mute_until > datetime.now().astimezone()
    mute = "M" if is_mute else "-"

    unread = f"[{unread_color}]{(str(x.unread_count) if have_unread else ' '):<{unread_count_len}}[/{unread_color}]"

    message_line = ""
    message_prefix_space_count = 2 + 5 + 2 + unread_count_len + 2 + 2 + peer_id_len
    if x.message.message and not x.message.out and have_unread and not is_mute:
        unread_message = "".join([f"{' ' * message_prefix_space_count}| " + m for m in x.message.message.splitlines(keepends=True)])
        message_line = "\n" + f"{' ' * message_prefix_space_count}* id: {x.message.id} at {x.message.date} \n" + unread_message

    return f"[{_color}]" + f"[{dialog_type}.{state}.{mute}] {unread} [{x.id:<{peer_id_len}}] {x.name} " + message_line + f"[/{_color}]"


def format_dialog_list(dialog_list: list[telethon.custom.Dialog], fmt: None | OutputFormat = None) -> str:
    output_fmt = fmt or OutputFormat.text
    match output_fmt:
        case OutputFormat.text:
            max_unread_count_len = max(list(map(lambda x: get_str_len_for_int(x.unread_count), dialog_list)))
            max_peer_id_len = max(list(map(lambda x: get_str_len_for_int(x.id), dialog_list)))
            return "\n".join([_format_dialog_to_str(x, max_unread_count_len, max_peer_id_len) for x in sorted(dialog_list, key=lambda x: x.archived)])

        case OutputFormat.json:

            def f(x: telethon.custom.Dialog) -> dict:
                return {
                    "_": "Dialog",
                    "pin": x.pinned,
                    "folder_id": x.folder_id,
                    "name": x.name,
                    "date": x.date,
                    "message": x.message.to_dict(),
                    "entity": x.entity.to_dict(),
                    "unread_count": x.unread_count,
                }

            obj_list = [f(item) for item in dialog_list]
            return json.dumps(obj_list, default=json_default_callback, ensure_ascii=False)

        case OutputFormat.toon:
            raise NotImplementedError("Not Supported Format For Dialog")


def _format_message_to_str(msg: Message, relative_time: bool = True) -> str:
    sender_name = "unknown"
    if msg.out:
        sender_name = "me"
    elif msg.sender:
        sender_name = f"{telethon.utils.get_display_name(msg.sender)} (id: {msg.sender.id})"

    if relative_time:
        date_str = arrow.get(msg.date).humanize() if msg.date else "?"
    else:
        date_str = msg.date.strftime("%Y-%m-%d %H:%M") if msg.date else "?"

    text = msg.message or ""
    if getattr(msg, "file", None):
        file_info = []
        if getattr(msg.file, "name", None):
            file_info.append(f"name='{msg.file.name}'")
        if getattr(msg.file, "ext", None) and not getattr(msg.file, "name", None):
            file_info.append(f"ext='{msg.file.ext}'")
        if getattr(msg.file, "size", None):
            file_info.append(f"size={msg.file.size}")

        file_info_str = ", ".join(file_info)
        attachment_str = f"[📎 Attachment: {file_info_str}]" if file_info_str else "[📎 Attachment]"
        text = f"{text}\n{attachment_str}" if text else attachment_str

    message = "".join(["  " + x for x in text.splitlines(keepends=True)])

    return f"* {msg.id} ({date_str}) - {sender_name}\n" + "\n" + message + "\n"


def format_message_list(messages: list[Message], fmt: None | OutputFormat = None) -> str:
    output_fmt = fmt or OutputFormat.text
    match output_fmt:
        case OutputFormat.text:
            return "\n".join([_format_message_to_str(msg) for msg in messages])
        case OutputFormat.json:
            obj_list = [msg.to_dict() for msg in messages]
            return json.dumps(obj_list, default=json_default_callback, ensure_ascii=False)
        case OutputFormat.toon:
            raise NotImplementedError("Not Supported Format For Message List")


def _format_session_info_to_str(x: SessionInfo) -> str:
    username = f"@{x.user_name}" if x.user_name else "unknown"
    return f"{x.user_id: <12} {x.user_display_name or 'unknown'} ({username}) {x.session_name}"


def format_session_info_list(session_info_list: list[SessionInfo], fmt: None | OutputFormat = None) -> str:
    output_fmt = fmt or OutputFormat.text

    match output_fmt:
        case OutputFormat.text:
            return "\n".join([_format_session_info_to_str(obj) for obj in session_info_list])
        case OutputFormat.json:
            obj_list = [item.model_dump(mode="json") for item in session_info_list]
            return json.dumps(obj_list, ensure_ascii=False)
        case OutputFormat.toon:
            raise NotImplementedError("Not Supported Format For SessionInfo List")


def _format_authorization_to_str(x: telethon.types.Authorization, max_hash_len: int, max_device_model_len: int) -> str:
    is_current = x.current or False
    current = ">" if is_current else " "

    date_active = x.date_active and arrow.get(x.date_active).humanize()

    return f"{current} [{x.hash: <{max_hash_len}}] {date_active:14} {x.device_model: <{max_device_model_len}} - {x.app_name} {x.app_version} "


def format_authorizations(
    authorizations: telethon.types.account.Authorizations,
    fmt: None | OutputFormat = None,
) -> str:
    output_fmt = fmt or OutputFormat.text

    match output_fmt:
        case OutputFormat.text:
            max_hash_len = max(list(map(lambda x: get_str_len_for_int(x.hash), authorizations.authorizations)))
            max_device_model_len = max(list(map(lambda x: len(x.device_model), authorizations.authorizations)))

            rows = [_format_authorization_to_str(item, max_hash_len, max_device_model_len) for item in authorizations.authorizations]
            return "\n".join(rows)
        case OutputFormat.json:
            return json.dumps(authorizations.to_dict(), default=json_default_callback, ensure_ascii=False)
        case OutputFormat.toon:
            raise NotImplementedError("Not Supported Format For Authorizations")
