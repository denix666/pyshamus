from pyshamus.helpers import *
from pyshamus.constants import *


class Question(arcade.Sprite):
    def __init__(self):
        super().__init__()

        self.scale = QUESTION_SCALING
        self.cur_texture = 0
        self.update_interval = 0

        # Load textures for enemy
        self.question_textures = []
        for i in range(8):
            texture = arcade.load_texture(resource_path("images/question/question_%s.png" % i))
            self.question_textures.append(texture)

        self.texture = self.question_textures[0]
        self.hit_box = self.texture.hit_box_points

    def update_animation(self, delta_time):
        # Question animation
        self.update_interval += 1
        if self.update_interval > QUESTION_ANIMATION_SPEED:
            self.update_interval = 0
            self.cur_texture += 1
            if self.cur_texture > 2:
                self.cur_texture = 0
            self.texture = self.question_textures[self.cur_texture]
