import socket
import threading
import json
import random

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
# GAME DATA
# =========================================================

game_started = False

game_round = 0

game_sequence = []

completed_players = set()


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

        sockets = [
            player["socket"]
            for player in players.values()
        ]

    for client_socket in sockets:

        send_message(
            client_socket,
            message
        )


# =========================================================
# GENERATE NEW COLOUR
# =========================================================

def generate_new_colour():

    global game_sequence

    # First colour
    if len(game_sequence) == 0:

        return random.randint(0, 3)

    # Don't allow same colour twice
    previous = game_sequence[-1]

    available = [
        i
        for i in range(4)
        if i != previous
    ]

    return random.choice(
        available
    )


# =========================================================
# START GAME
# =========================================================

def start_game():

    global game_started
    global game_round
    global game_sequence
    global completed_players

    with lock:

        game_started = True

        game_round = 1

        game_sequence = [
            generate_new_colour()
        ]

        completed_players.clear()

        # Reset player data
        for player in players.values():

            player["score"] = 0
            player["input_index"] = 0
            player["ready"] = True

        scores = {
            str(player_id): player["score"]
            for player_id, player in players.items()
        }

        message = {
            "type": "round_start",
            "round": game_round,
            "sequence": game_sequence.copy(),
            "scores": scores
        }

    print()
    print("=" * 50)
    print("GAME STARTED")
    print("=" * 50)
    print(f"Round: {game_round}")
    print(f"Sequence: {game_sequence}")
    print()

    broadcast(message)


# =========================================================
# CHECK IF ALL PLAYERS ARE READY
# =========================================================

def check_all_players_ready():

    with lock:

        if len(players) == 0:

            return False

        for player in players.values():

            if not player["ready"]:

                return False

        return True


# =========================================================
# HANDLE PLAYER
# =========================================================

