import random, math
import networkx as nx

class Generator:

    def __init__(self, screen_size):
        self.g = nx.Graph()
        self.pos_list = []
        self.cell_list = []
        self.size = 30
        self.screen_size = screen_size
        self.row_col = int(self.screen_size / self.size)
        self.level_map = None
        self.modify_level_map = []
        self.goals = None  # [[1, 0], [1, 0]]
        self.map_queue = None
        self.on_init()

    def on_init(self):
        file = open('config/map_queue.txt', 'r')
        self.map_queue = file.readline().split(',')
        file.close()

    def create(self, shuffle, random_g=True):

        self.pos_list = []
        self.cell_list = []
        for str_index in range(0, self.row_col):
            for col_index in range(0, self.row_col):
                self.cell_list.append((col_index * self.size + shuffle, str_index * self.size + shuffle))

        if not random_g:
            file = open('resources/maps/{0}.txt'.format(self.map_queue.pop(0)), 'r')
            self.level_map = file.readlines()
            file.close()

            for str_index in range(0, self.row_col):
                for col_index in range(0, self.row_col):
                    if self.level_map[str_index][col_index] == '1':
                        self.pos_list.append([col_index*self.size + shuffle, str_index*self.size + shuffle])
            self.create_graph()
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

    def create_graph(self):
        self.g = nx.Graph()
        self.modify_level_map = []

        for flags in self.level_map:
            self.modify_level_map += list(flags)[:-1]


        def add_free_cells(cell1, cell2, dis = 1, check=False):
            if check:
                if self.modify_level_map[cell1] + self.modify_level_map[cell2] == '00':
                    return True
                return False

            if self.modify_level_map[cell1] + self.modify_level_map[cell2] == '00':
                self.g.add_edge(cell1, cell2, distance=dis)

        dis = 1.01
        for index in range(0, self.row_col**2):

            if index % self.row_col == 0:  # первая колонка
                add_free_cells(index, index + 1)

            elif index % self.row_col == self.row_col-1:  # последняя колонка
                add_free_cells(index, index - 1)

            else:  # колонки между первой и последней
                add_free_cells(index, index + 1)
                add_free_cells(index, index - 1)


            if index in range(0, self.row_col ** 2 - self.row_col):  # все строки, кроме последней
                add_free_cells(index, index + self.row_col)

                if add_free_cells(index, index + self.row_col, dis, True):

                    if index % self.row_col != self.row_col - 1 and add_free_cells(index, index + 1, dis, True):
                        add_free_cells(index, index + self.row_col + 1, dis)
                    if index % self.row_col != 0 and add_free_cells(index, index - 1, dis, True):
                        add_free_cells(index, index + self.row_col - 1, dis)

        return self.g, self.cell_list






