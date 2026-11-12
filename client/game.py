import pygame
import random
import time

from client import NetworkClient


# =========================================================
# INITIALIZE PYGAME
# =========================================================

pygame.init()


# =========================================================
# WINDOW
# =========================================================

WIDTH = 900
HEIGHT = 650

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "Colour Code Challenge"
)

clock = pygame.time.Clock()


# =========================================================
# FONTS
# =========================================================

TITLE_FONT = pygame.font.Font(
    None,
    64
)

BIG_FONT = pygame.font.Font(
    None,
    52
)

FONT = pygame.font.Font(
    None,
    36
)

SMALL_FONT = pygame.font.Font(
    None,
    28
)


# =========================================================
# COLOURS
# =========================================================

BACKGROUND = (
    25,
    25,
    35
)

WHITE = (
    255,
    255,
    255
)

GRAY = (
    160,
    160,
    160
)

RED = (
    220,
    60,
    60
)

BLUE = (
    60,
    110,
    230
)

GREEN = (
    60,
    190,
    100
)

YELLOW = (
    230,
    200,
    60
)

COLORS = [
    RED,
    BLUE,
    GREEN,
    YELLOW
]

COLOR_NAMES = [
    "RED",
    "BLUE",
    "GREEN",
    "YELLOW"
]


# =========================================================
# GAME STATES
# =========================================================

MENU = "menu"
WAITING = "waiting"
COUNTDOWN = "countdown"
SHOW_SEQUENCE = "show_sequence"
PLAYING = "playing"
GAME_OVER = "game_over"

game_state = MENU


# =========================================================
# GAME VARIABLES
# =========================================================

sequence = []

player_sequence = []

round_number = 1

score = 0

countdown_start = 0

sequence_start = 0

message = ""

waiting_for_players = False

input_locked = False

final_scores = {}

game_result = ""

winner_ids = []

loser_id = None

# Per-player final statistics
player_stats = {}


# =========================================================
# BUTTONS
# =========================================================

start_button = pygame.Rect(
    325,
    330,
    250,
    70
)

play_again_button = pygame.Rect(
    325,
    420,
    250,
    70
)


# =========================================================
# COLOUR BUTTONS
# =========================================================

color_buttons = []

for i in range(4):

    x = 120 + i * 190

    button = pygame.Rect(
        x,
        400,
        130,
        130
    )

    color_buttons.append(
        button
    )


# =========================================================
# DRAW TEXT
# =========================================================

def draw_text(
    text,
    font,
    color,
    x,
    y,
    center=True
):

    image = font.render(
        str(text),
        True,
        color
    )

    if center:

        rect = image.get_rect(
            center=(x, y)
        )

    else:

        rect = image.get_rect(
            topleft=(x, y)
        )

    screen.blit(
        image,
        rect
    )


# =========================================================
# START COUNTDOWN
# =========================================================

def start_countdown():

    global countdown_start
    global game_state

    countdown_start = time.time()

    game_state = COUNTDOWN


# =========================================================
# SHOW SEQUENCE
# =========================================================

def show_sequence():

    global sequence_start
    global game_state
    global player_sequence
    global input_locked

    player_sequence = []

    input_locked = False

    sequence_start = time.time()

    game_state = SHOW_SEQUENCE


# =========================================================
# START NEW GAME
# =========================================================

def reset_game():

    global sequence
    global player_sequence
    global round_number
    global score
    global message
    global game_state
    global waiting_for_players
    global input_locked
    global final_scores
    global game_result
    global winner_ids
    global loser_id
    global player_stats
    global my_completed_rounds
    global my_failed_round

    sequence = []

    player_sequence = []

    round_number = 1

    score = 0

    message = ""

    final_scores = {}

    game_result = ""

    winner_ids = []

    loser_id = None

    player_stats = {}

    my_completed_rounds = 0
    my_failed_round = None

    waiting_for_players = True

    input_locked = True

    # -----------------------------------------------------
    # IMPORTANT:
    # The server creates the first sequence.
    # -----------------------------------------------------

    game_state = WAITING


