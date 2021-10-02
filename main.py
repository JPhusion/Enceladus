import pygame
import sys
import os
import time
import random
from pygame.draw import polygon
from pygame.locals import *

# INITIATE WINDOW =========================================================== #
clock = pygame.time.Clock()

pygame.init()

pygame.display.set_caption("Enceladus")

framerate = 60

SCREEN_SIZE = (pygame.display.Info().current_w,
               pygame.display.Info().current_h)
WINDOW_SIZE = (1024, 576)
DISPLAY_SIZE = (512, 288)

win = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
display = pygame.Surface(DISPLAY_SIZE)

# LOAD IMAGES =============================================================== #


def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


bg_img1 = pygame.image.load(resource_path(
    'assets/background/background_1.png')).convert()
bg_img2 = pygame.image.load(resource_path(
    'assets/background/background_2.png')).convert()
bg_img3 = pygame.image.load(resource_path(
    'assets/background/background_3.png')).convert()
bg_img4 = pygame.image.load(resource_path(
    'assets/background/background_4.png')).convert()
bg_img5 = pygame.image.load(resource_path(
    'assets/background/background_5.png')).convert()
bg_img6 = pygame.image.load(resource_path(
    'assets/background/background_6.png')).convert()
backgrounds = [bg_img1, bg_img2, bg_img3, bg_img4, bg_img5, bg_img6]

player1 = pygame.image.load('assets/player/player1.png').convert()

# INITIATE PHYSICS ========================================================== #
accelleration = 0.2
in_water = True
contact = 1
dive = False
vel = 0


# PLAYER MECHANICS ========================================================== #
class player:

    def __init__(self, pos_y=192, vel_y=0):
        self.pos_y = pos_y
        self.vel_y = vel_y

    def gravity(self):
        global vel
        vel += accelleration
        s_player["y"] += vel * dt

    def hitbox(self):
        return pygame.Rect((s_player["x"], s_player["y"]), (48, 32))

    def draw(self):
        display.blit(s_player["img"], (s_player["x"], s_player["y"]))

    def update(self):
        global vel
        global contact
        global in_water
        self.gravity()
        self.draw()
        if not dive:
            for hitbox in h_water:
                if self.hitbox().colliderect(hitbox):
                    s_player["y"] = hitbox.topleft[1] - 30
                    if contact == 0 and vel > 0.2:
                        s_water.splash(
                            int(s_player["x"]/512 * 100 + 24/512 * 100), (1.5 ** (vel*1) - 1.1) * 10 * dt)
                    contact += 1
                    in_water = True
                    vel = 0
                else:
                    contact = 0


# WATER MECHANICS =========================================================== #
class surface_water_particle():
    k = 0.02  # spring constant
    d = 0.10  # damping constant

    def __init__(self, x, y):
        self.x_pos = x
        self.y_pos = y
        self.target_y = y
        self.velocity = 0

    def update(self):
        x = self.y_pos - self.target_y              # displacement of "spring"
        a = -self.k * x - self.d * self.velocity    # unit of acceleration

        self.y_pos += self.velocity
        self.velocity += a


