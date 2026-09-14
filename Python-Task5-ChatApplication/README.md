# Chat Application (OIBSIP Internship - Task 5)

A beginner-friendly desktop chat application built with Python, sockets, threading, Tkinter, and SQLite.

## Features Implemented

- Real-time two-way messaging over TCP sockets
- Multi-client support using Python threads
- Tkinter desktop GUI client
- User registration and login
- Password hashing with PBKDF2-HMAC-SHA256 (random salt, 100,000 iterations)
- Message timestamps
- Graceful disconnect handling
- System notifications for join/leave events
- Multiple named chat rooms with `/join` and `/rooms`
- Room-specific persistent message history (latest 50 messages, oldest → newest)
- Online presence with `/users` and `/roomusers`
- Private messaging with `/msg <username> <message>`
- Private message delivery and read receipts
- Emoji support via built-in emoji picker
- Typing indicators showing when users are typing in the same room

## Technology Stack

- Python 3
- `socket` — TCP networking
- `threading` — concurrent client handling
- `sqlite3` — user account storage
- `hashlib` — PBKDF2 password hashing

## Project Structure

```
Chat_Bot_App/
├── server.py       # TCP chat server with threading
├── client.py       # Tkinter desktop client
├── database.py     # SQLite database & PBKDF2 password hashing
├── requirements.txt
├── README.md
└── chat_app.db     # Created automatically on first run
```

## Available Commands

| Command | Description |
|---------|-------------|
| `/join <room>` | Join or create a named chat room |
| `/rooms` | List all available rooms and user counts |
| `/users` | Show all currently online users |
| `/roomusers` | Show users in your current room |
| `/msg <username> <message>` | Send a private message to a specific user |
| `/typing` | Internal — start typing indicator |
| `/stoptyping` | Internal — stop typing indicator |
| `/exit` | Leave the chat application |

## Private Messaging

### How it works
- Use `/msg <username> <message>` to send a private message.
- The message is delivered directly to the recipient's client, bypassing room broadcasting.
- The sender receives a local confirmation: `[PRIVATE] You → <username>: <message>`
- The recipient receives: `[PRIVATE] <username> → You: <message>`
- Private messages are **not** stored in the SQLite message history.
- Private messages support delivery and read receipts (see below).

### Example
```
/msg Bob Hello Bob, this is a private message!
```

### Limitations
- The recipient must be online (connected to the server) to receive the message.
- Private messages are not persisted.
- This is an internship learning project and is not production-grade secure messaging.

## Private Message Read Receipts

### How it works
- When you send a private message with `/msg`, the sender sees a `✓` next to the message.
- When the recipient's client receives and displays the message, the sender sees `✓✓`.
- When the recipient's GUI displays the message, a read receipt is sent back, and the sender sees `✓✓ Read`.

### Example
```
/msg Bob Hello 😊
```
Sender sees:
```
[PRIVATE] You → Bob: Hello 😊 ✓
[PRIVATE] You → Bob: Hello 😊 ✓✓
[PRIVATE] You → Bob: Hello 😊 ✓✓ Read
```
Recipient sees:
```
[PRIVATE] Alice → You: Hello 😊
```

### Protocol
- `PRIVATE_SENT|<id>|<sender>|<target>|<text>` — sent to sender when the server accepts the message.
- `PRIVATE_DELIVERED|<id>` — sent to sender when the message is successfully sent to the recipient's socket.
- `PRIVATE|<id>|<sender>|<target>|<text>` — sent to the recipient.
- `PRIVATE_READ|<id>` — sent from recipient back to server, then forwarded to the sender after the recipient's GUI displays the message.

### Status meanings
- `✓` — Server accepted and sent the message.
- `✓✓` — Recipient's client received the message.
- `✓✓ Read` — Recipient's GUI displayed the message.

### Limitations
- Read receipts are only sent after the recipient's GUI processes the message.
- Private messages and read receipts are not stored in SQLite.
- Message IDs are runtime-only and reset when the server stops.
- This is an internship learning project.

## Emoji Support

### How it works
- Click the **😊 Emoji** button in the chat window to open the built-in emoji picker.
- Click any emoji to insert it at the cursor position in the message input box.
- Emojis are sent as normal UTF-8 text through the existing TCP socket connection.
- No external emoji library is required.

