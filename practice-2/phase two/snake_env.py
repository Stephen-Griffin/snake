"""
Snake Eater Environment
Made with PyGame
Last modification in April 2024 by José Luis Perán
Machine Learning Classes - University Carlos III of Madrid
"""
import numpy as np
import random

class SnakeGameEnv:
    def __init__(self, frame_size_x=150, frame_size_y=150, growing_body=True):
        # Initializes the environment with default values
        self.frame_size_x = frame_size_x
        self.frame_size_y = frame_size_y
        self.growing_body = growing_body
        self.reset()

    def reset(self):
        # Resets the environment with default values
        self.snake_pos = [50, 50]
        self.snake_body = [[50, 50], [60, 50], [70, 50]]
        self.food_pos = [random.randrange(1, (self.frame_size_x // 10)) * 10, random.randrange(1, (self.frame_size_y // 10)) * 10]
        self._prev_dist = abs(self.snake_pos[0] - self.food_pos[0]) \
                        + abs(self.snake_pos[1] - self.food_pos[1])
        self.food_spawn = True
        self.direction = 'RIGHT'
        self.score = 0
        self.game_over = False
        return self.get_state()

    def step(self, action):
        # Implements the logic to change the snake's direction based on action
        # Update the snake's head position based on the direction
        # Check for collision with food, walls, or self
        # Update the score and reset food as necessary
        # Determine if the game is over
        self.update_snake_position(action)
        reward = self.calculate_reward()
        self.update_food_position()
        state = self.get_state()
        self.game_over = self.check_game_over()
        return state, reward, self.game_over

    def get_state(self):
        """
        Compute a 7-bit integer state:
          bit 6 = danger_straight
          bit 5 = danger_right
          bit 4 = danger_left
          bit 3 = food_left
          bit 2 = food_right
          bit 1 = food_up
          bit 0 = food_down
        """
        head_x, head_y = self.snake_pos
        dir_map = {'UP': (0, -10), 'DOWN': (0, 10),
                   'LEFT': (-10, 0), 'RIGHT': (10, 0)}
        dx, dy = dir_map[self.direction]

        # compute the three “will I crash?” points
        point_s = [head_x + dx, head_y + dy]
        point_l = [head_x - dy, head_y + dx]
        point_r = [head_x + dy, head_y - dx]

        danger_straight = int(
            point_s[0] < 0 or point_s[0] > self.frame_size_x-10 or
            point_s[1] < 0 or point_s[1] > self.frame_size_y-10 or
            point_s in self.snake_body
        )
        danger_right = int(
            point_r[0] < 0 or point_r[0] > self.frame_size_x-10 or
            point_r[1] < 0 or point_r[1] > self.frame_size_y-10 or
            point_r in self.snake_body
        )
        danger_left = int(
            point_l[0] < 0 or point_l[0] > self.frame_size_x-10 or
            point_l[1] < 0 or point_l[1] > self.frame_size_y-10 or
            point_l in self.snake_body
        )

        food_left  = int(self.food_pos[0] < head_x)
        food_right = int(self.food_pos[0] > head_x)
        food_up    = int(self.food_pos[1] < head_y)
        food_down  = int(self.food_pos[1] > head_y)


        bits = [
            danger_straight, danger_right, danger_left,
            food_left, food_right, food_up, food_down
        ]

        dir_encoding = {'UP':0, 'RIGHT':1, 'DOWN':2, 'LEFT':3}
        direction_code = dir_encoding[self.direction]    # 2 bits

        # bucket distance into 4 roughly even ranges
        head_x, head_y = self.snake_pos
        fx, fy       = self.food_pos
        cell_dist    = (abs(head_x - fx) + abs(head_y - fy)) // 10  # 0–28 cells
        if   cell_dist <= 3:  dist_bucket = 0
        elif cell_dist <= 8:  dist_bucket = 1
        elif cell_dist <= 15: dist_bucket = 2
        else:                 dist_bucket = 3
        # also 2 bits

        # now stick them on the bit‐list:
        # direction_code  → 2 bits
        # dist_bucket     → 2 bits
        for b in [(direction_code >> 1)&1, direction_code&1,
                (dist_bucket   >> 1)&1, dist_bucket&1]:
            bits.append(b)

        # finally pack all 11 bits into a single integer:
        state = 0
        for b in bits:
            state = (state << 1) | b
        return state

    def get_body(self):
        return self.snake_body

    def get_food(self):
        return self.food_pos

    def calculate_reward(self):
        # 10 for eating
        if not self.food_spawn:
            return 10.0

        # 2) -30 for crashing
        if self.check_game_over():
            return -30.0

        # distance to food and wall danger
        head_x, head_y = self.snake_pos
        fx, fy = self.food_pos
        curr_dist = abs(head_x - fx) + abs(head_y - fy)

        # initialize on first call after reset
        if not hasattr(self, '_prev_dist'):
            self._prev_dist = curr_dist

        delta = self._prev_dist - curr_dist
        self._prev_dist = curr_dist

        # basic distance reward: +1 if closer, –1 if farther
        reward = 1.0 if delta > 0 else (-1.0 if delta < 0 else 0.0)

        # danger penalty: check one step ahead in all three relative directions
        dir_map = {'UP': (0, -10), 'DOWN': (0, 10),
                   'LEFT': (-10, 0), 'RIGHT': (10, 0)}
        dx, dy = dir_map[self.direction]
        # straight, right, left
        points = [
            (head_x + dx, head_y + dy),
            (head_x + dy, head_y - dx),
            (head_x - dy, head_y + dx)
        ]
        for px, py in points:
            if (px < 0 or px > self.frame_size_x-10 or
                py < 0 or py > self.frame_size_y-10):
                reward -= 1.0   # penalty for “would hit wall” in that direction

        return reward

    def check_game_over(self):
        # Return True if the game is over, else False
        if self.snake_pos[0] < 0 or self.snake_pos[0] > self.frame_size_x-10:
            return True
        if self.snake_pos[1] < 0 or self.snake_pos[1] > self.frame_size_y-10:
            return True
        for block in self.snake_body[1:]:
            if self.snake_pos[0] == block[0] and self.snake_pos[1] == block[1]:
                return True

        return False

    def update_snake_position(self, action):
        # Updates the snake's position based on the action
        # Map action to direction
        change_to = ''
        direction = self.direction
        if action == 0:
            change_to = 'UP'
        elif action == 1:
            change_to = 'DOWN'
        elif action == 2:
            change_to = 'LEFT'
        elif action == 3:
            change_to = 'RIGHT'

        # Move the snake
        if change_to == 'UP' and direction != 'DOWN':
            direction = 'UP'
        if change_to == 'DOWN' and direction != 'UP':
            direction = 'DOWN'
        if change_to == 'LEFT' and direction != 'RIGHT':
            direction = 'LEFT'
        if change_to == 'RIGHT' and direction != 'LEFT':
            direction = 'RIGHT'

        if direction == 'UP':
            self.snake_pos[1] -= 10
        elif direction == 'DOWN':
            self.snake_pos[1] += 10
        elif direction == 'LEFT':
            self.snake_pos[0] -= 10
        elif direction == 'RIGHT':
            self.snake_pos[0] += 10

        self.direction = direction


        self.snake_body.insert(0, list(self.snake_pos))

        if self.snake_pos[0] == self.food_pos[0] and self.snake_pos[1] == self.food_pos[1]:
            self.score += 10
            self.food_spawn = False
            # If the snake is not growing
            if not self.growing_body:
                self.snake_body.pop()
        else:
            self.snake_body.pop()

    def update_food_position(self):
        if not self.food_spawn:
            self.food_pos = [random.randrange(1, (self.frame_size_x//10)) * 10, random.randrange(1, (self.frame_size_x//10)) * 10]
        self.food_spawn = True