class water():

    def __init__(self, x_start, x_end, y_start, y_end, segment_length):
        self.springs = []
        self.x_start = x_start
        self.y_start = y_start
        self.x_end = x_end
        self.y_end = y_end - 10
        for i in range(abs(x_end - x_start) // segment_length):
            self.springs.append(surface_water_particle(
                i * segment_length + x_start, y_end))

    def update(self, spread):
        passes = 4  # more passes = more splash spreading
        for i in range(len(self.springs)):
            self.springs[i].update()

        leftDeltas = [0] * len(self.springs)
        rightDeltas = [0] * len(self.springs)
        for p in range(passes):
            for i in range(0, len(self.springs) - 1):
                if i > 0:
                    leftDeltas[i] = spread * \
                        (self.springs[i].y_pos - self.springs[i - 1].y_pos)
                    self.springs[i - 1].velocity += leftDeltas[i]
                if i < len(self.springs) - 1:
                    rightDeltas[i] = spread * \
                        (self.springs[i].y_pos - self.springs[i + 1].y_pos)
                    self.springs[i + 1].velocity += rightDeltas[i]

            for i in range(0, len(self.springs) - 1):
                if i > 0:
                    self.springs[i - 1].y_pos += leftDeltas[i]
                if i < len(self.springs) - 1:
                    self.springs[i + 1].y_pos += rightDeltas[i]

    def splash(self, index, speed):
        if index > 0 and index < len(self.springs):
            self.springs[index].velocity = speed
            for i in range(int(speed-10)):
                splash_particles.append([[player.hitbox().center[0] + random.randint(-10, 10), self.springs[index].y_pos + speed/3], [
                                        random.uniform(-speed/50, +speed/50), -speed/60 + random.uniform(-5, 0)], random.randint(1, 4)])

    def draw(self, type="visual"):
        polygon_points = []
        polygon_points.append((self.x_start, self.y_start))
        for spring in range(len(self.springs)):
            polygon_points.append(
                (s_water.springs[spring].x_pos, s_water.springs[spring].y_pos))
        polygon_points.append(
            (s_water.springs[len(self.springs) - 1].x_pos, self.y_start))

        underWater = pygame.Surface(DISPLAY_SIZE, pygame.SRCALPHA)

        pygame.draw.polygon(underWater, (50, 150, 200, 128),
                            polygon_points + [(512, 300), (0, 300)])

        if type == "node":
            for node in polygon_points:
                pygame.draw.circle(display, (255, 0, 0), node, 1)

        elif type == "visual":
            for spring in range(len(self.springs) - 1):
                pygame.draw.line(underWater, (255, 255, 255), (s_water.springs[spring].x_pos, s_water.springs[spring].y_pos), (
                    s_water.springs[spring + 1].x_pos, s_water.springs[spring + 1].y_pos), 2)
            display.blit(underWater, (0, 0))

        elif type == "hitbox":
            hitboxes = []
            for node in polygon_points:
                hitboxes.append(pygame.Rect(node, (1, 1)))
            return hitboxes


# PARTICLES ================================================================= #
def update_particles():
    for particle in splash_particles:
        particle[0][0] += particle[1][0]
        particle[0][1] += particle[1][1]
        particle[2] -= 0.08
        particle[1][1] += 0.1
        pygame.draw.circle(display, (100, 200, 255), [int(
            particle[0][0]), int(particle[0][1])], int(particle[2]))
        if particle[2] <= 0:
            splash_particles.remove(particle)
        # TODO PARTICLE GRAVITY

# SCROLLING BACKGROUND ====================================================== #


class background:

    def __init__(self):
        pass

    def drawGrid(self):
        for x in range(32):
            for y in range(18):
                if x % 2 == 0:
                    if y % 2 == 0:
                        pygame.draw.rect(display, (200, 200, 200),
                                         pygame.Rect(x*16, y*16, 16, 16))
                    else:
                        pygame.draw.rect(display, (216, 216, 216),
                                         pygame.Rect(x*16, y*16, 16, 16))
                else:
                    if y % 2 == 1:
                        pygame.draw.rect(display, (200, 200, 200),
                                         pygame.Rect(x*16, y*16, 16, 16))
                    else:
                        pygame.draw.rect(display, (216, 216, 216),
                                         pygame.Rect(x*16, y*16, 16, 16))

    def addChunk(self):

        s_backgrounds.append([random.choice(backgrounds), [512, 0]])

    def scrollChunk(self):

        for chunk in s_backgrounds:
            chunk[1][0] -= 1 * dt

    def draw(self):

        for chunk in s_backgrounds:
            display.blit(chunk[0], (chunk[1][0], chunk[1][1]))

    def update(self):

        if s_backgrounds[0][1][0] < -512:
            s_backgrounds.pop(0)
        if len(s_backgrounds) < 3:
            self.addChunk()
        self.scrollChunk()
        self.draw()


# SCALING WINDOW ============================================================ #
def scaled_win():
    if WINDOW_SIZE[0]/16 > WINDOW_SIZE[1]/9:
        scaled_win = (WINDOW_SIZE[0], int(WINDOW_SIZE[0]/16 * 9))
        position = (0, -(scaled_win[1] - WINDOW_SIZE[1])/2)
    elif WINDOW_SIZE[0]/16 < WINDOW_SIZE[1]/9:
        scaled_win = (int(WINDOW_SIZE[1]/9 * 16), WINDOW_SIZE[1])
        position = (-(scaled_win[0] - WINDOW_SIZE[0])/2, 0)
    else:
        scaled_win = WINDOW_SIZE
        position = (0, 0)
    return scaled_win, position


# EVERYTHING ON THE SCREEN ================================================== #
s_backgrounds = [[random.choice(backgrounds), [0, 0]]]
s_player = {"img": player1, "x": 232, "y": 192}
s_water = water(0, 520, 200, 200, 5)
splash_particles = []

# HITBOXES ================================================================== #
h_water = s_water.draw("hitbox")

# OBJECTS =================================================================== #
player = player()


def updateHitboxes():
    global h_water
    h_water = s_water.draw("hitbox")


def update_fps():
    fps_text = pygame.font.SysFont("Arial", 12).render(
        str(int(clock.get_fps())), 1, pygame.Color("white"))
    display.blit(fps_text, (4, 4))


last_time = time.time()

while True:

    # FRAMERATE INDEPENDENCE ================================================ #
    dt = time.time() - last_time
    dt *= framerate
    last_time = time.time()

    updateHitboxes()
    background().update()
    player.update()
    s_water.update(0.3)
    s_water.draw()
    update_particles()
    update_fps()
    if random.randint(1, 120) == 60:
        s_water.splash(random.randint(0, 100), random.randint(1, 20))
    # background().drawGrid()
    # pygame.draw.rect(display, (200, 250, 250), pygame.Rect(240, 128, 32, 32))

    # FLY =================================================================== #
    pressed_keys = pygame.key.get_pressed()
    if pressed_keys[K_SPACE]:
        accelleration = -0.2
    else:
        accelleration = 0.2

    # DIVE ================================================================== #
    pressed_keys = pygame.key.get_pressed()
    if pressed_keys[K_DOWN]:
        dive = True
        if in_water:
            vel = 1.1
    else:
        dive = False

    # BUOYANCY ============================================================== #
    if player.hitbox().bottomleft[1] - 2 > h_water[50].center[1]:
        accelleration = -0.1
        dive = True
        in_water = True
    else:
        in_water = False

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == VIDEORESIZE:
            WINDOW_SIZE = (event.w, event.h)
            win = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                accelleration = -1.1

    win.blit(pygame.transform.scale(
        display, (scaled_win()[0])), scaled_win()[1])
    pygame.display.update()
    clock.tick(framerate)
    # time.sleep(0.1)