def handle_player(
    client_socket,
    address,
    player_id
):

    global game_started
    global game_round
    global game_sequence
    global completed_players

    print(
        f"[PLAYER {player_id}] Connected: {address}"
    )

    # -----------------------------------------------------
    # ADD PLAYER
    # -----------------------------------------------------

    with lock:

        players[player_id] = {
            "socket": client_socket,
            "address": address,
            "ready": False,
            "score": 0,
            "input_index": 0
        }

    # -----------------------------------------------------
    # SEND WELCOME MESSAGE
    # -----------------------------------------------------

    send_message(
        client_socket,
        {
            "type": "welcome",
            "player_id": player_id,
            "message": "Connected to Colour Code Challenge Server"
        }
    )

    # -----------------------------------------------------
    # SEND CURRENT PLAYER COUNT
    # -----------------------------------------------------

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

            # ------------------------------------------------
            # PROCESS COMPLETE JSON MESSAGES
            # ------------------------------------------------

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

                    # ========================================
                    # PING
                    # ========================================

                    if message.get("type") == "ping":

                        send_message(
                            client_socket,
                            {
                                "type": "pong"
                            }
                        )

                    # ========================================
                    # TEST MESSAGE
                    # ========================================

                    elif message.get("type") == "test":

                        send_message(
                            client_socket,
                            {
                                "type": "test_response",
                                "message": "Server received your message"
                            }
                        )

                    # ========================================
                    # PLAYER READY
                    # ========================================

                    elif message.get("type") == "player_ready":

                        should_start_game = False

                        with lock:

                            if player_id in players:

                                players[player_id]["ready"] = True

                                players[player_id]["score"] = 0

                                players[player_id]["input_index"] = 0

                        print(
                            f"[PLAYER {player_id}] "
                            "is ready"
                        )

                        # Send confirmation
                        send_message(
                            client_socket,
                            {
                                "type": "ready_ack",
                                "message": "Player is ready"
                            }
                        )

                        # Check whether everybody is ready
                        if not game_started:

                            should_start_game = (
                                check_all_players_ready()
                            )

                        if should_start_game:

                            start_game()

                    # ========================================
                    # PLAYER COLOUR CLICK
                    # ========================================

                    elif message.get("type") == "color_click":

                        clicked_colour = message.get(
                            "color"
                        )

                        should_start_next_round = False

                        game_over_message = None

                        with lock:

                            if player_id not in players:

                                continue

                            # Game must be running
                            if not game_started:

                                continue

                            # Colour must be valid
                            if clicked_colour not in [0, 1, 2, 3]:

                                continue

                            player = players[player_id]

                            # Ignore clicks after player
                            # already completed this round
                            if player_id in completed_players:

                                continue

                            expected_colour = (
                                game_sequence[
                                    player["input_index"]
                                ]
                            )

                            print(
                                f"[PLAYER {player_id}] "
                                f"Clicked: {clicked_colour} | "
                                f"Expected: {expected_colour}"
                            )

                            # --------------------------------
                            # WRONG COLOUR
                            # --------------------------------

                            if clicked_colour != expected_colour:

                                print(
                                    f"[PLAYER {player_id}] "
                                    "Wrong colour!"
                                )

                                game_started = False

                                completed_players.clear()

                                for p in players.values():

                                    p["ready"] = False

                                game_over_message = {
                                    "type": "game_over",
                                    "player_id": player_id,
                                    "reason": "Wrong sequence!",
                                    "scores": {
                                        str(pid): p["score"]
                                        for pid, p in players.items()
                                    }
                                }

                            # --------------------------------
                            # CORRECT COLOUR
                            # --------------------------------

                            else:

                                player["input_index"] += 1

                                # --------------------------------
                                # COMPLETE ROUND
                                # --------------------------------

                                if (
                                    player["input_index"]
                                    == len(game_sequence)
                                ):

                                    completed_players.add(
                                        player_id
                                    )

                                    print(
                                        f"[PLAYER {player_id}] "
                                        "completed the round."
                                    )

                                    # Give points
                                    player["score"] += 10

                                    # --------------------------------
                                    # ALL PLAYERS COMPLETED
                                    # --------------------------------

                                    if (
                                        len(completed_players)
                                        == len(players)
                                    ):

                                        game_round += 1

                                        game_sequence.append(
                                            generate_new_colour()
                                        )

                                        completed_players.clear()

                                        for p in players.values():

                                            p["input_index"] = 0

                                        scores = {
                                            str(pid): p["score"]
                                            for pid, p
                                            in players.items()
                                        }

                                        next_round_message = {
                                            "type": "round_start",
                                            "round": game_round,
                                            "sequence": game_sequence.copy(),
                                            "scores": scores
                                        }

                                        should_start_next_round = True

                        # ----------------------------------------
                        # SEND GAME OVER
                        # ----------------------------------------

                        if game_over_message is not None:

                            print()
                            print("=" * 50)
                            print("GAME OVER")
                            print("=" * 50)
                            print()

                            broadcast(
                                game_over_message
                            )

                        # ----------------------------------------
                        # START NEXT ROUND
                        # ----------------------------------------

                        elif should_start_next_round:

                            print()
                            print("=" * 50)
                            print(
                                f"ROUND {game_round}"
                            )
                            print("=" * 50)
                            print(
                                f"Sequence: {game_sequence}"
                            )
                            print()

                            broadcast(
                                next_round_message
                            )

                        # ----------------------------------------
                        # ONE PLAYER FINISHED
                        # ----------------------------------------

                        else:

                            send_message(
                                client_socket,
                                {
                                    "type": "round_wait",
                                    "message":
                                    "Waiting for other players..."
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

        # -----------------------------------------------------
        # REMOVE PLAYER
        # -----------------------------------------------------

        with lock:

            if player_id in players:

                del players[player_id]

            completed_players.discard(
                player_id
            )

            remaining_players = len(players)

            if remaining_players == 0:

                game_started = False

        try:

            client_socket.close()

        except:

            pass

        print(
            f"[PLAYER {player_id}] Disconnected"
        )

        # -----------------------------------------------------
        # UPDATE PLAYER COUNT
        # -----------------------------------------------------

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