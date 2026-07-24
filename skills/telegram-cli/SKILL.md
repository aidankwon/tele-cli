---
name: telegram-cli
description: Use `tele` to authenticate, list dialogs, and fetch messages from Telegram.
metadata:
  author: Huanan
  version: "2026.1.0"
---

# Telegram CLI Usage Guide

## Overview

Use `tele` to authenticate, list dialogs, fetch messages, download files from messages, and delete messages from Telegram directly from the terminal.


## Setup

- Requires `uv`.
- Install/upgrade (one-time per session): `uv tool install --upgrade git+https://github.com/aidankwon/tele-cli`
- Verify install: `tele -V`
- Per terminal session: run `tele -h` once, then confirm auth with `tele -f json me` (log in if needed).
- Output format (`-f`): `text` (default), `json`, or `toon`.


## Notice

- Call `tele -h` once before running any command for the first time in the session.
- Always use JSON output: always pass `-f json` to `tele` (example: `tele -f json me`).
- In each session, confirm authentication before running non-auth commands: run `tele -f json me`.
- Commands under `tele auth ...` do not require an existing authenticated session.

## Quick Start

1. Read help once: `tele -h`
2. Log in (interactive prompts): `tele auth login`
3. Confirm who you are: `tele -f json me`
4. List dialogs and find a `dialog_id`: `tele -f json dialog list`
5. Fetch recent messages from a dialog:
   - `tele -f json message list <dialog_id> -n 20`
6. Download media files from a messages: `tele message download <dialog_id> -n 10 -o ~/.cache/tele-cli/<dialog_id>`

## Session Management

Global options:

- `--config <path>`: alternate config file (default: `~/.config/tele/config.toml`)
- `--session <name>`: use a specific session file by name (listed by `tele auth list`)

Login / logout:

- `tele auth login` (creates a local session; prompts for phone, code, and optional 2FA password)
- `tele auth login --switch` (log in and make the new session active)
- `tele auth logout` (logs out of the selected session)

List and switch sessions:

- `tele auth list`
- `tele auth switch --uid <user_id>`
- `tele auth switch --username <username>` (accepts `@alice` or `alice`)
- `tele auth switch --session <session_name>`

