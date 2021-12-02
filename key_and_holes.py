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


class KeyHole(arcade.Sprite):
    def __init__(self, keyhole_type):
        super().__init__()

        self.scale = KEYHOLE_SCALING

        # Load texture
        self.keyhole_textures = []
        texture = arcade.load_texture(resource_path("images/keyholes/%s.png" % keyhole_type))
        self.keyhole_textures.append(texture)
        self.texture = self.keyhole_textures[0]
        self.hit_box = self.texture.hit_box_points


class Door(arcade.Sprite):
    def __init__(self):
        super().__init__()

        self.scale = 2

        # Load texture
        self.door_textures = []
        texture = arcade.load_texture(resource_path("images/doors/door_0.png"))
        self.door_textures.append(texture)
        self.texture = self.door_textures[0]
        self.hit_box = self.texture.hit_box_points
