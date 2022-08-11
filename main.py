# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


import pyxel
import time
import enum
import random
import collections


# smer
class Direction(enum.Enum):
    RIGHT = 0
    LEFT = 1
    UP = 2
    DOWN = 4


# rizeni hry
class GameControl(enum.Enum):
    PLAY = 0
    STOP = 1


class Level:
    def __init__(self):
        self.tile_map = 0
        self.a = 0
        self.b = 0
        self.w = 32
        self.h = 24

    def draw(self):
        pyxel.bltm(0, 0, self.tile_map, self.a, self.b, self.w, self.h)


# Trida vajicko - vykreslovani, pohyb, kontrola snezeni
class Egg:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 8
        self.h = 8

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 16, 0, self.w, self.h)

    def collision(self, a, b, w, h):
        is_colliding = False
        if (
                a + w > self.x
                and self.x + self.w > a
                and b + h > self.y
                and self.y + self.h > b
        ):
            is_colliding = True
        return is_colliding

    def move(self, moved_x, moved_y):
        self.x = moved_x
        self.y = moved_y


# telo hada, vykresluje telo a orientuje hlavu, kontroluje kolize
class SnakePart:
    def __init__(self, x, y, is_head=False):
        self.x = x
        self.y = y
        self.w = 8
        self.h = 8
        self.is_head = is_head

    def draw(self, direction):
        width = self.w
        height = self.h
        texture_x = 0
        texture_y = 0
        # orientace hlavy
        if self.is_head:
            if direction == Direction.RIGHT:
                texture_x = 8
                texture_y = 0
            if direction == Direction.LEFT:
                texture_x = 8
                texture_y = 0
                width = width * -1
            if direction == Direction.UP:
                texture_x = 0
                texture_y = 8
                height = height * -1
            if direction == Direction.DOWN:
                texture_x = 0
                texture_y = 8

        pyxel.blt(self.x, self.y, 0, texture_x, texture_y, width, height)

    def collision(self, a, b, w, h):
        is_colliding = False
        if (
                a + w > self.x
                and self.x + self.w > a
                and b + h > self.y
                and self.y + self.h > b
        ):
            is_colliding = True
        return is_colliding


def align_center(text, screen_width, char_width=pyxel.FONT_WIDTH):
    text_width = len(text) * char_width
    return (screen_width - text_width) / 2


def align_middle(screen_height, char_height=pyxel.FONT_HEIGHT):
    return (screen_height - char_height) / 2


def align_right(text, screen_width, char_width=pyxel.FONT_WIDTH):
    text_width = len(text) * char_width
    return screen_width - (text_width + char_width)


class Display:
    def __init__(self):
        self.game_over = "GAME OVER."
        self.game_over_x = align_center(self.game_over, 256)
        self.game_over_y = align_middle(192)
        self.game_over_prompt = "Press the 'Enter' key to start."
        self.game_over_prompt_x = align_center(self.game_over_prompt, 256)
        self.title = "SNAKE"
        self.title_x = align_center(self.title, 256)
        self.score = str(0)
        self.score_x = align_right(self.score, 256)
        self.egg_count = "Eggs "
        self.egg_count_x = 9

    def draw_title(self):
        pyxel.rect(self.title_x - 1, 0, len(self.title) * pyxel.FONT_WIDTH + 1, pyxel.FONT_HEIGHT + 1, 1)
        pyxel.text(self.title_x, 1, self.title, 12)

    def draw_score(self, score):
        self.score = str(score)
        self.score_x = align_right(self.score, 256)
        pyxel.rect(self.score_x - 1, 0, len(self.score) * pyxel.FONT_WIDTH + 1, pyxel.FONT_HEIGHT + 1, 1)
        pyxel.text(self.score_x, 1, self.score, 3)

    def draw_eggs(self, eggs):
        self.egg_count = "Eggs " + str(eggs)
        pyxel.rect(self.egg_count_x - 1, 0, len(self.egg_count) * pyxel.FONT_WIDTH + 1, pyxel.FONT_HEIGHT + 1, 1)
        pyxel.text(self.egg_count_x, 1, self.egg_count, 8)

    def draw_game_over(self):
        pyxel.rect(self.game_over_prompt_x - 5, self.game_over_y - 5,
                   len(self.game_over_prompt) * pyxel.FONT_WIDTH + 10, 2 * pyxel.FONT_HEIGHT + 10, 1)
        pyxel.text(self.game_over_x, self.game_over_y, self.game_over, 8)
        pyxel.text(self.game_over_prompt_x, self.game_over_y + pyxel.FONT_HEIGHT + 2, self.game_over_prompt, 8)


