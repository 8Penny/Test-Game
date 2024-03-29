import math
class Bullet:
    def __init__(self, curs_coords, player_coords, screen_size):
        self.radius = 4
        self.speed = 8
        self.x, self.y = curs_coords
        self.x2, self.y2 = player_coords
        self.bullet_vec = [self.x - self.x2, self.y - self.y2]
        vec_lenght = math.sqrt(self.bullet_vec[0]**2+self.bullet_vec[1]**2)
        self.bullet_vec[0] = (self.bullet_vec[0] / vec_lenght) * self.speed
        self.bullet_vec[1] = (self.bullet_vec[1] / vec_lenght) * self.speed
        self.screen_size = screen_size

        self.direction = 1 if self.x > self.x2 else -1

    def f(self, X):
        return int((self.y * self.x2 - self.y2 * self.x - (self.y - self.y2) * X)/(self.x2 - self.x))

    def new_position(self):
        '''self.x += 1 * self.direction
        self.y = self.f(self.x)'''
        self.x += int(self.bullet_vec[0])
        self.y += int(self.bullet_vec[1])
        #print(self.bullet_vec)