# =========================================================
# NEXT ROUND
# =========================================================

# The server controls the next round.
#
# Therefore this function is kept only for compatibility
# with the original structure and is no longer called
# locally.
# =========================================================

def next_round():

    pass


# =========================================================
# NETWORK CONNECTION
# =========================================================

network = NetworkClient()

print()
print(
    "Connecting game to Colour Code Challenge Server..."
)

if network.connect():

    print(
        "Game connected to server."
    )

else:

    print(
        "Could not connect to server."
    )

    print(
        "Make sure server/server.py is running."
    )


player_id = None

server_player_count = 0


# =========================================================
# MAIN LOOP
# =========================================================

running = True

while running:

    clock.tick(60)


    # =====================================================
    # RECEIVE SERVER MESSAGES
    # =====================================================

    while True:

        network_message = (
            network.get_message()
        )

        if network_message is None:

            break


        message_type = (
            network_message.get(
                "type"
            )
        )


        # =================================================
        # WELCOME
        # =================================================

        if message_type == "welcome":

            player_id = (
                network_message.get(
                    "player_id"
                )
            )

            print()

            print(
                "Welcome from server."
            )

            print(
                f"Player ID: {player_id}"
            )


        # =================================================
        # PLAYER COUNT
        # =================================================

        elif message_type == "player_count":

            server_player_count = (
                network_message.get(
                    "count",
                    0
                )
            )

            print(
                f"Players connected: "
                f"{server_player_count}"
            )


        # =================================================
        # READY ACK
        # =================================================

        elif message_type == "ready_ack":

            print(
                "Server confirmed that player is ready."
            )


        # =================================================
        # ROUND START
        # =================================================

        elif message_type == "round_start":

            global_round = (
                network_message.get(
                    "round",
                    1
                )
            )

            new_sequence = (
                network_message.get(
                    "sequence",
                    []
                )
            )

            scores = (
                network_message.get(
                    "scores",
                    {}
                )
            )

            round_number = global_round

            sequence = [
                int(value)
                for value in new_sequence
            ]

            # ------------------------------------------------
            # GET THIS PLAYER'S SCORE
            # ------------------------------------------------

            if player_id is not None:

                score = scores.get(
                    str(player_id),
                    score
                )

            final_scores = scores.copy()

            waiting_for_players = False

            input_locked = False

            print()

            print(
                "=" * 40
            )

            print(
                f"ROUND {round_number}"
            )

            print(
                f"Sequence received: "
                f"{sequence}"
            )

            print(
                f"Score: {score}"
            )

            print(
                "=" * 40
            )


            # ------------------------------------------------
            # ROUND 1 STARTS WITH COUNTDOWN
            # ------------------------------------------------

            if round_number == 1:

                start_countdown()

            else:

                show_sequence()


        # =================================================
        # WAIT FOR OTHER PLAYERS
        # =================================================

        elif message_type == "round_wait":

            # ------------------------------------------------
            # Do NOT lock the buttons after the first click.
            #
            # Only lock input when the player has already
            # entered the complete sequence.
            # ------------------------------------------------

            server_score = (
                network_message.get(
                    "score",
                    score
                )
            )

            server_scores = (
                network_message.get(
                    "scores",
                    final_scores
                )
            )

            score = server_score

            final_scores = server_scores.copy()

            # ------------------------------------------------
            # IMPORTANT:
            #
            # The server broadcasts the same round_wait message
            # to ALL players.
            #
            # Therefore, the "failed" field by itself cannot be
            # used to lock the client. If Player 1 failed, Player 2
            # must still be allowed to continue entering colours.
            #
            # Instead, check whether THIS player's ID is inside
            # the failed_players list.
            # ------------------------------------------------

            failed_players = (
                network_message.get(
                    "failed_players",
                    []
                )
            )

            failed_this_round = (
                player_id is not None
                and (
                    player_id in failed_players
                    or str(player_id) in [
                        str(pid)
                        for pid in failed_players
                    ]
                )
            )

            if failed_this_round:

                # This player made a mistake.
                # Lock only THIS player's buttons.
                # Other players remain free to enter input.
                waiting_for_players = True

                input_locked = True

                print(
                    "You entered the wrong sequence."
                )

            elif (
                len(player_sequence)
                >= len(sequence)
                and len(sequence) > 0
            ):

                waiting_for_players = True

                input_locked = True

                print(
                    "Waiting for other players..."
                )

            else:

                # Another player may have failed or completed,
                # but THIS player still has input to enter.
                waiting_for_players = False

                input_locked = False

                print(
                    "Player can continue entering "
                    "the sequence."
                )


        # =================================================
        # INPUT PROGRESS
        # =================================================

        elif message_type == "input_progress":

            progress = (
                network_message.get(
                    "progress",
                    len(player_sequence)
                )
            )

            total = (
                network_message.get(
                    "total",
                    len(sequence)
                )
            )

            server_score = (
                network_message.get(
                    "score",
                    score
                )
            )

            score = server_score

            print(
                f"Server progress: "
                f"{progress}/{total}"
            )


        # =================================================
        # GAME OVER
        # =================================================

        elif message_type == "game_over":

            reason = (
                network_message.get(
                    "reason",
                    "Game Over"
                )
            )

            scores = (
                network_message.get(
                    "scores",
                    {}
                )
            )

            winner_ids = (
                network_message.get(
                    "winners",
                    []
                )
            )

            loser_id = (
                network_message.get(
                    "loser",
                    None
                )
            )

            # ------------------------------------------------
            # GET PER-PLAYER FINAL STATISTICS
            # ------------------------------------------------
            #
            # Expected server format:
            #
            # "player_stats": {
            #     "1": {
            #         "score": 30,
            #         "completed_rounds": 3,
            #         "failed_round": None
            #     },
            #     "2": {
            #         "score": 20,
            #         "completed_rounds": 2,
            #         "failed_round": 3
            #     }
            # }
            #
            # Keep a fallback for older server messages so the
            # client does not crash if player_stats is missing.
            # ------------------------------------------------

            received_player_stats = (
                network_message.get(
                    "player_stats",
                    {}
                )
            )

            if received_player_stats:

                player_stats = received_player_stats.copy()

            else:

                # Fallback: build basic statistics from scores.
                player_stats = {}

                for pid, player_score in scores.items():

                    player_stats[str(pid)] = {
                        "score": player_score,
                        "completed_rounds": 0,
                        "failed_round": None
                    }

                # If the server has not yet sent per-player
                # round statistics, use the current round as
                # the best available information.
                for pid in player_stats:

                    if (
                        str(pid)
                        == str(loser_id)
                    ):

                        player_stats[pid][
                            "completed_rounds"
                        ] = max(
                            0,
                            round_number - 1
                        )

                        player_stats[pid][
                            "failed_round"
                        ] = round_number

                    else:

                        player_stats[pid][
                            "completed_rounds"
                        ] = round_number


            final_scores = scores.copy()

            # ------------------------------------------------
            # GET THIS PLAYER'S FINAL SCORE AND STATISTICS
            # ------------------------------------------------

            if player_id is not None:

                score = scores.get(
                    str(player_id),
                    score
                )

            my_stats = player_stats.get(
                str(player_id),
                {}
            )

            my_completed_rounds = my_stats.get(
                "completed_rounds",
                round_number
            )

            my_failed_round = my_stats.get(
                "failed_round",
                None
            )

            # ------------------------------------------------
            # GET ALL LOSERS
            # ------------------------------------------------
            #
            # When both players make a wrong move in the same
            # round, there is no winner. Both players are losers.
            # ------------------------------------------------

            loser_ids = (
                network_message.get(
                    "losers",
                    []
                )
            )

            # Backward compatibility with the older server:
            # if "losers" is missing, use the single "loser".
            if not loser_ids and loser_id is not None:

                loser_ids = [
                    loser_id
                ]

            loser_ids = [
                int(pid)
                for pid in loser_ids
            ]

            # ------------------------------------------------
            # DETERMINE RESULT
            # ------------------------------------------------

            if player_id in winner_ids:

                game_result = "YOU WIN!"

                # Winner did not make the wrong move.
                # Tell them who caused the game to end.
                if len(loser_ids) == 1:

                    message = (
                        f"Player {loser_ids[0]} entered "
                        f"the wrong sequence."
                    )

                elif len(loser_ids) > 1:

                    message = (
                        "The other players entered "
                        "the wrong sequence."
                    )

                else:

                    message = "Game completed."

            elif player_id in loser_ids:

                # This player is one of the players who made
                # a wrong move.

                game_result = "YOU LOST!"

                # If every player failed in this round,
                # there is no winner.
                if (
                    len(loser_ids)
                    == len(scores)
                    and len(loser_ids) > 1
                ):

                    if len(loser_ids) == 2:

                        message = (
                            "You both entered the wrong sequence!"
                        )

                    else:

                        message = (
                            "All players entered the wrong sequence!"
                        )

                else:

                    message = (
                        "You entered the wrong sequence!"
                    )

            else:

                # Fallback for an unexpected server state.
                game_result = "GAME OVER"

                message = reason

            # Store the final round information locally.
            # This is used only if the server does not provide
            # per-player statistics.
            round_number = (
                my_failed_round
                if my_failed_round is not None
                else my_completed_rounds
            )

            waiting_for_players = False

            input_locked = True

            game_state = GAME_OVER


            print()

            print(
                "=" * 40
            )

            print(
                "GAME OVER"
            )

            print(
                f"Result: {game_result}"
            )

            print(
                f"Reason: {reason}"
            )

            print(
                f"Final Score: {score}"
            )

            print(
                f"All Scores: {scores}"
            )

            print(
                "=" * 40
            )


        # =================================================
        # OTHER SERVER MESSAGES
        # =================================================

        else:

            print(
                "Message from server:",
                network_message
            )


    # =====================================================
    # EVENTS
    # =====================================================

    for event in pygame.event.get():


        # =================================================
        # QUIT
        # =================================================

        if event.type == pygame.QUIT:

            running = False


        # =================================================
        # MENU
        # =================================================

        if (
            event.type
            == pygame.MOUSEBUTTONDOWN
            and start_button.collidepoint(
                event.pos
            )
            and game_state == MENU
        ):

            network.send_message(
                {
                    "type":
                        "player_ready"
                }
            )

            print(
                "Player is ready."
            )

            reset_game()


        # =================================================
        # PLAYING
        # =================================================

        elif (
            game_state == PLAYING
            and not input_locked
        ):

            if (
                event.type
                == pygame.MOUSEBUTTONDOWN
            ):

                for i, button in enumerate(
                    color_buttons
                ):

                    if button.collidepoint(
                        event.pos
                    ):

                        # ---------------------------------
                        # ADD LOCAL CLICK
                        # ---------------------------------

                        player_sequence.append(
                            i
                        )

                        position = (
                            len(
                                player_sequence
                            )
                            - 1
                        )


                        # ---------------------------------
                        # SEND CLICK TO SERVER
                        # ---------------------------------

                        network.send_message(
                            {
                                "type":
                                    "color_click",

                                "color":
                                    i
                            }
                        )


                        print(
                            f"Colour clicked: "
                            f"{COLOR_NAMES[i]}"
                        )


                        # ---------------------------------
                        # WRONG COLOUR
                        # ---------------------------------

                        if (
                            player_sequence[
                                position
                            ]
                            != sequence[
                                position
                            ]
                        ):

                            # IMPORTANT:
                            # The server is now the
                            # authority for GAME OVER.

                            input_locked = True

                            waiting_for_players = True


                        # ---------------------------------
                        # COMPLETE SEQUENCE
                        # ---------------------------------

                        elif (
                            len(
                                player_sequence
                            )
                            == len(
                                sequence
                            )
                        ):

                            # ---------------------------------
                            # The player has finished.
                            # Wait for the server to tell
                            # us when the next round starts.
                            # ---------------------------------

                            input_locked = True

                            waiting_for_players = True

                            print(
                                "Sequence completed."
                            )


                        # ---------------------------------
                        # MORE COLOURS ARE REQUIRED
                        # ---------------------------------

                        else:

                            # Keep buttons active.
                            #
                            # Example:
                            #
                            # Sequence = [0, 2]
                            #
                            # First click:
                            # [0] -> 1 / 2
                            #
                            # Second click:
                            # [0, 2] -> 2 / 2

                            input_locked = False

                            waiting_for_players = False

                        break


        # =================================================
        # GAME OVER
        # =================================================

        elif (
            game_state == GAME_OVER
        ):

            if (
                event.type
                == pygame.MOUSEBUTTONDOWN
            ):

                if (
                    play_again_button.collidepoint(
                        event.pos
                    )
                ):

                    network.send_message(
                        {
                            "type":
                                "player_ready"
                        }
                    )

                    print(
                        "Player is ready again."
                    )

                    reset_game()


    # =====================================================
    # MENU SCREEN
    # =====================================================

    if game_state == MENU:

        screen.fill(
            BACKGROUND
        )


        draw_text(
            "COLOUR CODE",
            TITLE_FONT,
            WHITE,
            WIDTH // 2,
            130
        )

        draw_text(
            "CHALLENGE",
            TITLE_FONT,
            WHITE,
            WIDTH // 2,
            190
        )


        pygame.draw.rect(
            screen,
            BLUE,
            start_button,
            border_radius=15
        )


        draw_text(
            "START GAME",
            FONT,
            WHITE,
            WIDTH // 2,
            365
        )


        draw_text(
            "Remember → Reproduce → Win!",
            SMALL_FONT,
            GRAY,
            WIDTH // 2,
            500
        )


        draw_text(
            f"Players Online: "
            f"{server_player_count}",
            SMALL_FONT,
            GRAY,
            WIDTH // 2,
            545
        )


    # =====================================================
    # WAITING SCREEN
    # =====================================================

    elif game_state == WAITING:

        screen.fill(
            BACKGROUND
        )


        draw_text(
            "COLOUR CODE",
            TITLE_FONT,
            WHITE,
            WIDTH // 2,
            150
        )


        draw_text(
            "Waiting for players...",
            BIG_FONT,
            GRAY,
            WIDTH // 2,
            270
        )


        draw_text(
            f"Players Online: "
            f"{server_player_count}",
            FONT,
            WHITE,
            WIDTH // 2,
            350
        )


    # =====================================================
    # COUNTDOWN
    # =====================================================

    elif game_state == COUNTDOWN:

        screen.fill(
            BACKGROUND
        )


        draw_text(
            f"ROUND {round_number}",
            BIG_FONT,
            WHITE,
            WIDTH // 2,
            150
        )


        draw_text(
            "GET READY!",
            TITLE_FONT,
            WHITE,
            WIDTH // 2,
            230
        )


        elapsed = (
            time.time()
            -
            countdown_start
        )

        number = (
            3
            -
            int(elapsed)
        )


        if number > 0:

            draw_text(
                str(number),
                BIG_FONT,
                WHITE,
                WIDTH // 2,
                350
            )

        else:

            show_sequence()


    # =====================================================
    # MEMORIZE THE SEQUENCE
    # =====================================================

    elif game_state == SHOW_SEQUENCE:

        screen.fill(
            BACKGROUND
        )


        # -----------------------------------------------
        # ROUND
        # -----------------------------------------------

        draw_text(
            f"ROUND {round_number}",
            BIG_FONT,
            WHITE,
            WIDTH // 2,
            80
        )


        # -----------------------------------------------
        # TITLE
        # -----------------------------------------------

        draw_text(
            "MEMORIZE THE SEQUENCE",
            FONT,
            GRAY,
            WIDTH // 2,
            140
        )


        # -----------------------------------------------
        # CALCULATE BOX SIZE
        # -----------------------------------------------

        sequence_length = (
            len(sequence)
        )

        available_width = (
            WIDTH - 80
        )

        box_size = 100

        gap = 30


        # -----------------------------------------------
        # REDUCE BOX SIZE FOR LONG SEQUENCES
        # -----------------------------------------------

        if sequence_length >= 7:

            box_size = 80

            gap = 18


        if sequence_length >= 9:

            box_size = 65

            gap = 12


        if sequence_length >= 12:

            box_size = 55

            gap = 10


        # -----------------------------------------------
        # CALCULATE TOTAL WIDTH
        # -----------------------------------------------

        total_width = (
            sequence_length
            * box_size
            +
            (sequence_length - 1)
            * gap
        )


        # -----------------------------------------------
        # SAFETY CHECK
        # -----------------------------------------------

        if total_width > available_width:

            box_size = (
                available_width
                -
                (sequence_length - 1)
                * gap
            ) // sequence_length

            box_size = max(
                box_size,
                35
            )


            total_width = (
                sequence_length
                * box_size
                +
                (sequence_length - 1)
                * gap
            )


        # -----------------------------------------------
        # CENTER THE SEQUENCE
        # -----------------------------------------------

        start_x = (
            WIDTH
            -
            total_width
        ) // 2

        y = 250


        # -----------------------------------------------
        # DRAW COMPLETE SEQUENCE
        # -----------------------------------------------

        for i, colour_index in enumerate(
            sequence
        ):

            x = (
                start_x
                +
                i
                *
                (
                    box_size
                    +
                    gap
                )
            )


            rect = pygame.Rect(
                x,
                y,
                box_size,
                box_size
            )


            pygame.draw.rect(
                screen,
                COLORS[
                    colour_index
                ],
                rect,
                border_radius=15
            )


            # -----------------------------------------
            # COLOR NAME
            # -----------------------------------------

            if box_size < 60:

                name_font = (
                    pygame.font.Font(
                        None,
                        20
                    )
                )

            elif box_size < 80:

                name_font = (
                    pygame.font.Font(
                        None,
                        24
                    )
                )

            else:

                name_font = (
                    SMALL_FONT
                )


            draw_text(
                COLOR_NAMES[
                    colour_index
                ],
                name_font,
                WHITE,
                x
                +
                box_size // 2,
                y
                +
                box_size
                +
                25
            )


        # -----------------------------------------------
        # DISPLAY TIME
        # -----------------------------------------------

        elapsed = (
            time.time()
            -
            sequence_start
        )


        display_time = (
            2.5
            +
            len(sequence)
            *
            0.5
        )


        if elapsed >= display_time:

            game_state = PLAYING

            input_locked = False

            waiting_for_players = False


    # =====================================================
    # REPEAT THE SEQUENCE
    # =====================================================

    elif game_state == PLAYING:

        screen.fill(
            BACKGROUND
        )


        # -----------------------------------------------
        # HEADER
        # -----------------------------------------------

        draw_text(
            f"Round {round_number}",
            FONT,
            WHITE,
            100,
            50
        )


        draw_text(
            f"Score: {score}",
            FONT,
            WHITE,
            780,
            50
        )


        # -----------------------------------------------
        # TITLE
        # -----------------------------------------------

        draw_text(
            "REPEAT THE SEQUENCE",
            BIG_FONT,
            WHITE,
            WIDTH // 2,
            130
        )


        # -----------------------------------------------
        # STATUS TEXT
        # -----------------------------------------------

        if waiting_for_players:

            draw_text(
                "Waiting for other players...",
                SMALL_FONT,
                GRAY,
                WIDTH // 2,
                180
            )

        else:

            draw_text(
                "Click the colours in the correct order",
                SMALL_FONT,
                GRAY,
                WIDTH // 2,
                180
            )


        # -----------------------------------------------
        # COLOUR BUTTONS
        # -----------------------------------------------

        for i, button in enumerate(
            color_buttons
        ):

            pygame.draw.rect(
                screen,
                COLORS[i],
                button,
                border_radius=20
            )


            draw_text(
                COLOR_NAMES[i],
                SMALL_FONT,
                WHITE,
                button.centerx,
                button.centery
            )


        # -----------------------------------------------
        # PROGRESS
        # -----------------------------------------------

        progress = (
            f"{len(player_sequence)} / "
            f"{len(sequence)}"
        )


        draw_text(
            progress,
            SMALL_FONT,
            GRAY,
            WIDTH // 2,
            570
        )


    # =====================================================
    # GAME OVER
    # =====================================================

    elif game_state == GAME_OVER:

        screen.fill(
            BACKGROUND
        )


        # -----------------------------------------------
        # RESULT
        # -----------------------------------------------

        if game_result == "YOU WIN!":

            result_color = GREEN

        elif game_result == "YOU LOST!":

            result_color = RED

        else:

            result_color = WHITE


        draw_text(
            game_result,
            TITLE_FONT,
            result_color,
            WIDTH // 2,
            120
        )


        draw_text(
            message,
            FONT,
            WHITE,
            WIDTH // 2,
            190
        )


        draw_text(
            f"Final Score: {score}",
            BIG_FONT,
            WHITE,
            WIDTH // 2,
            260
        )


        # -----------------------------------------------
        # PLAYER ROUND INFORMATION
        # -----------------------------------------------

        if my_failed_round is not None:

            draw_text(
                f"Completed Rounds: "
                f"{my_completed_rounds}",
                SMALL_FONT,
                GRAY,
                WIDTH // 2,
                315
            )

            draw_text(
                f"Failed in Round: "
                f"{my_failed_round}",
                SMALL_FONT,
                GRAY,
                WIDTH // 2,
                350
            )

        else:

            draw_text(
                f"Completed Rounds: "
                f"{my_completed_rounds}",
                SMALL_FONT,
                GRAY,
                WIDTH // 2,
                325
            )


        # -----------------------------------------------
        # FINAL SCOREBOARD
        # -----------------------------------------------

        y = 395

        draw_text(
            "FINAL SCORES",
            SMALL_FONT,
            GRAY,
            WIDTH // 2,
            y
        )

        y += 32


        # ------------------------------------------------
        # SIMPLE FINAL SCOREBOARD
        # ------------------------------------------------
        #
        # YOU is ALWAYS shown first.
        #
        # Example:
        #
        # YOU: 20
        # PLAYER 1: 30
        #
        # The order does not depend on whether the player
        # won or lost.
        # ------------------------------------------------

        scoreboard_order = []

        if player_id is not None:

            own_id = str(player_id)

            if own_id in final_scores:

                scoreboard_order.append(
                    own_id
                )

        # Add all other players after YOU.
        for pid in sorted(
            final_scores.keys(),
            key=lambda value: int(value)
        ):

            if (
                player_id is None
                or str(pid) != str(player_id)
            ):

                scoreboard_order.append(
                    str(pid)
                )

        for pid in scoreboard_order:

            if (
                player_id is not None
                and str(pid) == str(player_id)
            ):

                prefix = "YOU"

            else:

                prefix = f"PLAYER {pid}"

            draw_text(
                f"{prefix}: {final_scores[pid]}",
                SMALL_FONT,
                WHITE,
                WIDTH // 2,
                y
            )

            y += 32


        # -----------------------------------------------
        # PLAY AGAIN BUTTON
        # -----------------------------------------------

        # Keep the button below the scoreboard so that
        # player scores are never covered by the button.
        button_y = max(
            500,
            y + 10
        )

        play_again_button.topleft = (
            325,
            button_y
        )

        pygame.draw.rect(
            screen,
            BLUE,
            play_again_button,
            border_radius=15
        )

        draw_text(
            "PLAY AGAIN",
            FONT,
            WHITE,
            play_again_button.centerx,
            play_again_button.centery
        )

    # =====================================================
    # UPDATE DISPLAY
    # =====================================================

    pygame.display.flip()


# =========================================================
# CLOSE NETWORK CONNECTION
# =========================================================

network.close()

pygame.quit()