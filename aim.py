import math
from player import Player
class Aim:
    def __init__(self):
        self.radius = 50
        self.x = 0
        self.y = 0
        self.degree = 0
        self.speed = 4
        self.player_speed = Player().speed

    def change_position(self, x_mult, y_mult):
        self.x += x_mult * self.player_speed
        self.y += y_mult * self.player_speed

    def find_position(self, direction, player_coords, radius):
        if self.degree == 360:
            self.degree = 0
        self.degree += direction*self.speed
        x_pos = round(player_coords[0]+radius*math.cos(self.degree*math.pi/180))
        y_pos = round(player_coords[1]+radius*math.sin(self.degree*math.pi/180))
        return (x_pos, y_pos)
