import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('pixelFont.ttf', 48)


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


Point = namedtuple('Point', 'x, y')

# define color
WHITE = (255, 255, 255)
RED = (216, 72, 13)
BLUE = (91, 122, 250)
BLACK = (0, 0, 0)
LIGHT_GREEN = (173, 214, 68)
DARK_GREEN = (148, 187, 54)

GRID_SIZE = 20
SPEED = 120


class SnakeGameAI:
    def __init__(self, w=200, h=200):
        self.w = w
        self.h = h

        # setup display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake with AI')
        self.clock = pygame.time.Clock()

        self.setup()

    def setup(self):
        # set begining direction
        self.direction = Direction.RIGHT

        # setup snake
        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head]

        # setup score
        self.score = 0
        self.apple = None
        self._place_apple()
        self.frame_iteration = 0

    def _move(self, action):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN,
                      Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]  # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]  # right turn r -> d -> l -> u
        else:  # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]  # left turn r -> u -> l -> d

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += GRID_SIZE
        elif self.direction == Direction.LEFT:
            x -= GRID_SIZE
        elif self.direction == Direction.UP:
            y -= GRID_SIZE
        elif self.direction == Direction.DOWN:
            y += GRID_SIZE

        self.head = Point(x, y)

    # place apple on the map

    def _place_apple(self):
        x = random.randint(0, (self.w-GRID_SIZE)//GRID_SIZE)*GRID_SIZE
        y = random.randint(0, (self.h-GRID_SIZE)//GRID_SIZE)*GRID_SIZE
        self.apple = Point(x, y)
        if self.apple in self.snake:
            self._place_apple()

    # check game over
    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits  the wall
        if pt.x > self.w - GRID_SIZE or pt.x < 0 or pt.y > self.h - GRID_SIZE or pt.y < 0:
            return True
        # hits itself
        if pt in self.snake[1:]:
            return True

        return False

        # show game in window
    def _update_display(self):
        self.display.fill(LIGHT_GREEN)

        for x in range(0, self.w, GRID_SIZE * 3):
            for y in range(0, self.h, GRID_SIZE * 3):
                if ((x + y) // GRID_SIZE * 3) % 2 == 1:
                    pygame.draw.rect(self.display, DARK_GREEN, pygame.Rect(
                        x, y, GRID_SIZE * 3, GRID_SIZE * 3))

        # draw snake
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE, pygame.Rect(
                pt.x, pt.y, GRID_SIZE, GRID_SIZE))

        # draw face on head

        if self.direction == Direction.RIGHT:
            pygame.draw.rect(self.display, BLACK, pygame.Rect(
                self.head.x + GRID_SIZE - 10, self.head.y, GRID_SIZE // 4, GRID_SIZE // 4))
            pygame.draw.rect(self.display, BLACK, pygame.Rect(
                self.head.x + GRID_SIZE - 10, self.head.y + GRID_SIZE - 5, GRID_SIZE // 4, GRID_SIZE // 4))
        elif self.direction == Direction.LEFT:
            pygame.draw.rect(self.display, BLACK, pygame.Rect(
                self.head.x + 5, self.head.y, GRID_SIZE // 4, GRID_SIZE // 4))
            pygame.draw.rect(self.display, BLACK, pygame.Rect(
                self.head.x + 5, self.head.y + GRID_SIZE - 5, GRID_SIZE // 4, GRID_SIZE // 4))
        elif self.direction == Direction.UP:
            pygame.draw.rect(self.display, BLACK, pygame.Rect(
                self.head.x, self.head.y + 5, GRID_SIZE // 4, GRID_SIZE // 4))
            pygame.draw.rect(self.display, BLACK, pygame.Rect(
                self.head.x + GRID_SIZE - GRID_SIZE // 4, self.head.y + 5, GRID_SIZE // 4, GRID_SIZE // 4))
        elif self.direction == Direction.DOWN:
            pygame.draw.rect(self.display, BLACK, pygame.Rect(
                self.head.x, self.head.y + GRID_SIZE // 4 + 5, GRID_SIZE // 4, GRID_SIZE // 4))
            pygame.draw.rect(self.display, BLACK, pygame.Rect(self.head.x + GRID_SIZE -
                                                              GRID_SIZE // 4, self.head.y + GRID_SIZE // 4 + 5, GRID_SIZE // 4, GRID_SIZE // 4))

        # draw apple
        pygame.draw.rect(self.display, RED, pygame.Rect(
            self.apple.x, self.apple.y, GRID_SIZE, GRID_SIZE))

        # draw score
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])

        pygame.display.flip()

    def map_state(self):
        snake_map = []

        for y in range(self.h // GRID_SIZE):
            for x in range(self.w // GRID_SIZE):
                block = Point(x, y)
                if block in self.snake:
                    snake_map.append(0)
                elif block == self.apple:
                    snake_map.append(1)
                else:
                    snake_map.append(1)

        return snake_map

    def apple_position(self):
        return self.apple

    def play_step(self, action):
        self.frame_iteration += 1
        # get action input from AI
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # move snake to direction
        self._move(action)
        self.snake.insert(0, self.head)

        # check game over
        reward = 0
        game_over = False
        # game over or stuck in loop
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            game_over = True
            reward = -1
            return reward, game_over, self.score

        # check if snake eat apple
        if self.head == self.apple:
            # place new apple
            self.score += 1
            reward = 1
            self._place_apple()
        else:
            # continue
            self.snake.pop()

        # update display
        self._update_display()
        self.clock.tick(SPEED)

        # return game state
        return reward, game_over, self.score
