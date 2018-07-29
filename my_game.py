import pygame
from player import Player
from coin import Coin
from aim import Aim
from bullet import Bullet
from pygame import gfxdraw
from generator import Generator
from enemy import Enemy
from check import *
from level_editor import LevelEditor


class App:
    def __init__(self):

        self.player = Player()  # игрок
        self.coin = Coin()  # монетка
        self.aim = Aim()  # прицел
        self.generator_obstacles = None  # генератор смертельных ячеек
        self.level_editor = None  # редактор уровня
        self.enemy = Enemy()  # враг

        self.win = None  # окно
        self._image_surf = None
        self.screen_size = 500  # размер экрана (квадратный)
        self.obst_size = None  # размер смертельной ячейки
        self.obst_list = []  # список координат смертельных ячеек
        self.free_rects = []  # координаты свободных клеток
        self.shuffle = None  # отступ по краям карты
        self.dot = None  # координаты точки прицела
        self.clock = pygame.time.Clock()
        self.time_counter = 0  # секундомер для смены смертельных ячеек
        self.myfont = None  # шрифт
        self.textsurface = None
        self.seconds_count = 0  # секундомер для сбора очков
        self.weapon = 1  # начальное оружие 1 - для сбора очков, -1 для стрельбы
        self.bullet_list = []  # списко пуль
        self.heart_image = None
        self.gameover_image = None
        self.congratulations_image = None
        self.win_image = None
        self.volume_images = None
        self.tips = ()  # список картинок подсказок
        self.tip_index = 0  # индекс текущей подсказки

        self._running = True   # флаг заппуска приложения
        self.intro = True  # сцена меню
        self.gameover = False  # сцена "конец игры"
        self.editor = False  # сцена редактора
        self.timer_On = False  # флаг для начала отсчета времени сбора
        self.random_generate = False  # рандомная генерация смертельных ячеек
        self.is_up_pressed = False  # флаг для плавной смены оружия
        self.stop_click = False  # запрет клика в меню
        self.islevel_complete = False
        self.iswin = False
        self.istips = False


    def on_init(self):

        pygame.init()
        pygame.font.init()
        pygame.display.set_caption('FireRun')  # заголовок окна
        pygame.mouse.set_cursor(*pygame.cursors.diamond)  # форма курсора
        pygame.mixer.music.load('resources/music/1.mp3')
        pygame.mixer.music.play(-1, 0.0)
        pygame.mixer.music.set_volume(0.1)

        self.generator_obstacles = Generator(self.screen_size)
        self.myfont = pygame.font.SysFont('Comic Sans MS', 30)
        self.obst_size = self.generator_obstacles.size
        self.shuffle = int((self.screen_size % self.obst_size) / 2)
        self.win = pygame.display.set_mode((self.screen_size, self.screen_size + 150))
        self.level_editor = LevelEditor(self.screen_size, self.shuffle, self.obst_size, self.win)
        self.heart_image = pygame.transform.smoothscale(pygame.image.load('resources/images/heart.png'), (40, 40))
        self.gameover_image = pygame.transform.smoothscale(pygame.image.load('resources/images/skull.png'), (250, 250))
        self.congratulations_image = pygame.transform.smoothscale(pygame.image.load('resources/images/award.png'), (250, 250))
        self.win_image = pygame.transform.smoothscale(pygame.image.load('resources/images/win.png'), (180, 250))
        tip1 = self.congratulations_image = pygame.transform.smoothscale(pygame.image.load('resources/images/tip1.png'),
                                                                         (500, 650))
        tip2 = self.congratulations_image = pygame.transform.smoothscale(pygame.image.load('resources/images/tip2.png'),
                                                                         (500, 650))
        vol_on = self.congratulations_image = pygame.transform.smoothscale(pygame.image.load('resources/images/volume.png'),
                                                                         (40, 40))
        vol_off = self.congratulations_image = pygame.transform.smoothscale(pygame.image.load('resources/images/no_volume.png'),
                                                                         (40, 40))
        self.tips = (tip1, tip2)
        self.volume_images = (vol_on, vol_off)

        #  предварительная генерация списка всех клеток
        for x in range(0, int(self.screen_size / self.obst_size)):
            for y in range(0, int(self.screen_size / self.obst_size)):
                self.free_rects.append([self.shuffle + self.obst_size * x, self.shuffle + self.obst_size * y])

        self._running = True
        return True

    def start(self, beginning=True):

        # невидимость курсора
        pygame.mouse.set_visible(0)
        # генерация списка смертельных клеток
        self.obst_list = self.generator_obstacles.create(self.shuffle, self.random_generate)
        # генерация графа пути для врага
        self.enemy.on_init(self.generator_obstacles.create_graph(), self.screen_size, self.shuffle, self.player.pos,
                           self.player.width, self.player.height, self.obst_list, self.obst_size)
        # генерация новой позиции монетки
        self.coin.new_pos(self.screen_size, self.shuffle, (self.player.x, self.player.y),
                          self.player.width, self.player.height, self.obst_list, self.obst_size)

        free_pos = False
        # генерация списка свободных клеток
        self.free_rects = [item for item in self.free_rects if item not in self.obst_list]
        # если игрок касается смертельных клеток
        while not free_pos:
            for rect in self.free_rects:
                self.player.x = rect[0]
                self.player.y = rect[1]
                if (not player_touch_obst(self.player.x, self.player.y, self.player.width, self.player.height,
                                         self.obst_list, self.obst_size,
                                         self.shuffle)) and self.player.x + self.player.width < self.screen_size - self.player.width - self.shuffle and self.player.y + self.player.height < self.screen_size - self.shuffle - self.player.height:
                    free_pos = True
                    break
        # определение клетки игрока к которой будет проложен путь врага
        self.player.first_cell = tuple(player_touch_obst(self.player.x, self.player.y, self.player.width, self.player.height,
                                  self.obst_list, self.obst_size,
                                  self.shuffle, True)[0])
        # генерация точки прицела
        self.aim.x, self.aim.y = (self.player.x + int(self.player.width / 2) + self.aim.radius,
                                  self.player.y + int(self.player.height / 2))
        self.dot = [self.aim.x, self.aim.y]  # обновление координат прицела
        # поиск пути врага до игрока
        self.enemy.find_way(self.player.first_cell, self.shuffle, self.obst_size)

        if not beginning:  # если уровень пройден, необходимое количество монет и убитых врагов увеличится на 2
            for val in self.generator_obstacles.goals:
                val[0] += 2
                val[1] = 0
        else:  # если игра началась заново, обновление жизней и цели
            self.player.lives = 3
            self.generator_obstacles.goals = [[1, 0], [1, 0]]

    def coin_check(self):

        #  если произошло касание
        if self.coin.alive and player_touch_circle(self.dot[0], self.dot[1], 1, 1,
                                                   self.coin.radius, self.coin.x, self.coin.y) and self.weapon == 1:
            if not self.timer_On:
                self.timer_On = True  # таймер включен
                self.seconds_count = pygame.time.get_ticks()
            if pygame.time.get_ticks() - self.seconds_count >= 1500:  # если время сбора монеты кончилось
                self.coin.alive = False  # удалить монету
                self.generator_obstacles.goals[0][1] += 1  # добавить очко
                self.coin.new_pos(self.screen_size, self.shuffle, (self.player.x, self.player.y), self.player.width,
                                  self.player.height, self.obst_list, self.obst_size)  # найти позицию новой монеты
        # обнулить таймер, если нет касания с монетой
        if self.timer_On and not player_touch_circle(self.dot[0], self.dot[1], 1, 1, self.coin.radius, self.coin.x,
                                                     self.coin.y):
            self.timer_On = False
            self.seconds_count = 0

    def shoot(self):

        if self.weapon == -1:  # если оружие - пистолет
            self.timer_On = False  # обнулить таймер
            if pygame.key.get_pressed()[pygame.K_UP] == 1:  # если нажата кнопка выстрела
                if self.seconds_count == 0:  # запуск таймера
                    self.seconds_count = pygame.time.get_ticks()
                else:
                    if pygame.time.get_ticks() - self.seconds_count >= 300:  # если необходимое время после выстрела прошло
                        # создание пули
                        self.bullet_list.append(Bullet((self.dot[0], self.dot[1]), (self.player.x+self.player.width/2,
                                                                 self.player.y+self.player.height/2), self.screen_size))
                        self.seconds_count = 0  # обнуление таймера

    def touching_obst(self):
        # обновление верхней левой клетки игрока
        self.player.first_cell = tuple(player_touch_obst(self.player.x, self.player.y, self.player.width, self.player.height,
                                                   self.obst_list, self.obst_size,
                                                   self.shuffle, True)[0])
        # проверка касания смертельных клеток
        if player_touch_obst(self.player.x, self.player.y, self.player.width, self.player.height,
                             self.obst_list, self.obst_size, self.shuffle):
            self.gameover = True  # закончить игру


    def bullets_update(self):

        if self.bullet_list != []:  # если пули существуют
            for bullet in self.bullet_list:
                bullet.new_position()  # обновление позиции
                #  если пуля попала во врага
                if bullet.x in range(self.enemy.x - self.enemy.radius,
                                     self.enemy.x + self.enemy.radius) and bullet.y in range(
                                self.enemy.y - self.enemy.radius, self.enemy.y + self.enemy.radius):
                    self.generator_obstacles.goals[1][1] += 1  # добавляеся очко
                    self.enemy.refresh(self.screen_size, self.shuffle, self.player.pos, self.player.width,
                                       self.player.height,
                                       self.obst_list, self.obst_size)  # появляется новый враг
                    while len(self.enemy.find_way(self.player.first_cell, self.shuffle, self.obst_size)) < 5:  # не ближе 5 клеток
                        self.enemy.refresh(self.screen_size, self.shuffle, self.player.pos, self.player.width,
                                           self.player.height,
                                           self.obst_list, self.obst_size)
                    self.bullet_list.remove(bullet)  # удаляется пуля

                if bullet.x not in range(0, self.screen_size) or bullet.y not in range(0, self.screen_size):
                    self.bullet_list.remove(bullet)  # если пуля выходит за пределы экрана

    def on_loop(self):

        #  проверка достижения цели
        if self.generator_obstacles.goals[0][0] <= self.generator_obstacles.goals[0][1] and \
                        self.generator_obstacles.goals[1][0] <= self.generator_obstacles.goals[1][1]:
            if len(self.generator_obstacles.map_queue) == 0:  # если уровни кончились
                self.iswin = True
            else:
                self.islevel_complete = True
        # если расстояние от врага до игрока больше 1
        if self.enemy.find_way(self.player.first_cell, self.shuffle, self.obst_size):
            self.enemy.update(self.generator_obstacles.cell_list)
        else:  # если нет - враг ударил игрока
            self.enemy.refresh(self.screen_size, self.shuffle, self.player.pos, self.player.width,
                               self.player.height,
                               self.obst_list, self.obst_size)  # новый враг
            while len(self.enemy.find_way(self.player.first_cell, self.shuffle, self.obst_size)) < 9:  # не ближе 9 клеток
                self.enemy.refresh(self.screen_size, self.shuffle, self.player.pos, self.player.width,
                                   self.player.height,
                                   self.obst_list, self.obst_size)
            self.player.lives -= 1  # -1 жизнь
        if self.player.lives == 0:
            self.gameover = True

        # если кнопка UP не нажата обнулить флаг
        if pygame.key.get_pressed()[pygame.K_DOWN] == 0 and self.is_up_pressed:
            self.is_up_pressed = False

        self.dot = [self.aim.x, self.aim.y]  # обновление координат прицела

        self.coin_check()  # проверка касания монеты
        self.shoot()  # проверка выстрела
        self.touching_obst()  # проверка касания со смертельным квадратом
        self.bullets_update()  # обновление положений пуль
        '''
        self.time_counter += self.clock.tick()
        if self.time_counter > 2000:
            self.generator_obstacles.change_pos(self.coin.x, self.coin.y, self.shuffle)
            self.time_counter = 0'''

    def help_render(self):

        for line in range(0, int(self.screen_size / self.obst_size)):
            pygame.draw.line(self.win, (255, 255, 255), (line * self.obst_size + self.shuffle, 0),
                             (line * self.obst_size + self.shuffle, self.screen_size))
        for line in range(0, int(self.screen_size / self.obst_size)):
            pygame.draw.line(self.win, (255, 255, 255), (0, line*self.obst_size+self.shuffle),
                             (self.screen_size, line*self.obst_size+self.shuffle))
        if not self.gameover and self.enemy.find_way(self.player.first_cell, self.shuffle, self.obst_size):
            for rect_index in self.enemy.find_way(self.player.first_cell, self.shuffle, self.obst_size):
                pygame.draw.rect(self.win, (200, 250, 205), (
                self.generator_obstacles.cell_list[rect_index][0], self.generator_obstacles.cell_list[rect_index][1],
                self.obst_size, self.obst_size))


    def help_over_render(self):

        touch_areas = player_touch_obst(self.player.x, self.player.y, self.player.width, self.player.height,
                                        self.obst_list, self.obst_size, self.shuffle, True)
        for area in touch_areas:
            pygame.draw.rect(self.win, (255, 200, 255), (area[0], area[1], self.obst_size, self.obst_size))

    def on_render(self):

        # цвет монеты ( при прикосновении, в спокойствии)
        coin_color = (255, 165, 0) if self.timer_On else (255, 215, 0)
        # заполнение экрана
        self.win.fill((205, 92, 92))
        # нижнее поле с информацией
        self.built_text("Goals:", (self.screen_size/9, self.screen_size + self.shuffle), 20)
        self.built_text("Coins: {0}/{1}".format(self.generator_obstacles.goals[0][1], self.generator_obstacles.goals[0][0]),
                        (self.screen_size / 9 + 3, self.screen_size + self.shuffle + 30), 20)
        self.built_text("Enemies: {0}/{1}".format(self.generator_obstacles.goals[1][1], self.generator_obstacles.goals[1][0]),
                        (self.screen_size / 7, self.screen_size + self.shuffle + 50), 20)
        # заполнение области поля
        pygame.draw.rect(self.win, (255, 240, 245), (self.shuffle, self.shuffle, self.screen_size-2*self.shuffle,
                                                     self.screen_size - 2 * self.shuffle))
        # жизни
        for live_count in range(0, self.player.lives):
            self.win.blit(self.heart_image, (self.screen_size - self.shuffle - 50*live_count - 40, self.screen_size, 40, 40))


        # отображение смертельных клеток
        for rect in self.obst_list:
            pygame.draw.rect(self.win, (255, 0, 0), (rect[0], rect[1], self.obst_size, self.obst_size))

        #self.help_render()
        # отображение монетки
        if self.coin.alive:
            pygame.gfxdraw.filled_circle(self.win, self.coin.x, self.coin.y, self.coin.radius, coin_color)
            pygame.gfxdraw.aacircle(self.win, self.coin.x, self.coin.y, self.coin.radius, coin_color)

        pygame.gfxdraw.filled_circle(self.win, self.enemy.x, self.enemy.y, self.enemy.radius, (0, 0, 0))
        # отображение игрока
        pygame.draw.rect(self.win, (0, 0, 0), (self.player.x, self.player.y, self.player.width, self.player.height))
        # отображение окружности прицела
        pygame.draw.circle(self.win, (255, 255, 255), (self.player.x + int(self.player.width/2),
                                                       self.player.y + int(self.player.height/2)), 50, 2)
        # отображение оружия
        pygame.draw.circle(self.win, (0, 0, 0), self.dot, 5, 0) if self.weapon == 1\
            else pygame.draw.circle(self.win, (128, 0, 0), self.dot, 5, 0)
        # отображение пуль
        if self.bullet_list != []:
            for bullet in self.bullet_list:
                pygame.draw.circle(self.win, (0, 0, 0), (bullet.x, bullet.y), bullet.radius)

        pygame.display.update()

    def text_objects(self, text, font, color):
        textSurface = font.render(text, True, color)
        return textSurface, textSurface.get_rect()

    def built_text(self, text, coords, size=30, color=(255, 255, 255)):
        self.myfont = pygame.font.SysFont('Comic Sans MS', size)
        self.textsurface, TextRect = self.text_objects(text, self.myfont, color)
        TextRect.center = coords
        self.win.blit(self.textsurface, TextRect)

    def intro_screen(self):

        self.win.fill((188, 143, 143))
        #  отображение кнопок
        pygame.draw.rect(self.win, (0, 255, 0),
                         (self.screen_size / 8, self.screen_size / 3, self.screen_size - self.screen_size * 2 / 8, 100))
        pygame.draw.rect(self.win, (250, 128, 114),
                     (self.screen_size / 8, self.screen_size * 2 / 3, self.screen_size - self.screen_size * 2 / 8, 100))
        pygame.draw.rect(self.win, (250, 128, 114),
                         (self.screen_size / 8, self.screen_size, self.screen_size - self.screen_size * 2 / 8,
                          100))
        pygame.draw.rect(self.win, (250, 128, 114), (self.screen_size - 50, 0, 50, 50))
        pygame.draw.rect(self.win, (250, 128, 114), (self.screen_size - 110, 0, 50, 50))

        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        #  ожидание момента, когда кнопка не будет нажата (необходимо для плавности в момент изменения сцен)
        if self.stop_click and pygame.mouse.get_pressed()[0] == 0:
            self.stop_click = False

        #  действия при нажатии одной из кнопок
        if not self.stop_click:
            if self.screen_size / 8 < mouse[0] < int(self.screen_size * 3 / 4) and \
                                            self.screen_size / 3 < mouse[1] < int(self.screen_size / 3) + 100:
                pygame.draw.rect(self.win, (152, 251, 152),
                                 (self.screen_size / 8, self.screen_size / 3, self.screen_size * 3 / 4, 100))
                if click[0] == 1:
                    self.intro = False
                    self.start()
                    pygame.mouse.set_visible(0)
            if self.screen_size / 8 < mouse[0] < int(self.screen_size * 3 / 4) and \
                                                    self.screen_size * 2 / 3 < mouse[1] < int(
                                        self.screen_size * 2 / 3) + 100:

                pygame.draw.rect(self.win, (255, 160, 122),
                                 (self.screen_size / 8, self.screen_size * 2 / 3,
                                  self.screen_size - self.screen_size * 2 / 8, 100))
                if click[0] == 1:
                    self._running = False
            if self.screen_size / 8 < mouse[0] < int(self.screen_size * 3 / 4) and \
                                    self.screen_size < mouse[1] < int(self.screen_size) + 100:
                pygame.draw.rect(self.win, (255, 160, 122),
                                 (self.screen_size / 8, self.screen_size,
                                  self.screen_size - self.screen_size * 2 / 8, 100))
                if click[0] == 1:
                    self.intro = False
                    self.editor = True
                    self.level_editor.quit = False
                    self.stop_click = True

            if self.screen_size - 50 < mouse[0] < self.screen_size and 0 < mouse[1] < 50:
                    pygame.draw.rect(self.win, (255, 160, 122), (self.screen_size - 50, 0, 50, 50))
                    if click[0] == 1:
                        self.intro = False
                        self.istips = True
                        self.stop_click = True

            if self.screen_size - 110 < mouse[0] < self.screen_size - 60 and 0 < mouse[1] < 50:
                    pygame.draw.rect(self.win, (255, 160, 122), (self.screen_size - 110, 0, 50, 50))
                    if click[0] == 1:
                        if pygame.mixer.music.get_volume() != 0.0:
                            pygame.mixer.music.set_volume(0.0)
                        else:
                            pygame.mixer.music.set_volume(0.1)
                        self.stop_click = True
        if pygame.mixer.music.get_volume() != 0.0:
            self.win.blit(self.volume_images[0], (self.screen_size - 105, 5))
        else:
            self.win.blit(self.volume_images[1], (self.screen_size - 105, 5))





        #  отображение текста
        self.built_text("MENU", ((self.screen_size / 2), (self.screen_size / 6)), 60)
        self.built_text("START", (self.screen_size / 2, self.screen_size / 3 + 47))
        self.built_text("QUIT", (self.screen_size / 2, self.screen_size * 2 / 3 + 47))
        self.built_text("EDITOR", (self.screen_size / 2, self.screen_size + 47))
        self.built_text("?", (self.screen_size - 25, 25))

        pygame.display.update()

    def gameover_screen(self):

        self.win.fill((188, 143, 143))
        self.win.blit(self.gameover_image, (self.screen_size/4, self.screen_size/4))
        self.built_text("GAME OVER", ((self.screen_size / 2), (self.screen_size / 3)), 60)
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        pygame.draw.rect(self.win, (0, 255, 0),
                         (self.screen_size / 8, self.screen_size * 4/5, self.screen_size - self.screen_size * 2/8, 60))
        if self.screen_size / 8 < mouse[0] < int(self.screen_size * 6/8) and \
                                        self.screen_size * 4/5 < mouse[1] < int((self.screen_size * 4/5) + 60):
            pygame.draw.rect(self.win, (152, 251, 152),
                             (self.screen_size / 8, self.screen_size * 4/5, self.screen_size - self.screen_size * 2/8, 60))
            if click[0] == 1:
                self.gameover = False
                self.generator_obstacles.on_init()
                self.start()
        self.built_text("START AGAIN", ((self.screen_size / 2), (self.screen_size * 17/20)), 40)
        pygame.display.update()

    def level_complete(self):

        self.win.fill((188, 143, 143))
        self.win.blit(self.congratulations_image, (self.screen_size / 4, self.screen_size / 4))
        self.built_text("CONGRATULATIONS!", ((self.screen_size / 2), (self.screen_size / 5)), 40)
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        pygame.draw.rect(self.win, (0, 255, 0),
                         (self.screen_size / 8, self.screen_size * 4 / 5, self.screen_size - self.screen_size * 2 / 8,
                          60))
        if self.screen_size / 8 < mouse[0] < int(self.screen_size * 6 / 8) and \
                                                self.screen_size * 4 / 5 < mouse[1] < int(
                            (self.screen_size * 4 / 5) + 60):
            pygame.draw.rect(self.win, (152, 251, 152),
                             (self.screen_size / 8, self.screen_size * 4 / 5,
                              self.screen_size - self.screen_size * 2 / 8, 60))
            if click[0] == 1:
                self.islevel_complete = False

                self.start(False)
        self.built_text("NEXT LEVEL", ((self.screen_size / 2), (self.screen_size * 17 / 20)), 40)
        pygame.display.update()

    def win_screen(self):
        self.win.fill((188, 143, 143))
        self.win.blit(self.win_image, (self.screen_size / 3, self.screen_size / 4))
        self.built_text("You win!", ((self.screen_size / 2), (self.screen_size / 5)), 40)
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        pygame.draw.rect(self.win, (0, 255, 0),
                         (self.screen_size / 8, self.screen_size * 4 / 5, self.screen_size - self.screen_size * 2 / 8,
                          60))
        if self.screen_size / 8 < mouse[0] < int(self.screen_size * 6 / 8) and \
                                                self.screen_size * 4 / 5 < mouse[1] < int(
                            (self.screen_size * 4 / 5) + 60):
            pygame.draw.rect(self.win, (152, 251, 152),
                             (self.screen_size / 8, self.screen_size * 4 / 5,
                              self.screen_size - self.screen_size * 2 / 8, 60))
            if click[0] == 1:
                self.iswin = False
                self.intro = True

        self.built_text("MENU", ((self.screen_size / 2), (self.screen_size * 17 / 20)), 40)
        pygame.display.update()

    def tips_screen(self):

        self.win.blit(self.tips[self.tip_index], (0, 0))
        if not pygame.mouse.get_pressed()[0] and self.stop_click:
            self.stop_click = False

        if self.screen_size - 50 < pygame.mouse.get_pos()[0] < self.screen_size and 0 < pygame.mouse.get_pos()[1] < 50:
            pygame.draw.rect(self.win, (255, 160, 122), (self.screen_size - 50, 0, 50, 50))
            if not self.stop_click and pygame.mouse.get_pressed()[0]:
                self.intro = True
                self.istips = False
                self.stop_click = True

        else:
            pygame.draw.rect(self.win, (250, 128, 114), (self.screen_size - 50, 0, 50, 50))
            if not self.stop_click and pygame.mouse.get_pressed()[0]:
                self.stop_click = True
                self.tip_index = 1 if self.tip_index == 0 else 0
        self.built_text("X", (self.screen_size - 25, 25))

        pygame.display.update()

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):

        if not self.on_init():
            self._running = False

        while self._running:

            pygame.time.delay(16)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button in (4, 5):
                        self.weapon *= -1

            if self.intro:
                pygame.mouse.set_visible(1)
                self.intro_screen()
            elif self.istips:
                self.tips_screen()
            elif self.editor:
                if self.level_editor.quit:
                    self.intro = True
                    self.editor = False
                    self.stop_click = True
                self.level_editor.update()
                self.level_editor.render()

            elif self.gameover:
                pygame.mouse.set_visible(1)
                self.gameover_screen()
            elif self.islevel_complete:
                pygame.mouse.set_visible(1)
                self.level_complete()
            elif self.iswin:
                pygame.mouse.set_visible(1)
                self.win_screen()

            else:

                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE] and not self.intro:
                    self.intro = True
                    self.generator_obstacles.on_init()

                if keys[pygame.K_a] and self.player.x > self.shuffle:
                    self.player.control(-1, 0)
                    self.aim.change_position(-1, 0)

                if keys[pygame.K_d] and self.player.x < self.screen_size - self.player.width - self.shuffle:
                    self.player.control(1, 0)
                    self.aim.change_position(1, 0)

                if keys[pygame.K_w] and self.player.y > self.shuffle:
                    self.player.control(0, -1)
                    self.aim.change_position(0, -1)

                if keys[pygame.K_s] and self.player.y < self.screen_size - self.player.height - self.shuffle:
                    self.player.control(0, 1)
                    self.aim.change_position(0, 1)

                if keys[pygame.K_LEFT]:
                    self.aim.x, self.aim.y = self.aim.find_position(-1, (self.player.x + int(self.player.width / 2),
                                                                         self.player.y + int(self.player.height / 2)),
                                                                    self.aim.radius)
                if keys[pygame.K_RIGHT]:
                    self.aim.x, self.aim.y = self.aim.find_position(1, (self.player.x + int(self.player.width / 2),
                                                                        self.player.y + int(self.player.height / 2)),
                                                                    self.aim.radius)
                if keys[pygame.K_DOWN]:
                    if not self.is_up_pressed:
                        self.is_up_pressed = True
                        self.weapon *= -1

                self.on_loop()
                self.on_render()

        self.on_cleanup()


if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()
