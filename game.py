# Imports
import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

# Initialise pygame
pygame.init()

# Add a custom font
font = pygame.font.Font('mountains.ttf', 20)

# Reset function
# Reward function
# change play(action) -> direction
# game_iteration
# is_collision


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


Point = namedtuple('Point', 'x, y')

# Game's colours
BLACK = (0, 0, 0)
RED = (200, 0, 0)
WHITE = (255, 255, 255)
GREEN1 = (0, 128, 0)
SILVER = (192, 192, 192)

BLOCK_SIZE = 20
SPEED = 19

class SnakeAI:
    # Create the size of the window
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h

        # Initialise display
        self.display = pygame.display.set_mode((self.w, self.h))

        # Set the title of the game
        pygame.display.set_caption('Automated SnakeAI')
        self.clock = pygame.time.Clock()
        self.reset()



    def reset(self):
        # Initialise the direction of the game when executed
        self.direction = Direction.RIGHT

        # Initialise the snake
        self.head = Point(self.w / 2, self.h / 2)

        self.snake = [self.head, Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)]

        # Initialise the score
        self.score = 0

        # Initialise food
        self.food = None

        # Place random food function
        self._add_food()

        self.frame_iteration = 0

    def _add_food(self):
        # Generate random food
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._add_food()

    def play(self, action):
        self.frame_iteration += 1
        # Get the user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()


        # Move the snake based on input
        # Update the head
        self._move(action)
        self.snake.insert(0, self.head)

        # If snake touches the end of display => game over
        reward = 0
        game_over = False

        # If snake doesn't improve, stop the game
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # If snake's head touches the food
        # Add 1 to the score
        # Spawn new food
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._add_food()
        else:
            self.snake.pop()

        # Update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # Return game over and score
        return reward, game_over, self.score

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # Check if snake hits the end of the screen
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        # Check if snake eats himself
        if pt in self.snake[1:]:
            return True

        return False

    def _update_ui(self):
        # Background colour
        self.display.fill(BLACK)

        # Colour the snake
        for pt in self.snake:
            pygame.draw.rect(self.display, GREEN1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, SILVER, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    # Function to define the controls
    # We define an action as follows:
    # [1, 0, 0] => move straight
    # [0, 1, 0] => turn right
    # [0, 0, 1] => turn left

    def _move(self, action):

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        index = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_direction = clock_wise[index] # nothing changes
        elif np.array_equal(action, [0, 1, 0]):
            next_index = (index + 1) % 4
            new_direction = clock_wise[next_index] # right turn right => down => left => up
        else: # [0, 0, 1]
            next_index = (index - 1) % 4
            new_direction = clock_wise[next_index] # counter clock wise right => up => left => down

        self.direction = new_direction

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)