### Supported places
- Public chat messages
- Private messages (`/msg`)
- Room message history (persisted in SQLite)

### Example
```
Hello 😊
Great job! 🎉🔥❤️👍
```

### Notes
- Emojis are stored in SQLite as Unicode text and survive server restarts.
- The emoji picker uses a standard Tkinter `Toplevel` window with no external dependencies.
- This is an internship learning project. Emoji rendering may vary depending on your operating system and fonts.

## Typing Indicators

### How it works
- When you type in the message input box, other users in the same room see a small typing indicator below the chat area.
- The indicator shows: `Alice is typing...` or `Alice and Bob are typing...`
- Typing indicators are **not** saved to message history.

### Protocol
- The client sends `/typing` when typing starts.
- The client sends `/stoptyping` when typing stops (after a 2-second debounce, when the message is sent, or when switching rooms).
- The server broadcasts `TYPING_START|<username>` and `TYPING_STOP|<username>` to other users in the same room.

### Debounce
- The client sends `/typing` only once when typing begins.
- If you keep typing, the stop timer is reset.
- If you stop typing for approximately 2 seconds, `/stoptyping` is sent automatically.
- Sending a message immediately stops the typing indicator.

### Room isolation
- Typing indicators are room-specific.
- Users in different rooms do not see each other's typing indicators.

### Limitations
- Typing status is runtime-only and resets when the server stops.
- Typing indicators are not persisted.
- This is an internship learning project.

## Notifications & Presence

### Desktop notifications
- When a new public message or private message arrives and the chat window is **not focused**, a Windows desktop toast notification is shown.
- When the window is focused, no notification is shown — the message simply appears in the chat.
- Notifications are not triggered for: own messages, typing indicators, read/delivery receipts, system messages, history loading, or presence list responses.

### Implementation
- Focus check: `root.focus_displayof()` is called from the GUI thread inside `_process_queue`.
- If unfocused, a background thread calls PowerShell with a WinRT `ToastNotification` script.
- No external Python package is required — only Windows PowerShell, which is available on all modern Windows installations.

### Platform support
- Windows: full toast notifications via WinRT.
- macOS / Linux: notifications are silently skipped. The in-app chat still shows all messages normally.

### Sidebar presence panels
The chat window sidebar shows three sections:
- **Chat Rooms** — available rooms with user counts
- **Online Users** — all currently connected users
- **Users in Room** — users in your current room

Each section has a refresh button.

### Join notifications
- When a user logs in, other users in the same room see: `[SYSTEM] <user> joined the <room> room.`
- When a user switches rooms with `/join <room>`, users in the old room see: `[SYSTEM] <user> left the room.`
- Users in the new room see: `[SYSTEM] <user> joined the <new_room> room.`

### Disconnect notifications
- When a user disconnects (types `/exit`, closes the GUI, or loses connection), remaining users in the same room see: `[SYSTEM] <user> left the chat.`

### Online users
- Use `/users` or click **Refresh Users** to see all currently connected users.
- This shows only users who are currently online, not all registered accounts.

### Room users
- Use `/roomusers` or click **Refresh Room Users** to see who is in your current room.
- This updates automatically when users join or leave rooms.

### Automatic updates
The sidebar presence lists refresh automatically when:
- You join a new room
- Another user joins or leaves your room
- Another user disconnects

### Example output
```
Online users (3):
- Alice
- Bob
- Charlie

Users in #general (2):
- Alice
- Bob
```

## How to Run

### 1. Start the Server
```bash
python server.py
```

### 2. Start Client(s) (in separate terminal windows)
```bash
python client.py
```

### 3. Choose Register or Login
Follow the on-screen menu to register a new account or log in with an existing one.

### 4. Chat
After logging in, type messages and press Enter to send. Type `/exit` to leave.

## Security & Privacy

This is an internship learning project and is **not production-grade secure messaging**.

### What is stored
- Usernames and password hashes are stored in a local SQLite database file (`chat_app.db`).
- Public chat messages are stored in SQLite and persist across server restarts.
- Private messages are **not** stored persistently.

### Password storage
- Passwords are **not** stored in plaintext.
- Passwords are hashed using **PBKDF2-HMAC-SHA256** with a random 16-byte salt and 100,000 iterations.
- The salt and hash are stored together in the database.

