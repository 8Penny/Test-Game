
class Player:
    def __init__(self):
        self.x = 50
        self.y = 50
        self.speed = 2

        self.width = 40
        self.height = 40

    def control(self, x, y):
        self.x += x * self.speed
        self.y += y * self.speed
        pass

    def update(self):
        pass
