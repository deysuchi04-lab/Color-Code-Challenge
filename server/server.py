import socket
import threading
import json

# =========================================================
# SERVER CONFIGURATION
# =========================================================

HOST = "0.0.0.0"
PORT = 5000

server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server.bind((HOST, PORT))
server.listen()

print("=" * 50)
print("COLOUR CODE CHALLENGE SERVER")
print("=" * 50)
print(f"Server started on port {PORT}")
print("Waiting for players...")
print()


# =========================================================
# PLAYER DATA
# =========================================================

players = {}

player_count = 0

lock = threading.Lock()


# =========================================================
# SEND JSON MESSAGE
# =========================================================

def send_message(client_socket, message):

    try:

        data = json.dumps(message)

        client_socket.send(
            (data + "\n").encode()
        )

    except Exception as e:

        print(f"Error sending message: {e}")


# =========================================================
# BROADCAST MESSAGE
# =========================================================

def broadcast(message):

    with lock:

        for player in players.values():

            send_message(
                player["socket"],
                message
            )


# =========================================================
# HANDLE PLAYER
# =========================================================

def handle_player(
    client_socket,
    address,
    player_id
):

    print(
        f"[PLAYER {player_id}] Connected: {address}"
    )

    # Add player
    with lock:

        players[player_id] = {
            "socket": client_socket,
            "address": address
        }

    # Send welcome message
    send_message(
        client_socket,
        {
            "type": "welcome",
            "player_id": player_id,
            "message": "Connected to Colour Code Challenge Server"
        }
    )

    # Send current player count
    broadcast(
        {
            "type": "player_count",
            "count": len(players)
        }
    )

    try:

        buffer = ""

        while True:

            data = client_socket.recv(4096)

            if not data:

                break

            buffer += data.decode()

            # Process complete JSON messages
            while "\n" in buffer:

                message_text, buffer = buffer.split(
                    "\n",
                    1
                )

                if not message_text.strip():

                    continue

                try:

                    message = json.loads(
                        message_text
                    )

                    print(
                        f"[PLAYER {player_id}] "
                        f"Received: {message}"
                    )

                    # -------------------------------------
                    # PING
                    # -------------------------------------

                    if message.get("type") == "ping":

                        send_message(
                            client_socket,
                            {
                                "type": "pong"
                            }
                        )

                    # -------------------------------------
                    # CHAT / TEST MESSAGE
                    # -------------------------------------

                    elif message.get("type") == "test":

                        send_message(
                            client_socket,
                            {
                                "type": "test_response",
                                "message": "Server received your message"
                            }
                        )

                except json.JSONDecodeError:

                    print(
                        f"[PLAYER {player_id}] "
                        "Invalid JSON received"
                    )

    except ConnectionResetError:

        print(
            f"[PLAYER {player_id}] Connection reset"
        )

    except Exception as e:

        print(
            f"[PLAYER {player_id}] Error: {e}"
        )

    finally:

        with lock:

            if player_id in players:

                del players[player_id]

        try:

            client_socket.close()

        except:

            pass

        print(
            f"[PLAYER {player_id}] Disconnected"
        )

        # Update player count
        broadcast(
            {
                "type": "player_count",
                "count": len(players)
            }
        )


# =========================================================
# ACCEPT PLAYERS
# =========================================================

while True:

    try:

        client_socket, address = server.accept()

        with lock:

            player_count += 1

            player_id = player_count

        thread = threading.Thread(
            target=handle_player,
            args=(
                client_socket,
                address,
                player_id
            ),
            daemon=True
        )

        thread.start()

        print(
            f"Active players: {len(players)}"
        )

    except KeyboardInterrupt:

        print("\nServer shutting down...")
        break

    except Exception as e:

        print(
            f"Server error: {e}"
        )


# =========================================================
# CLOSE SERVER
# =========================================================

server.close()

print("Server closed.")