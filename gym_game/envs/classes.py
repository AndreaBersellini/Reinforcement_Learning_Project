try:
    import gym_game.envs.g2d as g2d
    from gym_game.envs.abstract import Point, Actor, check_collision
except:
    pass

try:
    import g2d
    from abstract import Point, Actor, check_collision
except:
    pass

import os, sys, math

class Arena:
    def __init__(self, size: Point):
        self._w, self._h = size
        self._level_lenght = 5000

        self._bg_x = 0

        self._count = 0
        self._turn = -1
        self._actors: list[Actor] = []
        self._curr_keys = self._prev_keys = tuple()
        self._collisions = []
        self._spawned = 0
        self._score = 0
        self._final_state = 0

    def spawn(self, a: Actor):
        if a not in self._actors:
            self._actors.append(a)

    def kill(self, a: Actor):
        if a in self._actors:
            self._actors.remove(a)
        if isinstance(a, Player):
            self._endGame()

    def tick(self, keys=[]):
        actors = list(reversed(self._actors))
        self._detect_collisions(actors)
        self._prev_keys = self._curr_keys
        self._curr_keys = keys

        # UI INTERACTION
        if "Escape" in keys:
            exit(1)

        for self._turn, a in enumerate(actors):
            a.move()

        self._count += 1

    def _naive_collisions(self, actors):
        # self._collisions = [[a2 for a2 in actors if a1 is not a2 and check_collision(a1, a2)] for a1 in actors]
        self._collisions.clear()
        for a1 in actors:
            colls1 = []
            for a2 in actors:
                if a1 is not a2 and check_collision(a1, a2):
                    colls1.append(a2)
            self._collisions.append(colls1)

    def _detect_collisions(self, actors):
        self._collisions.clear()
        tile = 40
        nx, ny = -(-self._w // tile),  -(-self._h // tile)
        cells = [set() for _ in range(nx * ny)]
        for i, a in enumerate(actors):
            x, y, w, h = (round(v) for v in a.position() + a.size())
            for tx in range((x - 1) // tile, 1 + (x + w + 1) // tile):
                for ty in range((y - 1) // tile, 1 + (y + h + 1) // tile):
                    if 0 <= tx < nx and 0 <= ty < ny:
                        cells[ty * nx + tx].add(i)
        for i, a in enumerate(actors):
            neighs = set()
            x, y, w, h = (round(v) for v in a.position() + a.size())
            for tx in range((x - 1) // tile, 1 + (x + w + 1) // tile):
                for ty in range((y - 1) // tile, 1 + (y + h + 1) // tile):
                    if 0 <= tx < nx and 0 <= ty < ny:
                        neighs |= cells[ty * nx + tx]
            colls = [actors[j] for j in sorted(neighs, reverse=True)
                     if i != j and check_collision(a, actors[j])]
            self._collisions.append(colls)
    
    def actors(self) -> list:
        return list(self._actors)
    
    def collisions(self) -> list[Actor]:
        t, colls = self._turn, self._collisions
        return colls[t] if 0 <= t < len(colls) else []
    
    def moveActors(self, distance, px, pw) -> None:
        actors = list(reversed(self._actors))

        stop_left = self._bg_x == 0 and (px - distance) <= (self._w / 2)
        stop_right = self._bg_x == (-self._level_lenght + self._w) and (px + pw - distance) >= (self._w / 2)
                
        if stop_left or stop_right:
            for a in actors:
                if isinstance(a, Player):
                    a.forceMove(-distance)

        elif self._bg_x + distance <= 0 and self._bg_x + distance >= -self._level_lenght + self._w:
            for a in actors:
                if not isinstance(a, Player):
                    a.forceMove(distance)
            self._bg_x += distance
        else:
            if self._bg_x + distance > 0:
                self._bg_x = 0 # COMPENSATION IF THE RESULT OF BG + DIST IS NOT 0
            elif self._bg_x + distance < (-self._level_lenght + self._w):
                self._bg_x = (-self._level_lenght + self._w) # COMPENSATION IF THE RESULT OF BG + DIST IS NOT DIVISOR OF LEV_LEN + ARENA_W

    def draw(self) -> None:
        # BACKGROUND
        for i in range(int(self._level_lenght / self._w)):
            g2d.draw_image('Images/background.png', (self._bg_x + i * self._w, 0), (0, 0), (self._w, self._h))

        # SCORE
        g2d.set_color((0, 0, 0))
        g2d.draw_text("SCORE: " + str(self._score), (80, 50), 20)

        for a in self._actors:
            if isinstance(a, Progress):
                g2d.draw_text("DISTANCE: " + str(a()), (self._w / 2, 50), 20)

        for a in self._actors:
            if isinstance(a, Player):
                g2d.draw_text("LIVES: " + str(a.lives()), (self._w - 80, 50), 20)

        # ACTORS
        for a in self._actors:
            a.draw()

    def addScore(self, value: int) -> None:
        self._score += value
    
    def size(self) -> Point:
        return (self._w, self._h)

    def count(self) -> int:
        return self._count

    def currentKeys(self) -> list[str]:
        return self._curr_keys

    def previousKeys(self) -> list[str]:
        return self._prev_keys

    def _endGame(self) -> None:
        self._final_state = 2
        """
        fin_str = "GAME OVER\nTotal points: " + str(self._score) + "\n\nRetry?"
        if g2d.confirm(fin_str):
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            exit(1)
        """

    def _winGame(self) -> None:
        self._final_state = 1
        """
        fin_str = "YOU WIN!\nTotal points: " + str(self._score) + "\n\nRetry?"
        if g2d.confirm(fin_str):
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            exit(1)
        """

    def finalState(self) -> int:
        return self._final_state
    
    # Check if the game is running (True only if a player is alive)
    def gameRunning(self):
        for a in self._actors:
            if isinstance (a, Player):
                return True
        return False
    
    # Input player action from AI
    def control(self, action):
        for a in self._actors:
            if isinstance(a, Player):
                if action == 0: # Do Nothing
                    pass
                elif action == 1: # Move left
                    a.addKey("a")
                elif action == 2: # Move right
                    a.addKey("d")
                elif action == 3: # Jump
                    a.addKey("Spacebar")


class Ground(Actor):
    def __init__(self, arena, pos):
        self._arena = arena

        self._x, self._y = pos
        self._w, self._h = 100, 70

    def move(self):
        return 0
    
    def forceMove(self, distance) -> None:
        self._x += distance

    def draw(self) -> None:
        position = (self._x, self._y)
        size = (self._w, self._h)

        g2d.draw_image('Images/ground_100.png', position, (0, 0), size)

    def position(self) -> Point:
        return self._x, self._y

    def size(self) -> Point:
        return self._w, self._h
    
class Platform(Actor):
    def __init__(self, arena, pos):
        self._arena = arena

        self._x, self._y = pos
        self._w, self._h = 100, 50

    def move(self):
        return 0
    
    def forceMove(self, distance) -> None:
        self._x += distance

    def draw(self) -> None:
        position = (self._x, self._y)
        size = (self._w, self._h)

        g2d.draw_image('Images/platform_100.png', position, (0, 0), size)

    def position(self) -> Point:
        return self._x, self._y

    def size(self) -> Point:
        return self._w, self._h

class Player(Actor):
    def __init__(self, arena, pos, spd):
        self._arena = arena
        self._x, self._y = pos
        self._w, self._h = 30, 60
        self._prev_pos = (self._y, self._y + self._h)
        self._speed_y = 20
        self._speed_x = spd
        self._life = 2
        self._pose = 1

        self._absolute_pos = self._x

        self._autoplay_keys = []

    def forceMove(self, distance) -> None:
        self._x += distance

    def move(self):
        arena_w, arena_h = self._arena.size()
        prev1, prev2 = self._prev_pos
        self._speed_y += 0.9 # GRAVITY
        stop = False

        # COLLISIONS
        for other in self._arena.collisions():
            ox, oy = other.position()
            _, oh = other.size()

            if isinstance(other, Plant):
                if other.isActive():
                    self._life -= 1
            if isinstance(other, Ground):
                if prev2 <= oy:
                    self._y = oy - self._h
                    self._speed_y = 0
                elif self._x < ox:
                    stop = True
                elif self._x > ox:
                    stop = True
            if isinstance(other, Platform):
                if prev2 <= oy:
                    self._y = oy - self._h
                    self._speed_y = 0
                elif prev1 >= oy + oh:
                    self._y = oy + oh
                    self._speed_y = -self._speed_y
                elif self._x < ox:
                    stop = True
                elif self._x > ox:
                    stop = True

        # CONTROLS
        keys = self._arena.currentKeys()
        prev_keys = self._arena.previousKeys()
        
        # AUTOPLAY KEYS
        for key in self._autoplay_keys:
            keys.append(key)

        # CONTROL KEYS
        if "Spacebar" in keys and "Spacebar" not in prev_keys:
            if self._speed_y == 0:
                self._speed_y = -17 # JUMP SPEED
        if "a" in keys:
            if not stop:
                self._absolute_pos += -self._speed_x
                self._arena.moveActors(self._speed_x, self._x, self._w)
                if self._pose < 9: self._pose += 1
                else: self._pose = 0
        if "d" in keys:
            if not stop:
                self._absolute_pos += self._speed_x
                self._arena.moveActors(-self._speed_x, self._x, self._w)
                if self._pose < 9: self._pose += 1
                else: self._pose = 0

        self._autoplay_keys.clear() # RESET AUTO INPUT LIST
        
        if self._x < 0:
            self._x = 0
        elif self._x + self._w > arena_w:
            self._x = arena_w - self._w

        if self._life == 0:
            self._arena.kill(self)

        if self._y >= arena_h:
            self._life = 0

        # MOVEMENT
        self._prev_pos = (self._y, self._y + self._h)
        self._y += self._speed_y

    def lives(self) -> int:
        return self._life

    def draw(self) -> None:
        position = (self._x, self._y)
        size = (self._w, self._h)

        if self._speed_y != 0:
            g2d.draw_image('Images/player_jump.png', position, (0, 0), size)
        elif self._pose < 4:
            g2d.draw_image('Images/player_00.png', position, (0, 0), size)
        else:
            g2d.draw_image('Images/player_01.png', position, (0, 0), size)

    def position(self) -> Point:
        return self._x, self._y

    def size(self) -> Point:
        return self._w, self._h
    
    def addKey(self, key):
        self._autoplay_keys.append(key)
    
    def absPos(self):
        return self._absolute_pos

class Coin(Actor):
    def __init__(self, arena, pos):
        self._arena = arena
        self._x, self._y = pos
        self._w, self._h = 50, 50
        self._value = 10

    def forceMove(self, distance) -> None:
        self._x += distance

    def move(self) -> None:      
        # COLLISIONS
        for other in self._arena.collisions():
            if isinstance(other, Player):
                self._arena.kill(self)
                self._arena.addScore(self._value)

    def draw(self) -> None:
        position = (self._x, self._y)
        size = (self._w, self._h)
        #g2d.draw_rect(position, size)
        g2d.draw_image('Images/coin.png', position, (0, 0), size)
    
    def position(self) -> Point:
        return self._x, self._y

    def size(self) -> Point:
        return self._w, self._h
    
class Progress(Actor):
    def __init__(self, arena, pos, size):
        self._arena = arena
        self._x, self._y = pos
        self._w, self._h = size
        self._progress = 0

    def __call__(self):
        return self._progress

    def forceMove(self, distance) -> None:
        self._x += distance

    def move(self) -> None:      
        # COLLISIONS
        for other in self._arena.collisions():
            if isinstance(other, Player):
                px, _ = other.position()
                pw, _ = other.size()
                if self._x < px + pw:
                    self._progress += ((px + pw) - self._x)
                    self._x = px + pw

    def draw(self) -> None:
        pass
    
    def position(self) -> Point:
        return self._x, self._y

    def size(self) -> Point:
        return self._w, self._h
    
class Flag(Actor):
    def __init__(self, arena, pos, size):
        self._arena = arena
        self._x, self._y = pos
        self._w, self._h = size

    def forceMove(self, distance) -> None:
        self._x += distance

    def move(self) -> None:      
        # COLLISIONS
        for other in self._arena.collisions():
            if isinstance(other, Player):
                ox, oy = other.position()
                if ox >= self._x + self._w / 2:
                    self._arena.kill(other)
                    self._arena._winGame()

    def draw(self) -> None:
        position = (self._x, self._y)
        size = (self._w, self._h)
        #g2d.draw_rect(position, size)
        g2d.draw_image('Images/flag.png', position, (0, 0), size)
    
    def position(self) -> Point:
        return self._x, self._y

    def size(self) -> Point:
        return self._w, self._h

class Plant(Actor):
    def __init__(self, arena, pos):
        self._arena = arena
        self._x, self._y = pos
        self._w, self._h = 40, 60
        self._value = -10
        self._active = True

    def forceMove(self, distance) -> None:
        self._x += distance

    def move(self) -> None:      
        # COLLISIONS
        for other in self._arena.collisions():
            if isinstance(other, Player):
                if self._active:
                    self._arena.addScore(self._value)
                    self._active = False

    def draw(self) -> None:
        position = (self._x, self._y)
        size = (self._w, self._h)
        #g2d.draw_rect(position, size)
        if self._active:
            g2d.draw_image('Images/plant_0.png', position, (0, 0), size)
        else:
            g2d.draw_image('Images/plant_1.png', position, (0, 0), size)
    
    def isActive(self):
        return self._active
    
    def position(self) -> Point:
        return self._x, self._y

    def size(self) -> Point:
        return self._w, self._h
    
class Sensor(Actor):
    def __init__(self, arena, pos, radius):
        self._arena = arena
        self._x, self._y = pos

        self._x -= radius
        self._y -= radius

        self._w, self._h = radius * 2, radius * 2
        self._radius = radius

        self._perception = [Actor]

    def forceMove(self, distance) -> None:
        self._x += distance

    def move(self, pos) -> None:      
        # COLLISIONS
        for other in self._arena.collisions():
            if isinstance(other, Platform):
                other.position()
                pass
        
        self._x, self._y = pos

    def draw(self) -> None:
        position = (self._x - self._radius, self._y - self._radius)
        size = (self._w, self._h)
        g2d.draw_rect(position, size)
    
    def position(self) -> Point:
        return self._x - self._radius, self._y - self._radius

    def size(self) -> Point:
        return self._w , self._h