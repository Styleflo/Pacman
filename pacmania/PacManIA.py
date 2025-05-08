import random


class PacManIA:
    def __init__(self, main_scene):
        self.main_scene = main_scene
        self.bool = False

    def get_ghosts(self):
        return self.main_scene.__ghosts

    def get_pacman(self):
        return self.main_scene.__pacman

    def get_seeds(self):
        return self.main_scene.get_seeds().get_seeds()

    def get_direction(self):
        self.print_seed()
        return ["up", "down", "left", "right"][random.randint(0, 3)]  # bah voilà

    def print_seed(self):
        if self.bool:
            return
        self.bool = True
        seed = self.get_seeds()
        for y in seed:
            for x in y:
                if x :
                    print("+", end="")
                else:
                    print("-", end="")
            print("")