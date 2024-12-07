import gym
from gym import spaces
import numpy as np
from gym_game.envs.super_marion import SuperMarion
from gym_game.envs.parameters import *

class CustomEnv(gym.Env):
    #metadata = {'render.modes' : ['human']}
    def __init__(self):
        self.game = SuperMarion()

        self.action_space = spaces.Discrete(4)

        # [(AGENT_X, AGENT_Y)]
        self.observation_space = spaces.Box(np.array([0, 0]), np.array([LEVEL_LENGTH, ARENA_H + 100]), dtype=np.int32)

    def _get_obs(self):
        observation = self.game.observe()
        return observation
    
    def _get_info(self):
        return {}

    def reset(self, seed=None, options=None):
        # Optionally handle the seed
        if seed is not None:
            self.np_random, seed = gym.utils.seeding.np_random(seed)
        
        # Initialize a new game
        del self.game
        self.game = SuperMarion()

        # Get initial state
        obs = self._get_obs()
        info = self._get_info()

        return obs, info

    def step(self, action):
        # Execute actions
        self.game.action(action)

        # Get state and info of the current step
        obs = self._get_obs()
        info = self._get_info()

        # Get the raward obtained in this step
        reward = self.game.evaluate()

        # Check if the current game is running
        terminated = self.game.is_done()
        
        return obs, reward, terminated, False, info

    def render(self, mode = "human", close = False):
        self.game.view()

   