import random
from check import *

class Coin:
    def __init__(self):
        self.alive = True
        self.x = None
        self.y = None
        self.radius = 15
        self.shuffle = 5


    def update(self):
        pass

    def new_pos(self, screen_size, shuffle, player_pos, player_w, player_h, obst_list, obst_size):

        correct = False
        while not correct:
            for index in [0, 1]:
                self.x = shuffle + obst_size * random.randint(0, int(screen_size / obst_size) - 1)
                self.y = shuffle + obst_size * random.randint(0, int(screen_size / obst_size) - 1)


            check = player_touch_circle(player_pos[0], player_pos[1], player_w, player_h, self.radius, self.x, self.y)
            if [self.x, self.y] not in obst_list and not check:
                    self.x += self.radius
                    self.y += self.radius
                    correct = True

        self.alive = True


