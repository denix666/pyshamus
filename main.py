import arcade
from helpers import *


# Main sizes
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 770
SCREEN_TITLE = "PyShamus v0.1"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1
TILE_SCALING = 0.2

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 4

# Start player in coordinates 100/390
PLAYER_INIT_X = 100
PLAYER_INIT_Y = 390


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):
        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.csscolor.BLACK)
        self.player = None
        self.tile_map = None
        self.scene = None
        self.score = 0
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
        }
        self.tile_map = arcade.load_tilemap(resource_path("maps/room_"+self.room+".json"), TILE_SCALING, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Player init
        self.player = arcade.Sprite(resource_path("images/player.png"), CHARACTER_SCALING)
        self.player.center_x = self.player_pos_x
        self.player.center_y = self.player_pos_y
        self.scene.add_sprite("Player", self.player)

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, walls=self.scene["Walls"]
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

        # TODO remove
        #print(self.player.center_x)
        #print(self.player.center_y)

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
            self.player.change_x = 0
            self.player_direction = None
        elif key == arcade.key.UP or key == arcade.key.DOWN:
            self.player.change_y = 0
            self.player_direction = None

    def on_update(self, delta_time):
        """Movement and game logic"""

        # Move the player with the physics engine
        self.physics_engine.update()

        if self.player_direction == "up":
            self.player.change_y = PLAYER_MOVEMENT_SPEED
        elif self.player_direction == "right":
            self.player.change_x = PLAYER_MOVEMENT_SPEED
        elif self.player_direction == "left":
            self.player.change_x = -PLAYER_MOVEMENT_SPEED
        elif self.player_direction == "down":
            self.player.change_y = -PLAYER_MOVEMENT_SPEED

        hit_list = arcade.check_for_collision_with_list(
            sprite=self.player,
            sprite_list=self.scene["Exits"]
        )

        for hit in hit_list:
            # Переход в другую комнату
            self.room = hit.properties["to_room"]

            # Соблюдение позиции при переходе между комнатами
            if hit.properties["x"] == 9999:
                self.player_pos_x = self.player.center_x
            else:
                self.player_pos_x = hit.properties["x"]

            if hit.properties["y"] == 9999:
                self.player_pos_y = self.player.center_y
            else:
                self.player_pos_y = hit.properties["y"]

            self.setup()


def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
