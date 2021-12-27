import arcade.color
"""
Global game constants
"""

# Main sizes
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 720
SCREEN_TITLE = "PyShamus v0.5 beta"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1
TILE_SCALING = 1

# Start player in coordinates (100/390)
PLAYER_INIT_X = 100
PLAYER_INIT_Y = 390

# Movement speed of player, in pixels per frame (3)
PLAYER_MOVEMENT_SPEED = 3

# Enemy
ENEMY_ANIMATION_SPEED = 4

# Lives coordinates
LIVE_TEXTURE_X = 1081
LIVE_TEXTURE_Y = 690

# Keys coordinates
KEY_TEXTURE_X = 1065
KEY_TEXTURE_Y = 22
KEY_SCALING = 0.3

KEYHOLE_SCALING = 1.2

# Live water
WATER_SCALING = 0.2
WATER_ANIMATION_SPEED = 8

# Bullet speed and shoots
BULLET_SPEED = 5
BULLET_SCALING = 0.5
ONE_TIME_MAX_BULLETS = 2
ENEMY_BULLET_SCALING = 0.5
ENEMY_BULLET_SPEED = 2

# Question
QUESTION_SCALING = 1.4
QUESTION_ANIMATION_SPEED = 9

# How match time player can be in the room before the shadow get in
MAX_TIME_IN_THE_ROOM = 12
SHADOW_ANIMATION_SPEED = 5
SHADOW_SCALING = 2

# --- Explosion Particles Related

# How fast the particle will accelerate down. Make 0 if not desired
PARTICLE_GRAVITY = 0.05

# How fast to fade the particle
PARTICLE_FADE_RATE = 8

# How fast the particle moves. Range is from 2.5 <--> 5 with 2.5 and 2.5 set.
PARTICLE_MIN_SPEED = 2.5
PARTICLE_SPEED_RANGE = 2.5

# How many particles per explosion
PARTICLE_COUNT = 20

# How big the particle
PARTICLE_RADIUS = 3

# Possible particle colors
PARTICLE_COLORS = [arcade.color.ALIZARIN_CRIMSON,
                   arcade.color.COQUELICOT,
                   arcade.color.LAVA,
                   arcade.color.KU_CRIMSON,
                   arcade.color.DARK_TANGERINE]

# Chance we'll flip the texture to white and make it 'sparkle'
PARTICLE_SPARKLE_CHANCE = 0.02
