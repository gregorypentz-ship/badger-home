APP_DIR = "/system/apps/fire_golf_hit"

import os
import sys
import random

os.chdir(APP_DIR)
sys.path.insert(0, APP_DIR)

screen.font = font.sins
screen.antialias = image.X2
badge.default_clear = color.rgb(16, 24, 20)

# (name, par, tee, hole, obstacles)
LEVELS = (
    (
        "FLAME FAIRWAY",
        3,
        (22, 92),
        (138, 32),
        ((55, 68, 18, 18), (92, 48, 14, 14)),
    ),
    (
        "EMBER LOOP",
        4,
        (20, 96),
        (142, 22),
        ((48, 58, 18, 40), (82, 25, 18, 32),
         (112, 65, 18, 28)),
    ),
    (
        "INFERNO CUP",
        5,
        (18, 96),
        (142, 18),
        ((38, 48, 16, 52), (65, 25, 18, 38),
         (94, 62, 20, 38), (125, 42, 10, 30)),
    ),
)

level_index = 0
scene = "menu"
ball_x = 0.0
ball_y = 0.0
velocity_x = 0.0
velocity_y = 0.0
aim_angle = -45
power = 40
putting = False
shots = 0
max_shots = 8
fire_ticks = 0
particles = []


def reset_level():
    global ball_x, ball_y, velocity_x, velocity_y
    global aim_angle, power, putting, shots, particles

    _, _par, tee, _hole, _obstacles = LEVELS[level_index]
    ball_x, ball_y = tee
    velocity_x = 0.0
    velocity_y = 0.0
    aim_angle = -45
    power = 40
    putting = False
    shots = 0
    particles = []


def centered(text, y, ink):
    width, _ = screen.measure_text(text)
    screen.pen = ink
    screen.text(text, (screen.width - width) / 2, y)


def add_fire_particle():
    global particles
    particles.append([
        ball_x + random.uniform(-2, 2),
        ball_y + random.uniform(-2, 2),
        random.uniform(-8, 8),
        random.uniform(-18, 4),
        350,
    ])

    if len(particles) > 50:
        particles.pop(0)


def ball_distance_from_hole():
    _, _par, _tee, hole, _obstacles = LEVELS[level_index]
    dx = ball_x - hole[0]
    dy = ball_y - hole[1]
    return (dx * dx + dy * dy) ** 0.5


def point_in_obstacle(x, y):
    _, _par, _tee, _hole, obstacles = LEVELS[level_index]

    for left, top, width, height in obstacles:
        if left <= x <= left + width and top <= y <= top + height:
            return True
    return False


def draw_hole():
    _, _par, _tee, hole, _obstacles = LEVELS[level_index]
    screen.pen = color.rgb(8, 8, 8)
    screen.shape(shape.circle(hole[0], hole[1], 7))
    screen.pen = color.rgb(255, 80, 20)
    screen.line(hole[0] + 1, hole[1], hole[0] + 1, hole[1] - 20)
    screen.pen = color.rgb(255, 220, 70)
    screen.shape(shape.regular_polygon(hole[0] + 7, hole[1] - 18, 5, 3))


def draw_course():
    _, _par, _tee, _hole, obstacles = LEVELS[level_index]

    screen.pen = color.rgb(42, 116, 65)
    screen.rectangle(0, 0, screen.width, screen.height)

    screen.pen = color.rgb(58, 145, 78)
    screen.shape(shape.circle(80, 64, 70))

    screen.pen = color.rgb(115, 68, 38)
    for left, top, width, height in obstacles:
        screen.shape(shape.rounded_rectangle(left, top, width, height, 4))

    draw_hole()

    screen.pen = color.rgb(255, 245, 210)
    screen.shape(shape.circle(ball_x, ball_y, 4))


def draw_aim():
    radians = aim_angle * 3.14159265 / 180
    length = 12 + power / 3

    end_x = ball_x + __import__("math").cos(radians) * length
    end_y = ball_y + __import__("math").sin(radians) * length

    screen.pen = color.rgb(255, 255, 255)
    screen.line(ball_x, ball_y, end_x, end_y)

    screen.pen = color.rgb(255, 105, 20)
    screen.rectangle(4, screen.height - 8, 64, 4)
    screen.pen = color.rgb(255, 220, 60)
    screen.rectangle(4, screen.height - 8, int(64 * power / 100), 4)


def update_particles(dt):
    global particles
    for particle in particles:
        particle[0] += particle[2] * dt
        particle[1] += particle[3] * dt
        particle[3] += 20 * dt
        particle[4] -= dt * 1000

    particles = [particle for particle in particles if particle[4] > 0]

    for particle in particles:
        screen.pen = color.rgb(
            255,
            max(40, int(180 * particle[4] / 350)),
            20,
        )
        screen.shape(shape.circle(particle[0], particle[1], 2))


