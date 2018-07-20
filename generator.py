import random, math

class Generator:

    def __init__(self, screen_size):
        self.pos_list = []
        self.size = 30
        self.screen_size = screen_size
        self.row_col = int(self.screen_size / self.size)

    def create(self, screen_size, shuffle, random_g=True):
        self.pos_list = []

        if not random_g:
            file = open('resources/maps/2.txt', 'r')
            level_map = file.readlines()
            file.close()
            for str_index in range(0, self.row_col):
                for col_index in range(0, self.row_col):
                    if level_map[str_index][col_index] == '1':
                        self.pos_list.append([col_index*self.size + shuffle, str_index*self.size + shuffle])
            print(level_map)
            return self.pos_list

        def gen_coords():
            coords = [0, 0]
            for index in [0, 1]:
                coords[index] = shuffle + self.size * random.randint(0, self.row_col - 1)
            return coords

        for i in range(0, random.randint(15, 20)):
            founded = False
            while not founded:
                coords = gen_coords()
                if coords not in self.pos_list:
                    self.pos_list.append(coords)
                    founded = True

        return self.pos_list

    def change_pos(self, c_x, c_y, shuffle):
        for pos in self.pos_list[::5]:
            correct = False
            while not correct:
                x = random.choice([-1, 0, 1])
                y = random.choice([-1, 0, 1])
                pos[0] += x*self.size
                pos[1] += y*self.size
                if math.floor((c_x - shuffle)/self.size) != (pos[0] - shuffle)/self.size and \
                                math.floor((c_y - shuffle)/self.size) != (pos[1] - shuffle)/self.size:
                    correct = True

