import game
from helpers import *
from constants import *


class Shadow(arcade.Sprite):
    def __init__(self):
        super().__init__()

        self.scale = SHADOW_SCALING
        self.cur_texture = 0
        self.update_interval = 0

        # Load textures for shadow
        self.shadow_textures = []
        for i in range(3):
            texture = arcade.load_texture(resource_path("images/enemy/shadow_%s.png" % i))
            self.shadow_textures.append(texture)

        self.texture = self.shadow_textures[0]
        self.hit_box = self.texture.hit_box_points

    def update_animation(self, delta_time):
        # Shadow animation
        self.update_interval += 1
        if self.update_interval > SHADOW_ANIMATION_SPEED:
            self.update_interval = 0
            self.cur_texture += 1
            if self.cur_texture > 2:
                self.cur_texture = 0
            self.texture = self.shadow_textures[self.cur_texture]
