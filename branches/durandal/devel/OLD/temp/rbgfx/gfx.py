#!/usr/bin/env python

# LICENSE:
#
# Copyright (c) 2007 Brandon Barnes and GalaxyMage Redux contributors.
#
# GalaxyMage Redux is free software; you can redistribute it and/or 
# modify it under the terms of version 2 of the GNU General Public 
# License, as published by the Free Software Foundation.
# 
# GalaxyMage Redux is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with GalaxyMage Redux; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

#This module is used for rendering the game screen, and switching to gui rendering mode and back.

import random

from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *


#globals
ScreenSize = (640, 480) #this is the width/height of teh screen in pixels

RegImageSize = (50, 50) #this can be any number, basically any image that has the dimensions (50, 50)
                        #will be rendered as a 1x1 textured quad, (100,100) images will be 2x2, etc.

def init():
    """creates a screen, enables required OpenGL rendering controls, and sets up the viewport"""

    pygame.init()

    pygame.display.set_mode(ScreenSize, OPENGL|DOUBLEBUF)#|FULLSCREEN)
        
    glEnable(GL_TEXTURE_2D)
    glFrontFace(GL_CCW)
    glEnable(GL_COLOR_MATERIAL)

    glEnable(GL_LIGHTING)
    glEnable(GL_NORMALIZE)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

    glClearColor(1,1,1,1)
    return None

def set_3d():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.0*ScreenSize[0]/ScreenSize[1],
                   0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    return None

def set_2d():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, ScreenSize[0],
            0, ScreenSize[1],
            -1000, 1000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    return None

def clear_screen():
    glClear(GL_DEPTH_BUFFER_BIT|GL_COLOR_BUFFER_BIT)

    return None


class Camera(object):
    def __init__(self, position=(0, 0, 0),
                 angle=(0, 0, 0),
                 distance=15):
        """This is a generic camera class.
           It is used to keep track of and move the position,
               angle and distance of the OpenGL camera.
           While there can be any number of Camera's active at one time,
               it should be noted that they are all technically in control of the
               <i>same</i> camera, and are just different settings.

           position is a list or tuple of len 3,
               it specifies the position that the camera is looking at.

           angle is a list or tuple of len 3,
               it specifies the angle the camera is turned to.

           distance is how far back the camera is from position."""

        self.position = position
        self.angle = angle
        self.distance = distance

        self.dirty = False

    def __check_values(self):
        """This method checks to make sure he angle of the camera is correct."""
        self.angle = list(self.angle)
        for i in range(len(self.angle)):
            while self.angle[i] > 360:
                self.angle[i] -= 360
            while self.angle[i] < 0:
                self.angle[i] += 360

        return None

    def rotate(self, angle=(0, 0, 0)):
        x, y, z = self.angle
        x += angle[0]
        y += angle[1]
        z += angle[2]

        self.angle = (x, y, z)
        return None

    def move(self, direction=(0, 0, 0)):
        x, y, z = self.position
        x += direction[0]
        y += direction[1]
        z += direction[2]

        self.position = (x, y, z)
        return None

    def update(self):
        """This method rotates, moves and then zooms the camera."""
        self.__check_values()
        if self.dirty:
            glPopMatrix()
            self.dirty = False

        glPushMatrix()

        glTranslatef(0, 0, -self.distance)

        glRotatef(self.angle[0], 1, 0, 0)
        glRotatef(self.angle[1], 0, 1, 0)
        glRotatef(self.angle[2], 0, 0, 1)

        glTranslatef(*self.position)

        self.dirty = True

        return None


