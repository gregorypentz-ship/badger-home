APP_DIR = "/system/apps/calculator"

import os
import sys

os.chdir(APP_DIR)
sys.path.insert(0, APP_DIR)

screen.font = font.sins
screen.antialias = image.X2
badge.default_clear = color.rgb(18, 24, 32)

expression = ""
result = ""
error = False

KEYS = (
    ("7", "8", "9", "/", "C"),
    ("4", "5", "6", "*", "DEL"),
    ("1", "2", "3", "-", "("),
    ("0", ".", "+", ")", "="),
)


def display_text(text, y, size):
    screen.font = size
    width, _ = screen.measure_text(text)
    screen.pen = color.rgb(255, 255, 255)
    screen.text(text, max(5, screen.width - width - 5), y)


def calculate():
    global expression, result, error

    if not expression:
        return

    try:
        value = eval(expression, {"__builtins__": {}}, {})
        result = str(value)
        expression = result
        error = False
    except Exception:
        result = "Error"
        error = True


def update():
    global expression, result, error

    key = None
    if badge.pressed(BUTTON_UP):
        pass
    elif badge.pressed(BUTTON_DOWN):
        pass
    elif badge.pressed(BUTTON_LEFT):
        pass
    elif badge.pressed(BUTTON_RIGHT):
        pass
    elif badge.pressed(BUTTON_SELECT):
        pass
    elif badge.pressed(BUTTON_BACK):
        expression = expression[:-1] if expression else ""
        result = ""
        error = False
        return

    screen.pen = color.rgb(18, 24, 32)
    screen.rectangle(0, 0, screen.width, screen.height)

    screen.pen = color.rgb(35, 43, 54)
    screen.shape(shape.rounded_rectangle(
        5, 5, screen.width - 10, 35, 5
    ))

    display_text(expression[-18:] if expression else "0", 10, font.sins)
    display_text(result[-18:] if result else "", 25, font.nope)

    button_width = (screen.width - 20) // 5
    button_height = 18

    for row, keys in enumerate(KEYS):
        for column, text in enumerate(keys):
            x = 5 + column * button_width
            y = 46 + row * button_height

            screen.pen = (
                color.rgb(75, 105, 145)
                if text in ("=", "C")
                else color.rgb(48, 58, 72)
            )
            screen.shape(shape.rounded_rectangle(
                x, y, button_width - 3, button_height - 3, 3
            ))

            screen.pen = color.rgb(255, 255, 255)
            screen.font = font.nope
            width, height = screen.measure_text(text)
            screen.text(
                text,
                x + (button_width - width - 3) / 2,
                y + (button_height - height - 3) / 2,
            )


run(update)
