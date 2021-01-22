from random import *

from pyrr import Vector3


class Particle:
    def __init__(self, pos):
        self.pos = pos.copy()
        self.vel = Vector3([randrange(-3, 3), randrange(-3, 3), randrange(-3,3)])
        self.lifeTime = 340

    def update(self, dt):
        self.pos += self.vel
        self.lifeTime -= 1
