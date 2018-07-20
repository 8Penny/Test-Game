import pygame
from player import Player
from coin import Coin
from aim import Aim
from bullet import Bullet
from pygame import gfxdraw
from generator import Generator
from check import *
from level_editor import LevelEditor


class App:
    def __init__(self):

        self.player = Player()  # игрок
        self.coin = Coin()  # монетка
        self.aim = Aim()  # прицел
        self.generator_obstacles = None  # генератор смертельных ячеек
        self.level_editor = None  # редактор уровня

        self.win = None  # окно
        self._image_surf = None
        self.screen_size = 500  # размер экрана (квадратный)
        self.obst_size = None  # размер смертельной ячейки
        self.obst_list = []  # список координат смертельных ячеек
        self.points = None  # количество очков
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

        self._running = True   # флаг заппуска приложения
        self.intro = True  # сцена меню
        self.gameover = False  # сцена "конец игры"
        self.editor = False  # сцена редактора
        self.timer_On = False  # флаг для начала отсчета времени сбора
        self.random_generate = False # рандомная генерация смертельных ячеек
        self.is_up_pressed = False  # флаг для плавной смены оружия
        self.stop_click = False  # запрет клика в меню



    def on_init(self):

        pygame.init()
        pygame.display.set_caption('FireRun')  # заголовок окна
        pygame.font.init()
        pygame.mouse.set_cursor(*pygame.cursors.diamond)

        self.generator_obstacles = Generator(self.screen_size)
        self.myfont = pygame.font.SysFont('Comic Sans MS', 30)
        self.obst_size = self.generator_obstacles.size
        self.shuffle = int((self.screen_size % self.obst_size) / 2)
        self.win = pygame.display.set_mode((self.screen_size, self.screen_size + 150))
        self.level_editor = LevelEditor(self.screen_size, self.shuffle, self.obst_size, self.win)


        for x in range(0, int(self.screen_size / self.obst_size)):
            for y in range(0, int(self.screen_size / self.obst_size)):
                self.free_rects.append([self.shuffle + self.obst_size * x, self.shuffle + self.obst_size * y])

        self._running = True
        self.start()
        return True

    def start(self):

        self.points = 0  # обнуление очков
        if not self.intro and not self.editor:  # невидимость курсора, если не сцена
            pygame.mouse.set_visible(0)

        # генерация списка смертельных клеток
        self.obst_list = self.generator_obstacles.create(self.screen_size, self.shuffle, self.random_generate)
        # генерация новой позиции монетки
        self.coin.new_pos(self.screen_size, self.shuffle, (self.player.x, self.player.y),
                          self.player.width, self.player.height, self.obst_list, self.obst_size)
        free_pos = False
        self.free_rects = [item for item in self.free_rects if item not in self.obst_list]
        # если игрок касается смертельных клеток
        while not free_pos:
            for rect in self.free_rects:
                self.player.x = rect[0]
                self.player.y = rect[1]
                if not player_touch_obst(self.player.x, self.player.y, self.player.width, self.player.height,
                                         self.obst_list, self.obst_size,
                                         self.shuffle) and self.player.x < self.screen_size - self.player.width - self.shuffle and self.player.y < self.screen_size - self.shuffle - self.player.height:
                    free_pos = True


        # генерация точки прицела
        self.aim.x, self.aim.y = (self.player.x + int(self.player.width / 2) + self.aim.radius,
                                  self.player.y + int(self.player.height / 2))

    def on_event(self, event):
        pass

    def coin_check(self):

        if self.coin.alive and player_touch_circle(self.dot[0], self.dot[1], 1, 1,
                                                   self.coin.radius, self.coin.x, self.coin.y) and self.weapon == 1:
            if not self.timer_On:
                self.timer_On = True
                self.seconds_count = pygame.time.get_ticks()
            if pygame.time.get_ticks() - self.seconds_count >= 1500:
                self.coin.alive = False
                self.points += 1
                self.coin.new_pos(self.screen_size, self.shuffle, (self.player.x, self.player.y), self.player.width,
                                  self.player.height, self.obst_list, self.obst_size)

        if self.timer_On and not player_touch_circle(self.dot[0], self.dot[1], 1, 1, self.coin.radius, self.coin.x,
                                                     self.coin.y):
            self.timer_On = False
            self.seconds_count = 0

    def shoot(self):

        if self.weapon == -1:
            self.timer_On = False
            if (pygame.key.get_pressed()[pygame.K_UP] != 0):
                if self.seconds_count == 0:
                    self.seconds_count = pygame.time.get_ticks()
                else:
                    if pygame.time.get_ticks() - self.seconds_count >= 300:
                        self.bullet_list.append(
                            Bullet((self.dot[0], self.dot[1]), (self.player.x+self.player.width/2, self.player.y+self.player.height/2), self.screen_size))
                        self.seconds_count = 0

    def touching_obst(self):
        if player_touch_obst(self.player.x, self.player.y, self.player.width, self.player.height,
                             self.obst_list, self.obst_size, self.shuffle):
            self.gameover = True
            pygame.mouse.set_visible(1)

    def bullets_update(self):

        if self.bullet_list != []:
            for bullet in self.bullet_list:
                bullet.new_position()
                if bullet.x not in range(0, self.screen_size) or bullet.y not in range(0, self.screen_size):
                    self.bullet_list.remove(bullet)

    def on_loop(self):

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

    def help_over_render(self):

        touch_areas = player_touch_obst(self.player.x, self.player.y, self.player.width, self.player.height,
                                        self.obst_list, self.obst_size, self.shuffle, True)
        for area in touch_areas:
            pygame.draw.rect(self.win, (255, 200, 255), (area[0], area[1], self.obst_size, self.obst_size))


    def on_render(self):

        # цвет монеты ( при прикосновении, в спокойствии)
        coin_color = (100, 100, 100) if self.timer_On else (145, 66, 98)
        # заполнение экрана
        self.win.fill((205, 92, 92))
        # заполнение области поля
        pygame.draw.rect(self.win, (255, 240, 245), (self.shuffle, self.shuffle, self.screen_size-2*self.shuffle,
                                                     self.screen_size - 2 * self.shuffle))
        # отображение смертельных клеток
        for rect in self.obst_list:
            pygame.draw.rect(self.win, (255, 0, 0), (rect[0], rect[1], self.obst_size, self.obst_size))
        # отображение монетки
        if self.coin.alive:
            pygame.gfxdraw.filled_circle(self.win, self.coin.x, self.coin.y, self.coin.radius, coin_color)
            pygame.gfxdraw.aacircle(self.win, self.coin.x, self.coin.y, self.coin.radius, coin_color)
        # отображение игрока
        pygame.draw.rect(self.win, (0, 0, 0), (self.player.x, self.player.y, self.player.width, self.player.height))
        # отображение квадрата заднего плана для очков
        pygame.draw.rect(self.win, (205, 92, 92), (0, 0, 40, 40))
        # отображение оружия
        pygame.draw.circle(self.win, (0, 0, 0), self.dot, 5, 0) if self.weapon == 1\
            else pygame.draw.circle(self.win, (255, 0, 255), self.dot, 5, 0)
        # отображение окружности прицела
        pygame.draw.circle(self.win, (255, 255, 255), (self.player.x + int(self.player.width/2),
                                                       self.player.y + int(self.player.height/2)), 50, 2)
        # отображение пуль
        if self.bullet_list != []:
            for bullet in self.bullet_list:
                pygame.draw.circle(self.win, (0, 0, 0), (bullet.x, bullet.y), bullet.radius)
        # отображение собранных монет
        self.built_text(str(self.points), (20, 20), 30)
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
        pygame.draw.rect(self.win, (0, 255, 0),
                         (self.screen_size / 8, self.screen_size / 3, self.screen_size - self.screen_size * 2 / 8, 100))
        pygame.draw.rect(self.win, (250, 128, 114),
            (self.screen_size / 8, self.screen_size * 2 / 3, self.screen_size - self.screen_size * 2 / 8, 100))
        pygame.draw.rect(self.win, (250, 128, 114),
                         (self.screen_size / 8, self.screen_size, self.screen_size - self.screen_size * 2 / 8,
                          100))

        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if self.stop_click and pygame.mouse.get_pressed()[0] == 0:
            self.stop_click = False
        if not self.stop_click:
            if self.screen_size / 8 < mouse[0] < int(self.screen_size * 3 / 4) and \
                                            self.screen_size / 3 < mouse[1] < int(self.screen_size / 3) + 100:
                pygame.draw.rect(self.win, (152, 251, 152),
                                 (self.screen_size / 8, self.screen_size / 3, self.screen_size * 3 / 4, 100))
                if click[0] == 1:
                    self.intro = False
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

        self.built_text("MENU", ((self.screen_size / 2), (self.screen_size / 6)), 60)
        self.built_text("START", (self.screen_size / 2, self.screen_size / 3 + 47))
        self.built_text("QUIT", (self.screen_size / 2, self.screen_size * 2 / 3 + 47))
        self.built_text("EDITOR", (self.screen_size / 2, self.screen_size + 47))

        pygame.display.update()

    def gameover_screen(self):

        self.win.fill((188, 143, 143))
        image = pygame.transform.smoothscale(pygame.image.load('resources/images/skull.png'), (250, 250))
        self.win.blit(image, (self.screen_size/4, self.screen_size/4))
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
                self.start()
        self.built_text("START AGAIN", ((self.screen_size / 2), (self.screen_size * 17/20)), 40)
        pygame.display.update()

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):

        if not self.on_init():
            self._running = False

        while self._running:

            pygame.time.delay(13)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button in (4, 5):
                        self.weapon *= -1

            if self.intro:
                self.intro_screen()
            elif self.editor:
                if self.level_editor.quit:
                    self.intro = True
                    self.editor = False
                    self.stop_click = True
                self.level_editor.update()
                self.level_editor.render()

            elif self.gameover:
                self.gameover_screen()
            else:

                keys = pygame.key.get_pressed()
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
