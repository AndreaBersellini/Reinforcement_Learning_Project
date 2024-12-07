import random
import os
import gym
import gym_game
import numpy as np
from scipy import stats
from datetime import datetime
from gym_game.envs.parameters import *

def simulate():
    global epsilon, epi_epsilon, gen_epsilon, epsilon_decay, epsilon_min, epsilon_max, q_table, up_reward_mean, learning_rate, gamma

    # CREATE RESULTS ARCHIVE
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    directory = "results"
    if not os.path.exists(directory):
        os.makedirs(directory)

    for generation in range(MAX_GENERATIONS):

        max_reward = [0] * MAX_EPISODES

        for episode in range(MAX_EPISODES):
            # INITIALIZE EPISODE PARAMETERS
            steps = 1
            total_reward = 0
            exploit_actions = 0
            explore_actions = 0

            state, _ = env.reset()

            while True:
                # CHOOSE WITCH EPSILON TO USE ON THE CURRENT STEP
                if total_reward < up_reward_mean:
                    epsilon = gen_epsilon # BEFORE PASSING THE BEST REWAR OF PREVIOUS GEN, USE THE GENERATION EPSILON (SHOULD BE SMALL)
                else:
                    epsilon = epi_epsilon # AFTER PASSING THE BEST REWARD OF PREVIOUS GEN, USE THE EPISODE EPSILON (DECREMENTAL)

                q_action = np.argmax(q_table[state])

                # DECIDE IF TAKE A RANDOM ACTION OR FOLLOW THE Q-TABLE
                if q_action != 0:
                    if random.uniform(0, 1) < epsilon:
                        action = env.action_space.sample()
                        explore_actions += 1
                    else:
                        action = q_action
                        exploit_actions += 1
                else:
                    action = env.action_space.sample()

                next_state, reward, terminated, truncated, _ = env.step(action)

                episode_done = terminated or truncated

                # TOTAL REWARD OF THE EPISODE
                total_reward += reward

                # TAKE THE CURRENT AND THE BEST NEXT Q-VALUE
                q_value = q_table[state][action]
                best_q = np.max(q_table[next_state])

                # USE GREEDY TO CALCULATE NEW Q-VALUE
                q_table[state][action] = (1 - learning_rate) * q_value + learning_rate * (reward + gamma * best_q)
                
                state = next_state

                # RENDER THE GAME CANVAS
                env.render()

                # INCREMENT THE NUMBER OF STEPS
                steps += 1

                if episode_done:
                    # RANDOM ACTION RATE INCREMENT
                    if epi_epsilon >= epsilon_min and epi_epsilon == epsilon:
                        epi_epsilon *= epsilon_decay

                    # ADD THE TOTAL REWARD IF IT'S GREATER THAN ANOTHER REGISTERED REWARD
                    if total_reward - DEATH_REWARD > min(max_reward):
                        max_reward.remove(min(max_reward))
                        max_reward.append(total_reward - DEATH_REWARD)

                    result = f"Episode {episode} finished after {steps} time steps with total reward = {total_reward:.2f}, explorations = {explore_actions}, exploitations = {exploit_actions}, last epsilon used = {epsilon}."
                    print(result)

                    # SAVE EPISODE RESULTS EVERY X EPISODES
                    if episode % 100 == 0:
                        filename = f"{timestamp}.txt"      
                        filepath = os.path.join(directory, filename)
                        with open(filepath, "a") as file:
                            file.write(f"\n{result}")

                    break
        
        reward_mean = stats.trim_mean(max_reward, 0.1) # MEAN WITHOUT OUTLIERS
        result = f"Generation {generation} finished after {episode} episodes with max reward mean = {reward_mean}."
        print(result)
        
        # AFTER EVERY GENERATION UPDATE THE EPSILON
        gen_epsilon = min(epi_epsilon, gen_epsilon)
        epi_epsilon = epsilon_max
        up_reward_mean = reward_mean

        # SAVING Q-TABLE AND HYPERPARAMETERS
        hyperparameters = np.array([gen_epsilon, epi_epsilon, up_reward_mean])
        np.save("checkpoint/state.npy", q_table)
        np.save("checkpoint/params.npy", hyperparameters)

if __name__ == "__main__":
    env = gym.make("SuperMarion-v0")
    MAX_GENERATIONS = 10
    MAX_EPISODES = 1000

    epsilon_decay = 0.999
    epsilon_min = 0.05
    epsilon_max = 1

    gen_epsilon = epsilon_min
    epi_epsilon = epsilon_max
    epsilon = epsilon_max

    learning_rate = 0.8
    gamma = 0.7

    # LIST OF BEST REWARD REACHED
    up_reward_mean = 0

    num_box = tuple((env.observation_space.high + np.ones(env.observation_space.shape)).astype(int))

    state_path = os.path.join("checkpoint", "state.npy")
    params_path = os.path.join("checkpoint", "params.npy")

    if os.path.exists(state_path) and os.path.exists(params_path):
        q_table = np.load(state_path)
        params = np.load(params_path)
        gen_epsilon, epi_epsilon, up_reward_mean = params[0], params[1], params[2]
        print("Continuing previous training.")
    else:
        q_table = np.zeros(num_box + (env.action_space.n,))
        print("New training initialize.")

    simulate()
