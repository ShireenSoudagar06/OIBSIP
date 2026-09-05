import socket
import threading
import datetime
from database import init_db, register_user, authenticate_user, save_message, get_message_history

HOST = "127.0.0.1"
PORT = 5555

init_db()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"[SERVER] Listening on {HOST}:{PORT}...")

rooms = {}  # room_name -> set of client_sockets
clients = []  # [(client_socket, username, room), ...]
typing_users = {}  # username -> room
private_message_counter = 0
private_messages = {}  # msg_id -> {"from": username, "to": target_username}
lock = threading.Lock()


def broadcast_to_room(message, room, exclude_socket=None):
    with lock:
        if room not in rooms:
            return
        sockets = list(rooms[room])

    for client_socket in sockets:
        if client_socket == exclude_socket:
            continue
        try:
            send_msg(client_socket, message)
        except Exception:
            pass


def send_msg(sock, msg):
    try:
        sock.sendall((msg + "\n").encode("utf-8"))
    except Exception:
        pass


def send_history(client_socket, room):
    history = get_message_history(room)
    send_msg(client_socket, "HISTORY_START")

    if not history:
        send_msg(client_socket, "[SYSTEM] No previous messages in this room.")
    else:
        send_msg(client_socket, "==============================")
        send_msg(client_socket, f"Message history for #{room}")
        send_msg(client_socket, "==============================")

        for username, message, timestamp in history:
            formatted = f"[{timestamp}] {username}: {message}"
            send_msg(client_socket, formatted)

        send_msg(client_socket, "==============================")
        send_msg(client_socket, f"You are now in #{room}")
        send_msg(client_socket, "==============================")

    send_msg(client_socket, "HISTORY_END")


