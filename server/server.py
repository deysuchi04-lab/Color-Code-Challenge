import socket
import threading
import json
import random


# =========================================================
# SERVER CONFIGURATION
# =========================================================

HOST = "0.0.0.0"
PORT = 5000


# =========================================================
# CREATE SERVER SOCKET
# =========================================================

server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server.bind(
    (HOST, PORT)
)

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

# Players who have finished the current round.
# A player finishes a round either by:
#   - completing the whole sequence correctly, or
#   - making a wrong move.
#
# The server waits for ALL players before showing
# the final result.
round_finished_players = set()


# =========================================================
# SEND JSON MESSAGE
# =========================================================

def send_message(client_socket, message):

    try:

        data = json.dumps(
            message
        )

        client_socket.send(
            (data + "\n").encode()
        )

    except Exception as e:

        print(
            f"Error sending message: {e}"
        )


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
# GET CURRENT SCORES
# =========================================================

def get_scores():

    return {
        str(player_id): player["score"]
        for player_id, player in players.items()
    }


# =========================================================
# GENERATE NEW COLOUR
# =========================================================

def generate_new_colour():

    global game_sequence

    # -----------------------------------------------
    # First colour
    # -----------------------------------------------

    if len(game_sequence) == 0:

        return random.randint(
            0,
            3
        )

    # -----------------------------------------------
    # Do not allow same colour twice
    # -----------------------------------------------

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
# FIND WINNER
# =========================================================

def find_winner(loser_id=None):

    # -----------------------------------------------
    # No players
    # -----------------------------------------------

    if len(players) == 0:

        return []


    # -----------------------------------------------
    # IMPORTANT:
    #
    # The player who made the wrong sequence
    # must NOT be considered for the winner.
    # -----------------------------------------------

    eligible_players = {
        player_id: player
        for player_id, player in players.items()
        if player_id != loser_id
    }


    # -----------------------------------------------
    # If there are no eligible players
    # -----------------------------------------------

    if len(eligible_players) == 0:

        return []


    # -----------------------------------------------
    # Find highest score among eligible players
    # -----------------------------------------------

    highest_score = max(
        player["score"]
        for player in eligible_players.values()
    )


    # -----------------------------------------------
    # Find all players with highest score
    # -----------------------------------------------

    winners = [
        player_id
        for player_id, player
        in eligible_players.items()
        if player["score"] == highest_score
    ]


    return winners


# =========================================================
# START GAME
# =========================================================

