from pyshamus.constants import *
from pyshamus.helpers import *
import random
import math


class PlayerExplosion(arcade.Sprite):
    def __init__(self):
        super().__init__()

        self.scale = CHARACTER_SCALING
        self.cur_texture = 0
        self.update_interval = 0

        # Start at the first frame
        self.current_texture = 0

        # Load textures for enemy
        self.player_animation_textures = []
        for i in range(3):
            texture = arcade.load_texture(resource_path("images/player/die_%s.png" % i))
            self.player_animation_textures.append(texture)

        self.texture = self.player_animation_textures[0]

    def update(self):
        self.update_interval += 1
        if self.update_interval > 3:
            self.update_interval = 0
            self.cur_texture += 1
            if self.cur_texture > 2:
                self.remove_from_sprite_lists()
                return
            self.texture = self.player_animation_textures[self.cur_texture]


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
    def __init__(self, level):
        super().__init__()

        self.scale = 1
        self.cur_texture = 0
        self.update_interval = 0

        # Start at the first frame
        self.current_texture = 0

        # Load textures for enemy
        self.door_animation_textures = []
        for i in range(37):
            texture = arcade.load_texture(resource_path("images/doors/level_%s/door_%s.png" % (level, i)))
            self.door_animation_textures.append(texture)

        self.texture = self.door_animation_textures[0]

    def update(self):
        self.update_interval += 1
        if self.update_interval > 1:
            self.update_interval = 0
            self.cur_texture += 1
            if self.cur_texture > 36:
                self.remove_from_sprite_lists()
                return
            self.texture = self.door_animation_textures[self.cur_texture]
            self.center_y += 2  # How many pixels less every slide too keep it on top


class Particle(arcade.SpriteCircle):
    def __init__(self, my_list):
        # Choose a random color
        color = random.choice(PARTICLE_COLORS)

        # Make the particle
        super().__init__(PARTICLE_RADIUS, color)

        # Track normal particle texture, so we can 'flip' when we sparkle.
        self.normal_texture = self.texture

        # Keep track of the list we are in, so we can add a smoke trail
        self.my_list = my_list

        # Set direction/speed
        speed = random.random() * PARTICLE_SPEED_RANGE + PARTICLE_MIN_SPEED
        direction = random.randrange(360)
        self.change_x = math.sin(math.radians(direction)) * speed
        self.change_y = math.cos(math.radians(direction)) * speed

        # Track original alpha. Used as part of 'sparkle' where we temp set the
        # alpha back to 255
        self.my_alpha = 255

        # What list do we add smoke particles to?
        self.my_list = my_list

    def update(self):
        if self.my_alpha <= PARTICLE_FADE_RATE:
            # Faded out, remove
            self.remove_from_sprite_lists()
        else:
            # Update
            self.my_alpha -= PARTICLE_FADE_RATE
            self.alpha = self.my_alpha
            self.center_x += self.change_x
            self.center_y += self.change_y
            self.change_y -= PARTICLE_GRAVITY

            # Should we sparkle this?
            if random.random() <= PARTICLE_SPARKLE_CHANCE:
                self.alpha = 255
                self.texture = arcade.make_circle_texture(int(self.width),
                                                          arcade.color.WHITE)
            else:
                self.texture = self.normal_texture
