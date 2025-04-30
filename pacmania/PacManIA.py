import random


class PacManIA:
    def __init__(self, main_scene):
        self.main_scene = main_scene

    def get_ghosts(self):
        return self.main_scene.__ghosts

    def get_pacman(self):
        return self.main_scene.__pacman

    def get_seeds(self):
        return self.main_scene.__seeds.__seeds

    def get_direction(self):
        return ["up", "down", "left", "right"][random.randint(0, 3)]  # bah voilà