def handle_client(client_socket):
    global private_message_counter
    username = None
    current_room = None
    try:
        data = client_socket.recv(1024)
        if not data:
            client_socket.close()
            return

        raw_message = data.decode("utf-8").strip()
        parts = raw_message.split("|")

        if len(parts) != 4 or parts[0] != "AUTH":
            send_msg(client_socket, "AUTH|fail|Invalid command format")
            client_socket.close()
            return

        action = parts[1]
        username = parts[2]
        password = parts[3]

        if "|" in username or "|" in password:
            send_msg(client_socket, "AUTH|fail|Username and password cannot contain '|'")
            client_socket.close()
            return

        if action == "register":
            success, msg = register_user(username, password)
            response = f"AUTH|success|{msg}" if success else f"AUTH|fail|{msg}"
        elif action == "login":
            success, msg = authenticate_user(username, password)
            response = f"AUTH|success|{msg}" if success else f"AUTH|fail|{msg}"
        else:
            response = "AUTH|fail|Invalid action"

        send_msg(client_socket, response)

        if not response.startswith("AUTH|success"):
            client_socket.close()
            return

        current_room = "general"
        rooms.setdefault(current_room, set()).add(client_socket)
        with lock:
            clients.append((client_socket, username, current_room))

        print(f"[SERVER] {username} connected.")
        broadcast_to_room(f"[SYSTEM] {username} joined the {current_room} room.", current_room)
        send_msg(client_socket, f"[SYSTEM] You are currently in room: {current_room}")
        send_history(client_socket, current_room)

        buffer = ""
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            buffer += data.decode("utf-8")

            while "\n" in buffer:
                message, buffer = buffer.split("\n", 1)
                if not message:
                    continue

                if message.startswith("PRIVATE_READ|"):
                    msg_id = message.split("|", 1)[1]
                    sender_username = None

                    with lock:
                        info = private_messages.get(msg_id)
                        if info:
                            sender_username = info["from"]
                            del private_messages[msg_id]

                    if sender_username:
                        sender_socket = None

                        with lock:
                            for s, u, r in clients:
                                if u == sender_username:
                                    sender_socket = s
                                    break

                        if sender_socket:
                            send_msg(sender_socket, f"PRIVATE_READ|{msg_id}")

                elif message.startswith("/"):
                    if message.startswith("/join "):
                        new_room = message[6:].strip()
                        if not new_room:
                            send_msg(client_socket, "[SYSTEM] Usage: /join roomname")
                            continue

                        old_room = current_room
                        if old_room in rooms:
                            broadcast_to_room(f"[SYSTEM] {username} left the room.", old_room, exclude_socket=client_socket)
                            rooms[old_room].discard(client_socket)

                        should_notify_typing_stop = False
                        with lock:
                            if username in typing_users:
                                del typing_users[username]
                                should_notify_typing_stop = True

                        if should_notify_typing_stop:
                            broadcast_to_room(f"TYPING_STOP|{username}", old_room, exclude_socket=client_socket)

                        current_room = new_room
                        rooms.setdefault(current_room, set()).add(client_socket)
                        broadcast_to_room(f"[SYSTEM] {username} joined the {current_room} room.", current_room)

                        with lock:
                            for i, (s, u, r) in enumerate(clients):
                                if s == client_socket:
                                    clients[i] = (s, u, current_room)
                                    break

                        send_history(client_socket, current_room)

                    elif message == "/rooms":
                        send_msg(client_socket, "ROOMS_START")
                        send_msg(client_socket, "Available rooms:")
                        for room, users in rooms.items():
                            send_msg(client_socket, f"- {room} ({len(users)} users)")
                        send_msg(client_socket, "ROOMS_END")

                    elif message == "/users":
                        with lock:
                            all_users = [u for _, u, _ in clients]
                        send_msg(client_socket, "USERS_START")
                        send_msg(client_socket, f"Online users ({len(all_users)}):")
                        for u in all_users:
                            send_msg(client_socket, f"- {u}")
                        send_msg(client_socket, "USERS_END")

                    elif message == "/roomusers":
                        with lock:
                            room_users = [u for _, u, r in clients if r == current_room]
                        send_msg(client_socket, "ROOMUSERS_START")
                        send_msg(client_socket, f"Users in #{current_room} ({len(room_users)}):")
                        for u in room_users:
                            send_msg(client_socket, f"- {u}")
                        send_msg(client_socket, "ROOMUSERS_END")

                    elif message == "/typing":
                        with lock:
                            typing_users[username] = current_room
                        broadcast_to_room(f"TYPING_START|{username}", current_room, exclude_socket=client_socket)

                    elif message == "/stoptyping":
                        with lock:
                            if username in typing_users:
                                del typing_users[username]
                        broadcast_to_room(f"TYPING_STOP|{username}", current_room, exclude_socket=client_socket)

                    elif message.startswith("/msg "):
                        parts = message.split(" ", 2)
                        if len(parts) < 3:
                            send_msg(client_socket, "[SYSTEM] Usage: /msg <username> <message>")
                            continue

                        target_username = parts[1].strip()
                        private_text = parts[2].strip()

                        if not target_username or not private_text:
                            send_msg(client_socket, "[SYSTEM] Usage: /msg <username> <message>")
                            continue

                        if target_username == username:
                            send_msg(client_socket, "[SYSTEM] You cannot message yourself.")
                            continue

                        target_socket = None
                        with lock:
                            for s, u, r in clients:
                                if u == target_username:
                                    target_socket = s
                                    break

                        if target_socket is None:
                            send_msg(client_socket, f"[SYSTEM] User '{target_username}' is not online.")
                            continue

                        with lock:
                            private_message_counter += 1
                            msg_id = f"PM{private_message_counter}"
                            private_messages[msg_id] = {"from": username, "to": target_username}

                        try:
                            send_msg(target_socket, f"PRIVATE|{msg_id}|{username}|{target_username}|{private_text}")
                            send_msg(client_socket, f"PRIVATE_SENT|{msg_id}|{username}|{target_username}|{private_text}")
                            send_msg(client_socket, f"PRIVATE_DELIVERED|{msg_id}")
                        except Exception:
                            send_msg(client_socket, f"[SYSTEM] Failed to deliver message to '{target_username}'.")

                    else:
                        send_msg(client_socket, "[SYSTEM] Unknown command. Try /join, /rooms, /users, /roomusers, /msg, /typing, or /stoptyping")
                else:
                    timestamp = datetime.datetime.now().strftime("%H:%M")
                    formatted = f"[{timestamp}] {username}: {message}"
                    print(formatted)
                    try:
                        save_message(current_room, username, message)
                    except Exception as e:
                        print(f"[SERVER] Failed to save message: {e}")
                    broadcast_to_room(formatted, current_room)

    except ConnectionResetError:
        pass
    except Exception as e:
        print(f"[SERVER] Error: {e}")
    finally:
        with lock:
            for item in clients:
                if item[0] == client_socket:
                    clients.remove(item)
                    break
            if current_room and current_room in rooms:
                rooms[current_room].discard(client_socket)

        if username:
            print(f"[SERVER] {username} disconnected.")
            should_notify_typing_stop = False
            with lock:
                if username in typing_users:
                    del typing_users[username]
                    should_notify_typing_stop = True
                for msg_id, info in list(private_messages.items()):
                    if info["from"] == username or info["to"] == username:
                        del private_messages[msg_id]
            if should_notify_typing_stop and current_room and current_room in rooms:
                broadcast_to_room(f"TYPING_STOP|{username}", current_room)
            if current_room:
                broadcast_to_room(f"[SYSTEM] {username} left the chat.", current_room)

        client_socket.close()


while True:
    client_socket, addr = server_socket.accept()
    print(f"[SERVER] New connection from {addr}")
    thread = threading.Thread(target=handle_client, args=(client_socket,))
    thread.start()