class Light(object):
    num_lights=0
    def __init__(self, position=(0, 0, 0), specular=(0, 0, 0, 0),
                 ambient=(0, 0, 0, 0), diffuse=(0, 0, 0, 0),
                 shininess=50, directional=1):
        """This is a container class for a glLight.
           There should at most be 8 lights at one time.
           Each light is independant of the others, so any changes to
               will not affect the others.

           position is a list or tuple of len 3,
               it specifies the lights position in 3d space.

           specular is a list or tuple of len 4,
               it determines how shiny the highlights produced by this light will be.

           ambient is a list or tuple of len 4,
                it is the color of the normal light that comes from all directions equally
                and is scattered across the scene uniformally.

           diffuse is a list or tuple of len 4,
               it determines the color of a specific direction source - like the sun -
               and it will light objects more intensely the more they face towards it.

           shininess is an int > 0 < 128, that determines how widespread(for a low number),
               or how concentrated(for a high number) the specular light is applied.

           directional must be 0, 1, True or False - used to determine whether the
               light fills everywhere - like a lightbulb,
               or only in one direction - like a flashlight."""

        self.position = position
        self.specular = specular
        self.ambient = ambient
        self.diffuse = diffuse
        self.shininess = shininess

        self.directional = directional

        self.light_num = int(self.num_lights)
        self.num_lights += 1

        self.compile()

    def __get_pos(self):
        """This method returns the position <i>plus</i> directional of the light"""

        return self.position[0], self.position[1], self.position[2], -int(self.directional)

    def compile(self):
        """This method compiles the light to a GL_LIGHT(n),
           using the parameters stored here."""
        exec "kind = GL_LIGHT" + str(self.light_num) #yes, I'm using the evil exec, but it saves about
                                                     #40+ lines of code here.
        glEnable(kind)
        glMaterialfv( GL_FRONT_AND_BACK, GL_SPECULAR, self.specular )
        glMaterialfv( GL_FRONT_AND_BACK, GL_AMBIENT, self.ambient )
        glMaterialfv( GL_FRONT_AND_BACK, GL_SHININESS, self.shininess )
        glLightfv(kind, GL_AMBIENT, self.ambient)
        glLightfv(kind, GL_DIFFUSE, self.diffuse)
        glLightfv(kind, GL_SPECULAR, self.specular)
        glLightfv(kind, GL_POSITION, self.__get_pos())

        return None



def fix_image_dimensions(h, w):
    """This function finds the nearest power of 2 that is >= the h/w of an image.
       Usage: to convert image sizes to work with opengl."""
    nh = 16
    nw = 16

    while nh < h:
        nh *= 2
    while nw < w:
        nw *= 2

    return nh, nw


def create_texture(surface):
    """This function generates a texture, converts the image to the texture,
       and returns the opengl texture pointer."""
    image=glGenTextures(1)

    sw, sh = fix_image_dimensions(*surface.get_size())
    textureSurface = pygame.transform.scale(surface, (sw, sh))

    textureData = pygame.image.tostring(textureSurface, "RGBA", 1)

    glBindTexture(GL_TEXTURE_2D, image)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                 textureSurface.get_width(),
                 textureSurface.get_height(),
                 0, GL_RGBA,
                 GL_UNSIGNED_BYTE, textureData)

    return image

def load_image(filename):
    return create_texture(pygame.image.load(filename))

class Sprite(object):
    def __init__(self, surface,
                 camera=None,
                 color=(1, 1, 1, 1)):
        self.surface = surface
        self.color = color

        self.texture = create_texture(self.surface)

        self.size = self.surface.get_size()
        self.fixed_size = (float(self.size[0]) / RegImageSize[0] / 2,
                           float(self.size[1]) / RegImageSize[1] / 2)

        self.camera = camera

    def render(self, pos):
        posx, posy, posz = pos

        posx *= 2
        posy += 0.5
        posz *= 2 #compensate because the squares are + and - 1

        sx, sy = self.fixed_size

        glBindTexture(GL_TEXTURE_2D, self.texture)

        ble_return = glGetBooleanv(GL_BLEND)
        light_return = glGetBooleanv(GL_LIGHTING)

        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)

        glPushMatrix()
        glTranslatef(posx, posy, posz)
        if self.camera:
            glRotatef(-self.camera.angle[2], 0, 0, 1)
            glRotatef(-self.camera.angle[1], 0, 1, 0)
            glRotatef(-self.camera.angle[0], 1, 0, 0)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 1);glVertex3f(-sx, sy, 0)
        glTexCoord2f(1, 1);glVertex3f(sx, sy, 0)
        glTexCoord2f(1, 0);glVertex3f(sx, -sy, 0)
        glTexCoord2f(0, 0);glVertex3f(-sx, -sy, 0)
        glEnd()

        glPopMatrix()

        if not ble_return:glDisable(GL_BLEND)
        if light_return:glEnable(GL_LIGHTING)

        return None