def start_game():

    global game_started
    global game_round
    global game_sequence
    global completed_players
    global round_finished_players

    with lock:

        game_started = True

        game_round = 1

        game_sequence = [
            generate_new_colour()
        ]

        completed_players.clear()
        round_finished_players.clear()


        # -----------------------------------------------
        # Reset all players
        # -----------------------------------------------

        for player in players.values():

            player["score"] = 0

            player["input_index"] = 0

            player["completed_rounds"] = 0

            player["failed_round"] = None

            player["ready"] = True


        scores = get_scores()


        message = {

            "type":
                "round_start",

            "round":
                game_round,

            "sequence":
                game_sequence.copy(),

            "scores":
                scores
        }


    print()
    print("=" * 50)
    print("GAME STARTED")
    print("=" * 50)
    print(f"Round: {game_round}")
    print(f"Sequence: {game_sequence}")
    print()


    broadcast(
        message
    )


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
    global round_finished_players


    print(
        f"[PLAYER {player_id}] "
        f"Connected: {address}"
    )


    # =====================================================
    # ADD PLAYER
    # =====================================================

    with lock:

        players[player_id] = {

            "socket":
                client_socket,

            "address":
                address,

            "ready":
                False,

            "score":
                0,

            "input_index":
                0,

            "completed_rounds":
                0,

            "failed_round":
                None
        }


    # =====================================================
    # SEND WELCOME MESSAGE
    # =====================================================

    send_message(
        client_socket,
        {

            "type":
                "welcome",

            "player_id":
                player_id,

            "message":
                "Connected to Colour Code Challenge Server"
        }
    )


    # =====================================================
    # SEND PLAYER COUNT
    # =====================================================

    broadcast(
        {

            "type":
                "player_count",

            "count":
                len(players)
        }
    )


    try:

        buffer = ""


        while True:

            data = client_socket.recv(
                4096
            )


            if not data:

                break


            buffer += data.decode()


            # =================================================
            # PROCESS COMPLETE JSON MESSAGES
            # =================================================

            while "\n" in buffer:

                message_text, buffer = (
                    buffer.split(
                        "\n",
                        1
                    )
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


                    # =========================================
                    # PING
                    # =========================================

                    if message.get(
                        "type"
                    ) == "ping":

                        send_message(
                            client_socket,
                            {
                                "type":
                                    "pong"
                            }
                        )


                    # =========================================
                    # TEST MESSAGE
                    # =========================================

                    elif message.get(
                        "type"
                    ) == "test":

                        send_message(
                            client_socket,
                            {

                                "type":
                                    "test_response",

                                "message":
                                    "Server received your message"
                            }
                        )


                    # =========================================
                    # PLAYER READY
                    # =========================================

                    elif message.get(
                        "type"
                    ) == "player_ready":

                        should_start_game = False


                        with lock:

                            if player_id in players:

                                players[
                                    player_id
                                ][
                                    "ready"
                                ] = True

                                players[
                                    player_id
                                ][
                                    "score"
                                ] = 0

                                players[
                                    player_id
                                ][
                                    "input_index"
                                ] = 0

                                players[
                                    player_id
                                ][
                                    "completed_rounds"
                                ] = 0

                                players[
                                    player_id
                                ][
                                    "failed_round"
                                ] = None


                        print(
                            f"[PLAYER {player_id}] "
                            "is ready"
                        )


                        # -------------------------------------
                        # SEND READY CONFIRMATION
                        # -------------------------------------

                        send_message(
                            client_socket,
                            {

                                "type":
                                    "ready_ack",

                                "message":
                                    "Player is ready"
                            }
                        )


                        # -------------------------------------
                        # CHECK IF EVERYONE IS READY
                        # -------------------------------------

                        if not game_started:

                            should_start_game = (
                                check_all_players_ready()
                            )


                        # -------------------------------------
                        # START GAME
                        # -------------------------------------

                        if should_start_game:

                            start_game()


                    # =========================================
                    # PLAYER COLOUR CLICK
                    # =========================================

                    elif message.get(
                        "type"
                    ) == "color_click":

                        clicked_colour = (
                            message.get(
                                "color"
                            )
                        )

                        should_start_next_round = False

                        game_over_message = None

                        next_round_message = None

                        with lock:

                            if player_id not in players:

                                continue

                            if not game_started:

                                continue

                            if clicked_colour not in [
                                0,
                                1,
                                2,
                                3
                            ]:

                                continue

                            player = players[
                                player_id
                            ]

                            # A player who has already finished
                            # this round cannot click again.
                            if (
                                player_id
                                in round_finished_players
                            ):

                                continue

                            expected_colour = (
                                game_sequence[
                                    player[
                                        "input_index"
                                    ]
                                ]
                            )

                            print(
                                f"[PLAYER {player_id}] "
                                f"Clicked: {clicked_colour} | "
                                f"Expected: {expected_colour}"
                            )

                            # =================================
                            # WRONG COLOUR
                            # =================================

                            if (
                                clicked_colour
                                != expected_colour
                            ):

                                print()
                                print(
                                    f"[PLAYER {player_id}] "
                                    "WRONG COLOUR!"
                                )

                                # IMPORTANT:
                                # Do NOT stop the whole game.
                                # Only this player is finished.
                                player[
                                    "failed_round"
                                ] = game_round

                                round_finished_players.add(
                                    player_id
                                )

                                failed_players = [
                                    pid
                                    for pid, p
                                    in players.items()
                                    if p[
                                        "failed_round"
                                    ]
                                    == game_round
                                ]

                                finished_players = list(
                                    round_finished_players
                                )

                                # --------------------------------
                                # WAIT FOR OTHER PLAYERS
                                # --------------------------------

                                if (
                                    len(
                                        round_finished_players
                                    )
                                    < len(players)
                                ):

                                    next_round_message = {
                                        "type":
                                            "round_wait",

                                        "message":
                                            "Waiting for other players...",

                                        "score":
                                            player[
                                                "score"
                                            ],

                                        "scores":
                                            get_scores(),

                                        "failed_players":
                                            failed_players,

                                        "finished_players":
                                            finished_players
                                    }

                                else:

                                    # Everyone has finished.
                                    # At least this player failed,
                                    # so end the game now.
                                    game_started = False

                                    completed_players.clear()

                                    for p in players.values():

                                        p[
                                            "ready"
                                        ] = False

                                    scores = get_scores()

                                    loser_ids = (
                                        failed_players
                                    )

                                    winners = [
                                        pid
                                        for pid in players
                                        if pid
                                        not in loser_ids
                                    ]

                                    if winners:

                                        highest_score = max(
                                            players[
                                                pid
                                            ][
                                                "score"
                                            ]
                                            for pid
                                            in winners
                                        )

                                        winners = [
                                            pid
                                            for pid in winners
                                            if players[
                                                pid
                                            ][
                                                "score"
                                            ]
                                            == highest_score
                                        ]

                                    player_stats = {
                                        str(pid): {
                                            "score":
                                                p[
                                                    "score"
                                                ],

                                            "completed_rounds":
                                                p[
                                                    "completed_rounds"
                                                ],

                                            "failed_round":
                                                p[
                                                    "failed_round"
                                                ]
                                        }
                                        for pid, p
                                        in players.items()
                                    }

                                    game_over_message = {
                                        "type":
                                            "game_over",

                                        "player_id":
                                            player_id,

                                        "reason":
                                            "Wrong sequence!",

                                        "scores":
                                            scores,

                                        "winners":
                                            winners,

                                        "loser":
                                            (
                                                loser_ids[
                                                    0
                                                ]
                                                if loser_ids
                                                else None
                                            ),

                                        "losers":
                                            loser_ids,

                                        "player_stats":
                                            player_stats
                                    }

                            # =================================
                            # CORRECT COLOUR
                            # =================================

                            else:

                                player[
                                    "input_index"
                                ] += 1

                                # =================================
                                # COMPLETE ROUND
                                # =================================

                                if (
                                    player[
                                        "input_index"
                                    ]
                                    ==
                                    len(
                                        game_sequence
                                    )
                                ):

                                    round_finished_players.add(
                                        player_id
                                    )

                                    completed_players.add(
                                        player_id
                                    )

                                    player[
                                        "score"
                                    ] += 10

                                    player[
                                        "completed_rounds"
                                    ] += 1

                                    print(
                                        f"[PLAYER {player_id}] "
                                        "completed the round."
                                    )

                                    # --------------------------------
                                    # NOT EVERYONE FINISHED YET
                                    # --------------------------------

                                    if (
                                        len(
                                            round_finished_players
                                        )
                                        <
                                        len(
                                            players
                                        )
                                    ):

                                        next_round_message = {
                                            "type":
                                                "round_wait",

                                            "message":
                                                "Waiting for other players...",

                                            "score":
                                                player[
                                                    "score"
                                                ],

                                            "scores":
                                                get_scores(),

                                            "failed_players":
                                                [
                                                    pid
                                                    for pid, p
                                                    in players.items()
                                                    if p[
                                                        "failed_round"
                                                    ]
                                                    == game_round
                                                ],

                                            "finished_players":
                                                list(
                                                    round_finished_players
                                                )
                                        }

                                    # --------------------------------
                                    # EVERYONE FINISHED
                                    # --------------------------------

                                    else:

                                        any_failed = any(
                                            p[
                                                "failed_round"
                                            ]
                                            ==
                                            game_round
                                            for p
                                            in players.values()
                                        )

                                        if any_failed:

                                            game_started = False

                                            completed_players.clear()

                                            for p in players.values():

                                                p[
                                                    "ready"
                                                ] = False

                                            scores = (
                                                get_scores()
                                            )

                                            loser_ids = [
                                                pid
                                                for pid, p
                                                in players.items()
                                                if p[
                                                    "failed_round"
                                                ]
                                                ==
                                                game_round
                                            ]

                                            winners = [
                                                pid
                                                for pid in players
                                                if pid
                                                not in loser_ids
                                            ]

                                            if winners:

                                                highest_score = max(
                                                    players[
                                                        pid
                                                    ][
                                                        "score"
                                                    ]
                                                    for pid
                                                    in winners
                                                )

                                                winners = [
                                                    pid
                                                    for pid in winners
                                                    if players[
                                                        pid
                                                    ][
                                                        "score"
                                                    ]
                                                    ==
                                                    highest_score
                                                ]

                                            player_stats = {
                                                str(pid): {
                                                    "score":
                                                        p[
                                                            "score"
                                                        ],

                                                    "completed_rounds":
                                                        p[
                                                            "completed_rounds"
                                                        ],

                                                    "failed_round":
                                                        p[
                                                            "failed_round"
                                                        ]
                                                }
                                                for pid, p
                                                in players.items()
                                            }

                                            game_over_message = {
                                                "type":
                                                    "game_over",

                                                "player_id":
                                                    (
                                                        loser_ids[
                                                            0
                                                        ]
                                                        if loser_ids
                                                        else None
                                                    ),

                                                "reason":
                                                    "Wrong sequence!",

                                                "scores":
                                                    scores,

                                                "winners":
                                                    winners,

                                                "loser":
                                                    (
                                                        loser_ids[
                                                            0
                                                        ]
                                                        if loser_ids
                                                        else None
                                                    ),

                                                "losers":
                                                    loser_ids,

                                                "player_stats":
                                                    player_stats
                                            }

                                        else:

                                            # Everyone completed
                                            # correctly -> next round.
                                            game_round += 1

                                            game_sequence.append(
                                                generate_new_colour()
                                            )

                                            completed_players.clear()
                                            round_finished_players.clear()

                                            for p in players.values():

                                                p[
                                                    "input_index"
                                                ] = 0

                                            scores = (
                                                get_scores()
                                            )

                                            next_round_message = {
                                                "type":
                                                    "round_start",

                                                "round":
                                                    game_round,

                                                "sequence":
                                                    game_sequence.copy(),

                                                "scores":
                                                    scores
                                            }

                                            should_start_next_round = True

                                # =================================
                                # PLAYER STILL ENTERING
                                # =================================

                                else:

                                    send_message(
                                        client_socket,
                                        {
                                            "type":
                                                "input_progress",

                                            "progress":
                                                player[
                                                    "input_index"
                                                ],

                                            "total":
                                                len(
                                                    game_sequence
                                                ),

                                            "score":
                                                player[
                                                    "score"
                                                ]
                                        }
                                    )

                        # =================================================
                        # SEND ROUND WAIT
                        # =================================================

                        if (
                            next_round_message is not None
                            and next_round_message.get(
                                "type"
                            )
                            == "round_wait"
                        ):

                            # Broadcast because all players need to
                            # know that the round is still in progress.
                            # Each client decides whether it is itself
                            # finished/failed using failed_players.
                            broadcast(
                                next_round_message
                            )

                        # =================================================
                        # SEND GAME OVER
                        # =================================================

                        if game_over_message is not None:

                            print()
                            print("=" * 50)
                            print("GAME OVER")
                            print("=" * 50)
                            print(
                                f"Final Scores: "
                                f"{game_over_message['scores']}"
                            )
                            print(
                                f"Losers: "
                                f"{game_over_message['losers']}"
                            )
                            print(
                                f"Winners: "
                                f"{game_over_message['winners']}"
                            )
                            print("=" * 50)
                            print()

                            broadcast(
                                game_over_message
                            )

                        # =================================================
                        # START NEXT ROUND
                        # =================================================

                        elif (
                            should_start_next_round
                            and next_round_message is not None
                            and next_round_message.get(
                                "type"
                            )
                            == "round_start"
                        ):

                            print()
                            print("=" * 50)
                            print(
                                f"ROUND {game_round}"
                            )
                            print("=" * 50)
                            print(
                                f"Sequence: "
                                f"{game_sequence}"
                            )
                            print()

                            broadcast(
                                next_round_message
                            )

                except json.JSONDecodeError:

                    print(
                        f"[PLAYER {player_id}] "
                        "Invalid JSON received"
                    )


    except ConnectionResetError:

        print(
            f"[PLAYER {player_id}] "
            "Connection reset"
        )


    except Exception as e:

        print(
            f"[PLAYER {player_id}] "
            f"Error: {e}"
        )


    finally:

        # =====================================================
        # REMOVE PLAYER
        # =====================================================

        with lock:

            if player_id in players:

                del players[
                    player_id
                ]


            completed_players.discard(
                player_id
            )


            remaining_players = (
                len(players)
            )


            if remaining_players == 0:

                game_started = False
                player_count = 0


        try:

            client_socket.close()

        except:

            pass


        print(
            f"[PLAYER {player_id}] "
            "Disconnected"
        )


        # =====================================================
        # UPDATE PLAYER COUNT
        # =====================================================

        broadcast(
            {

                "type":
                    "player_count",

                "count":
                    len(players)
            }
        )


# =========================================================
# ACCEPT PLAYERS
# =========================================================

while True:

    try:

        client_socket, address = (
            server.accept()
        )


        with lock:

            # Reuse the lowest available player ID.
            # This keeps new sessions at Player 1, Player 2, ...
            player_id = 1

            while player_id in players:

                player_id += 1

            player_count = max(
                player_count,
                player_id
            )


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
            f"Active players: "
            f"{len(players)}"
        )


    except KeyboardInterrupt:

        print(
            "\nServer shutting down..."
        )

        break


    except Exception as e:

        print(
            f"Server error: {e}"
        )


# =========================================================
# CLOSE SERVER
# =========================================================

server.close()

print(
    "Server closed."
)