class App:
    def __init__(self):
        pyxel.init(256, 192, scale=4, caption="SNAKE", fps=240)
        pyxel.load("assety/zdroj.pyxres")
        self.game_state = GameControl.PLAY
        self.level = Level()
        self.display = Display()
        self.egg = Egg(64, 32)
        self.snake = []  # Ukladani tela hada
        self.snake.append(SnakePart(32, 32, is_head=True))
        self.snake.append(SnakePart(24, 32))
        self.snake.append(SnakePart(16, 32))
        self.snake_direction = Direction.RIGHT
        self.snake_parts_add = 0
        self.speed = 10
        self.time_prev_frame = time.time()
        self.delta = 0
        self.time_prev_move = 0
        self.score = 0
        self.eggs_collected = 0
        self.inputs = collections.deque()
        pyxel.run(self.update, self.draw)

    def new_game(self):
        self.game_state = GameControl.PLAY
        self.snake.clear()
        self.egg = Egg(64, 32)
        self.snake = []  # Ukladani tela hada
        self.snake.append(SnakePart(32, 32, is_head=True))
        self.snake.append(SnakePart(24, 32))
        self.snake.append(SnakePart(16, 32))
        self.snake_direction = Direction.RIGHT
        self.snake_parts_add = 0
        self.speed = 10
        self.time_prev_frame = time.time()
        self.delta = 0
        self.time_prev_move = 0
        self.time_prev_move = 0
        self.score = 0
        self.eggs_collected = 0
        self.inputs.clear()
        self.move_egg()

    def update(self):
        time_curr_frame = time.time()
        self.delta = time_curr_frame - self.time_prev_frame
        self.time_prev_frame = time_curr_frame
        self.time_prev_move += self.delta
        self.check_input()
        if self.game_state == GameControl.PLAY:
            if self.time_prev_move >= 1 / self.speed:
                self.time_prev_move = 0
                self.move_snake()
                self.check_collisions()

    def draw(self):
        pyxel.cls(0)
        self.level.draw()
        self.egg.draw()
        for i in self.snake:
            i.draw(self.snake_direction)
        self.display.draw_title()
        self.display.draw_score(self.score)
        self.display.draw_eggs(self.eggs_collected)
        if self.game_state == GameControl.STOP:
            self.display.draw_game_over()

    def check_collisions(self):
        # vajicko
        if self.egg.collision(self.snake[0].x, self.snake[0].y, self.snake[0].w, self.snake[0].h):
            self.speed += (self.speed * 0.05)
            self.snake_parts_add += 2
            self.move_egg()
            self.eggs_collected += 1
            self.score += len(self.snake) * self.eggs_collected + 1
        # ocas
        for i in self.snake:
            if i == self.snake[0]:
                continue
            if i.collision(self.snake[0].x, self.snake[0].y, self.snake[0].w, self.snake[0].h):
                self.game_state = GameControl.STOP
        # steny
        if pyxel.tilemap(0).get(self.snake[0].x / 8, self.snake[0].y / 8) == 3:
            self.game_state = GameControl.STOP

    def move_egg(self):
        # nastavi nahodne souradnice pro vajicko
        valid_pos = False
        while not valid_pos:
            moved_x = random.randrange(8, 248, 8)
            moved_y = random.randrange(8, 184, 8)
            valid_pos = True
            # kontrola hada
            for i in self.snake:
                if (
                        moved_x + 8 > i.x
                        and i.x + i.w > moved_x
                        and moved_y + 8 > i.y
                        and i.y + i.h > moved_y
                ):
                    valid_pos = False
                    break
            # kontrola steny
            if valid_pos:
                self.egg.move(moved_x, moved_y)

    def move_snake(self):
        # zmena smeru
        if len(self.inputs):
            self.snake_direction = self.inputs.popleft()
        # rust hada
        if self.snake_parts_add > 0:
            self.snake.append(SnakePart(self.snake[-1].x, self.snake[-1].y))
            self.snake_parts_add -= 1
        # pohyb hlavy
        prev_location_x = self.snake[0].x
        prev_location_y = self.snake[0].y
        if self.snake_direction == Direction.RIGHT:
            self.snake[0].x += self.snake[0].w
        if self.snake_direction == Direction.LEFT:
            self.snake[0].x -= self.snake[0].w
        if self.snake_direction == Direction.UP:
            self.snake[0].y -= self.snake[0].w
        if self.snake_direction == Direction.DOWN:
            self.snake[0].y += self.snake[0].w
        # pohyb ocasku
        for i in self.snake:
            if i == self.snake[0]:
                continue
            curr_location_x = i.x
            curr_location_y = i.y
            i.x = prev_location_x
            i.y = prev_location_y
            prev_location_x = curr_location_x
            prev_location_y = curr_location_y

    def check_input(self):
        if self.game_state == GameControl.STOP:
            if pyxel.btn(pyxel.KEY_ENTER):
                self.new_game()

        if pyxel.btn(pyxel.KEY_RIGHT):
            if len(self.inputs) == 0:
                if self.snake_direction != Direction.LEFT and self.snake_direction != Direction.RIGHT:
                    self.inputs.append(Direction.RIGHT)
            else:
                if self.inputs[-1] != Direction.LEFT and self.inputs[-1] != Direction.RIGHT:
                    self.inputs.append(Direction.RIGHT)
        elif pyxel.btn(pyxel.KEY_LEFT):
            if len(self.inputs) == 0:
                if self.snake_direction != Direction.RIGHT and self.snake_direction != Direction.LEFT:
                    self.inputs.append(Direction.LEFT)
            else:
                if self.inputs[-1] != Direction.RIGHT and self.inputs[-1] != Direction.LEFT:
                    self.inputs.append(Direction.LEFT)
        elif pyxel.btn(pyxel.KEY_UP):
            if len(self.inputs) == 0:
                if self.snake_direction != Direction.DOWN and self.snake_direction != Direction.UP:
                    self.inputs.append(Direction.UP)
            else:
                if self.inputs[-1] != Direction.DOWN and self.inputs[-1] != Direction.UP:
                    self.inputs.append(Direction.UP)
        elif pyxel.btn(pyxel.KEY_DOWN):
            if len(self.inputs) == 0:
                if self.snake_direction != Direction.UP and self.snake_direction != Direction.DOWN:
                    self.inputs.append(Direction.DOWN)
            else:
                if self.inputs[-1] != Direction.UP and self.inputs[-1] != Direction.DOWN:
                    self.inputs.append(Direction.DOWN)


# spusti program
App()