### What is NOT encrypted
- Chat traffic uses plain TCP and is **not encrypted**.
- Messages travel over the network in readable text.
- There is no TLS/SSL or end-to-end encryption.
- Authentication commands (including passwords in transit) are sent as plain text over the socket.

### Limitations
- No protection against man-in-the-middle attacks.
- No forward secrecy.
- Not intended for sensitive or confidential communication.
- Authentication uses a simple `|`-delimited frame, so usernames and passwords must not contain the `|` character.
- This application must not be exposed to untrusted networks.

## License

Educational project for OASIS Infobyte Internship.

## Internship Requirement Audit

| # | Requirement (Task Card) | Implementation | Status |
|---|-------------------------|----------------|--------|
| 1 | GUI chat window using Tkinter | `client.py` `ChatClient` class (`_build_chat_screen`, `tk.Tk`, `tk.Text`, `ttk`) | PASS |
| 2 | User registration and login using username and password, stored in SQLite | `database.py` `register_user`, `authenticate_user`; `users` table in `chat_app.db` | PASS |
| 3 | Multiple chat rooms where users can create or join named rooms | `server.py` `rooms` dict; `/join` command at `server.py:150` | PASS |
| 4 | Message history loaded when a user joins a room | `database.py` `get_message_history`; `server.py` `send_history` | PASS |
| 5 | Desktop or in-app notifications for new messages | Windows toast notifications via PowerShell when the window is unfocused; in-app `[SYSTEM]` and chat scrolling otherwise | PASS |
| 6 | Emoji support, including common shortcuts | Built-in emoji picker (`_open_emoji_picker`) and full Unicode/UTF-8 emoji transmission | PASS |
| 7 | Security transparency in README explaining storage and what is not encrypted | This document, dedicated Security & Privacy section | PASS |
| 8 | Beginner features (real-time chat, register, login, rooms) | All working | PASS |

> Note on requirement 5: the application shows in-app system messages and chat updates but does not integrate with the operating system's native notification system (Windows toast / macOS Notification Center / libnotify). This was intentionally scoped out to keep the project dependency-free.

## Manual Test Plan

### Authentication
- [ ] Register a new user
- [ ] Register with an existing username (must fail with "Username already exists.")
- [ ] Register with empty username or password (must fail)
- [ ] Login with valid credentials
- [ ] Login with wrong password (must fail)
- [ ] Login with unknown username (must fail)

### Public Messaging
- [ ] Send a public message
- [ ] Multiple clients receive it in real time
- [ ] Rapid messages all arrive in order

### Rooms
- [ ] Create a new room with `/join programming`
- [ ] Join an existing room
- [ ] Switch rooms
- [ ] Confirm room isolation (users in other rooms don't see messages)

### Message History
- [ ] Stop the server, restart it, log in, and confirm old messages still appear
- [ ] Confirm only the latest 50 messages are loaded
- [ ] Confirm history is per-room

### Presence
- [ ] `/users` shows all online users
- [ ] `/roomusers` shows users in the current room
- [ ] Join/leave/disconnect notifications appear in the chat

### Typing Indicators
- [ ] Typing shows `Alice is typing...` in other clients
- [ ] Indicator disappears after ~2s of inactivity
- [ ] Indicator disappears immediately on send
- [ ] Indicator disappears on room switch, logout, disconnect

### Emoji
- [ ] Picker opens and closes
- [ ] Emoji is inserted at cursor, not sent
- [ ] Emoji-only message works
- [ ] Emoji + text works
- [ ] Emoji survives server restart

### Private Messages
- [ ] Send to an online recipient
- [ ] Send to an offline recipient (must show "not online")
- [ ] Cross-room private message works
- [ ] Delivery and read receipts appear
- [ ] Self-message rejected
- [ ] Invalid command rejected
- [ ] Private message with emoji works

### Connection Handling
- [ ] Server unavailable (start client first) — friendly error, no crash
- [ ] Server restart while client is connected — client reports loss
- [ ] Client window close — no server crash, others notified
- [ ] Logout — socket closed, returns to login screen

### GUI
- [ ] No freezing while waiting for messages
- [ ] All buttons respond
- [ ] Window close (X) cleanly destroys the app

