
class Player:
    def __init__(self):
        self.x = 50
        self.y = 50
        self.pos = (self.x, self.y)
        self.speed = 3

        self.width = 40
        self.height = 40

        self.first_cell = None

        self.lives = None

    def control(self, x, y):
        self.x += x * self.speed
        self.y += y * self.speed
        pass

    def update(self):
        pass
