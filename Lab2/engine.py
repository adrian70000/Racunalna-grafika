from pyglet.gl import *
from pyglet.window import key

from particleSystem import ParticleSystem


class Window(pyglet.window.Window):
    global pyglet

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(600, 400)
        self.POV = 60
        self.source = [0, 0, 0]
        pyglet.clock.schedule_interval(self.update, 1.0 / 60.0)

        texture = pyglet.image.load('explosion.bmp').get_texture()

        self.ParticleSys = ParticleSystem(texture, 5)

    def update(self, dt):
        self.ParticleSys.update(dt)

    def on_draw(self):
        self.clear()
        glClear(GL_COLOR_BUFFER_BIT)
        camera_position = [1000, 0, 0]
        lookAt = [0, 0, 0]

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.POV, self.width / self.height, 0.05, 10000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        gluLookAt(camera_position[0], camera_position[1], camera_position[2],
                  lookAt[0], lookAt[1], lookAt[2],
                  0.0, 1.0, 0.0)
        glPushMatrix()
        self.ParticleSys.draw()
        glPopMatrix()
        glFlush()


if __name__ == '__main__':
    window = Window(width=1500, height=700, caption='Particle generator', resizable=True)

    pyglet.app.run()
