#!/usr/bin/python

# -*- coding: utf-8 -*-

import random
import time
import arcade.color
import pygame
from game_player import *
from key_and_holes import *
from enemy import Enemy
from water import Water
from question import Question
from animations import *
from numpy import array


class IntroView(arcade.View):
    def __init__(self):
        super().__init__()
        pygame.mixer.init()
        self.intro_music = pygame.mixer.Sound(resource_path("sounds/intro.mp3"))
        self.intro_music.set_volume(0.6)

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)
        pygame.mixer.Sound.play(self.intro_music, -1)

    def on_draw(self):
        arcade.start_render()
        intro_texture = arcade.load_texture(resource_path("images/intro.png"))
        arcade.draw_texture_rectangle(intro_texture.width // 2,
                                      intro_texture.height // 2, SCREEN_WIDTH, SCREEN_HEIGHT, intro_texture)

        # Show intro and instructions for game
        arcade.draw_text("SPACE - Shoot", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 150,
                         arcade.color.YELLOW, font_size=30, anchor_x="center")
        arcade.draw_text("Up, Down, Left, Right - walk", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 210,
                         arcade.color.YELLOW, font_size=30, anchor_x="center")
        arcade.draw_text("Hit SPACE to start game", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 300,
                         arcade.color.YELLOW, font_size=30, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE or key == arcade.key.ESCAPE:
            pygame.mixer.Sound.stop(self.intro_music)
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)


class GameOverView(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        arcade.start_render()
        intro_texture = arcade.load_texture(resource_path("images/intro.png"))
        arcade.draw_texture_rectangle(intro_texture.width // 2,
                                      intro_texture.height // 2, SCREEN_WIDTH, SCREEN_HEIGHT, intro_texture)
        arcade.draw_text("Game over!", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 150,
                         arcade.color.YELLOW, font_size=30, anchor_x="center")
        arcade.draw_text("Hit SPACE to start new game", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 250,
                         arcade.color.YELLOW, font_size=30, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE or key == arcade.key.ESCAPE:
            game_view = GameView()
            GameView().room = "00"
            GameView().score = 0
            GameView().lives = 5
            GameView().level = 1
            game_view.setup()
            self.window.show_view(game_view)

###########################################################################
# Game code ###############################################################
###########################################################################


class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        # Set sounds and colors
        arcade.set_background_color(arcade.csscolor.BLACK)
        self.die_sound = arcade.load_sound(resource_path("sounds/die.wav"))
        self.walk_sound = pygame.mixer.Sound(resource_path("sounds/walk.wav"))
        self.key_sound = arcade.load_sound(resource_path("sounds/key.wav"))
        self.life_sound = arcade.load_sound(resource_path("sounds/life.wav"))
        self.game_over_sound = arcade.load_sound(resource_path("sounds/game_over.wav"))
        self.opening_door_sound = arcade.load_sound(resource_path("sounds/opening_door.wav"))
        self.question_sound = arcade.load_sound(resource_path("sounds/question.wav"))
        self.enemy_destroyed = arcade.load_sound(resource_path("sounds/enemy_destroyed.wav"))

        self.player_list = None
        self.player_sprite = None
        self.player_direction = None
        self.last_player_direction = None
        self.enemy_sprite = None
        self.bullet_list = None
        self.key_list = None
        self.key_sprite = None
        self.door_list = None
        self.door_sprite = None
        self.keyhole_list = None
        self.keyhole_sprite = None
        self.room = "00"
        self.score = 0
        self.lives = 3
        self.level = 1
        self.tile_map = None
        self.scene = None
        self.physics_engine = None
        self.player_pos_x = PLAYER_INIT_X
        self.player_pos_y = PLAYER_INIT_Y
        self.bullet_direction = None
        self.enemy_explosion_list = None
        self.enemy_explosion_sprite = None
        self.water_sprite = None
        self.water_list = None
        self.question_sprite = None
        self.question_list = None

        self.water_used_in_rooms = []
        self.question_used_in_rooms = []
        self.keyholes_used_in_rooms = []
        self.rooms_with_open_door = []

        self.opening_door_list = None
        self.opening_door_sprite = None

        # Keys info array
        # 0 - Don't have a key
        # 1 - Have a key
        # 2 - A key was already used
        self.keys = array([["blue", "0"],
                           ['gold', "0"],
                           ['red', "0"],
                           ['purple', "0"],
                           ['green', "0"],
                           ['cyan', "0"],
                           ['brown', "0"]
                           ])

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.fire_pressed = False

    # noinspection PyBroadException
    def setup(self):
        # Load tile map
        layer_options = {
            "Walls": {
                "use_spatial_hash": True,
            },
            "Properties": {
                "use_spatial_hash": True,
            },
        }
        self.tile_map = arcade.load_tilemap(resource_path("maps/room_" + self.room + ".json"), TILE_SCALING,
                                            layer_options)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Add player
        self.player_list = arcade.SpriteList()
        self.player_sprite = GamePlayer()
        self.player_sprite.center_x = self.player_pos_x
        self.player_sprite.center_y = self.player_pos_y
        self.scene.add_sprite("Player", self.player_sprite)

        # Enemy explosion animation
        self.enemy_explosion_list = arcade.SpriteList()
        self.enemy_explosion_sprite = EnemyExplosion()

        # Opening door animation
        self.opening_door_list = arcade.SpriteList()
        self.opening_door_sprite = DoorOpenAnimation()

        # Init bullets list
        self.bullet_list = arcade.SpriteList()

        # Init key list
        self.key_list = arcade.SpriteList()

        # Init keyhole list
        self.keyhole_list = arcade.SpriteList()

        # Init door list
        self.door_list = arcade.SpriteList()

        # Init water list
        self.water_list = arcade.SpriteList()

        # Init question list
        self.question_list = arcade.SpriteList()

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite,
            walls=self.scene["Walls"]
        )

        # Set level
        try:
            self.level = self.scene["Properties"][1].properties["level"]
        except:
            pass

        # Add doors to rooms
        if self.room not in self.rooms_with_open_door:
            try:
                if self.scene["Properties"][1].properties["keyhole"]:
                    self.door_sprite = Door()
                    self.door_sprite.center_x = self.scene["Properties"][1].properties["door_x"]
                    self.door_sprite.center_y = self.scene["Properties"][1].properties["door_y"]
                    self.scene.add_sprite("Doors", self.door_sprite)
                    self.door_list.append(self.door_sprite)
            except:
                pass

        # Add water with life in random place of the room if it defined in that room
        try:
            if self.scene["Properties"][1].properties["water"]:
                if self.room not in self.water_used_in_rooms:
                    item_placed_successfully = False
                    self.water_sprite = Water()
                    while not item_placed_successfully:
                        self.water_sprite.center_x = random.randrange(180, SCREEN_WIDTH - 200)
                        self.water_sprite.center_y = random.randrange(180, SCREEN_HEIGHT - 200)

                        wall_hit_list = arcade.check_for_collision_with_list(self.water_sprite,
                                                                             sprite_list=self.scene["Walls"])
                        if len(wall_hit_list) == 0:
                            item_placed_successfully = True
                    self.scene.add_sprite("Waters", self.water_sprite)
                    self.water_list.append(self.water_sprite)
        except:
            pass

        # Add keyholes to the rooms
        try:
            if self.scene["Properties"][1].properties["keyhole"]:
                if self.room not in self.keyholes_used_in_rooms:
                    keyhole_type = self.scene["Properties"][1].properties["keyhole"]
                    item_placed_successfully = False
                    self.keyhole_sprite = KeyHole(keyhole_type)
                    while not item_placed_successfully:
                        self.keyhole_sprite.center_x = random.randrange(180, SCREEN_WIDTH - 200)
                        self.keyhole_sprite.center_y = random.randrange(180, SCREEN_HEIGHT - 200)

                        wall_hit_list = arcade.check_for_collision_with_list(self.keyhole_sprite,
                                                                             sprite_list=self.scene["Walls"])
                        if len(wall_hit_list) == 0:
                            item_placed_successfully = True
                    self.scene.add_sprite("KeyHoles", self.keyhole_sprite)
                    self.keyhole_list.append(self.keyhole_sprite)
        except:
            pass

        # Add question in random place of the room if it defined in that room
        try:
            if self.scene["Properties"][1].properties["question"]:
                if self.room not in self.question_used_in_rooms:
                    item_placed_successfully = False
                    self.question_sprite = Question()
                    while not item_placed_successfully:
                        self.question_sprite.center_x = random.randrange(180, SCREEN_WIDTH - 200)
                        self.question_sprite.center_y = random.randrange(180, SCREEN_HEIGHT - 200)

                        wall_hit_list = arcade.check_for_collision_with_list(self.question_sprite,
                                                                             sprite_list=self.scene["Walls"])
                        if len(wall_hit_list) == 0:
                            item_placed_successfully = True
                    self.scene.add_sprite("Questions", self.question_sprite)
                    self.question_list.append(self.question_sprite)
        except:
            pass

        # Add key in random place of the room only if it wasn't used or taken already
        try:
            for i in range(0, 7):
                if self.keys[i][0] == self.scene["Properties"][1].properties["key"]:
                    if self.keys[i][1] == "0":
                        key_type = self.scene["Properties"][1].properties["key"]
                        item_placed_successfully = False
                        self.key_sprite = Key(key_type)
                        while not item_placed_successfully:
                            self.key_sprite.center_x = random.randrange(180, SCREEN_WIDTH - 200)
                            self.key_sprite.center_y = random.randrange(180, SCREEN_HEIGHT - 200)

                            wall_hit_list = arcade.check_for_collision_with_list(self.key_sprite,
                                                                                 sprite_list=self.scene["Walls"])
                            if len(wall_hit_list) == 0:
                                item_placed_successfully = True
                        self.scene.add_sprite("Keys", self.key_sprite)
                        self.key_list.append(self.key_sprite)
        except:
            pass

        # Add random enemies
        try:
            amount_of_enemy = self.scene["Properties"][1].properties["amount_of_enemy"] * self.level
        except:
            amount_of_enemy = 3 * self.level

        for i in range(amount_of_enemy):
            enemy_placed_successfully = False

            # Random type of enemy from the list set in the map property
            enemy_type = random.choice((self.scene["Properties"][0].properties["enemy_types"]))
            self.enemy_sprite = Enemy(enemy_type)

            # Place and make sure that they are inside the walls and not collide with themselves
            while not enemy_placed_successfully:
                self.enemy_sprite.center_x = random.randrange(180, SCREEN_WIDTH - 180)
                self.enemy_sprite.center_y = random.randrange(180, SCREEN_HEIGHT - 180)

                wall_hit_list = arcade.check_for_collision_with_list(self.enemy_sprite,
                                                                     sprite_list=self.scene["Walls"])
                try:
                    enemy_hit_list = arcade.check_for_collision_with_list(self.enemy_sprite,
                                                                          sprite_list=self.scene["Enemies"])
                except:
                    enemy_hit_list = []

                if len(wall_hit_list) == 0 and len(enemy_hit_list) == 0:
                    enemy_placed_successfully = True

            self.scene.add_sprite("Enemies", self.enemy_sprite)

    # noinspection PyBroadException
    def on_draw(self):
        arcade.start_render()

        # Draw rooms and units
        self.player_list.draw()
        self.scene.draw()
        self.bullet_list.draw()
        self.enemy_explosion_list.draw()
        self.opening_door_list.draw()

        # Draw game statuses (room, level, score)
        arcade.draw_text(f"Score: {self.score}", 10, 10, arcade.color.WHITE, 15)
        arcade.draw_text(f"Room: {self.room}", 10, 35, arcade.color.YELLOW, 15)
        arcade.draw_text(f"Level: {self.level}", 10, 65, arcade.color.RED_DEVIL, 15)

        # Show keys
        have_number_of_keys = 0
        for i in range(0, 7):
            if self.keys[i][1] == "1":
                have_number_of_keys += 1
                key_texture = arcade.load_texture(resource_path("images/keys/%s.png" % self.keys[i][0]))
                key_texture_x = KEY_TEXTURE_X + 40 * have_number_of_keys
                key_texture.draw_scaled(key_texture_x, KEY_TEXTURE_Y, KEY_SCALING)

        # Show lives
        live_texture = arcade.load_texture(resource_path("images/player/idle.png"))
        if self.lives >= 13:
            lives_to_draw = 12
        else:
            lives_to_draw = self.lives - 1

        for i in range(0, lives_to_draw):
            x = LIVE_TEXTURE_X + 30 * i
            if 3 < i < 8:
                y = LIVE_TEXTURE_Y - 30
                x = LIVE_TEXTURE_X + 30 * (i - 4)
            elif i > 7:
                y = LIVE_TEXTURE_Y - 60
                x = LIVE_TEXTURE_X + 30 * (i - 8)
            else:
                y = LIVE_TEXTURE_Y
            arcade.draw_texture_rectangle(live_texture.width // 2 + x,
                                          live_texture.height // 2 + y,
                                          live_texture.width,
                                          live_texture.height,
                                          live_texture, 0)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True

        if key == arcade.key.SPACE:
            self.fire_pressed = True

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False

    # noinspection PyBroadException
    def on_update(self, delta_time):
        self.physics_engine.update()

        self.bullet_list.update()

        try:
            self.scene.update_animation(
                delta_time, ["Waters"]
            )
        except:
            pass

        try:
            self.scene.update_animation(
                delta_time, ["Questions"]
            )
        except:
            pass

        self.enemy_explosion_list.update()

        self.opening_door_list.update()

        self.scene.update_animation(
            delta_time, ["Player"]
        )

        self.scene.update_animation(
            delta_time, ["Enemies"]
        )

        # TODO Проигрывание звука шагов при передвижении (improve sound effect)
        if self.player_sprite.change_y or self.player_sprite.change_x:
            pygame.mixer.Sound.play(self.walk_sound, 0, 1)

        # Moving player
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0
        if self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            self.bullet_direction = "up"
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
            self.bullet_direction = "down"
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
            self.bullet_direction = "left"
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
            self.bullet_direction = "right"

        # Shooting
        if self.player_sprite.change_x > 0 and self.player_sprite.change_y > 0:
            self.bullet_direction = "up_right"

        if self.player_sprite.change_x < 0 and self.player_sprite.change_y > 0:
            self.bullet_direction = "up_left"

        if self.player_sprite.change_x > 0 and self.player_sprite.change_y < 0:
            self.bullet_direction = "down_right"

        if self.player_sprite.change_x < 0 and self.player_sprite.change_y < 0:
            self.bullet_direction = "down_left"

        if self.fire_pressed:
            bullet = arcade.Sprite(resource_path("images/bullet.png"), BULLET_SCALING)

            if self.bullet_direction == "up_right":
                bullet.angle = 45
                bullet.center_x = self.player_sprite.center_x + 10
                bullet.center_y = self.player_sprite.center_y + 10
                bullet.change_x = BULLET_SPEED
                bullet.change_y = BULLET_SPEED

            if self.bullet_direction == "up_left":
                bullet.angle = 135
                bullet.center_x = self.player_sprite.center_x - 10
                bullet.center_y = self.player_sprite.center_y + 10
                bullet.change_x = -BULLET_SPEED
                bullet.change_y = BULLET_SPEED

            if self.bullet_direction == "down_right":
                bullet.angle = 315
                bullet.center_x = self.player_sprite.center_x + 10
                bullet.center_y = self.player_sprite.center_y - 10
                bullet.change_x = BULLET_SPEED
                bullet.change_y = -BULLET_SPEED

            if self.bullet_direction == "down_left":
                bullet.angle = 225
                bullet.center_x = self.player_sprite.center_x - 10
                bullet.center_y = self.player_sprite.center_y - 10
                bullet.change_x = -BULLET_SPEED
                bullet.change_y = -BULLET_SPEED

            if self.bullet_direction == "down":
                bullet.angle = 270
                bullet.change_y = -BULLET_SPEED
                bullet.center_x = self.player_sprite.center_x
                bullet.top = self.player_sprite.bottom

            if self.bullet_direction == "up":
                bullet.angle = 90
                bullet.change_y = BULLET_SPEED
                bullet.center_x = self.player_sprite.center_x
                bullet.bottom = self.player_sprite.top

            if self.bullet_direction == "left":
                bullet.angle = 180
                bullet.change_x = -BULLET_SPEED
                bullet.center_y = self.player_sprite.center_y
                bullet.right = self.player_sprite.left

            if self.bullet_direction == "right":
                bullet.angle = 0
                bullet.change_x = BULLET_SPEED
                bullet.center_y = self.player_sprite.center_y
                bullet.left = self.player_sprite.right

            if len(self.bullet_list) < ONE_TIME_MAX_BULLETS:
                self.bullet_list.append(bullet)
            self.fire_pressed = False

        # Moving from room to room
        hit_list = arcade.check_for_collision_with_list(
            sprite=self.player_sprite,
            sprite_list=self.scene["Exits"]
        )
        for hit in hit_list:
            self.room = hit.properties["to_room"]

            # Save player position while moving from room to room
            if hit.properties["x"] == 9999:
                self.player_pos_x = self.player_sprite.center_x
            else:
                self.player_pos_x = hit.properties["x"]

            if hit.properties["y"] == 9999:
                self.player_pos_y = self.player_sprite.center_y
            else:
                self.player_pos_y = hit.properties["y"]

            self.setup()

        # Manage enemies objects - do not allow get out of the walls and follow the player
        for en in self.scene["Enemies"]:
            if en.center_y < self.player_sprite.center_y:
                en.center_y += 1
                if arcade.check_for_collision_with_list(en, sprite_list=self.scene["Walls"]) or \
                        arcade.check_for_collision_with_list(en, sprite_list=self.scene["Enemies"]):
                    en.center_y -= 1
            else:
                en.center_y -= 1
                if arcade.check_for_collision_with_list(en, sprite_list=self.scene["Walls"]) or \
                        arcade.check_for_collision_with_list(en, sprite_list=self.scene["Enemies"]):
                    en.center_y += 1

            if en.center_x < self.player_sprite.center_x:
                en.center_x += 1
                if arcade.check_for_collision_with_list(en, sprite_list=self.scene["Walls"]) or \
                        arcade.check_for_collision_with_list(en, sprite_list=self.scene["Enemies"]):
                    en.center_x -= 1
            else:
                en.center_x -= 1
                if arcade.check_for_collision_with_list(en, sprite_list=self.scene["Walls"]) or \
                        arcade.check_for_collision_with_list(en, sprite_list=self.scene["Enemies"]):
                    en.center_x += 1

        # Check if player collided with enemy
        if arcade.check_for_collision_with_list(self.player_sprite, sprite_list=self.scene["Enemies"]):
            self.lives -= 1
            arcade.play_sound(self.die_sound)
            time.sleep(1)
            if self.lives < 1:
                arcade.play_sound(self.game_over_sound)
                game_view = GameOverView()
                self.window.show_view(game_view)
            self.setup()

        # Check if we have water
        for water_hit in self.water_list:
            if arcade.check_for_collision_with_list(self.player_sprite, self.water_list):
                self.lives += 1
                arcade.play_sound(self.life_sound)
                water_hit.remove_from_sprite_lists()
                # Store if this water already used
                self.water_used_in_rooms.append(self.room)

        # Do not allow player to enter into the closed door
        if arcade.check_for_collision_with_list(self.player_sprite, self.door_list):
            if self.player_sprite.center_x < 200:
                self.player_sprite.center_x += PLAYER_MOVEMENT_SPEED
            else:
                self.player_sprite.center_x -= PLAYER_MOVEMENT_SPEED

        # Check if we have question
        for question_hit in self.question_list:
            if arcade.check_for_collision_with_list(self.player_sprite, self.question_list):
                # Set random item life/score
                if random.choice([True, False]):
                    self.score += 100
                    arcade.play_sound(self.question_sound)
                else:
                    self.lives += 1
                    arcade.play_sound(self.life_sound)
                question_hit.remove_from_sprite_lists()
                # Store if this question already used
                self.question_used_in_rooms.append(self.room)

        # Check if we have key
        for key_hit in self.key_list:
            if arcade.check_for_collision_with_list(self.player_sprite, self.key_list):
                key_hit.remove_from_sprite_lists()
                arcade.play_sound(self.key_sound)
                for i in range(0, 7):
                    if self.keys[i][0] == self.scene["Properties"][1].properties["key"]:
                        self.keys[i][1] = "1"
                        return

        # Check if we got to the keyhole
        for keyhole_hit in self.keyhole_list:
            if arcade.check_for_collision_with_list(self.player_sprite, self.keyhole_list):
                # Check if we have the right key
                for i in range(0, 7):
                    if self.keys[i][0] == self.scene["Properties"][1].properties["keyhole"]:
                        if self.keys[i][1] == "1":
                            # Open door animation, sound and removing unneeded sprites
                            keyhole_hit.remove_from_sprite_lists()
                            self.keys[i][1] = "2"
                            self.keyholes_used_in_rooms.append(self.room)
                            arcade.play_sound(self.opening_door_sound)
                            self.door_list[0].remove_from_sprite_lists()
                            self.rooms_with_open_door.append(self.room)
                            opening_door = DoorOpenAnimation()
                            opening_door.center_y = self.scene["Properties"][1].properties["door_y"]
                            opening_door.center_x = self.scene["Properties"][1].properties["door_x"]
                            opening_door.update()
                            self.opening_door_list.append(opening_door)

        # Check if bullet destroyed something
        for bullet in self.bullet_list:
            hit_list = arcade.check_for_collision_with_list(bullet, sprite_list=self.scene["Enemies"])

            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()

            # If we destroyed the enemy - remove the bullet, remove destroyed enemy, add score
            for enemy in hit_list:
                enemy.remove_from_sprite_lists()
                self.score += 5
                arcade.sound.play_sound(self.enemy_destroyed)

                explosion = EnemyExplosion()
                explosion.center_y = hit_list[0].center_y
                explosion.center_x = hit_list[0].center_x
                explosion.update()
                self.enemy_explosion_list.append(explosion)

            # Remove shoots into wall
            hit_list = arcade.check_for_collision_with_list(bullet, sprite_list=self.scene["Walls"])
            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()

            # Remove shoots that get out of the game field
            if bullet.center_x < 0 or bullet.center_x > SCREEN_WIDTH or \
                    bullet.center_y < 0 or bullet.center_y > SCREEN_HEIGHT:
                bullet.remove_from_sprite_lists()
