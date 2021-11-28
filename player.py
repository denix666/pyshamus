import time

import arcade
from helpers import *
from constants import *

# Constants used to track if the player is facing left or right (index of texture pair array)
RIGHT_FACING = 0
LEFT_FACING = 1


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__()

        self.scale = CHARACTER_SCALING
        self.cur_texture = 0
        self.character_face_direction = RIGHT_FACING

        # Load textures for walk left right
        self.walk_textures = []
        for i in range(3):
            texture = load_texture_pair(resource_path("images/player/walk_%s.png" % i))
            self.walk_textures.append(texture)

        # Load textures for climbing up
        self.up_textures = []
        for i in range(3):
            texture = arcade.load_texture(resource_path("images/player/up_%s.png" % i))
            self.up_textures.append(texture)

        # Load textures for climbing down
        self.down_textures = []
        for i in range(3):
            texture = arcade.load_texture(resource_path("images/player/down_%s.png" % i))
            self.down_textures.append(texture)

        self.idle_texture = arcade.load_texture(resource_path("images/player/idle.png"))
        self.hit_box = self.idle_texture.hit_box_points

    def update_animation(self, delta_time):
        if self.change_y < 0:
            self.cur_texture += 1
            if self.cur_texture > 2:
                self.cur_texture = 0
            self.texture = self.down_textures[self.cur_texture]
            return
        elif self.change_y > 0:
            self.cur_texture += 1
            if self.cur_texture > 2:
                self.cur_texture = 0
            self.texture = self.up_textures[self.cur_texture]
            return

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Idle animation
        if self.change_x == 0:
            self.texture = self.idle_texture
            return

        # Walking animation left/right
        self.cur_texture += 1
        if self.cur_texture > 2:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture][
            self.character_face_direction
        ]

    def update(self):
        # Check for out-of-bounds
        if self.left < 0:
            self.left = 0
        elif self.right > SCREEN_WIDTH - 1:
            self.right = SCREEN_WIDTH - 1

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > SCREEN_HEIGHT - 1:
            self.top = SCREEN_HEIGHT - 1


class DieAnimation(arcade.Sprite):
    def __init__(self):
        super().__init__()

        self.scale = CHARACTER_SCALING

        # Load textures of die
        self.die_textures = []
        for i in range(3):
            texture = arcade.load_texture(resource_path("images/player/die_%s.png" % i))
            self.die_textures.append(texture)

        # Start at the first frame
        self.cur_texture = 0
        self.textures = self.die_textures

    def update(self):
        # Update to the next frame of the animation. If we are at the end
        # of our frames, then delete this sprite.
        #self.current_texture += 1
        #time.sleep(1)
        #if self.current_texture < len(self.textures):
        #    self.set_texture(self.current_texture)
        #    print(self.current_texture)
        #else:
            #self.remove_from_sprite_lists()

        self.cur_texture += 1
        if self.cur_texture > 2:
            self.cur_texture = 0
        self.texture = self.die_textures[self.cur_texture]
