"""
Snake Eater
Made with PyGame
Last modification in January 2024 by José Carlos Pulido
Machine Learning Classes - University Carlos III of Madrid
"""

import pygame, sys, time, random, math
from collections import deque
from wekaI import Weka


# DIFFICULTY settings
# Easy      ->  10
# Medium    ->  25
# Hard      ->  40
# Harder    ->  60
# Impossible->  120
DIFFICULTY = 1500

# Window size
FRAME_SIZE_X = 480
FRAME_SIZE_Y = 480

# Colors (R, G, B)
BLACK = pygame.Color(51, 51, 51)
WHITE = pygame.Color(255, 255, 255)
RED = pygame.Color(204, 51, 0)
GREEN = pygame.Color(204, 255, 153)
BLUE = pygame.Color(0, 51, 102)



# GAME STATE CLASS
class GameState:
    def __init__(self, FRAME_SIZE):
        self.snake_pos = [100, 50]
        self.snake_body = [[100, 50], [100-10, 50], [100-(2*10), 50]]
        self.food_pos = [random.randrange(1, (FRAME_SIZE[0]//10)) * 10,
                         random.randrange(1, (FRAME_SIZE[1]//10)) * 10]
        self.food_spawn = True
        self.direction = 'RIGHT'
        self.change_to = self.direction
        self.score = 0
        # To help with detecting oscillations.
        self.move_history = []
        self.is_new_game = True
        self.ticks_since_last_fruit = 0


# Game Over
def game_over(game):
    my_font = pygame.font.SysFont('times new roman', 90)
    game_over_surface = my_font.render('YOU DIED', True, WHITE)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (FRAME_SIZE_X/2, FRAME_SIZE_Y/4)
    game_window.fill(BLUE)
    game_window.blit(game_over_surface, game_over_rect)
    show_score(game, 0, WHITE, 'times', 20)
    pygame.display.flip()
    time.sleep(3)
    pygame.quit()
    sys.exit()

# Score
def show_score(game, choice, color, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(game.score), True, color)
    score_rect = score_surface.get_rect()
    if choice == 1:
        score_rect.midtop = (FRAME_SIZE_X/8, 15)
    else:
        score_rect.midtop = (FRAME_SIZE_X/2, FRAME_SIZE_Y/1.25)
    game_window.blit(score_surface, score_rect)
    # pygame.display.flip()

# Move the snake via keyboard
def move_keyboard(game, event):
    change_to = game.direction
    if event.type == pygame.KEYDOWN:
        # W -> Up; S -> Down; A -> Left; D -> Right
        if (event.key == pygame.K_UP or event.key == ord('w')) and game.direction != 'DOWN':
            change_to = 'UP'
        if (event.key == pygame.K_DOWN or event.key == ord('s')) and game.direction != 'UP':
            change_to = 'DOWN'
        if (event.key == pygame.K_LEFT or event.key == ord('a')) and game.direction != 'RIGHT':
            change_to = 'LEFT'
        if (event.key == pygame.K_RIGHT or event.key == ord('d')) and game.direction != 'LEFT':
            change_to = 'RIGHT'
    return change_to

# Checks if the next move is safe
def is_safe_move(game, x, y):
    # Check bounds.
    if x < 0 or x >= FRAME_SIZE_X or y < 0 or y >= FRAME_SIZE_Y:
        return False
    # Avoid collision with the snake’s body except the tail (since it will move).
    if [x, y] in game.snake_body[:-1]:
        return False
    return True

# Using BFS to find the best path and avoid self-traps.
def bfs_path(game, start, target):

    # Returns the first move (as a string) on a valid path from start to target using BFS.
    directions = {
        "UP": (0, -10), #UP
        "DOWN": (0, 10), #Down
        "LEFT": (-10, 0), # Left
        "RIGHT": (10, 0) # Right
    }
    queue = deque([(start, [])])
    visited = set()
    visited.add(tuple(start))

    while queue:
        (current_x, current_y), path = queue.popleft()
        if [current_x, current_y] == target and path:
            return path[0]
        for move, (dx, dy) in directions.items():
            next_x, next_y = current_x + dx, current_y + dy
            if is_safe_move(game, next_x, next_y) and (next_x, next_y) not in visited:
                queue.append(([next_x, next_y], path + [move]))
                visited.add((next_x, next_y))
    return None  # No valid path found.

def fruit_inside_snake(game):
    # Returns True if the fruit is spawning inside the snake's body.
    return game.food_pos in game.snake_body

def find_safe_location(game):

    # When the fruit spawns inside the snake's body (causing oscillation),
    # this function computes a target on a far wall (relative to the snake's current direction)
    # and returns a safe move toward that target using BFS.

    snake_x, snake_y = game.snake_pos

    # Determine target based on current movement direction.
    if game.direction in ('UP', 'DOWN'):
        # For vertical movement, choose a horizontal target.
        left_distance = snake_x  # Distance to left wall (x=0)
        right_distance = FRAME_SIZE_X - snake_x - 10  # Distance to right wall
        if right_distance > left_distance:
            target = [FRAME_SIZE_X - 10, snake_y]
        else:
            target = [0, snake_y]
    elif game.direction in ('LEFT', 'RIGHT'):
        # For horizontal movement, choose a vertical target.
        top_distance = snake_y  # Distance to top (y=0)
        bottom_distance = FRAME_SIZE_Y - snake_y - 10  # Distance to bottom
        if bottom_distance > top_distance:
            target = [snake_x, FRAME_SIZE_Y - 10]
        else:
            target = [snake_x, 0]
    else:
        target = [FRAME_SIZE_X - 10, snake_y]  # Default

    move = bfs_path(game, [snake_x, snake_y], target)
    if move is not None:
        return move


def move_tutorial_1(game):
    # Using BFS to find the best path and avoid self-traps.
    snake_x, snake_y = game.snake_pos
    food_x, food_y = game.food_pos

    best_move = bfs_path(game, [snake_x, snake_y], [food_x, food_y])

    if best_move is None:
        # If the fruit spawned inside the snake's body, use the safe location method.
        if fruit_inside_snake(game):
            return find_safe_location(game)

        # Otherwise, choose any safe move.
        possible_moves = {
            'UP':    (snake_x, snake_y - 10),
            'DOWN':  (snake_x, snake_y + 10),
            'LEFT':  (snake_x - 10, snake_y),
            'RIGHT': (snake_x + 10, snake_y)
        }
        for move, (new_x, new_y) in possible_moves.items():
            if is_safe_move(game, new_x, new_y):
                return move

        # If no safe moves are available, continue in the current direction.
        return game.direction

    # If a BFS path is found, follow it.
    return best_move

def is_valid_move(curr, new):
    if curr == "UP" and new == "DOWN":
        return False
    if curr == "DOWN" and new == "UP":
        return False
    if curr == "LEFT" and new == "RIGHT":
        return False
    if curr == "RIGHT" and new == "LEFT":
        return False
    return True

# PRINTING DATA FROM GAME STATE
def print_state(game):
    print("--------GAME STATE--------")
    print("FrameSize:", FRAME_SIZE_X, FRAME_SIZE_Y)
    print("Direction:", game.direction)
    print("Snake X:", game.snake_pos[0], ", Snake Y:", game.snake_pos[1])
    print("Snake Body:", game.snake_body)
    print("Food X:", game.food_pos[0], ", Food Y:", game.food_pos[1])
    print("Score:", game.score)

# TODO: IMPLEMENT HERE THE NEW INTELLIGENT METHOD
def print_line_data(game):
    if game.direction == "UP":
        numeric_direction = 0
    elif game.direction == "DOWN":
        numeric_direction = 1
    elif game.direction == "LEFT":
        numeric_direction = 2
    else:
        numeric_direction = 3

    snake_x, snake_y = game.snake_pos
    fruit_x, fruit_y = game.food_pos

    # Compute deltas and distance
    delta_x = fruit_x - snake_x
    delta_y = fruit_y - snake_y
    distance = math.sqrt(delta_x ** 2 + delta_y ** 2)

    isSafeUp = is_safe_move(game, snake_x, snake_y - 10)
    isSafeRight = is_safe_move(game, snake_x + 10, snake_y)
    isSafeDown = is_safe_move(game, snake_x, snake_y + 10)
    isSafeLeft = is_safe_move(game, snake_x - 10, snake_y)

    data = [
        snake_x,
        snake_y,
        fruit_x,
        fruit_y,
        len(game.snake_body),
        delta_x,
        delta_y,
        distance,
        # isSafeUp,
        # isSafeDown,
        # isSafeLeft,
        # isSafeRight,
        numeric_direction
    ]

    return ",".join(map(str,data))

def print_line_data2(game, next_score):
    snake_x, snake_y = game.snake_pos
    fruit_x, fruit_y = game.food_pos

    # Compute deltas and distance
    delta_x = fruit_x - snake_x
    delta_y = fruit_y - snake_y
    distance = math.sqrt(delta_x ** 2 + delta_y ** 2)

    data = [
        distance,
        len(game.snake_body),
        game.score,
        game.ticks_since_last_fruit,
        next_score
    ]

    return ",".join(map(str,data))

# Checks for errors encountered
check_errors = pygame.init()
if check_errors[1] > 0:
    print(f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
    sys.exit(-1)
else:
    print('[+] Game successfully initialised')

# Initialise game window
pygame.display.set_caption('Snake Eater - Machine Learning (UC3M)')
game_window = pygame.display.set_mode((FRAME_SIZE_X, FRAME_SIZE_Y))

# FPS (frames per second) controller
fps_controller = pygame.time.Clock()

weka = Weka()
weka.start_jvm()


prev_game_state = None
# Main logic
game = GameState((FRAME_SIZE_X, FRAME_SIZE_Y))
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            # Esc -> Create event to quit the game
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
        # CALLING MOVE METHOD
        game.direction = move_keyboard(game, event)


    prev_game_state = GameState((FRAME_SIZE_X, FRAME_SIZE_Y))
    prev_game_state.snake_pos = game.snake_pos.copy()
    prev_game_state.food_pos = game.food_pos.copy()
    prev_game_state.snake_body = game.snake_body.copy()
    prev_game_state.direction = game.direction
    prev_game_state.score = game.score
    prev_game_state.ticks_since_last_fruit = game.ticks_since_last_fruit

    # UNCOMMENT WHEN METHOD IS IMPLEMENTED
    game.direction = move_tutorial_1(game)

    if game.direction == "UP":
        nominal = 0
    elif game.direction == "DOWN":
        nominal = 1
    elif game.direction == "LEFT":
        nominal = 2
    else:
        nominal = 3

    snake_x, snake_y = game.snake_pos
    fruit_x, fruit_y = game.food_pos

    # Compute deltas and distance
    delta_x = fruit_x - snake_x
    delta_y = fruit_y - snake_y
    distance = math.sqrt(delta_x ** 2 + delta_y ** 2)

    # isSafeUp = is_safe_move(game, snake_x, snake_y - 10)
    # isSafeRight = is_safe_move(game, snake_x + 10, snake_y)
    # isSafeDown = is_safe_move(game, snake_x, snake_y + 10)
    # isSafeLeft = is_safe_move(game, snake_x - 10, snake_y)

    x = [
    snake_x,
        snake_y,
        fruit_x,
        fruit_y,
        len(game.snake_body),
        delta_x,
        delta_y,
        distance,
        # str(isSafeUp),
        # str(isSafeDown),
        # str(isSafeLeft),
        # str(isSafeRight)
    ]


    predicted_action = weka.predict("./multimore.model", x, "./training_keyboard.arff")

    if is_valid_move(game.direction, predicted_action):
        game.direction = predicted_action




    # Record the move to help detect oscillation.
    game.move_history.append(game.direction)
    if len(game.move_history) > 10:
        game.move_history = game.move_history[-10:]

    # Moving the snake (THIS CAUSES ISSUES !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!)
    if game.direction == '0':
        game.snake_pos[1] -= 10
    if game.direction == '1':
        game.snake_pos[1] += 10
    if game.direction == '2':
        game.snake_pos[0] -= 10
    if game.direction == '3':
        game.snake_pos[0] += 10

    # Snake body growing mechanism
    game.snake_body.insert(0, list(game.snake_pos))
    if game.snake_pos[0] == game.food_pos[0] and game.snake_pos[1] == game.food_pos[1]:
        game.score += 100
        game.food_spawn = False
        game.ticks_since_last_fruit = 0
    else:
        game.snake_body.pop()
        game.score -= 1
        game.ticks_since_last_fruit += 1

    # Spawning food on the screen
    if not game.food_spawn:
        game.food_pos = [random.randrange(1, (FRAME_SIZE_X//10)) * 10,
                         random.randrange(1, (FRAME_SIZE_Y//10)) * 10]
    game.food_spawn = True

    # if prev_game_state:
    #     line_data = print_line_data2(prev_game_state, game.score)
    #     with open("test_phase4.arff", "a") as logfile:
    #         logfile.write(line_data + "\n")

    # GFX
    game_window.fill(BLUE)
    for pos in game.snake_body:
        pygame.draw.rect(game_window, GREEN, pygame.Rect(pos[0], pos[1], 10, 10))

    pygame.draw.rect(game_window, RED, pygame.Rect(game.food_pos[0], game.food_pos[1], 10, 10))

    # Game Over conditions
    if game.snake_pos[0] < 0 or game.snake_pos[0] > FRAME_SIZE_X-10:
        game_over(game)
    if game.snake_pos[1] < 0 or game.snake_pos[1] > FRAME_SIZE_Y-10:
        game_over(game)
    for block in game.snake_body[1:]:
        if game.snake_pos[0] == block[0] and game.snake_pos[1] == block[1]:
            game_over(game)

    show_score(game, 1, WHITE, 'consolas', 15)
    pygame.display.update()

    # Logging data to training arff file
    # line_data = print_line_data(game)
    # with open ("test_keyboard.arff", "a") as logfile:
    #     logfile.write(line_data + "\n")

    # Logging data to test arff file
    # line_data = print_line_data(game)
    # with open ("test_1.arff", "a") as logfile:
    #     logfile.write(line_data + "\n")

    # manual1_data = print_line_data_manual1(game)
    # with open ("filter_data_snake_manual1.arff", "a") as logfile:
    #     logfile.write(manual1_data + "\n")

    # manual2_data = print_line_data_manual2(game)
    # with open ("filter_data_snake_manual2.arff", "a") as logfile:
    #     logfile.write(manual2_data + "\n")

    if game.is_new_game:
        game.is_new_game = False

    fps_controller.tick(DIFFICULTY)
    print_state(game)
