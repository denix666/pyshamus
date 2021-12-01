import random
import time
import arcade.color
import pygame
from game_player import *
from key import *
from enemy import Enemy
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
        arcade.draw_text("Hit 'space' to start new game", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 250,
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
        self.enemy_destroyed = arcade.load_sound(resource_path("sounds/enemy_destroyed.wav"))

        self.player_list = None
        self.player_sprite = None
        self.player_direction = None
        self.last_player_direction = None
        self.enemy_sprite = None
        self.bullet_list = None
        self.key_list = None
        self.key_sprite = None
        self.room = "00"
        self.score = 0
        self.lives = 5
        self.level = 1
        self.tile_map = None
        self.scene = None
        self.physics_engine = None
        self.player_pos_x = PLAYER_INIT_X
        self.player_pos_y = PLAYER_INIT_Y
        self.bullet_direction = None
        self.enemy_explosion_list = None
        self.enemy_explosion_sprite = None

        # Keys info
        # 0 - Don't have a key
        # 1 - Have a key
        # 2 - A key was already used
        self.keys = array([["blue", "0"],
                           ['orange', "0"],
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

        # Init bullets list
        self.bullet_list = arcade.SpriteList()

        # Init key list
        self.key_list = arcade.SpriteList()

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite,
            walls=self.scene["Walls"]
        )

        # Add key in random place of the map only if it wasn't used or taken already
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

    def on_draw(self):
        arcade.start_render()

        # Отрисовка персонажей и комнат
        self.player_list.draw()
        self.scene.draw()
        self.bullet_list.draw()
        self.enemy_explosion_list.draw()

        # Отображение надписей статуса игры
        arcade.draw_text(f"Score: {self.score}", 10, 10, arcade.color.WHITE, 15)
        arcade.draw_text(f"Room: {self.room}", 10, 35, arcade.color.YELLOW, 15)
        arcade.draw_text(f"Level: {self.level}", 10, 65, arcade.color.RED_DEVIL, 15)

        # Отображение собранных ключей
        have_number_of_keys = 0
        for i in range(0, 7):
            if self.keys[i][1] == "1":
                have_number_of_keys += 1
                key_texture = arcade.load_texture(resource_path("images/keys/%s.png" % self.keys[i][0]))
                key_texture_x = KEY_TEXTURE_X + 40 * have_number_of_keys
                key_texture.draw_scaled(key_texture_x, KEY_TEXTURE_Y, KEY_SCALING)

        # Отображение кол-ва жизней
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

    def on_update(self, delta_time):
        self.physics_engine.update()

        self.bullet_list.update()

        self.enemy_explosion_list.update()

        self.scene.update_animation(
            delta_time, ["Player"]
        )

        self.scene.update_animation(
            delta_time, ["Enemies"]
        )

        # TODO Проигрывание звука шагов при передвижении (improve sound effect)
        if self.player_sprite.change_y or self.player_sprite.change_x:
            pygame.mixer.Sound.play(self.walk_sound, 0, 1)

        # Передвижение игрока
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

        # Вычисление стрельбы "наискосок"
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

        # Переход в другую комнату
        hit_list = arcade.check_for_collision_with_list(
            sprite=self.player_sprite,
            sprite_list=self.scene["Exits"]
        )
        for hit in hit_list:
            self.room = hit.properties["to_room"]

            # Соблюдение позиции при переходе между комнатами
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
                game_view = GameOverView()
                self.window.show_view(game_view)
            self.setup()

        # Проверка подобрал ли игрок ключ
        for key_hit in self.key_list:
            if arcade.check_for_collision_with_list(self.player_sprite, self.key_list):
                key_hit.remove_from_sprite_lists()
                arcade.play_sound(self.key_sound)
                for i in range(0, 7):
                    if self.keys[i][0] == self.scene["Properties"][1].properties["key"]:
                        self.keys[i][1] = "1"
                        return

        # Проверка попала ли пуля куда-нибудь
        for bullet in self.bullet_list:
            hit_list = arcade.check_for_collision_with_list(bullet, sprite_list=self.scene["Enemies"])

            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()

            # Если попали в противника - удалить противника, удалить пулю, начислить очки
            for enemy in hit_list:
                enemy.remove_from_sprite_lists()
                self.score += 5
                arcade.sound.play_sound(self.enemy_destroyed)

                explosion = EnemyExplosion()
                explosion.center_y = hit_list[0].center_y
                explosion.center_x = hit_list[0].center_x
                explosion.update()
                self.enemy_explosion_list.append(explosion)

            # Удалить выстрелы попавшие в стены
            hit_list = arcade.check_for_collision_with_list(bullet, sprite_list=self.scene["Walls"])
            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()

            # Удалить все выстрелы вылетевшие за пределы игрового поля
            if bullet.center_x < 0 or bullet.center_x > SCREEN_WIDTH or \
                    bullet.center_y < 0 or bullet.center_y > SCREEN_HEIGHT:
                bullet.remove_from_sprite_lists()
