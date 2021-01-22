from random import *

import numpy as np
from pyglet.gl import *
from pyrr import Vector3

from particle import Particle


class ParticleSystem:
    def __init__(self, texture, num=1, size=50):
        self.particles = []
        self.texture = texture
        self.size = size
        self.newParticles(num)
        self.timer = 0

    def newParticles(self, num):
        for i in range(0, num):
            p = Particle(Vector3([0, 0, 0]))
            self.particles.append(p)

    def update(self, dt):
        self.timer += 1
        for p in self.particles:
            p.update(dt)
            if p.lifeTime <= 0:
                self.particles.remove(p)
        #if len(self.particles) == 0:
         #   self.newParticles(randint(10, 40))
        if self.timer % 120 == 0:
            self.newParticles(randint(10, 40))

    def draw(self):
        glEnable(self.texture.target)
        glBindTexture(self.texture.target, self.texture.id)

        glEnable(GL_BLEND)
        glBlendFunc(GL_ONE, GL_ONE)

        glPushMatrix()
        for p in self.particles:

            matrix = (GLfloat * 16)()
            glGetFloatv(GL_MODELVIEW_MATRIX, matrix)
            matrix = list(matrix)
            CameraUp = np.array([matrix[1], matrix[5], matrix[9]])
            CameraRight = np.array([matrix[0], matrix[4], matrix[8]])
            size = self.size

            v1 = p.pos + CameraRight * size + CameraUp * -size
            v2 = p.pos + CameraRight * size + CameraUp * size
            v3 = p.pos + CameraRight * -size + CameraUp * -size
            v4 = p.pos + CameraRight * -size + CameraUp * size

            glBegin(GL_QUADS)
            glTexCoord2f(0, 0)
            glVertex3f(v3[0], v3[1], v3[2])
            glTexCoord2f(1, 0)
            glVertex3f(v4[0], v4[1], v4[2])
            glTexCoord2f(1, 1)
            glVertex3f(v2[0], v2[1], v2[2])
            glTexCoord2f(0, 1)
            glVertex3f(v1[0], v1[1], v1[2])

            glEnd()
        glDisable(GL_BLEND)
        glPopMatrix()
        glDisable(self.texture.target)
