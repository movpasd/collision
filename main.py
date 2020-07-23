import pygame
import os
import random
import math
from collections import namedtuple

import collision_helper
from classes import Entity


os.environ['SDL_VIDEO_CENTERED'] = '1'


# Constants and stuff

Pair = namedtuple('Pair', ['x', 'y'])

SETTING_DRAW_VELOCITY = False

WRAP = False

ROOT2 = math.sqrt(2)

WINDOWSIZE = Pair(900, 600)
MAPSIZE = Pair(15.0, 10.0)
SCALE = 25.0
ORIGIN = Pair(450, 300)
TICKRATE = 100
DT = 1 / TICKRATE
VELOCITY_SCALE = 0.2
PLAYER_SPEED = 10.0
GROW_RATE = 3.0
MIN_PLAYER_SIZE = 0.1
MAX_PLAYER_SIZE = 100.0
NUMBER_OF_ENEMIES = 150

INITIAL_PLAYER_MASS = 4.0
MAX_PLAYER_MASS = 100.0
MIN_PLAYER_MASS = 0.1
MAX_ENEMY_MASS = 5.0
MIN_ENEMY_MASS = 1.0

MAXVEL = 4.0

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
MAGENTA = (255, 0, 255)

# UTILITY FUNCTIONS


def blue(mass):
    return (0, min(max(round(2 * 25.5 * (mass - 5)), 0), 255), min(round(2 * 25.5 * mass), 255))


def red(mass):
    return (min(round(2 * 25.5 * mass), 255), min(max(round(2 * 25.5 * (mass - 5)), 0), 255), 0)


def pixels(x: float, y: float=None):

    if y is None:
        return round(x * SCALE)
    else:
        return Pair(round(ORIGIN.x + x * SCALE), round(ORIGIN.y - y * SCALE))


def depixel(u, v=None):

    if v is None:
        return u / SCALE
    else:
        return ((u - ORIGIN.x) / SCALE, (ORIGIN.y - v) / SCALE)


# GAME FUNCTIONS

def render(screen, maprect, ticktime, visibles):

    screen.fill((64, 64, 64))
    pygame.draw.rect(screen, (255, 255, 255), maprect)

    screen.blit(*ticktime)

    for vis in visibles:
        if vis.player:
            pygame.draw.circle(screen, blue(vis.m), pixels(
                vis.x, vis.y), pixels(vis.r))
            if SETTING_DRAW_VELOCITY:
                end_pos = pixels(vis.x, vis.y)
                end_pos = (end_pos.x + pixels(vis.vx * VELOCITY_SCALE),
                           end_pos.y - pixels(vis.vy * VELOCITY_SCALE))
                pygame.draw.line(screen, MAGENTA, pixels(
                    vis.x, vis.y), end_pos, 2)

        else:
            pygame.draw.circle(screen, red(vis.m), pixels(
                vis.x, vis.y), pixels(vis.r))
            if SETTING_DRAW_VELOCITY:
                end_pos = pixels(vis.x, vis.y)
                end_pos = (end_pos.x + pixels(vis.vx * VELOCITY_SCALE),
                           end_pos.y - pixels(vis.vy * VELOCITY_SCALE))
                pygame.draw.line(screen, GREEN, pixels(vis.x, vis.y), end_pos)

    pygame.display.flip()


def check_keys(event, keys):

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_w:
            keys["up"] = True
        elif event.key == pygame.K_a:
            keys["left"] = True
        elif event.key == pygame.K_s:
            keys["down"] = True
        elif event.key == pygame.K_d:
            keys["right"] = True
        elif event.key == pygame.K_PERIOD:
            keys["grow"] = True
        elif event.key == pygame.K_COMMA:
            keys["shrink"] = True
        elif event.key == pygame.K_l:
            keys["fatten"] = True
        elif event.key == pygame.K_k:
            keys["lighten"] = True
    if event.type == pygame.KEYUP:
        if event.key == pygame.K_w:
            keys["up"] = False
        elif event.key == pygame.K_a:
            keys["left"] = False
        elif event.key == pygame.K_s:
            keys["down"] = False
        elif event.key == pygame.K_d:
            keys["right"] = False
        elif event.key == pygame.K_PERIOD:
            keys["grow"] = False
        elif event.key == pygame.K_COMMA:
            keys["shrink"] = False
        elif event.key == pygame.K_l:
            keys["fatten"] = False
        elif event.key == pygame.K_k:
            keys["lighten"] = False


