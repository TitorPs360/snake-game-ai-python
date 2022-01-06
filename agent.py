import torch
import random
import numpy as np
from collections import deque
from snake_ai import SnakeGameAI, Direction, Point
from model import Linear_QNet, QTrainer
from ploter import plot
import os.path

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

GRID_SIZE = 20

DEVICE = 'cuda'


class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)

        file_name = 'model.pth'
        model_folder_path = './model'
        file_name = os.path.join(model_folder_path, file_name)
        if os.path.isfile(file_name):
            self.model = Linear_QNet(11, 256, 3)

            file_name = 'model.pth'
            model_folder_path = './model'
            file_name = os.path.join(model_folder_path, file_name)

            self.model.load_state_dict(torch.load(file_name))
            self.model.eval()

            self.model = self.model.to(DEVICE)
            print('Loaded last model: ', file_name)
        else:
            self.model = Linear_QNet(11, 256, 3)
            self.model = self.model.to(DEVICE)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):
        # define head
        head = game.snake[0]

        # define surrounding
        point_right = Point(head.x + GRID_SIZE, head.y)
        point_left = Point(head.x - GRID_SIZE, head.y)
        point_up = Point(head.x, head.y - GRID_SIZE)
        point_down = Point(head.x, head.y + GRID_SIZE)

        # define direction
        direction_right = game.direction == Direction.RIGHT
        direction_left = game.direction == Direction.LEFT
        direction_up = game.direction == Direction.UP
        direction_down = game.direction == Direction.DOWN

        state = [
            # go straight will die
            (direction_right and game.is_collision(point_right)) or
            (direction_left and game.is_collision(point_left)) or
            (direction_up and game.is_collision(point_up)) or
            (direction_down and game.is_collision(point_down)),

            # go right will die
            (direction_right and game.is_collision(point_down)) or
            (direction_left and game.is_collision(point_up)) or
            (direction_up and game.is_collision(point_right)) or
            (direction_down and game.is_collision(point_left)),

            # go left will die
            (direction_right and game.is_collision(point_up)) or
            (direction_left and game.is_collision(point_down)) or
            (direction_up and game.is_collision(point_left)) or
            (direction_down and game.is_collision(point_right)),

            # set direction state
            direction_left,
            direction_right,
            direction_up,
            direction_down,

            # set apple location
            game.apple.x < game.head.x,  # apple on left
            game.apple.x > game.head.x,  # apple on right
            game.apple.y < game.head.y,  # apple on up
            game.apple.y > game.head.y,  # apple on down
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        # popleft if MAX_MEMORY is reached
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(
                self.memory, BATCH_SIZE)  # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves
        self.epsilon = 80 - self.n_games
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float).to('cuda')
            prediction = self.model(state0)
            move = torch.argmax(prediction).to('cuda').item()
            final_move[move] = 1

        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI()
    while True:
        # get stored state
        state_old = agent.get_state(game)

        # get agent action
        final_move = agent.get_action(state_old)

        # move and get new state
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        # train short memory
        agent.train_short_memory(
            state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # train long memory and plot result
            game.setup()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print('Game No.', agent.n_games, 'Last Score',
                  score, 'High score:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()
