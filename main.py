import arcade
from helpers import *


# Main sizes
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 770
SCREEN_TITLE = "PyShamus v0.1"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1
TILE_SCALING = 0.2

# Movement speed of player, in pixels per frame (3)
PLAYER_MOVEMENT_SPEED = 3

# Start player in coordinates (100/390)
PLAYER_INIT_X = 100
PLAYER_INIT_Y = 390

# Constants used to track if the player is facing left or right (index of texture pair array)
RIGHT_FACING = 0
LEFT_FACING = 1


class Enemy(arcade.Sprite):
    """Enemy sprite"""

    def __init__(self, enemy_type):
        super().__init__()

        self.scale = CHARACTER_SCALING
        self.cur_texture = 0
        self.update_interval = 0

        # Load textures for enemy
        self.enemy_textures = []
        for i in range(3):
            texture = arcade.load_texture(resource_path("images/enemy/%s_%s.png" % (enemy_type, i)))
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


class PlayerCharacter(arcade.Sprite):
    """Player sprite"""

    def __init__(self):
        super().__init__()

        self.scale = CHARACTER_SCALING
        self.cur_texture = 0

        self.character_face_direction = RIGHT_FACING

        # Load idle texture
        self.idle_texture = arcade.load_texture(resource_path("images/player/idle.png"))

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

        # Load textures for climbing up
        self.down_textures = []
        for i in range(3):
            texture = arcade.load_texture(resource_path("images/player/down_%s.png" % i))
            self.down_textures.append(texture)

        # Set the initial texture
        self.texture = self.idle_texture
        self.hit_box = self.texture.hit_box_points

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

        # Walking animation
        self.cur_texture += 1
        if self.cur_texture > 2:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture][
            self.character_face_direction
        ]


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):
        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.csscolor.BLACK)
        self.player_sprite = None
        self.enemy_sprite = None
        self.tile_map = None
        self.spawn_list = None
        self.scene = None
        self.score = 0
        self.level = 1
        self.room = "00"
        self.camera = None
        self.gui_camera = None
        self.physics_engine = None
        self.player_pos_x = PLAYER_INIT_X
        self.player_pos_y = PLAYER_INIT_Y
        self.player_direction = None
        self.last_direction = None

    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        # Setup the Cameras
        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)

        layer_options = {
            "Walls": {
                "use_spatial_hash": True,
            },
            "EnemySpawn": {
                "use_spatial_hash": True,
            },
        }

        self.tile_map = arcade.load_tilemap(resource_path("maps/room_"+self.room+".json"), TILE_SCALING, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        spawn_list = self.scene["EnemySpawn"]

        # Player init
        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = self.player_pos_x
        self.player_sprite.center_y = self.player_pos_y
        self.scene.add_sprite("Player", self.player_sprite)

        # Enemies init
        for i in range(0, 8):
            rand_index = random_enemy_index()
            self.enemy_sprite = Enemy("yel")
            self.enemy_sprite.center_x = spawn_list[rand_index].center_x
            self.enemy_sprite.center_y = spawn_list[rand_index].center_y
            self.scene.add_sprite("Enemies", self.enemy_sprite)

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite,
            walls=self.scene["Walls"]
        )

        # Workaround to not allow to stop our player when key is pressed and room is changed
        self.player_direction = self.last_direction

    def on_draw(self):
        """Render the screen."""

        arcade.start_render()
        self.camera.use()
        self.scene.draw()
        self.gui_camera.use()

        # Draw our score on the screen, scrolling it with the viewport
        score_text = f"Score: {self.score}"
        arcade.draw_text(
            score_text,
            10,
            10,
            arcade.csscolor.WHITE,
            18,
        )

        # Draw our room number on the screen
        room_text = f"Room: {self.room}"
        arcade.draw_text(
            room_text,
            10,
            35,
            arcade.csscolor.WHITE,
            18,
        )

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.UP:
            self.player_direction = "up"
            self.last_direction = "up"
        elif key == arcade.key.LEFT:
            self.player_direction = "left"
            self.last_direction = "left"
        elif key == arcade.key.RIGHT:
            self.player_direction = "right"
            self.last_direction = "right"
        elif key == arcade.key.DOWN:
            self.player_direction = "down"
            self.last_direction = "down"

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""

        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0
            self.player_direction = None
        elif key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
            self.player_direction = None

    def on_update(self, delta_time):
        """Movement and game logic"""

        # Move the player with the physics engine
        self.physics_engine.update()

        # Update player animations
        self.scene.update_animation(
            delta_time, ["Player"]
        )

        self.scene.update_animation(
            delta_time, ["Enemies"]
        )

        if self.player_direction == "up":
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif self.player_direction == "right":
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif self.player_direction == "left":
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif self.player_direction == "down":
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED

        hit_list = arcade.check_for_collision_with_list(
            sprite=self.player_sprite,
            sprite_list=self.scene["Exits"]
        )

        for hit in hit_list:
            # Переход в другую комнату
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

        for en in self.scene["Enemies"]:
            if en.center_y < self.player_sprite.center_y:
                en.center_y += 1
                if arcade.check_for_collision_with_list(sprite=en, sprite_list=self.scene["Walls"]) or \
                        arcade.check_for_collision_with_list(sprite=en, sprite_list=self.scene["Enemies"]):
                    en.center_y -= 1
            else:
                en.center_y -= 1
                if arcade.check_for_collision_with_list(sprite=en, sprite_list=self.scene["Walls"]) or \
                        arcade.check_for_collision_with_list(sprite=en, sprite_list=self.scene["Enemies"]):
                    en.center_y += 1

            if en.center_x < self.player_sprite.center_x:
                en.center_x += 1
                if arcade.check_for_collision_with_list(sprite=en, sprite_list=self.scene["Walls"]) or \
                        arcade.check_for_collision_with_list(sprite=en, sprite_list=self.scene["Enemies"]):
                    en.center_x -= 1
            else:
                en.center_x -= 1
                if arcade.check_for_collision_with_list(sprite=en, sprite_list=self.scene["Walls"]) or \
                        arcade.check_for_collision_with_list(sprite=en, sprite_list=self.scene["Enemies"]):
                    en.center_x += 1


def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
