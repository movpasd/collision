import random

MAX_V = 5.0
MAX_A = 20.0
VARIATION = 20.0


class Entity:

    def __init__(self, x, y, r=1.0, m=1.0, vx=0.0, vy=0.0, jiggle=False):

        self.x = float(x) 			# Position
        self.y = float(y)
        self.vx = float(vx)			# Velocity
        self.vy = float(vy)

        self.ax = float(0.0)
        self.ay = float(0.0)

        self.m = float(m) 			# Mass
        self.r = float(r) 			# Radius

        self.cx = 0.0				# Used by collision helper
        self.cy = 0.0

        self.player = False
        self.jiggle = jiggle

        # MAYBE: flag dictionary

    def tick(self, dt):

        if self.jiggle and not self.player:
            self.ax += VARIATION * (2 * random.random() - 1)
            self.ay += VARIATION * (2 * random.random() - 1)

            self.ax = MAX_A if self.ax > MAX_A else -MAX_A if self.ax < -MAX_A else self.ax
            self.ay = MAX_A if self.ay > MAX_A else -MAX_A if self.ay < -MAX_A else self.ay

            self.vx += self.ax * dt
            self.vy += self.ay * dt

            self.vx = MAX_V if self.vx > MAX_V else -MAX_V if self.vx < -MAX_V else self.vx
            self.vy = MAX_V if self.vy > MAX_V else -MAX_V if self.vy < -MAX_V else self.vy

        self.x += self.vx * dt
        self.y += self.vy * dt

    def push(self, dx, dy=None):

        self.x += dx
        self.y += dy
