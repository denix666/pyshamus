import os
import arcade


def resource_path(relative_path):
    """
    Calculates base path of resources.
    """
    base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True),
    ]
