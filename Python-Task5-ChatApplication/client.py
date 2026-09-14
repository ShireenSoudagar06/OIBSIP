import socket
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox

HOST = "127.0.0.1"
PORT = 5555

EMOJI_ROWS = [
    ["😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣"],
    ["😊", "😇", "🙂", "🙃", "😉", "😌", "😍", "🥰"],
    ["😘", "😗", "😙", "😚", "😋", "😛", "😜", "🤪"],
    ["🤔", "🤨", "😐", "😑", "😶", "🙄", "😏"],
    ["😣", "😥", "😮", "🤐", "😯", "😪", "😫"],
    ["🥳", "😎", "🤩", "😭", "😢", "😡", "😠"],
    ["👍", "👎", "👌", "✌️", "🤞", "🤟", "🤘"],
    ["👏", "🙌", "👐", "🤝", "❤️", "🧡", "💛", "💚"],
    ["💙", "💜", "🔥", "⭐", "✨", "🎉", "🎊", "💯"],
    ["🙏", "🎮", "💻", "☕", "🚀", "🌟"],
]


class ChatClient:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chat Application")
        self.root.geometry("900x600")

        self.socket = None
        self.receiver_thread = None
        self.running = False
        self.history_buffer = []
        self.queue = queue.Queue()

        self.current_room = tk.StringVar(value="general")
        self.username = tk.StringVar()
        self.users_buffer = []
        self.roomusers_buffer = []
        self._typing_users = set()
        self._typing_timer = None
        self._typing_active = False
        self._private_messages = {}

        self._build_login_screen()
        self._process_queue()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _build_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = ttk.Frame(self.root, padding="40")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(frame, text="CHAT APPLICATION", font=("", 16, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 20)
        )

        ttk.Label(frame, text="Username:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_user = ttk.Entry(frame, width=30, textvariable=self.username)
        self.entry_user.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="Password:").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_pass = ttk.Entry(frame, width=30, show="*")
        self.entry_pass.grid(row=2, column=1, pady=5)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="Login", command=self._login).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Register", command=self._register).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Exit", command=self._on_close).pack(side="left", padx=5)

        self.entry_user.bind("<Return>", lambda e: self._login())
        self.entry_pass.bind("<Return>", lambda e: self._login())

    def _build_chat_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        top = ttk.Frame(self.root)
        top.pack(fill="x", padx=10, pady=5)

        ttk.Label(top, text="Chat Application", font=("", 12, "bold")).pack(side="left")
        ttk.Label(top, textvariable=self.current_room, font=("", 10)).pack(side="right")

        main = ttk.PanedWindow(self.root, orient="horizontal")
        main.pack(fill="both", expand=True, padx=10, pady=5)

        sidebar = ttk.LabelFrame(main, text="Chat Rooms")
        main.add(sidebar, weight=1)

        ttk.Label(sidebar, text="Rooms").pack(anchor="w", padx=5)
        self.room_listbox = tk.Listbox(sidebar, height=6)
        self.room_listbox.pack(fill="x", padx=5, pady=2)
        self.room_listbox.bind("<<ListboxSelect>>", self._on_room_select)
        ttk.Button(sidebar, text="Refresh Rooms", command=self._refresh_rooms).pack(pady=2)

        ttk.Label(sidebar, text="Online Users").pack(anchor="w", padx=5, pady=(8, 0))
        self.online_users_listbox = tk.Listbox(sidebar, height=6)
        self.online_users_listbox.pack(fill="x", padx=5, pady=2)
        ttk.Button(sidebar, text="Refresh Users", command=self._refresh_users).pack(pady=2)

        ttk.Label(sidebar, text="Users in Room").pack(anchor="w", padx=5, pady=(8, 0))
        self.room_users_listbox = tk.Listbox(sidebar, height=6)
        self.room_users_listbox.pack(fill="x", padx=5, pady=2)
        ttk.Button(sidebar, text="Refresh Room Users", command=self._refresh_roomusers).pack(pady=2)

        chat_frame = ttk.Frame(main)
        main.add(chat_frame, weight=4)

        self.chat_text = tk.Text(chat_frame, wrap="word", state="disabled")
        self.chat_text.pack(fill="both", expand=True)

        self.typing_var = tk.StringVar()
        self.typing_label = ttk.Label(chat_frame, textvariable=self.typing_var, foreground="gray")
        self.typing_label.pack(fill="x", anchor="w")

        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill="x", pady=5)

        self.entry_msg = ttk.Entry(input_frame)
        self.entry_msg.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry_msg.bind("<Return>", lambda e: self._send_message())
        self.entry_msg.bind("<KeyRelease>", self._on_typing)

        ttk.Button(input_frame, text="😊 Emoji", command=self._open_emoji_picker).pack(side="right", padx=(0, 5))
        ttk.Button(input_frame, text="Send", command=self._send_message).pack(side="right")

        bottom = ttk.Frame(self.root)
        bottom.pack(fill="x", padx=10, pady=5)

        ttk.Label(bottom, text=f"Logged in as: {self.username.get()}").pack(side="left")
        ttk.Button(bottom, text="Logout", command=self._logout).pack(side="right")

    def _connect(self):
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((HOST, PORT))
            return True
        except ConnectionRefusedError:
            messagebox.showerror("Connection Error", "Could not connect to the chat server. Is it running?")
            return False
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
            return False

    def _send_auth(self, action, username, password):
        if not self._connect():
            return None
        command = f"AUTH|{action}|{username}|{password}"
        try:
            self.socket.sendall((command + "\n").encode("utf-8"))
            buffer = ""
            while "\n" not in buffer:
                data = self.socket.recv(1024)
                if not data:
                    return None
                buffer += data.decode("utf-8")
            return buffer.split("\n", 1)[0]
        except Exception as e:
            messagebox.showerror("Error", f"Authentication failed: {e}")
            self._close_socket()
            return None

    def _login(self):
        username = self.username.get().strip()
        password = self.entry_pass.get().strip()

        if not username or not password:
            messagebox.showwarning("Input Error", "Username and password cannot be empty.")
            return

        response = self._send_auth("login", username, password)
        if response is None:
            return

        if response.startswith("AUTH|success"):
            messagebox.showinfo("Success", response.split("|")[2])
            self._open_chat()
        else:
            reason = response.split("|")[2] if "|" in response else "Unknown error"
            messagebox.showerror("Login Failed", reason)

    def _register(self):
        username = self.username.get().strip()
        password = self.entry_pass.get().strip()

        if not username or not password:
            messagebox.showwarning("Input Error", "Username and password cannot be empty.")
            return

        response = self._send_auth("register", username, password)
        if response is None:
            return

        if response.startswith("AUTH|success"):
            messagebox.showinfo("Success", response.split("|")[2])
            self.entry_pass.delete(0, "end")
            self._open_chat()
        else:
            reason = response.split("|")[2] if "|" in response else "Unknown error"
            messagebox.showerror("Registration Failed", reason)

    def _open_chat(self):
        self.running = True
        self._build_chat_screen()
        self._append_system(f"Logged in as {self.username.get()}")
        self._refresh_rooms()
        self._refresh_users()
        self._refresh_roomusers()
        self._append_system("Commands: /join <room>, /rooms, /users, /roomusers, /msg <user> <message>, /exit")
        self._append_system("Click '😊 Emoji' to insert emojis into your messages.")
        self.receiver_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receiver_thread.start()

    def _receive_loop(self):
        buffer = ""
        in_history = False
        in_users_block = False
        in_roomusers_block = False
        while self.running:
            try:
                data = self.socket.recv(1024)
                if not data:
                    self.queue.put(('error', 'Connection closed by server.'))
                    break
                buffer += data.decode("utf-8")

                while "\n" in buffer:
                    message, buffer = buffer.split("\n", 1)
                    if not message:
                        continue

                    if message == "HISTORY_START":
                        self.queue.put(('history_start', None))
                        in_history = True
                    elif message == "HISTORY_END":
                        self.queue.put(('history_end', None))
                        in_history = False
                    elif in_history:
                        self.queue.put(('history_line', message))
                    elif message == "ROOMS_START":
                        self.queue.put(('rooms_start', None))
                    elif message == "ROOMS_END":
                        self.queue.put(('rooms_end', None))
                    elif message == "USERS_START":
                        self.queue.put(('users_start', None))
                        in_users_block = True
                    elif message == "USERS_END":
                        self.queue.put(('users_end', None))
                        in_users_block = False
                    elif message == "ROOMUSERS_START":
                        self.queue.put(('roomusers_start', None))
                        in_roomusers_block = True
                    elif message == "ROOMUSERS_END":
                        self.queue.put(('roomusers_end', None))
                        in_roomusers_block = False
                    elif message.startswith("TYPING_START|"):
                        self.queue.put(('typing_start', message.split("|", 1)[1]))
                    elif message.startswith("TYPING_STOP|"):
                        self.queue.put(('typing_stop', message.split("|", 1)[1]))
                    elif message.startswith("PRIVATE_SENT|"):
                        self.queue.put(('private_sent', message.split("|", 1)[1]))
                    elif message.startswith("PRIVATE_DELIVERED|"):
                        self.queue.put(('private_delivered', message.split("|", 1)[1]))
                    elif message.startswith("PRIVATE_READ|"):
                        self.queue.put(('private_read', message.split("|", 1)[1]))
                    elif message.startswith("PRIVATE|"):
                        self.queue.put(('private_in', message.split("|", 1)[1]))
                    elif in_users_block:
                        self.queue.put(('users_line', message))
                    elif in_roomusers_block:
                        self.queue.put(('roomusers_line', message))
                    elif message.startswith("Available rooms:"):
                        self.queue.put(('room_header', message))
                    elif message.startswith("- "):
                        self.queue.put(('room_item', message))
                    elif message.startswith("[SYSTEM]"):
                        self.queue.put(('system', message))
                    else:
                        self.queue.put(('chat', message))
            except OSError:
                if self.running:
                    self.queue.put(('error', 'Connection to server lost.'))
                break
            except Exception as e:
                self.queue.put(('error', f'Receiver error: {e}'))
                break

    def _process_queue(self):
        try:
            while True:
                msg_type, content = self.queue.get_nowait()
                if msg_type == 'chat':
                    self._append_chat(content)
                    self._maybe_notify_public(content)
                elif msg_type == 'system':
                    self._append_system(content)
                    if 'joined the' in content or 'left the room' in content or 'left the chat' in content:
                        self._refresh_users()
                        self._refresh_roomusers()
                elif msg_type == 'history_start':
                    self.history_buffer = []
                    self.chat_text.config(state="normal")
                    self.chat_text.delete("1.0", "end")
                    self.chat_text.config(state="disabled")
                elif msg_type == 'history_end':
                    if self.history_buffer:
                        self.chat_text.config(state="normal")
                        self.chat_text.insert("end", "\n")
                        for line in self.history_buffer:
                            self.chat_text.insert("end", line + "\n")
                        self.chat_text.insert("end", "\n")
                        self.chat_text.config(state="disabled")
                        self.chat_text.see("end")
                    self.history_buffer = []
                elif msg_type == 'history_line':
                    self.history_buffer.append(content)
                elif msg_type == 'rooms_start':
                    self.room_listbox.delete(0, "end")
                elif msg_type == 'room_header':
                    pass
                elif msg_type == 'room_item':
                    self.room_listbox.insert("end", content)
                elif msg_type == 'rooms_end':
                    pass
                elif msg_type == 'users_start':
                    self.users_buffer = []
                elif msg_type == 'users_line':
                    self.users_buffer.append(content)
                elif msg_type == 'users_end':
                    if hasattr(self, 'online_users_listbox'):
                        self.online_users_listbox.delete(0, "end")
                        for line in self.users_buffer:
                            if line.startswith("- "):
                                self.online_users_listbox.insert("end", line[2:])
                    self.users_buffer = []
                elif msg_type == 'roomusers_start':
                    self.roomusers_buffer = []
                elif msg_type == 'roomusers_line':
                    self.roomusers_buffer.append(content)
                elif msg_type == 'roomusers_end':
                    if hasattr(self, 'room_users_listbox'):
                        self.room_users_listbox.delete(0, "end")
                        for line in self.roomusers_buffer:
                            if line.startswith("- "):
                                self.room_users_listbox.insert("end", line[2:])
                    self.roomusers_buffer = []
                elif msg_type == 'typing_start':
                    self._add_typing_user(content)
                elif msg_type == 'typing_stop':
                    self._remove_typing_user(content)
                elif msg_type == 'private_sent':
                    parts = content.split("|", 3)
                    if len(parts) == 4:
                        msg_id, sender, target, text = parts
                        self._append_private_outgoing(msg_id, target, text, "✓")
                elif msg_type == 'private_delivered':
                    self._update_private_status(content, "✓✓")
                elif msg_type == 'private_read':
                    self._update_private_status(content, "✓✓ Read")
                elif msg_type == 'private_in':
                    parts = content.split("|", 3)
                    if len(parts) == 4:
                        msg_id, sender, target, text = parts
                        self._append_chat(f"[PRIVATE] {sender} → You: {text}")
                        self._maybe_notify_private(sender, text)
                        try:
                            self.socket.sendall((f"PRIVATE_READ|{msg_id}\n").encode("utf-8"))
                        except OSError:
                            pass
                elif msg_type == 'error':
                    self._append_system(f"[ERROR] {content}")
        except queue.Empty:
            pass

        self.root.after(100, self._process_queue)

    def _append_chat(self, message):
        self.chat_text.config(state="normal")
        self.chat_text.insert("end", message + "\n")
        self.chat_text.config(state="disabled")
        self.chat_text.see("end")

    def _append_system(self, message):
        self.chat_text.config(state="normal")
        self.chat_text.insert("end", message + "\n")
        self.chat_text.config(state="disabled")
        self.chat_text.see("end")

    def _send_message(self):
        self._send_typing_stop()
        message = self.entry_msg.get().strip()
        if not message or not self.socket:
            return

        if message.lower() == "/exit":
            self._logout()
            return

        try:
            self.socket.sendall((message + "\n").encode("utf-8"))
            self.entry_msg.delete(0, "end")
        except OSError:
            messagebox.showerror("Error", "Could not send message. Connection lost.")
            self._logout()

    def _on_room_select(self, event):
        selection = self.room_listbox.curselection()
        if not selection:
            return
        line = self.room_listbox.get(selection[0])
        if line.startswith("-"):
            room_name = line[1:].split("(")[0].strip()
            self._join_room(room_name)

    def _join_room(self, room_name):
        self._send_typing_stop()
        if not self.socket:
            return
        try:
            self.socket.sendall((f"/join {room_name}\n").encode("utf-8"))
            self.current_room.set(f"Room: {room_name}")
            self._refresh_users()
            self._refresh_roomusers()
        except OSError:
            messagebox.showerror("Error", "Could not join room. Connection lost.")
            self._logout()

    def _refresh_rooms(self):
        if not self.socket:
            return
        try:
            self.socket.sendall("/rooms\n".encode("utf-8"))
        except OSError:
            pass

    def _refresh_users(self):
        if not self.socket:
            return
        try:
            self.socket.sendall("/users\n".encode("utf-8"))
        except OSError:
            pass

    def _refresh_roomusers(self):
        if not self.socket:
            return
        try:
            self.socket.sendall("/roomusers\n".encode("utf-8"))
        except OSError:
            pass

    def _is_window_focused(self):
        try:
            focused = self.root.focus_displayof()
            return focused is not None
        except Exception:
            return True

    def _show_desktop_notification(self, title, message):
        try:
            if not self._is_window_focused():
                threading.Thread(
                    target=self._show_toast_windows,
                    args=(title, message),
                    daemon=True,
                ).start()
        except Exception:
            pass

    def _show_toast_windows(self, title, message):
        import subprocess
        safe_title = title.replace('"', "'")
        safe_message = message.replace('"', "'").replace("\n", " ")
        ps_script = (
            "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null | Out-Null;"
            "[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] > $null | Out-Null;"
            "$xml = @\"\n"
            "<toast><visual><binding template='ToastGeneric'><text>" + safe_title + "</text><text>" + safe_message + "</text></binding></visual></toast>\n"
            "\"@;"
            "$toastXml = New-Object Windows.Data.Xml.Dom.XmlDocument;"
            "$toastXml.LoadXml($xml);"
            "$appId = '{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\WindowsPowerShell\\v1.0\\powershell.exe';"
            "$toast = [Windows.UI.Notifications.ToastNotification]::new($toastXml);"
            "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($appId).Show($toast);"
        )
        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                capture_output=True,
                timeout=5,
            )
        except Exception:
            try:
                import tkinter.messagebox as mb
                self.root.after(0, lambda: mb.showinfo(safe_title, safe_message))
            except Exception:
                pass

    def _maybe_notify_public(self, formatted_line):
        try:
            import re
            m = re.match(r"\[(\d{1,2}:\d{2})\]\s+([^:]+):\s+(.*)", formatted_line)
            if not m:
                return
            sender = m.group(2)
            if sender == self.username.get():
                return
            text = m.group(3)
            self._show_desktop_notification("New message", f"{sender}: {text}")
        except Exception:
            pass

    def _maybe_notify_private(self, sender, text):
        try:
            self._show_desktop_notification("Private message", f"{sender}: {text}")
        except Exception:
            pass

    def _open_emoji_picker(self):
        if hasattr(self, "_emoji_picker") and self._emoji_picker.winfo_exists():
            self._emoji_picker.lift()
            return

        picker = tk.Toplevel(self.root)
        self._emoji_picker = picker
        picker.title("Emoji Picker")
        picker.resizable(False, False)
        picker.transient(self.root)
        picker.grab_set()

        for row_idx, row in enumerate(EMOJI_ROWS):
            for col_idx, emoji in enumerate(row):
                btn = tk.Button(
                    picker,
                    text=emoji,
                    font=("Segoe UI Emoji", 12),
                    width=3,
                    height=1,
                    command=lambda e=emoji: self._insert_emoji(e),
                )
                btn.grid(row=row_idx, column=col_idx, padx=2, pady=2)

        close_btn = ttk.Button(picker, text="Close", command=picker.destroy)
        close_btn.grid(row=len(EMOJI_ROWS), column=0, columnspan=8, pady=(4, 6), sticky="ew")

        picker.update_idletasks()
        width = picker.winfo_reqwidth()
        height = picker.winfo_reqheight()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (width // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (height // 2)
        picker.geometry(f"+{x}+{y}")

    def _insert_emoji(self, emoji):
        if self.entry_msg:
            self.entry_msg.insert(tk.INSERT, emoji)
            self.entry_msg.focus_set()
        if hasattr(self, "_emoji_picker") and self._emoji_picker.winfo_exists():
            self._emoji_picker.destroy()

    def _on_typing(self, event):
        if not self.running or not self.socket:
            return
        text = self.entry_msg.get().strip()

        if text and not self._typing_active:
            self._send_typing("/typing")
            self._typing_active = True
        elif not text and self._typing_active:
            self._send_typing_stop()
            return

        if self._typing_timer:
            self.root.after_cancel(self._typing_timer)
        if text:
            self._typing_timer = self.root.after(2000, self._send_typing_stop)

    def _send_typing(self, command):
        try:
            self.socket.sendall((command + "\n").encode("utf-8"))
        except OSError:
            pass

    def _send_typing_stop(self):
        self._typing_active = False
        if self._typing_timer:
            self.root.after_cancel(self._typing_timer)
            self._typing_timer = None
        self._send_typing("/stoptyping")

    def _add_typing_user(self, username):
        self._typing_users.add(username)
        self._update_typing_label()

    def _remove_typing_user(self, username):
        self._typing_users.discard(username)
        self._update_typing_label()

    def _update_typing_label(self):
        if not self._typing_users:
            self.typing_var.set("")
            return

        users = sorted(self._typing_users)
        if len(users) == 1:
            self.typing_var.set(f"{users[0]} is typing...")
        else:
            self.typing_var.set(f"{', '.join(users[:-1])} and {users[-1]} are typing...")

    def _append_private_outgoing(self, msg_id, target, text, status="✓"):
        self._private_messages[msg_id] = {"target": target, "text": text}
        display = f"[PRIVATE] You → {target}: {text} {status}"
        tag = f"pm_{msg_id}"
        self.chat_text.config(state="normal")
        self.chat_text.insert("end", display + "\n", tag)
        self.chat_text.config(state="disabled")
        self.chat_text.see("end")

    def _update_private_status(self, msg_id, suffix):
        info = self._private_messages.get(msg_id)
        if not info:
            return
        tag = f"pm_{msg_id}"
        ranges = self.chat_text.tag_ranges(tag)
        new_text = f"[PRIVATE] You → {info['target']}: {info['text']} {suffix}"
        if ranges:
            start = ranges[0]
            end = ranges[1]
            self.chat_text.config(state="normal")
            self.chat_text.delete(start, end)
            self.chat_text.insert(start, new_text + "\n", tag)
            self.chat_text.config(state="disabled")
        else:
            self.chat_text.config(state="normal")
            self.chat_text.insert("end", new_text + "\n")
            self.chat_text.config(state="disabled")
            self.chat_text.see("end")

    def _logout(self):
        self._send_typing_stop()
        self.running = False
        self._close_socket()
        self.socket = None
        self._build_login_screen()

    def _close_socket(self):
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

    def _on_close(self):
        self._send_typing_stop()
        self.running = False
        self._close_socket()
        self.root.destroy()


if __name__ == "__main__":
    ChatClient()
