import torch
import random
import numpy as np
from game import SnakeAI, Direction, Point
from collections import deque
from model import  Linear_QNet, QTrainer
from helper import plot

# Constants
MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LEARNING_RATE = 0.001

class Agent:
    def __init__(self):
        self.no_games = 0
        self.epsilon = 0 # control randomness
        self.gamma = 0
        self.memory = deque(maxlen=MAX_MEMORY)

        # Model & Trainer (Deep Q Learning
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, learning_rate=LEARNING_RATE, gamma=self.gamma)




    def get_state(self, game):
        head = game.snake[0]
        point_l = Point(head.x - 20, head.y)
        point_r = Point(head.x + 20, head.y)
        point_u = Point(head.x, head.y - 20)
        point_d = Point(head.x, head.y + 20)

        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        state = [
            # Danger straight
            (dir_r and game.is_collision(point_r)) or
            (dir_l and game.is_collision(point_l)) or
            (dir_u and game.is_collision(point_u)) or
            (dir_d and game.is_collision(point_d)),

            # Danger right
            (dir_u and game.is_collision(point_r)) or
            (dir_d and game.is_collision(point_l)) or
            (dir_l and game.is_collision(point_u)) or
            (dir_r and game.is_collision(point_d)),

            # Danger left
            (dir_d and game.is_collision(point_r)) or
            (dir_u and game.is_collision(point_l)) or
            (dir_r and game.is_collision(point_u)) or
            (dir_l and game.is_collision(point_d)),

            dir_l,
            dir_r,
            dir_u,
            dir_d,

            # Location of the food
            game.food.x < game.head.x, # food is left
            game.food.x > game.head.x, # food is right
            game.food.y < game.head.y, # food is up
            game.food.y > game.head.y # food is down
        ]

        # Convert booleans in integers
        return np.array(state, dtype=int)


    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached


    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # returns a list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)


    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # To random snake moves (Tradeoff Exploration/ Exploitation)
        # More games => smaller epsilon value
        self.epsilon = 80 - self.no_games
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move

def train():
    plot_scores = []
    plot_avg_score = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeAI()

    while True:
        # Get old state
        old_state = agent.get_state(game)

        # get move
        final_move = agent.get_action(old_state)

        # Perform move and get new state
        reward, done, score = game.play(final_move)
        new_state = agent.get_state(game)

        # Train short memory
        agent.train_short_memory(old_state, final_move, reward, new_state, done)

        # Remember all
        agent.remember(old_state, final_move, reward, new_state, done)

        if done:
            # Train long memory
            game.reset()
            agent.no_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print('Game', agent.no_games, 'Score', score, 'Record', record)

            # Plotting
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.no_games
            plot_avg_score.append(mean_score)
            plot(plot_scores, plot_avg_score)


if __name__ == '__main__':
    train()
