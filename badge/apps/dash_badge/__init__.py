APP_DIR = "/system/apps/dash_badge"

import os
import sys

os.chdir(APP_DIR)
sys.path.insert(0, APP_DIR)

from badgeware import State

# The player's chosen look is remembered between launches.
settings = {"color": 0, "style": 0}
try:
    State.load("dash_badge", settings)
except (OSError, ValueError):
    pass

COLORS = (
    color.rgb(80, 230, 150),
    color.rgb(255, 190, 60),
    color.rgb(100, 180, 255),
    color.rgb(255, 100, 130),
)
STYLES = ("SQUARE", "ROUND", "DIAMOND")

color_index = max(0, min(len(COLORS) - 1, settings["color"]))
style_index = max(0, min(len(STYLES) - 1, settings["style"]))

# Each level has a name, length, speed, and (position, height, width) hazards.
LEVELS = (
    (
        "FIRST STEPS",
        1050,
        170,
        ((190, 20, 12), (330, 28, 14), (500, 20, 12),
         (650, 32, 14), (825, 24, 12), (960, 34, 14)),
    ),
    (
        "DOUBLE JUMP",
        1250,
        190,
        ((180, 25, 12), (310, 35, 14), (455, 24, 12),
         (590, 38, 14), (735, 28, 12), (890, 38, 14),
         (1050, 30, 12), (1150, 36, 14)),
    ),
    (
        "FAST TRACK",
        1400,
        215,
        ((180, 28, 12), (300, 36, 12), (430, 24, 12),
         (560, 40, 14), (700, 32, 12), (840, 42, 14),
         (990, 28, 12), (1120, 40, 14), (1280, 34, 12)),
    ),
)

level_index = 0
scene = "title"
scroll = 0.0
player_y = 0.0
player_speed_y = 0.0


def save_look():
    settings["color"] = color_index
    settings["style"] = style_index
    try:
        State.save("dash_badge", settings)
    except OSError:
        pass


def centred(text, y, ink):
    width, _ = screen.measure_text(text)
    screen.pen = ink
    screen.text(text, (screen.width - width) / 2, y)


def start_level():
    global scene, scroll, player_y, player_speed_y
    scene = "playing"
    scroll = 0.0
    player_y = screen.height - 25 - 12
    player_speed_y = 0.0


def draw_player(x, y, size):
    screen.pen = COLORS[color_index]

    if style_index == 0:
        screen.rectangle(x, y, size, size)
    elif style_index == 1:
        screen.shape(shape.circle(x + size / 2, y + size / 2, size / 2))
    else:
        screen.shape(
            shape.regular_polygon(x + size / 2, y + size / 2, size / 2, 4)
        )


def draw_title():
    screen.pen = color.rgb(38, 44, 58)
    screen.shape(
        shape.rounded_rectangle(8, 8, screen.width - 16, screen.height - 16, 7)
    )

    centred("DASH BADGE", 13, color.rgb(255, 255, 255))
    centred(LEVELS[level_index][0], 38, color.rgb(255, 210, 90))
    centred("LEVEL %d / %d" % (level_index + 1, len(LEVELS)), 53,
            color.rgb(190, 200, 215))

    draw_player(screen.width / 2 - 7, 68, 14)
    centred("%s  -  LEFT/RIGHT COLOR" % STYLES[style_index], 86,
            color.rgb(160, 220, 190))
    centred("BACK: SHAPE   UP/DOWN: LEVEL", 100,
            color.rgb(170, 180, 195))
    centred("SELECT: START", 112, color.rgb(255, 255, 255))


def draw_level():
    name, length, speed, hazards = LEVELS[level_index]
    ground = screen.height - 25
    player_x = 30
    player_size = 12

    screen.pen = color.rgb(28, 33, 45)
    screen.rectangle(0, 0, screen.width, screen.height)

    screen.pen = color.rgb(100, 115, 140)
    screen.line(0, ground, screen.width, ground)

    screen.pen = color.rgb(255, 255, 255)
    screen.text(name, 5, 5)
    screen.text("L%d" % (level_index + 1), screen.width - 22, 5)

    # Draw a small progress bar.
    progress = min(1.0, scroll / length)
    screen.pen = color.rgb(65, 75, 92)
    screen.rectangle(5, 19, screen.width - 10, 3)
    screen.pen = color.rgb(80, 230, 150)
    screen.rectangle(5, 19, int((screen.width - 10) * progress), 3)

    for world_x, height, width in hazards:
        hazard_x = world_x - scroll
        if -width < hazard_x < screen.width:
            screen.pen = color.rgb(255, 90, 100)
            screen.rectangle(hazard_x, ground - height, width, height)

    draw_player(player_x, player_y, player_size)


def update():
    global color_index, style_index, level_index
    global scene, scroll, player_y, player_speed_y

    screen.pen = color.rgb(18, 22, 30)
    screen.rectangle(0, 0, screen.width, screen.height)

    if scene == "title":
        if badge.pressed(BUTTON_LEFT):
            color_index = (color_index - 1) % len(COLORS)
            save_look()
        if badge.pressed(BUTTON_RIGHT):
            color_index = (color_index + 1) % len(COLORS)
            save_look()
        if badge.pressed(BUTTON_BACK):
            style_index = (style_index + 1) % len(STYLES)
            save_look()
        if badge.pressed(BUTTON_UP):
            level_index = (level_index - 1) % len(LEVELS)
        if badge.pressed(BUTTON_DOWN):
            level_index = (level_index + 1) % len(LEVELS)
        if badge.pressed(BUTTON_SELECT):
            start_level()

        draw_title()
        return

    if scene == "dead":
        draw_level()
        centred("CRASH!", 45, color.rgb(255, 100, 110))
        centred("SELECT: TRY AGAIN", 67, color.rgb(255, 255, 255))
        centred("BACK: LEVEL MENU", 83, color.rgb(180, 190, 205))
        if badge.pressed(BUTTON_SELECT):
            start_level()
        elif badge.pressed(BUTTON_BACK):
            scene = "title"
        return

    if scene == "clear":
        draw_level()
        centred("LEVEL CLEAR!", 48, color.rgb(255, 220, 90))
        centred("SELECT: NEXT LEVEL", 70, color.rgb(255, 255, 255))
        centred("BACK: LEVEL MENU", 86, color.rgb(180, 190, 205))
        if badge.pressed(BUTTON_SELECT):
            level_index = (level_index + 1) % len(LEVELS)
            start_level()
        elif badge.pressed(BUTTON_BACK):
            scene = "title"
        return

    if badge.pressed(BUTTON_BACK):
        scene = "title"
        return

    dt = min(badge.ticks_delta / 1000, 0.05)
    name, length, speed, hazards = LEVELS[level_index]
    ground = screen.height - 25
    player_x = 30
    player_size = 12

    if badge.pressed(BUTTON_SELECT) and player_y >= ground - player_size:
        player_speed_y = -270

    player_speed_y += 800 * dt
    player_y += player_speed_y * dt

    if player_y > ground - player_size:
        player_y = ground - player_size
        player_speed_y = 0

    scroll += speed * dt

    for world_x, height, width in hazards:
        hazard_x = world_x - scroll
        overlaps_x = player_x + player_size > hazard_x and player_x < hazard_x + width
        hits_hazard = player_y + player_size > ground - height
        if overlaps_x and hits_hazard:
            scene = "dead"
            break

    if scroll >= length:
        scene = "clear"

    draw_level()


badge.default_clear = color.rgb(18, 22, 30)
screen.font = font.sins
screen.antialias = image.X2

run(update)
