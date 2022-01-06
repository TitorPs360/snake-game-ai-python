import pygame
import random
from enum import Enum
from collections import namedtuple

pygame.init()
font = pygame.font.Font('pixelFont.ttf', 48)


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


Point = namedtuple('Point', 'x, y')

# color
WHITE = (255, 255, 255)
RED = (216, 72, 13)
BLACK = (0, 0, 0)
BLUE = (91, 122, 250)
LIGHT_GREEN = (173, 214, 68)
DARK_GREEN = (148, 187, 54)

GRID_SIZE = 20
SPEED = 10


class snakeGame:
    def __init__(self, w=400, h=400):
        self.w = w
        self.h = h

        # setup display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake Game')
        self.clock = pygame.time.Clock()

        # set initial Direction
        self.direction = Direction.RIGHT

        # setup snake
        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head]

        # setup score
        self.score = 0
        self.apple = None
        self._place_apple()

    # make snake move
    def _move(self, direction):
        x = self.head.x
        y = self.head.y

        if direction == Direction.RIGHT:
            x += GRID_SIZE
        elif direction == Direction.LEFT:
            x -= GRID_SIZE
        elif direction == Direction.UP:
            y -= GRID_SIZE
        elif direction == Direction.DOWN:
            y += GRID_SIZE

        self.head = Point(x, y)

    # place apple on the map
    def _place_apple(self):
        x = random.randint(0, (self.w - GRID_SIZE)//GRID_SIZE) * GRID_SIZE
        y = random.randint(0, (self.h - GRID_SIZE)//GRID_SIZE) * GRID_SIZE
        self.apple = Point(x, y)

        # check apple not in snake postion
        if self.apple in self.snake:
            self._place_apple()

    # check game over
    def _is_collision(self):
        # hit the wall
        if self.head.x > self.w - GRID_SIZE or self.head.x < 0 or self.head.y > self.h - GRID_SIZE or self.head.y < 0:
            return True

        # eat it self
        if self.head in self.snake[1:]:
            return True

        return False

    # show game to display
    def _update_display(self):
        # set background
        self.display.fill(LIGHT_GREEN)

        # draw grid background
        for x in range(0, self.w, GRID_SIZE * 3):
            for y in range(0, self.h, GRID_SIZE * 3):
                if ((x+y) // GRID_SIZE * 3) % 2 == 1:
                    pygame.draw.rect(self.display, DARK_GREEN, pygame.Rect(
                        x, y, GRID_SIZE * 3, GRID_SIZE * 3))

        # draw snake
        for dot in self.snake:
            pygame.draw.rect(self.display, BLUE, pygame.Rect(
                dot.x, dot.y, GRID_SIZE, GRID_SIZE))

        # draw face on snake head
        if self.direction == Direction.LEFT:
            pygame.draw.rect(self.display, BLACK, pygame.Rect(
                self.head.x + 5, self.head.y, GRID_SIZE // 4, GRID_SIZE // 4))
            pygame.draw.rect(self.display, BLACK, pygame.Rect(
                self.head.x + 5, self.head.y + GRID_SIZE - 5, GRID_SIZE // 4, GRID_SIZE // 4))
        elif self.direction == Direction.RIGHT:
            pygame.draw.rect(self.display, BLACK, pygame.Rect(
                self.head.x + GRID_SIZE - 10, self.head.y, GRID_SIZE // 4, GRID_SIZE // 4))
            pygame.draw.rect(self.display, BLACK, pygame.Rect(
                self.head.x + GRID_SIZE - 10, self.head.y + GRID_SIZE - 5, GRID_SIZE // 4, GRID_SIZE // 4))
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

    # play game by press keyboard
    def play(self):
        # get key from user
        for event in pygame.event.get():
            # quit game
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            # wasd key
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_d:
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_s:
                    self.direction = Direction.DOWN
                elif event.key == pygame.K_w:
                    self.direction = Direction.UP

        # move snake
        self._move(self.direction)
        self.snake.insert(0, self.head)

        # check game over
        gameover = False
        if self._is_collision():
            gameover = True
            return gameover, self.score

        # check snake eat apple
        if self.head == self.apple:
            self.score += 1
            self._place_apple()
        else:
            # continue
            self.snake.pop()

        # update display
        self._update_display()
        self.clock.tick(SPEED)

        # return game state
        return gameover, self.score


if __name__ == '__main__':
    game = snakeGame()

    # loop play game
    while True:
        gameover, score = game.play()

        if gameover == True:
            break

    # show gameover score
    print("Latest score", score)

    pygame.quit()
