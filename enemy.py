import networkx as nx
from check import *


class Enemy:
    def __init__(self):
        self.x = None
        self.y = None
        self.radius = 15
        self.cell_list = None
        self.alive = None
        self.g = None
        self.path_list = None
        self.speed = 1

    def on_init(self, data, screen_size, shuffle, player_pos, player_w, player_h, obst_list, obst_size):
        self.g = data[0]
        self.cell_list = data[1]
        self.refresh(screen_size, shuffle, player_pos, player_w, player_h, obst_list, obst_size)

    def refresh(self, screen_size, shuffle, player_pos, player_w, player_h, obst_list, obst_size):
        self.x, self.y = new_pos(screen_size, shuffle, player_pos, player_w, player_h, obst_list, obst_size, self.radius)

    def find_way(self, player_pos, shuffle, obst_size):

        player_index = self.cell_list.index(player_pos)
        enemy_index = self.cell_list.index(first_rect(self.x, self.y, shuffle, obst_size))
        self.path_list = nx.dijkstra_path(self.g, enemy_index, player_index, 'distance')
        if len(self.path_list) == 1:
            return False
        return self.path_list

    def update(self, cell_list):

        next_rect = cell_list[self.path_list[1]]
        if self.x - self.radius < next_rect[0]:
            self.x += self.speed
        if self.x - self.radius > next_rect[0]:
            self.x -= self.speed
        if self.y - self.radius < next_rect[1]:
            self.y += self.speed
        if self.y - self.radius > next_rect[1]:
            self.y -= self.speed