def draw_menu():
    screen.pen = color.rgb(20, 25, 32)
    screen.rectangle(0, 0, screen.width, screen.height)

    centered("FIRE GOLF HIT", 12, color.rgb(255, 170, 55))
    name, par, _tee, _hole, _obstacles = LEVELS[level_index]

    centered("LEVEL %d / %d" % (level_index + 1, len(LEVELS)), 38,
             color.rgb(255, 255, 255))
    centered(name, 52, color.rgb(255, 105, 30))
    centered("PAR %d" % par, 67, color.rgb(170, 220, 180))

    centered("LEFT/RIGHT AIM", 82, color.rgb(180, 200, 190))
    centered("UP/DOWN POWER", 94, color.rgb(180, 200, 190))
    centered("SELECT: SHOOT", 107, color.rgb(255, 255, 255))


def draw_game():
    draw_course()
    draw_aim()
    update_particles(badge.ticks_delta / 1000)

    _, par, _tee, _hole, _obstacles = LEVELS[level_index]
    screen.pen = color.rgb(255, 255, 255)
    screen.text("L%d SHOTS %d/%d PAR %d" %
                (level_index + 1, shots, max_shots, par),
                5, 5)


def update():
    global scene, level_index, aim_angle, power
    global ball_x, ball_y, velocity_x, velocity_y, shots
    global putting, fire_ticks

    if scene == "menu":
        if badge.pressed(BUTTON_LEFT):
            level_index = (level_index - 1) % len(LEVELS)
        if badge.pressed(BUTTON_RIGHT):
            level_index = (level_index + 1) % len(LEVELS)
        if badge.pressed(BUTTON_SELECT):
            reset_level()
            scene = "play"

        draw_menu()
        return

    if scene == "won":
        draw_course()
        centered("HOLE OUT!", 42, color.rgb(255, 225, 90))
        centered("SHOTS: %d" % shots, 58, color.rgb(255, 255, 255))

        _, par, _tee, _hole, _obstacles = LEVELS[level_index]
        centered("PAR: %d" % par, 72, color.rgb(180, 220, 190))

        if level_index == len(LEVELS) - 1:
            centered("SELECT: MENU", 92, color.rgb(255, 255, 255))
        else:
            centered("SELECT: NEXT LEVEL", 92, color.rgb(255, 255, 255))

        if badge.pressed(BUTTON_SELECT):
            if level_index < len(LEVELS) - 1:
                level_index += 1
                reset_level()
                scene = "play"
            else:
                scene = "menu"

        if badge.pressed(BUTTON_BACK):
            scene = "menu"
        return

    if scene == "failed":
        draw_course()
        centered("OUT OF SHOTS", 48, color.rgb(255, 100, 70))
        centered("SELECT: RETRY", 66, color.rgb(255, 255, 255))

        if badge.pressed(BUTTON_SELECT):
            reset_level()
            scene = "play"
        if badge.pressed(BUTTON_BACK):
            scene = "menu"
        return

    if badge.pressed(BUTTON_BACK):
        scene = "menu"
        return

    dt = min(badge.ticks_delta / 1000, 0.05)

    if not putting:
        if badge.pressed(BUTTON_LEFT):
            aim_angle -= 5
        if badge.pressed(BUTTON_RIGHT):
            aim_angle += 5
        if badge.held(BUTTON_UP):
            power = min(100, power + 35 * dt)
        if badge.held(BUTTON_DOWN):
            power = max(10, power - 35 * dt)

        if badge.pressed(BUTTON_SELECT):
            radians = aim_angle * 3.14159265 / 180
            velocity_x = __import__("math").cos(radians) * power
            velocity_y = __import__("math").sin(radians) * power
            shots += 1
            putting = True
    else:
        ball_x += velocity_x * dt
        ball_y += velocity_y * dt

        velocity_x *= 0.985
        velocity_y *= 0.985

        if abs(velocity_x) + abs(velocity_y) < 3:
            velocity_x = 0
            velocity_y = 0
            putting = False

        fire_ticks += badge.ticks_delta
        if fire_ticks > 35:
            fire_ticks = 0
            add_fire_particle()

        if ball_x < 4:
            ball_x = 4
            velocity_x = abs(velocity_x) * 0.55
        if ball_x > screen.width - 4:
            ball_x = screen.width - 4
            velocity_x = -abs(velocity_x) * 0.55
        if ball_y < 4:
            ball_y = 4
            velocity_y = abs(velocity_y) * 0.55
        if ball_y > screen.height - 4:
            ball_y = screen.height - 4
            velocity_y = -abs(velocity_y) * 0.55

        if point_in_obstacle(ball_x, ball_y):
            velocity_x *= -0.45
            velocity_y *= -0.45
            ball_x -= velocity_x * dt
            ball_y -= velocity_y * dt

        if ball_distance_from_hole() < 8:
            scene = "won"

        if shots >= max_shots and not putting:
            scene = "failed"

    draw_game()


run(update)
