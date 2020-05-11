import numpy as np
from PIL import Image
import cv2
import matplotlib.pyplot as plt
import pickle
from matplotlib import style
import time


class QFeed:

    def __init__(self, l_rate: float, d_rate: float, iters: int, path: tuple):
        self.learning_rate = l_rate
        self.discount_rate = d_rate
        self.iters = iters
        self.path = path


style.use("ggplot")

ITERATIONS = 300

start_q_table = None # None or Filename


class QAgent:


    def __init__(self, x, y):
            self.x = x
            self.y = y

    @property
    def position(self):
        return self.x, self.y

    def __repr__(self):
        return f"{self.x}, {self.y}"

    def move(self, x=None, y=None):
        # If no value for x, move randomly
        if x is None:
            self.x += np.random.randint(-1, 2)
        else:
            self.x += x

        # If no value for y, move randomly
        if y is None:
            self.y += np.random.randint(-1, 2)
        else:
            self.y += y

    def action(self, choice):
        if choice == 0:
            self.move(x=1, y=0)
        elif choice == 1:
            self.move(x=-1, y=0)
        elif choice == 2:
            self.move(x=0, y=1)
        else:
            self.move(x=0, y=-1)


class QLearner:
    """"""

    MOVE_PENALTY = 1
    ENEMY_PENALTY = 300
    FOOD_REWARD = 25
    EPS_DECAY = 0.9998
    SHOW_EVERY = 500
    colors = {1: (255, 175, 0),
         2: (0, 255, 0),
         3: (0, 0, 255),
         4: (100, 20, 0)}
    PLAYER_N = 1  # player key in dict
    FOOD_N = 2  # food key in dict
    ENEMY_N = 3  # enemy key in dict
    ROUTE = 4

    def __init__(self, maze, episodes: int = 10000):
        self.array = maze.array
        self.size = max(maze.size)
        self.iterations = self.size**2
        self.episodes = episodes
        # lst = [[1 if np.random.random() < 0.8 else 0 for _ in range(self.size)]
        #        for __ in range(self.size)]
        self.start = maze.start
        self.finish = maze.finish
        # lst[start[0]][start[1]] = 2
        # lst[finish[0]][finish[1]] = 3
        self.env = np.array(self.array, dtype=np.int)
        self.q_table = np.random.random_sample((self.size, self.size) + (4,))

    def train(self, learning_rate = 0.1, discount = 0.95):
        epsilon = 1.0
        episode_rewards = []
        for episode in range(self.episodes):
            route = set()
            player = QAgent(*self.start)
            if episode % self.SHOW_EVERY == 0:
                print(f"on #{episode}, epsilon is {epsilon}")
                print(
                    f"{self.SHOW_EVERY} ep mean: "
                    f"{np.mean(episode_rewards[-self.SHOW_EVERY:])}")
                show = True
            else:
                show = False

            episode_reward = 0
            for i in range(ITERATIONS):
                obs = player.position
                if np.random.random() > epsilon:
                    # GET THE ACTION
                    choice = np.argmax(self.q_table[obs])
                else:
                    choice = np.random.randint(0, 4)
                # Take the action!
                player.action(choice)
                if (player.x >= self.size or
                        player.y >= self.size or
                        player.x < 0 or
                        player.y < 0 or
                        self.env[player.position] == 1):
                    reward = -self.ENEMY_PENALTY
                    player.x, player.y = obs
                elif self.env[player.position] == 3:
                    reward = self.FOOD_REWARD
                else:
                    reward = -self.MOVE_PENALTY

                new_obs = player.position
                route.add(new_obs)
                max_future_q = np.max(self.q_table[new_obs])
                current_q = self.q_table[obs][choice]

                if reward == self.FOOD_REWARD:
                    new_q = self.FOOD_REWARD
                else:
                    new_q = (1 - learning_rate) * current_q +\
                            learning_rate * (reward + discount * max_future_q)
                self.q_table[obs][choice] = new_q

                if show:
                    env = np.zeros((self.size, self.size, 3), dtype=np.uint8)
                    env[self.finish] = self.colors[self.FOOD_N]
                    for place in route:
                        env[place] = self.colors[self.ROUTE]
                    env[new_obs] = self.colors[self.PLAYER_N]
                    for ii in range(self.size):
                        for jj in range(self.size):
                            if self.env[ii][jj] == 1:
                                env[ii][jj] = self.colors[self.ENEMY_N]
                    img = Image.fromarray(env, 'RGB')  # reading to rgb.
                    # Apparently. Even tho color definitions are bgr. ???
                    img = img.resize((600, 600), Image.NEAREST)
                    cv2.imshow("image", np.array(img))  # show it!
                    time.sleep(0.01)
                    if reward == self.FOOD_REWARD:
                        if cv2.waitKey(500) & 0xFF == ord('q'):
                            break
                    else:
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break

                episode_reward += reward
                if reward == self.FOOD_REWARD:
                    break
            episode_rewards.append(episode_reward)
            epsilon *= self.EPS_DECAY

        moving_avg = np.convolve(episode_rewards,
                                 np.ones((self.SHOW_EVERY,)) / self.SHOW_EVERY,
                                 mode='valid')

        plt.plot([i for i in range(len(moving_avg))], moving_avg)
        plt.ylabel(f"Reward {self.SHOW_EVERY}ma")
        plt.xlabel("episode #")
        plt.show()