class Tile(object):
    def __init__(self, images,
                 pos, corner_adds=(0, 0, 0, 0),
                 bottom=0, height=1,
                 color=(1,1,1,1), color_deviation=(1,1,1,1)):

        self.images = images

        self.corner_adds = corner_adds #[topleft, topright, bottom;eft, bottomright]

        self.pos = pos
        self.bottom = bottom
        self.height = height

        self.color = color
        self.color_deviation = color_deviation

        self.use_color = self.get_color()

    def set_color(self, new, deviation=None):
        self.color = new
        if deviation:
            self.color_deviation = deviation
        self.use_color = self.get_color()

        return None

    def get_top(self):
        return self.pos[0], self.bottom+self.height, self.pos[1]

    def get_color(self):
        r, g, b, a = self.color
        rr = float(random.randint(int(-self.color_deviation[0]*100),
                                  int(self.color_deviation[0]*100)))/ 100
        rg = float(random.randint(int(-self.color_deviation[1]*100),
                                  int(self.color_deviation[1]*100)))/ 100
        rb = float(random.randint(int(-self.color_deviation[2]*100),
                                  int(self.color_deviation[2]*100)))/ 100
        ra = float(random.randint(int(-self.color_deviation[3]*100),
                                  int(self.color_deviation[3]*100)))/ 100

        r += rr
        g += rg
        b += rb
        a += ra

        if r > 1:
            r = 1.0
        if r < 0:
            r = 0.0

        if g > 1:
            g = 1.0
        if g < 0:
            g = 0.0

        if b > 1:
            b = 1.0
        if b < 0:
            b = 0.0

        if a > 1:
            a = 1.0
        if a < 0:
            a = 0.0

        return r, g, b, a

    def __render_top(self, mid, tl, tr, bl, br, tex):
        glBindTexture(GL_TEXTURE_2D, tex)
        glColor4f(*self.use_color)

        glBegin(GL_TRIANGLES)
        #render left face first:
        glTexCoord2f(0, 1); glVertex3f(-1, bl, 1)
        glTexCoord2f(0, 0); glVertex3f(-1, tl, -1)
        glTexCoord2f(0.5, 0.5); glVertex3f(0, mid, 0)

        #render top face second:
        glTexCoord2f(0, 0); glVertex3f(-1, tl, -1)
        glTexCoord2f(1, 0); glVertex3f(1, tr, -1)
        glTexCoord2f(0.5, 0.5); glVertex3f(0, mid, 0)

        #render right face third:
        glTexCoord2f(1, 0); glVertex3f(1, tr, -1)
        glTexCoord2f(1, 1); glVertex3f(1, br, 1)
        glTexCoord2f(0.5, 0.5); glVertex3f(0, mid, 0)

        #render bottom face last:
        glTexCoord2f(0, 1); glVertex3f(-1, bl, 1)
        glTexCoord2f(1, 1); glVertex3f(1, br, 1)
        glTexCoord2f(0.5, 0.5); glVertex3f(0, mid, 0)
        glEnd()

        return None

    def __render_top_pick(self, mid, tl, tr, bl, br):
        glBegin(GL_TRIANGLES)
        #render left face first:
        glVertex3f(-1, bl, 1)
        glVertex3f(-1, tl, -1)
        glVertex3f(0, mid, 0)

        #render top face second:
        glVertex3f(-1, tl, -1)
        glVertex3f(1, tr, -1)
        glVertex3f(0, mid, 0)

        #render right face third:
        glVertex3f(1, tr, -1)
        glVertex3f(1, br, 1)
        glVertex3f(0, mid, 0)

        #render bottom face last:
        glVertex3f(-1, bl, 1)
        glVertex3f(1, br, 1)
        glVertex3f(0, mid, 0)
        glEnd()

        return None

    def __render_side(self, coords, tex):
        tl, tr, br, bl = coords
        glBindTexture(GL_TEXTURE_2D, tex)
        glColor4f(*self.use_color)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0);glVertex3f(*tl)
        glTexCoord2f(1, 0);glVertex3f(*tr)
        glTexCoord2f(1, 1);glVertex3f(*br)
        glTexCoord2f(0, 1);glVertex3f(*bl)
        glEnd()

        return None

    def __render_side_pick(self, coords):
        tl, tr, br, bl = coords
        glBindTexture(GL_TEXTURE_2D, 0L)
        glBegin(GL_QUADS)
        glVertex3f(*tl)
        glVertex3f(*tr)
        glVertex3f(*br)
        glVertex3f(*bl)
        glEnd()

        return None
