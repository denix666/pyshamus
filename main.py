from game import *


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "PyShamus v0.2")
    menu_view = IntroView()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()
