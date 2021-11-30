from helpers import *
from constants import *


class Enemy(arcade.Sprite):
    def __init__(self, enemy_type):
        super().__init__()

        self.scale = CHARACTER_SCALING
        self.cur_texture = 0
        self.update_interval = 0
        self.enemy_type = enemy_type

        # Load textures for enemy
        self.enemy_textures = []
        for i in range(3):
            texture = arcade.load_texture(resource_path("images/enemy/%s_%s.png" % (self.enemy_type, i)))
            self.enemy_textures.append(texture)

        self.texture = self.enemy_textures[0]
        self.hit_box = self.texture.hit_box_points

    def update_animation(self, delta_time):
        # Enemy animation
        self.update_interval += 1
        if self.update_interval > 4:
            self.update_interval = 0
            self.cur_texture += 1
            if self.cur_texture > 2:
                self.cur_texture = 0
            self.texture = self.enemy_textures[self.cur_texture]
