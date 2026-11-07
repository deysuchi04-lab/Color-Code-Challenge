import pygame
import random
import time

pygame.init()

# =========================================================
# WINDOW
# =========================================================

WIDTH = 900
HEIGHT = 650

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Colour Code Challenge")

clock = pygame.time.Clock()


# =========================================================
# FONTS
# =========================================================

TITLE_FONT = pygame.font.Font(None, 64)
BIG_FONT = pygame.font.Font(None, 52)
FONT = pygame.font.Font(None, 36)
SMALL_FONT = pygame.font.Font(None, 28)


# =========================================================
# COLOURS
# =========================================================

BACKGROUND = (25, 25, 35)

WHITE = (255, 255, 255)
GRAY = (160, 160, 160)

RED = (220, 60, 60)
BLUE = (60, 110, 230)
GREEN = (60, 190, 100)
YELLOW = (230, 200, 60)

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


# =========================================================
# BUTTONS
# =========================================================

start_button = pygame.Rect(
    325, 330, 250, 70
)

play_again_button = pygame.Rect(
    325, 420, 250, 70
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

    color_buttons.append(button)


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
        text,
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

    screen.blit(image, rect)


# =========================================================
# GENERATE NEW COLOUR
# =========================================================

def generate_new_colour():

    # First colour can be anything
    if len(sequence) == 0:

        return random.randint(0, 3)

    # Don't allow same colour twice in a row
    previous = sequence[-1]

    available = [
        i
        for i in range(4)
        if i != previous
    ]

    return random.choice(
        available
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

    player_sequence = []

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

    sequence = []

    player_sequence = []

    round_number = 1

    score = 0

    message = ""

    # Generate FIRST colour
    sequence.append(
        generate_new_colour()
    )

    # Countdown → Memorize
    start_countdown()


# =========================================================
# NEXT ROUND
# =========================================================

def next_round():

    global round_number
    global sequence
    global player_sequence

    # Increase round
    round_number += 1

    # Add ONE new colour
    sequence.append(
        generate_new_colour()
    )

    # Clear previous answer
    player_sequence = []

    # Round 2 onwards directly
    # shows the new sequence.
    show_sequence()


# =========================================================
# MAIN LOOP
# =========================================================

running = True

while running:

    clock.tick(60)

    # =====================================================
    # EVENTS
    # =====================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False


        # =================================================
        # MENU
        # =================================================

        if game_state == MENU:

            if event.type == pygame.MOUSEBUTTONDOWN:

                if start_button.collidepoint(
                    event.pos
                ):

                    reset_game()


        # =================================================
        # PLAYING
        # =================================================

        elif game_state == PLAYING:

            if event.type == pygame.MOUSEBUTTONDOWN:

                for i, button in enumerate(
                    color_buttons
                ):

                    if button.collidepoint(
                        event.pos
                    ):

                        # Add player's choice
                        player_sequence.append(i)

                        position = (
                            len(player_sequence) - 1
                        )

                        # ---------------------------------
                        # WRONG COLOUR
                        # ---------------------------------

                        if (
                            player_sequence[position]
                            != sequence[position]
                        ):

                            message = (
                                "Wrong sequence!"
                            )

                            game_state = GAME_OVER

                        # ---------------------------------
                        # CORRECT COMPLETE SEQUENCE
                        # ---------------------------------

                        elif (
                            len(player_sequence)
                            == len(sequence)
                        ):

                            score += 10

                            next_round()


        # =================================================
        # GAME OVER
        # =================================================

        elif game_state == GAME_OVER:

            if event.type == pygame.MOUSEBUTTONDOWN:

                if play_again_button.collidepoint(
                    event.pos
                ):

                    reset_game()


    # =====================================================
    # MENU SCREEN
    # =====================================================

    if game_state == MENU:

        screen.fill(BACKGROUND)

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


    # =====================================================
    # COUNTDOWN
    # =====================================================

    elif game_state == COUNTDOWN:

        screen.fill(BACKGROUND)

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
            time.time() - countdown_start
        )

        number = 3 - int(elapsed)

        if number > 0:

            draw_text(
                str(number),
                BIG_FONT,
                WHITE,
                WIDTH // 2,
                350
            )

        else:

            # After countdown:
            # show sequence
            show_sequence()


    # =====================================================
    # MEMORIZE THE SEQUENCE
    # =====================================================

    elif game_state == SHOW_SEQUENCE:

        screen.fill(BACKGROUND)

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

        sequence_length = len(sequence)

        # Available horizontal space
        available_width = WIDTH - 80

        # Normal size
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
            sequence_length * box_size
            +
            (sequence_length - 1) * gap
        )

        # -----------------------------------------------
        # SAFETY CHECK
        # -----------------------------------------------

        # If the sequence is still too wide,
        # automatically calculate a smaller box.

        if total_width > available_width:

            box_size = (
                available_width
                -
                (sequence_length - 1) * gap
            ) // sequence_length

            # Minimum box size
            box_size = max(
                box_size,
                35
            )

            total_width = (
                sequence_length * box_size
                +
                (sequence_length - 1) * gap
            )

        # -----------------------------------------------
        # CENTER THE SEQUENCE
        # -----------------------------------------------

        start_x = (
            WIDTH - total_width
        ) // 2

        # -----------------------------------------------
        # VERTICAL POSITION
        # -----------------------------------------------

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
                i * (box_size + gap)
            )

            rect = pygame.Rect(
                x,
                y,
                box_size,
                box_size
            )

            pygame.draw.rect(
                screen,
                COLORS[colour_index],
                rect,
                border_radius=15
            )

            # -----------------------------------------
            # COLOR NAME
            # -----------------------------------------

            # Use smaller font for smaller boxes
            if box_size < 60:

                name_font = pygame.font.Font(
                    None,
                    20
                )

            elif box_size < 80:

                name_font = pygame.font.Font(
                    None,
                    24
                )

            else:

                name_font = SMALL_FONT

            draw_text(
                COLOR_NAMES[colour_index],
                name_font,
                WHITE,
                x + box_size // 2,
                y + box_size + 25
            )

        # -----------------------------------------------
        # DISPLAY TIME
        # -----------------------------------------------

        elapsed = (
            time.time()
            -
            sequence_start
        )

        # More colours = more time
        display_time = (
            2.5
            +
            len(sequence) * 0.5
        )

        if elapsed >= display_time:

            # Go to repeat screen
            game_state = PLAYING


    # =====================================================
    # REPEAT THE SEQUENCE
    # =====================================================

    elif game_state == PLAYING:

        screen.fill(BACKGROUND)

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

        screen.fill(BACKGROUND)

        draw_text(
            "GAME OVER",
            TITLE_FONT,
            RED,
            WIDTH // 2,
            150
        )

        draw_text(
            message,
            FONT,
            WHITE,
            WIDTH // 2,
            230
        )

        draw_text(
            f"Final Score: {score}",
            BIG_FONT,
            WHITE,
            WIDTH // 2,
            300
        )

        draw_text(
            f"You reached Round {round_number}",
            FONT,
            GRAY,
            WIDTH // 2,
            350
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
            WIDTH // 2,
            455
        )


    # =====================================================
    # UPDATE
    # =====================================================

    pygame.display.flip()


pygame.quit()