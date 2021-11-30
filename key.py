from helpers import *
from constants import *


class Key(arcade.Sprite):
    def __init__(self, key_type):
        super().__init__()

        self.scale = KEY_SCALING

        # Load texture
        self.key_textures = []
        texture = arcade.load_texture(resource_path("images/keys/%s.png" % key_type))
        self.key_textures.append(texture)
        self.texture = self.key_textures[0]
        self.hit_box = self.texture.hit_box_points