##        return self.__render_side(coords, self.images[0])

    def _get_corners(self):
        mid = self.bottom + self.height
        topleft = mid + self.corner_adds[0]
        topright = mid + self.corner_adds[1]
        bottomleft = mid + self.corner_adds[2]
        bottomright = mid + self.corner_adds[3]

        return mid, topleft, topright, bottomleft, bottomright

    def _render_reg(self, corners):
        mid, tl, tr, bl, br = corners

        #top
        self.__render_top(mid, tl, tr, bl, br, self.images[0])
        #west
        self.__render_side(((-1, tl, -1),
                           (-1, bl, 1),
                           (-1, self.bottom, 1),
                           (-1, self.bottom, -1)),
                           self.images[1])
        #east
        self.__render_side(((1, br, 1),
                           (1, tr, -1),
                           (1, self.bottom, -1),
                           (1, self.bottom, 1)),
                           self.images[2])
        #north
        self.__render_side(((1, tr, -1),
                           (-1, tl, -1),
                           (-1, self.bottom, -1),
                           (1, self.bottom, -1)),
                           self.images[3])
        #south
        self.__render_side(((-1, bl, 1),
                           (1, br, 1),
                           (1, self.bottom, 1),
                           (-1, self.bottom, 1)),
                           self.images[4])
        #bottom
        self.__render_side(((-1, self.bottom, -1),
                            (1, self.bottom, -1),
                            (1, self.bottom, 1),
                            (-1, self.bottom, 1)),
                           self.images[0])
        return None

    def _render_pick(self, corners):
        mid, tl, tr, bl, br = corners

        #top
        self.__render_top_pick(mid, tl, tr, bl, br)
        #west
        self.__render_side_pick(((-1, tl, -1),
                           (-1, bl, 1),
                           (-1, self.bottom, 1),
                           (-1, self.bottom, -1)))
        #east
        self.__render_side_pick(((1, br, 1),
                           (1, tr, -1),
                           (1, self.bottom, -1),
                           (1, self.bottom, 1)))
        #north
        self.__render_side_pick(((1, tr, -1),
                           (-1, tl, -1),
                           (-1, self.bottom, -1),
                           (1, self.bottom, -1)))
        #south
        self.__render_side_pick(((-1, bl, 1),
                           (1, br, 1),
                           (1, self.bottom, 1),
                           (-1, self.bottom, 1)))
        #bottom
        self.__render_side_pick(((-1, self.bottom, -1),
                            (1, self.bottom, -1),
                            (1, self.bottom, 1),
                            (-1, self.bottom, 1)))
        return None

    def render(self, pick=False):
        posx, posz = self.pos

        posx *= 2
        posz *= 2 #compensate because the squares are + and - 1

        corners = self._get_corners()

        glPushMatrix()
        glTranslatef(posx, 0, posz)

        if pick:
            self._render_pick(corners)
        else:
            self._render_reg(corners)

        glPopMatrix()

        return None

def select_tiles(tiles, mouse_pos):
    clear_screen()
    mx, my = mouse_pos
    my = ScreenSize[1] - my
    cur_color = 1
    last_color = glReadPixelsf(mx, my, 1, 1, GL_RGB)
    correct = None
    for i in tiles:
        glColor3f(cur_color, 0, 0)
        i.render(pick=True)
        result = glReadPixelsf(mx, my, 1, 1, GL_RGB)
        if last_color != result:
            last_color = result
            correct = i
            if cur_color == 0.5:
                cur_color = 1
            else:
                cur_color = 0.5
##    pygame.display.flip()
    clear_screen()
    return correct