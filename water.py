from helpers import *
from constants import *


class Water(arcade.Sprite):
    def __init__(self):
        super().__init__()

        self.scale = WATER_SCALING
        self.cur_texture = 0
        self.update_interval = 0

        # Load textures for enemy
        self.water_textures = []
        for i in range(3):
            texture = arcade.load_texture(resource_path("images/water/water_%s.png" % i))
            self.water_textures.append(texture)

        self.texture = self.water_textures[0]
        self.hit_box = self.texture.hit_box_points

    def update_animation(self, delta_time):
        # Water animation
        self.update_interval += 1
        if self.update_interval > 8:
            self.update_interval = 0
            self.cur_texture += 1
            if self.cur_texture > 2:
                self.cur_texture = 0
            self.texture = self.water_textures[self.cur_texture]
