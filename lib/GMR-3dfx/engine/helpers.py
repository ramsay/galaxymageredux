import texture
import animated_texture
import storage
import image

import include
from include import *

def get_best_array_type(render_type=None, max_size=10,
                        opt=0):
    """This function returns the best possible array type for what you need.
       render_type is the OpenGL constant used in rendering, ie GL_POLYGON, GL_TRINAGLES, etc.
       max_size is the number of individual points in the array
       opt is how the array is optimized, starting at 0 for fast access to 5 for fast rendering
           5 also makes use of a cached VBO (if possible) - so it is very fast rendering and modifying
           *if* you are modifying a very large number of points - otherwise it is slower at modifying"""

    assert opt >= 0 and opt <= 5

    if not VBO_AVAILABLE:
        return VertexArray(render_type, max_size)

    if opt == 0:
        return VertexArray(render_type, max_size)
    elif opt == 1:
        return VBOArray(render_type, max_size, "stream")
    elif opt == 2:
        return VBOArray(render_type, max_size, "dynamic")
    elif opt == 3:
        return VBOArray(render_type, max_size, "static")
    else:
        return VBOArray(render_type, max_size, "static", True)

def load_texture(name):
    iname = name.split('.')[-1].lower()
    if iname in ('png', 'bmp', 'jpg'):
        short = os.path.split(name)[1]
        new = texture.Texture()
        new._from_file(name)
        return new
    if iname == 'gif':
        short = os.path.split(name)[1]
        new = animated_texture.Texture()
        new._from_file(name)
        return new
    raise MissingData('No file "%s"'%name)

def load_image2D(name, area=None):
    return image.Image2D(load_texture(name), area)

class TextureHandler(object):
    def __init__(self):
        self.textures = {}

    def load_dir(self, dire, replace=False):
        for i in os.listdir(dire):
            self.load_texture(i, replace)

    def load_texture(self, name, replace=False):
        if name.split('.')[-1].lower() in ('png', 'bmp', 'jpg', 'gif'):
            short = os.path.split(name)[1]
            if replace or (not short in self.textures):
                self.textures[short] = load_texture(name)

    def get_texture(self, name):
        if name in self.textures:
            tex = self.textures[name]
            if isinstance(tex, texture.Texture):
                return texture.TextureClone(tex)
            else:
                return animated_texture.TextureClone(tex)

    def free_textures(self):
        for i in self.textures.values():
            i.free_texture()
        self.textures = {}
