from pyglet.gl import *
import numpy as np
from pyglet.window import key
import ctypes

timer = 0
dcm = False


def rotation(currOrient, newOrient):
    rot_axis = np.cross(currOrient, newOrient)
    dot_curr_next = np.dot(currOrient, newOrient)
    curr_norm = np.linalg.norm(currOrient)
    next_norm = np.linalg.norm(newOrient)

    rot_angle = np.rad2deg(np.arccos(dot_curr_next / (curr_norm * next_norm)))

    return rot_axis, rot_angle


def rotationDCM(tangent, d2):
    tangent = tangent / np.linalg.norm(tangent)
    d2 = d2 / np.linalg.norm(d2)
    all_zeros = not np.any(d2)
    w = tangent
    if all_zeros:
        u = tangent
    else:
        u = np.cross(tangent, d2)
    v = np.cross(w, u)
    tmp = [[w[0], u[0], v[0], 0], [w[1], u[1], v[1], 0], [w[2], u[2], v[2], 0], [0, 0, 0, 1]]
    R = np.array(tmp)
    return np.linalg.inv(R)


class Object:
    vertices = []
    polygons = []
    batch = pyglet.graphics.Batch()

    def __init__(self, filepath):
        data = open(filepath, 'r')
        for line in data:
            if line[0] == 'v':
                tmp = line.split(" ")
                self.vertices.append(list(map(float, tmp[1:4])))
            if line[0] == 'f':
                tmp = line.split(" ")
                self.polygons.append(list(map(int, tmp[1:4])))
        self.setBatch()

    def setBatch(self):
        for polygon in self.polygons:
            v1 = self.vertices[polygon[0] - 1]
            v2 = self.vertices[polygon[1] - 1]
            v3 = self.vertices[polygon[2] - 1]
            self.batch.add(3, GL_TRIANGLES, None,
                           ('v3f', [v1[0], v1[1], v1[2], v2[0], v2[1], v2[2], v3[0], v3[1], v3[2]]),
                           ('c3f', (2, 5, 0, 0, 5, 0, 0, 5, 0)))


class BSpline:
    vertices = []
    polygons = []
    segments = []
    tangents = []
    d2s = []
    resolution = 30
    batch = pyglet.graphics.Batch()

    def __init__(self, filepath):
        data = open(filepath, 'r')
        for line in data:
            if line[0] == 'v':
                tmp = line.split(" ")
                self.vertices.append(list(map(float, tmp[1:4])))
            if line[0] == 'f':
                tmp = line.split(" ")
                self.polygons.append(list(map(int, tmp[1:4])))
        self.calc_spline()
        self.setBatch()

    def diff2(self, i_segment, t):

        T = [2 * t, 1]

        B = 1 / 2 * np.array([[-1, 3, -3, 1],
                              [2, -4, 2, 0]])

        control_points = self.vertices
        R = np.array([control_points[i_segment - 1],
                      control_points[i_segment],
                      control_points[i_segment + 1],
                      control_points[i_segment + 2]])

        TB = np.dot(T, B)
        TBR = np.dot(TB, R)

        return TBR

    def calc_segment_t(self, i_segment, t):
        T = np.array([t ** 3, t ** 2, t, 1])
        B = 1 / 6 * np.array([[-1, 3, -3, 1], [3, -6, 3, 0], [-3, 0, 3, 0], [1, 4, 1, 0]])
        control_points = self.vertices
        R = np.array([control_points[i_segment - 1],
                      control_points[i_segment],
                      control_points[i_segment + 1],
                      control_points[i_segment + 2]])
        TB = np.dot(T, B)
        TBR = np.dot(TB, R)

        Tt = [t ** 2, t, 1]
        Bt = 1 / 2 * np.array([[-1, 3, -3, 1], [2, -4, 2, 0], [-1, 0, 1, 0]])
        TBt = np.dot(Tt, Bt)
        TBRt = np.dot(TBt, R)

        return TBR, TBRt

    def calc_spline(self):
        for index in range(1, len(self.vertices) - 3 + 1):
            for t in np.linspace(0, 1, self.resolution):
                points, tangents = self.calc_segment_t(index, t)
                self.segments.append(points)
                self.tangents.append(tangents)
                self.d2s.append(self.diff2(index, t))

    def tangent(self, segment, index):
        scale = 1
        return [segment[0], segment[1], segment[2], segment[0] + self.tangents[index][0] / scale,
                segment[1] + self.tangents[index][1] / scale, segment[2] + self.tangents[index][2] / scale]

    def setBatch(self):
        coordinates = []
        tangents = []
        i = 0
        for point in self.segments:
            for coordinate in self.tangent(point, i):
                tangents.append(coordinate)
            for coordinate in point:
                coordinates.append(coordinate)
            i = i + 1
        self.batch.add(len(self.segments), GL_LINE_STRIP, None, ('v3f', coordinates))
        for i in range(int(len(tangents) / 6)):
            self.batch.add(2, GL_LINES, None, ('v3f', tangents[6 * i:6 * i + 6]),
                           ('c3d', [5, 0.2, 0.2, 0.2, 5, 5]))


obj = Object("kocka.obj")
spline = BSpline("bspline.obj")

pos = [-20, 0, -60]
rot_y = 50
rot_x = 0
config = Config(sample_buffers=1, samples=8)
window = pyglet.window.Window(height=800, width=1200, config=config)


@window.event
def on_draw():
    global pos_z, rot_y, rot_x
    global timer
    global asdf
    window.clear()

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90, 1, 1, 100)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glTranslatef(*pos)
    glRotatef(rot_y, rot_x, 1, 0)

    glPushMatrix()
    current_point = spline.segments[timer]
    current_tangent = spline.tangents[timer]

    if dcm:
        R_inv = rotationDCM(spline.tangents[timer], spline.d2s[timer])
        tmp = []
        for i in range(4):
            for j in range(4):
                tmp.append(R_inv[j][i])
        tmp = (ctypes.c_float * len(tmp))(*tmp)
        glTranslatef(current_point[0], current_point[1], current_point[2])
        glMultMatrixf(tmp)

    else:
        glTranslatef(current_point[0], current_point[1], current_point[2])
        rot_axis, rot_angle = rotation([1, 0, 1], current_tangent)
        glRotatef(rot_angle, rot_axis[0], rot_axis[1], rot_axis[2])

    obj.batch.draw()
    glPopMatrix()

    spline.batch.draw()

    glFlush()


def update(dt):
    global timer
    timer = timer + 1
    if timer >= len(spline.segments):
        timer = 0


@window.event
def on_key_press(s, m):
    global rot_y, rot_x

    if s == pyglet.window.key.W:
        rot_x -= 5
    if s == pyglet.window.key.S:
        rot_x += 5
    if s == pyglet.window.key.A:
        rot_y += 5
    if s == pyglet.window.key.D:
        rot_y -= 5


pyglet.clock.schedule(update)
pyglet.app.run()
