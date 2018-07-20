import pygame, math, textwrap
from os import listdir
from os.path import isfile, join


class LevelEditor:

    def __init__(self,  screen_size, shuffle, obst_size, win):
        self.quit = False
        self.win = win
        self.screen_size = screen_size
        self.mouse_click = False
        self.shuffle = shuffle
        self.obst_size = obst_size
        self.level_map = []
        self.pos_list = []
        self.past_pos = None
        self.save_render_on = False
        self.rows_columns_count = int(self.screen_size / self.obst_size)

        for str_index in range(0, self.rows_columns_count):
            for col_index in range(0, self.rows_columns_count):
                self.pos_list.append((col_index * self.obst_size + shuffle, str_index * self.obst_size + shuffle))
                self.level_map.append('0')

    def update(self):
        if self.save_render_on and 1 in pygame.mouse.get_pressed():
            self.save_render_on = False
        mouse_x, mouse_y = pygame.mouse.get_pos()
        int_rect_x = math.floor((mouse_x - self.shuffle) / self.obst_size) * self.obst_size + self.shuffle
        int_rect_y = math.floor((mouse_y - self.shuffle) / self.obst_size) * self.obst_size + self.shuffle

        if mouse_x < self.screen_size - self.shuffle and mouse_x > self.shuffle and mouse_y < self.screen_size - self.shuffle and mouse_y > self.shuffle:

            index_pos = self.pos_list.index((int_rect_x, int_rect_y))

            if not self.mouse_click and pygame.mouse.get_pressed()[0] == 1 or \
                                    self.mouse_click and pygame.mouse.get_pressed()[0] == 1 and self.past_pos != index_pos:
                self.past_pos = index_pos
                self.mouse_click = True
                self.level_map[index_pos] = '1' if self.level_map[index_pos] == '0' else '0'


        if mouse_x > self.shuffle and mouse_y > self.screen_size + self.shuffle and mouse_x < self.shuffle + 150 and mouse_y < self.screen_size + self.shuffle + 60:
            if pygame.mouse.get_pressed()[0] == 1 and not self.mouse_click:
                self.mouse_click = True
                self.quit = True


        if mouse_x > self.screen_size - self.shuffle - 150 and mouse_y > self.screen_size + self.shuffle and mouse_x < self.screen_size - self.shuffle and mouse_y < self.screen_size + self.shuffle + 60:
            if pygame.mouse.get_pressed()[0] == 1 and not self.mouse_click:
                self.mouse_click = True
                self.save()
                self.erise()
                self.save_render_on = True


        if pygame.mouse.get_pressed()[0] == 0 and self.mouse_click:
            self.mouse_click = False

    def erise(self):
        self.level_map = [0] * self.rows_columns_count**2

    def save(self):

        maps_path = 'resources/maps/'
        onlyfiles = [f for f in listdir(maps_path) if isfile(join(maps_path, f))]
        map_name = str(int(sorted(onlyfiles)[-1].split('.')[0]) + 1)
        map_to_write = textwrap.wrap(''.join(self.level_map), self.rows_columns_count)
        file = open('resources/maps/{0}.txt'.format(map_name), 'w')
        file.writelines("%s\n" % line for line in map_to_write)
        file.close()

    def text_maker(self, text, coords, size=30, color=(0, 0, 0)):

        def text_objects(text, font, color):
            textSurface = font.render(text, True, color)
            return textSurface, textSurface.get_rect()

        myfont = pygame.font.SysFont('Comic Sans MS', size)
        textsurface, TextRect = text_objects(text, myfont, color)
        TextRect.center = coords
        self.win.blit(textsurface, TextRect)



    def render(self):

        # заполнение экрана
        self.win.fill((205, 92, 92))

        # заполнение области поля
        if self.save_render_on:
            self.text_maker('COMPLETELY SAVED', (int(self.screen_size / 2), int(self.screen_size / 2)))
        else:
            pygame.draw.rect(self.win, (255, 240, 245),
                             (self.shuffle, self.shuffle, self.screen_size - 2 * self.shuffle,
                              self.screen_size - 2 * self.shuffle))
            for line in range(0, int(self.screen_size / self.obst_size)):
                pygame.draw.line(self.win, (255, 255, 255), (line * self.obst_size + self.shuffle, self.shuffle),
                                 (line * self.obst_size + self.shuffle, self.screen_size - self.shuffle))
            for line in range(0, int(self.screen_size / self.obst_size)):
                pygame.draw.line(self.win, (255, 255, 255), (self.shuffle, line * self.obst_size + self.shuffle),
                                 (self.screen_size - self.shuffle, line * self.obst_size + self.shuffle))
            for rect in [self.pos_list[num] for num, i in enumerate(self.level_map) if i == '1']:
                pygame.draw.rect(self.win, (205, 92, 92), (rect[0], rect[1], self.obst_size, self.obst_size))

            pygame.draw.rect(self.win, (255, 240, 245), (self.shuffle, self.screen_size + self.shuffle, 150, 60))
            pygame.draw.rect(self.win, (255, 240, 245),
                             (self.screen_size - self.shuffle - 150, self.screen_size + self.shuffle, 150, 60))
            self.text_maker('MENU', ((self.shuffle + 150) / 2, self.screen_size + self.shuffle + (60) / 2))
            self.text_maker('SAVE',
                            (self.screen_size - (self.shuffle + 150) / 2, self.screen_size + self.shuffle + (60) / 2))

        pygame.display.update()

