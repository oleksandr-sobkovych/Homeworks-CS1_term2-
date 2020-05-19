import numpy as np
from PIL import Image
import cv2
import matplotlib.pyplot as plt
from matplotlib import style


class QAgent:
    """"""

    def __init__(self, x, y):
        """"""
        self.x = x
        self.y = y

    @property
    def position(self):
        """"""
        return self.x, self.y

    def __repr__(self):
        """"""
        return f"{self.x}, {self.y}"

    def move(self, x=None, y=None):
        """"""
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
        """"""
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
    OPTIMIZATION_COEFF = 7
    # BGR for some reason in cv2
    colors = {1: (255, 119, 0),
              2: (111, 216, 145),
              3: (250, 140, 125),
              4: (125, 142, 250),
              5: (252, 230, 119)}
    EMPTY_COLOR = 255  # white
    AGENT_NUM = 1  # player key in dict
    FINISH_NUM = 2  # food key in dict
    START_NUM = 3  # start key in dict
    WALL_NUM = 4  # enemy key in dict
    ROUTE_NUM = 5

    def __init__(self, maze, epsilon=1.0, episodes: int = 10000,
                 show_episodes=500):
        style.use("ggplot")
        self.array = maze.array
        self.size = max(maze.size)
        self.iterations = self.size**2
        self.episodes = episodes
        self.show_eps = show_episodes
        self.epsilon = epsilon
        self.start = maze.start
        self.finish = maze.finish
        self.env = np.array(self.array, dtype=np.int)
        self.q_table = np.random.random_sample((self.size, self.size) + (4,))

    def get_reward(self, player, obs):
        """"""
        if (player.x >= self.size or
                player.y >= self.size or
                player.x < 0 or
                player.y < 0 or
                self.env[player.position] == 1):
            player.x, player.y = obs
            return -self.ENEMY_PENALTY
        elif self.env[player.position] == 3:
            return self.FOOD_REWARD
        else:
            return -self.MOVE_PENALTY

    def draw_maze(self, route, reward=None, new_obs=None, verbose=False):
        """"""
        env = np.ndarray((self.size, self.size, 3),
                         dtype=np.uint8)
        env.fill(self.EMPTY_COLOR)
        for place in route:
            env[place] = self.colors[self.ROUTE_NUM]
        env[self.start] = self.colors[self.START_NUM]
        env[self.finish] = self.colors[self.FINISH_NUM]
        if new_obs:
            env[new_obs] = self.colors[self.AGENT_NUM]
        for ii in range(self.size):
            for jj in range(self.size):
                if self.env[ii][jj] == 1:
                    env[ii][jj] = self.colors[self.WALL_NUM]
        img = Image.fromarray(env, 'RGB')
        img = img.resize((600, 600), Image.NEAREST)
        if verbose:
            cv2.imshow("image", np.array(img))
            if reward and reward == self.FOOD_REWARD:
                if cv2.waitKey(500):
                    return img
            else:
                if cv2.waitKey(3):
                    return img
        return img

    def choose_action(self, obs):
        """"""
        if np.random.random() > self.epsilon:
            # GET THE ACTION
            return np.argmax(self.q_table[obs])
        else:
            return np.random.randint(0, 4)

    def train_single_episode(self, episode, episode_rewards,
                             learning_rate, discount, verbose,
                             track=False):
        """"""
        player = QAgent(*self.start)
        unsolved = True
        show = False
        if track or verbose:
            route = set()
        if verbose and episode % self.show_eps == 0:
            print(f"Episode #{episode}: epsilon = {self.epsilon}")
            print(f"{self.show_eps} episodes mean: "
                  f"{np.mean(episode_rewards[-self.show_eps:])}")
            show = True

        episode_reward = 0
        for i in range(ITERATIONS):
            obs = player.position
            choice = self.choose_action(obs)
            # take the action
            player.action(choice)
            reward = self.get_reward(player, obs)
            new_obs = player.position

            if track or verbose:
                route.add(new_obs)

            # get q values
            max_future_q = np.max(self.q_table[new_obs])
            current_q = self.q_table[obs][choice]

            # change q values according to the reward
            if reward == self.FOOD_REWARD:
                new_q = self.FOOD_REWARD
            else:
                new_q = ((1 - learning_rate) * current_q +
                         learning_rate * (reward + discount * max_future_q))
            self.q_table[obs][choice] = new_q

            if show:
                self.draw_maze(route, reward, new_obs, verbose)

            episode_reward += reward
            if reward == self.FOOD_REWARD:
                # end cycle if the goal is reached
                unsolved = False
                break
        self.epsilon *= self.EPS_DECAY
        episode_rewards.append(episode_reward)
        if track:
            return route
        return unsolved

    def train_env(self, learning_rate=0.1, discount=0.95,
                         verbose=False):
        """"""
        episode_rewards = []
        episode = 0
        unsolved = True
        q_feed = {}
        while unsolved and episode < self.episodes:
            episode += 1
            unsolved = self.train_single_episode(episode, episode_rewards,
                                                 learning_rate, discount,
                                                 verbose)
        if verbose:
            print(f"\nSolved at #{episode}: epsilon = {self.epsilon}")
            print(f"{self.show_eps} episodes mean: "
                  f"{np.mean(episode_rewards[-self.show_eps:])}\n")

        q_feed["solution episode"] = episode
        track = {}
        # allow agent to optimize found route
        for episode in range(episode, self.OPTIMIZATION_COEFF*episode):
            route = self.train_single_episode(episode, episode_rewards,
                                              learning_rate, discount, verbose,
                                              track=True)
            track[episode] = (episode_rewards[-1], route)

        optimal_values = track[max(track, key=lambda x: track[x][0])]
        q_feed["max_reward"], q_feed["solution_path"] = optimal_values

        moving_avg = np.convolve(episode_rewards,
                                 np.ones((self.show_eps,)) / self.show_eps,
                                 mode='valid')

        plt.plot([i for i in range(len(moving_avg))], moving_avg)
        plt.ylabel(f"Reward {self.show_eps}ma")
        plt.xlabel("episode #")
        if verbose:
            plt.show()

        return q_feed