List active Telegram authorizations (sessions/devices on Telegram's side, not just local):

- `tele auth authorizations`

Where sessions live on disk (macOS/Linux default):

- Sessions folder: `~/.config/tele/sessions/`
- Current activated session symlink: `~/.config/tele/sessions/Current.session`

## Dialog List

List all dialogs (users, groups, channels):

- `tele -f json dialog list`

Filtering and sorting options:

- `--type/-t [user|group|channel]`: Filter by dialog type. Repeatable (e.g., `-t user -t channel`).
- `--archived`: Include archived dialogs (hidden by default).
- `--older <duration>`: Show dialogs where the latest message is older than the given time (e.g., `1d`, `1w`, `1m`, `1y`).
- `--newer <duration>`: Show dialogs where the latest message is newer than the given time.
- `--empty`: Show only empty dialogs (no messages or only service messages).
- `--order asc|desc`: Output order by time (`desc` is latest first, `asc` is reverse).

Examples:

- `tele -f json dialog list -t user`
- `tele -f json dialog list -t user -t channel --archived`

Notes:

- For `-f text`, the output follows the template:
  - `[TYPE.UI.STATE] [UNREAD COUNT] [DIALOG_ID] NAME`
  - `TYPE`: `U` user, `G` group, `C` channel
  - `UI`: `P` pinned, `A` archived, `-` normal
  - `STATE`: `M` muted, `-` not muted
- For `-f json`, each dialog includes keys like `name`, `entity` (with `id`), `unread_count`, and the latest `message`.

## Delete Dialog

Delete one or more dialogs by their peer IDs:

- `tele dialog delete <dialog_id1> <dialog_id2> ...`

Options:

- `--revoke`: Withdraw for everyone (leave group, delete chat).

Examples:

- `tele dialog delete 1375282077`
- `tele dialog delete -1001234567890 1375282077`

## Message List

Fetch messages from a dialog:

- `tele -f json message list <dialog_id>`

Notes:

- Without `-n` or date filters, only the **latest single message** is returned.
- Default output order is `asc` (oldest first).

Common options:

- Limit count: `-n <num>` (example: `tele -f json message list <dialog_id> -n 20`)
- Pagination: `--offset_id <message_id>` (fetch around/older than a known message id; `offset_id` is excluded)
- Output order: `--order asc|desc` (default: `asc`)
- Time filters:
  - `--from "<natural language or date>"`
  - `--to "<natural language or date>"`
  - `--range "<natural language range>"` (overrides `--from/--to`, special: `"this week"`)

Examples:

- `tele -f json message list 1375282077 -n 10`
- `tele -f json message list 1375282077 --range "last week"`
- `tele -f json message list 1375282077 --from "2025-02-05" --to "yesterday"`
- `tele -f json message list 1375282077 --from "-5d"`
- `tele -f json message list 1375282077 --from "today" -n 100`
- `tele -f json message list -1001234567890 -n 10`

Notes:

- Negative peer IDs (e.g., `-1001234567890`) can be passed directly as arguments.

## Delete Messages

Delete specific messages in a dialog:

- `tele message delete <dialog_id> <message_id1> <message_id2> ...`

Options:

- `--revoke`: Delete for everyone (default is true).

Examples:

- `tele message delete 1375282077 123 124`
- `tele message delete -1001234567890 456`

## Download Messages

Download mediafiles from messages in a dialog:

- `tele message download <dialog_id>`

Options:

- Limit count: `--num <num>` or `-n <num>`
- Pagination: `--offset_id <message_id>` (fetch around/older than a known message id; `offset_id` is excluded)
- Output directory: `--out-dir <target dir>` or `-o <target_dir>`
- Time filters:
  - `--from`: Start boundary
  - `--to`: End boundary
  - `--range`: Natural language date range (overrides `--from`/`--to`)

Examples:

- `tele message download 1375282077 -n 10 -o ~/.cache/tele-cli/1375282077`

## Send Message

Send a text message (and/or files) to a user, group, or channel:

- Basic: `tele message send <receiver> "<message>"`
- Force peer id: `tele message send -t peer_id "<peer_id>" "<message>"`

Receiver formats:

- Username: `alice` or `@alice`
- Phone: `"+15551234567"`
- Dialog name: `"My Group"`
- Numeric peer id: `"-1001234567890"` (common for channels)

How the receiver is resolved:

- With `--entity/-t <type>`, `<receiver>` is passed through as that type (`username`, `phone`, or `peer_id`) with no matching attempted.
- Without `--entity`, it first tries Telegram/Telethon resolution (username/phone/id). If that fails, it scans your dialogs and picks the first match by:
  - dialog name contains `<receiver>` (case-insensitive), or
  - dialog id / entity id equals `<receiver>` (string compare).

Options:

- `--reply-to <message_id>`: Reply to a specific message.
- `--file <path>`: Attach a local file. Can be used multiple times for multiple files.

Examples:

- `tele message send alice "hi"`
- `tele message send "+15551234567" "hi"`
- `tele message send "My Group" "hi"`
- `tele message send -t peer_id "-1001234567890" "hi"`
- `tele message send alice --file ./photo.jpg "check this out"`
- `tele message send alice --file ./a.pdf --file ./b.pdf`
- `tele message send alice --reply-to 42 "got it"`

Notes:

- Message `CONTENT` is optional when `--file` is provided.
- Negative peer IDs (e.g., `-1001234567890`) can be passed directly.
- The command prints no output on success; verify by listing messages: `tele -f json message list <dialog_id> -n 5`.

## Recent Messages Across All Dialogs

`tele dialog list` already includes the latest message for each dialog in its JSON payload — no per-dialog `message list` calls needed. Use this to get the N most recent messages across all dialogs in a single API call:

```bash
tele -f json dialog list | python3 -c "
import sys, json
data = json.load(sys.stdin)
msgs = []
for d in data:
    m = d.get('message')
    if not m or not m.get('message'):
        continue
    msgs.append({
        'date': m['date'],
        'dialog': d['name'],
        'out': m.get('out', False),
        'text': m['message'][:80],
    })
msgs.sort(key=lambda x: x['date'], reverse=True)
for m in msgs[:20]:
    direction = '→' if m['out'] else '←'
    print(f\"{m['date']}  {direction}  {m['dialog']:<30}  {m['text']}\")
"
```

- `←` = received, `→` = sent by you.
- Change `[:20]` to adjust the count.
- Combine with `dialog list` filters (e.g., `-t user`, `--newer 1d`) to narrow scope before sorting.

## Daemon

Stream all incoming new messages in real time:

- `tele daemon start`

Options:

- `--rpc-stdio`: Enable newline-delimited JSON RPC over stdio (useful for programmatic/scripted consumption).

## Additional Information

- Config file: `tele` reads `~/.config/tele/config.toml` by default and will create it on first run;
