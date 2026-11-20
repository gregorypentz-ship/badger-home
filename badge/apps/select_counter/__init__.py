APP_DIR = "/system/apps/select_counter"

import os
import sys

os.chdir(APP_DIR)
sys.path.insert(0, APP_DIR)

count = 0

screen.font = font.sins
screen.antialias = image.X2
badge.default_clear = color.rgb(20, 24, 28)


def centre_text(text, y, pen):
    width, _ = screen.measure_text(text)
    screen.pen = pen
    screen.text(text, (screen.width - width) / 2, y)


def update():
    global count

    if badge.pressed(BUTTON_SELECT):
        count += 1

    screen.pen = color.rgb(40, 44, 52)
    screen.shape(
        shape.rounded_rectangle(
            12, 12, screen.width - 24, screen.height - 24, 8
        )
    )

    centre_text("SELECT COUNTER", 18, color.rgb(150, 170, 190))
    centre_text(str(count), 43, color.rgb(255, 255, 255))
    centre_text("Press SELECT", 93, color.rgb(100, 220, 160))


run(update)
