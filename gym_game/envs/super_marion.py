try:
    import gym_game.envs.g2d as g2d
    from gym_game.envs.classes import Arena, Player, Ground, Platform, Coin, Progress, Flag, Plant
    from gym_game.envs.parameters import *
except:
    print("Game running by human!")

try:
    import g2d
    from classes import Arena, Player, Ground, Platform, Coin, Progress, Flag, Plant
    from parameters import *
except:
    print("Game running by AI!")

import math

class SuperMarion():
    def __init__(self):

        # PRIVATE VARIABLES
        self._no_progress = 0
        self._max_distance = 0

        self._reward_progression = 10

        self._previous_pos = ARENA_W / 2

        # ARENA SETUP
        self._arena = Arena((ARENA_W, ARENA_H))

        # PROGRESS SETUP
        progress = Progress(self._arena, (ARENA_W / 2 + 30, 0), (5, ARENA_H))
        self._arena.spawn(progress)

        # FINISH LINE
        flag = Flag(self._arena, (LEVEL_LENGTH - 300, 0), (50, ARENA_H))
        self._arena.spawn(flag)

        # GROUND LAYOUT
        for i, g in enumerate(ground_layout):
            if g:
                ground = Ground(self._arena, (i * GROUND_UNIT, ARENA_H - 70))
                self._arena.spawn(ground)
        
        # PLATFORM LAYOUT
        for i, row in enumerate(platform_layout):
            for j, c in enumerate(row):
                if c:
                    platform = Platform(self._arena, (j * GROUND_UNIT, ARENA_H - 220 - i * 150))
                    self._arena.spawn(platform)

        # PLANT LAYOUT
        for i, row in enumerate(plant_layout):
            for j, c in enumerate(row):
                if c:
                    plant = Plant(self._arena, (j * CELL_UNIT, ARENA_H - 130 - i * 150))
                    #self._arena.spawn(plant)
                
        # COIN LAYOUT
        for i, row in enumerate(coin_layout):
            for j, c in enumerate(row):
                if c:
                    coin = Coin(self._arena, (j * CELL_UNIT, i * CELL_UNIT))
                    self._arena.spawn(coin)

        # PLAYER SPAWN
        player = Player(self._arena, (ARENA_W / 2, ARENA_H / 2), SPEED)
        self._arena.spawn(player)

        if DISPLAY:
            g2d.init_canvas((ARENA_W, ARENA_H))

    # A tick of the game (game update)
    def _tick(self):
        if DISPLAY:
            g2d.clear_canvas()
            self._arena.draw()
        self._arena.tick(g2d.current_keys())

    # Kill the player
    def _forceKill(self):
        for a in self._arena.actors():
            if isinstance(a, Player):
                self._arena.kill(a)

    # Execute action and update the game
    def action(self, action):
        self._arena.control(action)
        self._tick()

    # Assign reward
    def evaluate(self):

        reward = 0
        
        # Save the state of the progress line
        progress = 0
        for a in self._arena.actors():
            if isinstance(a, Progress):
                progress = a()

        # If no progress is made for some time then kill player
        if self._no_progress >= 500:
            self._forceKill()
        
        self._no_progress += 1

        

        if self._arena.gameRunning():
            if progress >= self._reward_progression:
                reward += PROGRESS_REWARD
                self._reward_progression += 10

            advance = progress - self._max_distance # Difference between current progress line and last known progress

            if advance > 0:
                self._max_distance = progress
                self._no_progress = 0

        else:
            final_state = self._arena.finalState() # Check the final state (1 = Win, 2 = Lost)

            if final_state == 1:
                reward += WIN_REWARD
            elif final_state == 2:
                reward += DEATH_REWARD
            else:
                print("GAME IS NOT RUNNING BUT FINAL STATE IS UNCLEAR -> " + str(final_state))

        return reward
  
    # Check if game is done
    def is_done(self):
        return not self._arena.gameRunning()
    
    # Return the observations
    def observe(self):
        n = 1 # Sampling unit (1 = no sampling)

        px, py = 0, 0
        for a in self._arena.actors():
            if isinstance(a, Player):
                px = a.absPos()
                _, py = a.position()

        px = n * math.floor(px / n)
        py = n * math.floor(py / n)

        return tuple([int(px),int(py)])
        
    # Render the game with g2d
    def view(self):
        if DISPLAY:
            g2d.clear_canvas()
            self._arena.draw()
            g2d.update_canvas()

    # Start function only use by human
    def start(self):
        g2d.main_loop(self._tick)


def main():
    game = SuperMarion()
    game.start()

if __name__ == "__main__":
    main()