def main():

    pygame.init()

    # Render setup
    pygame.display.set_caption("program")
    screen = pygame.display.set_mode(WINDOWSIZE)
    maprect = pygame.Rect(pixels(-MAPSIZE.x, MAPSIZE.y),
                          (2 * pixels(MAPSIZE.x), 2 * pixels(MAPSIZE.y)))

    font = pygame.font.Font('freesansbold.ttf', 32)
    text_ticktime = font.render("init", True, (255, 255, 255))
    rect_ticktime = pygame.Rect(10, 10, 200, 50)

    # Game setup
    keys = {}
    keys["up"], keys["left"], keys["down"], keys[
        "right"] = False, False, False, False
    keys["grow"], keys["shrink"] = False, False
    keys["fatten"], keys["lighten"] = False, False

    entities = []

    def randpos():
        r1 = 2 * random.random() - 1
        r2 = 2 * random.random() - 1
        return Pair(r1 * MAPSIZE.x, r2 * MAPSIZE.y)

    def randvel():
        return MAXVEL * (2 * random.random() - 1)

    def randm():
        return MIN_ENEMY_MASS + (MAX_ENEMY_MASS - MIN_ENEMY_MASS) * random.random()

    entities.append(Entity(0, 0, 1, m=INITIAL_PLAYER_MASS))
    entities[0].player = True
    player = entities[0]

    # # Randomised
    # for i in range(NUMBER_OF_ENEMIES):
    #     entities.append(Entity(*randpos(), r=0.5 *
    #                            (1 + random.random()), vx=randvel(), vy=randvel(), m=randm(), jiggle=True))

    # Randomised not moving
    for i in range(NUMBER_OF_ENEMIES):
        entities.append(Entity(*randpos(), r=MAPSIZE.x * MAPSIZE.y *
                               (1 + random.random()) /
                               1.55 / NUMBER_OF_ENEMIES,
                               m=randm(), jiggle=False))

    # # Walls
    # for i in range(-5, 5):
    #     entities.append(Entity(-10, 0.5 + 2*i, r=1.0, m=100.0, vx=+2.0, vy=0.0))
    #     entities.append(Entity(+10, 0.5 + 2*i, r=1.0, m=100.0, vx=-2.0, vy=0.0))

    collision_helper.load(entities)

    clock = pygame.time.Clock()

    # Main loop
    running = True
    while running:

        # Event loop
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            check_keys(event, keys)

        # Game loop
        if keys["up"] and not keys["down"]:
            if keys["left"] or keys["right"]:
                player.vy = PLAYER_SPEED / ROOT2
            else:
                player.vy = PLAYER_SPEED
        elif keys["down"] and not keys["up"]:
            if keys["left"] or keys["right"]:
                player.vy = -PLAYER_SPEED / ROOT2
            else:
                player.vy = -PLAYER_SPEED
        else:
            player.vy = 0.0

        if keys["right"] and not keys["left"]:
            if keys["down"] or keys["up"]:
                player.vx = PLAYER_SPEED / ROOT2
            else:
                player.vx = PLAYER_SPEED
        elif keys["left"] and not keys["right"]:
            if keys["down"] or keys["up"]:
                player.vx = -PLAYER_SPEED / ROOT2
            else:
                player.vx = -PLAYER_SPEED
        else:
            player.vx = 0.0

        if keys["grow"] and not keys["shrink"] and player.r < MAX_PLAYER_SIZE:
            player.r += GROW_RATE * DT
        elif keys["shrink"] and not keys["grow"] and player.r > MIN_PLAYER_SIZE:
            player.r -= GROW_RATE * DT

        if keys["fatten"] and not keys["lighten"] and player.m < MAX_PLAYER_MASS:
            player.m += GROW_RATE * DT
        elif keys["lighten"] and not keys["fatten"] and player.m > MIN_PLAYER_MASS:
            player.m -= GROW_RATE * DT

        if not WRAP:
            for ent in entities:
                if ent.x <= -MAPSIZE.x + ent.r:
                    ent.x = -MAPSIZE.x + ent.r
                elif ent.x >= MAPSIZE.x - ent.r:
                    ent.x = MAPSIZE.x - ent.r

                if ent.y <= -MAPSIZE.y + ent.r:
                    ent.y = -MAPSIZE.y + ent.r
                elif ent.y >= MAPSIZE.y - ent.r:
                    ent.y = MAPSIZE.y - ent.r
        else:
            for ent in entities:
                if ent.x <= -MAPSIZE.x:
                    ent.x = MAPSIZE.x
                elif ent.x >= MAPSIZE.x:
                    ent.x = -MAPSIZE.x

                if ent.y <= -MAPSIZE.y:
                    ent.y = MAPSIZE.y
                elif ent.y >= MAPSIZE.y:
                    ent.y = -MAPSIZE.y

        for ent in entities:
            ent.tick(DT)

        collision_helper.tick()

        # Call render loop
        ticktime = clock.get_time()
        text_ticktime = font.render(str(ticktime), True, (255, 255, 255))
        render(screen, maprect, (text_ticktime, rect_ticktime), entities)

        # Tick clock
        clock.tick(TICKRATE)


if __name__ == "__main__":
    main()
