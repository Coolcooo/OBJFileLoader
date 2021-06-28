import os

import pygame
import sys
from math import sqrt

from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.constants import *

from objloader import *
import numpy as np
import cv2


def crop(image):
    th = 20
    y_nonzero, x_nonzero, _ = np.nonzero(image > th)
    return image[np.min(y_nonzero):np.max(y_nonzero), np.min(x_nonzero):np.max(x_nonzero)]


viewport = (500, 500)
hx = viewport[0] / 2
hy = viewport[1] / 2
srf = pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF | pygame.HIDDEN)

glLightfv(GL_LIGHT0, GL_POSITION, (-40, 200, 100, 0.0))
glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
glEnable(GL_LIGHT0)
glEnable(GL_LIGHTING)
glEnable(GL_COLOR_MATERIAL)
glEnable(GL_DEPTH_TEST)
glShadeModel(GL_SMOOTH)

obj = OBJ(sys.argv[1], swapyz=True)
obj.generate()

clock = pygame.time.Clock()

glMatrixMode(GL_PROJECTION)
glLoadIdentity()
width, height = viewport
gluPerspective(90.0, width / float(height), 1, 9999)

glEnable(GL_DEPTH_TEST)
glMatrixMode(GL_MODELVIEW)

length = obj.list_max[0] - obj.list_min[0]
width = obj.list_max[1] - obj.list_min[1]
height = obj.list_max[2] - obj.list_min[2]
max_z = max(length, width, height)

rx, ry = (0, 0)
tx, ty = (0, -viewport[0] / 2)
zpos = max_z * 2
count_screenshots = 1440
obj_name = sys.argv[1].split('.')[-2]
rx_count = round(sqrt(count_screenshots))
ry_count = round(sqrt(count_screenshots))
try:
    os.mkdir(obj_name)
except FileExistsError:
    hfdsk = 5

for i in range(rx_count):
    rx += 360 / rx_count
    for j in range(ry_count):
        ry += 360 / ry_count

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslate(tx / 20., ty / 20., - zpos)
        glRotate(ry, 1, 0, 0)
        glRotate(rx, 0, 1, 0)
        obj.render()

        size = srf.get_size()
        buffer = glReadPixels(0, 0, *size, GL_RGBA, GL_UNSIGNED_BYTE)
        screen_surf = pygame.image.fromstring(buffer, size, "RGBA")
        index_for_image = i * (rx_count - 1) + j
        img_name = "{0}\\{0}{1}.jpg".format(obj_name, index_for_image)
        pygame.image.save(screen_surf, img_name)
        load_img = cv2.imread(img_name)
        load_img = crop(load_img)
        load_img = cv2.cvtColor(load_img, cv2.COLOR_BGR2GRAY)
        (thresh, load_img) = cv2.threshold(load_img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        load_img = cv2.resize(load_img, viewport)
        cv2.imwrite(img_name, load_img)
        pygame.display.flip()
