from constants import *
from helpers import *


class EnemyExplosion(arcade.Sprite):
    def __init__(self):
        super().__init__()

        self.scale = CHARACTER_SCALING
        self.cur_texture = 0
        self.update_interval = 0

        # Start at the first frame
        self.current_texture = 0

        # Load textures for enemy
        self.enemy_animation_textures = []
        for i in range(5):
            texture = arcade.load_texture(resource_path("images/animations/enemy_%s.png" % i))
            self.enemy_animation_textures.append(texture)

        self.texture = self.enemy_animation_textures[0]

    def update(self):
        self.update_interval += 1
        if self.update_interval > 2:
            self.update_interval = 0
            self.cur_texture += 1
            if self.cur_texture > 4:
                self.remove_from_sprite_lists()
                return
            self.texture = self.enemy_animation_textures[self.cur_texture]


class DoorOpenAnimation(arcade.Sprite):
    def __init__(self):
        super().__init__()

        self.scale = 2
        self.cur_texture = 0
        self.update_interval = 0

        # Start at the first frame
        self.current_texture = 0

        # Load textures for enemy
        self.door_animation_textures = []
        for i in range(19):
            texture = arcade.load_texture(resource_path("images/doors/level_0/door_%s.png" % i))
            self.door_animation_textures.append(texture)

        self.texture = self.door_animation_textures[0]

    def update(self):
        self.update_interval += 1
        if self.update_interval > 3:
            self.update_interval = 0
            self.cur_texture += 1
            if self.cur_texture > 18:
                self.remove_from_sprite_lists()
                return
            self.texture = self.door_animation_textures[self.cur_texture]
            self.center_y += 4  # How many pixels less every slide too keep it on top
