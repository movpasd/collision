import math
from main import Pair


collidables = []

BOUNCE = 0.8  # must be between 0.0 and 1.0


def load(entities):

    for ent in entities:

        collidables.append(ent)


def tick():

    resolve_corrections()
    apply_corrections()


def collision(ent1, ent2):

    # Edge cases

    if ent1 is ent2:

        return True, Pair(0.0, 0.0)

    # If the entities are in the same position,
    if math.isclose(ent1.x, ent2.x) and math.isclose(ent1.y, ent2.y):

        # if they have the same velocity
        if math.isclose(ent1.vx, ent2.vx) and math.isclose(ent1.vy, ent2.vy):

            # find their normalised common velocity
            ux, uy = ent1.vx + ent2.vx, ent1.vy + ent2.vy
            l = math.sqrt(ux**2 + uy**2)
            ux, uy = ux / l, uy / l

            # and return a correction vector perpendicular to that,
            # with magnitude of the sum of their radii.
            s = ent1.r + ent2.r
            return True, Pair(-uy * s, ux * s)

        # If they don't have the same velocity, same as above
        # but with their relative velocity.
        ux, uy = ent1.vx - ent2.vx, ent1.vy - ent2.vy
        l = math.sqrt(ux**2 + uy**2)
        ux, uy = ux / l, uy / l
        s = ent1.r + ent2.r
        return True, Pair(-uy * s, ux * s)

    # Main case

    flag = (ent1.x - ent2.x)**2 + (ent1.y - ent2.y)**2 <= (ent1.r + ent2.r)**2

    if flag:

        dx = ent2.x - ent1.x
        dy = ent2.y - ent1.y
        s = math.sqrt(dx**2 + dy**2)
        factor = (ent1.r + ent2.r) / s - 1

        return True, Pair(dx * factor, dy * factor)

    else:

        return False, None


def resolve_corrections():

    # Wipe corrections

    for ent in collidables:

        ent.cx = 0
        ent.cy = 0

    l = len(collidables)
    for i in range(l):
        ent1 = collidables[i]
        for j in range(i, l):
            ent2 = collidables[j]

            flag, correction = collision(ent1, ent2)

            if flag:

                tm = ent1.m + ent2.m

                ent1.cx -= BOUNCE * ent2.m * correction.x / tm
                ent1.cy -= BOUNCE * ent2.m * correction.y / tm

                ent2.cx += BOUNCE * ent1.m * correction.x / tm
                ent2.cy += BOUNCE * ent1.m * correction.y / tm


def apply_corrections():

    for ent in collidables:

        ent.x += ent.cx
        ent.y += ent.cy
