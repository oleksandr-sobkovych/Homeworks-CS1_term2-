"""Work with the Q Learning processing."""
import numpy as np
from PIL import Image
import cv2
import matplotlib.pyplot as plt
from matplotlib import style
from typing import Collection, Union


class QAgent:
    """Agent in the enviroment."""

    def __init__(self, x: int, y: int):
        """Create a new agent at position (x, y)."""
        self.x = x
        self.y = y

    @property
    def position(self) -> (int, int):
        """Get the agent's position."""
        return self.x, self.y

    def __repr__(self) -> str:
        return f"{self.x}, {self.y}"

    def move(self, x: int = None, y: int = None):
        """Move the agent by (x, y) or randomly if no value is given."""
        # supports all directions
        if x is None:
            self.x += np.random.randint(-1, 2)
        else:
            self.x += x

        if y is None:
            self.y += np.random.randint(-1, 2)
        else:
            self.y += y

    def action(self, choice: int):
        """Move the agent according to choice."""
        if choice == 0:
            self.move(x=1, y=0)
        elif choice == 1:
            self.move(x=-1, y=0)
        elif choice == 2:
            self.move(x=0, y=1)
        else:
            self.move(x=0, y=-1)


class QLearner:
    """Represent the enviroment for QLearning."""

    MOVE_PENALTY = 1
    WALL_PENALTY = 300
    FINISH_REWARD = 25
    EPS_DECAY = 0.9998
    OPTIMIZATION_COEFF = 2000
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

    def __init__(self, maze, epsilon: float = 1.0, episodes: int =
    10000,
                 show_episodes: int = 500):
        """Create a new Q enviroment.

        :param maze: maze to base upon
        :type maze: Maze
        :param epsilon: probability of choosing action randomly
        :param episodes: maximum episodes to repeat
        :param show_episodes: episodes to show (via %)
        """
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

    def get_reward(self, player: QAgent, obs: tuple) -> int:
        """Get the reward for moving.

        :param player: current agent
        :param obs: current observation (agent position)
        :return: the reward depending on action
        """
        if (player.x >= self.size or
                player.y >= self.size or
                player.x < 0 or
                player.y < 0 or
                self.env[player.position] == 1):
            player.x, player.y = obs
            return -self.WALL_PENALTY
        elif self.env[player.position] == 3:
            return self.FINISH_REWARD
        else:
            return -self.MOVE_PENALTY

    def draw_maze(self, route: Collection, reward: int = None,
                  new_obs: tuple = None, verbose: bool = False) -> Image:
        """Draw the maze and return the image.

        :param route: route to include
        :param reward: reward to indicate completion
        :param new_obs: new observation (next state)
        :param verbose: whether to display the image
        :return: the image object
        """
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
            if reward and reward == self.FINISH_REWARD:
                if cv2.waitKey(500):
                    return img
            else:
                if cv2.waitKey(3):
                    return img
        return img

    def choose_action(self, obs: tuple) -> Union[int, np.ndarray]:
        """Choose the action for q agent (randomly or optimally).

        :param obs: current state
        :return: the action (int 0-3)
        """
        if np.random.random() > self.epsilon:
            # GET THE ACTION
            return np.argmax(self.q_table[obs])
        else:
            return np.random.randint(0, 4)

    def train_single_episode(self, episode: int, episode_rewards: list,
                             learning_rate: float, discount: float,
                             verbose: bool,
                             track: bool = False) -> Union[Collection, bool]:
        """Train a single episode.

        :param episode: number of episode (from 0)
        :param episode_rewards: list of all episode rewards
        :param learning_rate: learning rate
        :param discount: discount rate
        :param verbose: whether to display additional information
        :param track: whether to track all episodes' routes and rewards
        :return: if track return route, if solved return False, else True
        """
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
        for i in range(self.iterations):
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
            if reward == self.FINISH_REWARD:
                new_q = self.FINISH_REWARD
            else:
                new_q = ((1 - learning_rate) * current_q +
                         learning_rate * (reward + discount * max_future_q))
            self.q_table[obs][choice] = new_q

            if show:
                self.draw_maze(route, reward, new_obs, verbose)

            episode_reward += reward
            if reward == self.FINISH_REWARD:
                # end cycle if the goal is reached
                unsolved = False
                break
        self.epsilon *= self.EPS_DECAY
        episode_rewards.append(episode_reward)
        if track:
            return route
        return unsolved

    def train_env(self, learning_rate: float = 0.1, discount: float = 0.95,
                  verbose: bool = False) -> dict:
        """Train the whole enviroment while not solved.

        When solved optimizes route for some iterations.
        :param learning_rate: learning rate
        :param discount: discount rate
        :param verbose: whether to display additional info
        :return: valuable analysis information
        """
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
        for episode in range(episode, self.OPTIMIZATION_COEFF+episode):
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
