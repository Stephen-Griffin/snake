# Snake (Q-Learning)

This project trains a Snake agent with tabular Q-learning using a compact, bit-encoded state. The active Q-learning implementation lives in `practice-2/phase two` and `practice-2/phase three` (phase three adds more state features and has a larger Q-table).

**Project Iterations (Phase 1 → Phase 2 → Phase 3)**  
- **Phase 1** (`practice-1`): Early iteration used to collect training/test data and experiment with models (Weka + ARFF datasets). It is not the final approach, but it informed later phases.  
- **Phase 2** (`practice-2/phase two`): First Q-learning version with a smaller state space. This built on Phase 1 insights.  
- **Phase 3** (`practice-2/phase three`): Final and most important version. Expanded state features and larger Q-table. This is the version to run and tune.

**Quick Start**
1. Install dependencies:

```bash
pip install numpy pygame
```

2. Run the Q-learning Snake (phase three recommended):

```bash
cd "practice-2"
python "phase three/SnakeGame.py"
```

Notes:
- The script loads `practice-2/phase three/q_table.txt` if present. If not, it initializes a zero Q-table.
- By default, `training = False`, so the agent plays using the loaded table.

**Training vs. Playing**
To train instead of play, open `practice-2/phase three/SnakeGame.py` and set:
- `training = True`
- Optional: `render_game = False` to speed up training
- Optional: increase or decrease `num_episodes`

The Q-table is saved every episode via `QLearning.save_q_table()`.

**How The Model Works**
- The environment encodes the game into a discrete integer state (bit-packed features).
- The agent uses epsilon-greedy action selection.
- The Q-table is updated with the standard Q-learning update rule.
- Rewards are shaped to favor moving toward food, penalize danger, and strongly penalize crashes.
- Actions are mapped as `0=UP`, `1=DOWN`, `2=LEFT`, `3=RIGHT`.

**State Encoding (Why `number_states` = 2048 / 4096)**
- Phase two (`practice-2/phase two/snake_env.py`) encodes 11 bits total, so `number_states = 2^11 = 2048`.
- Phase three (`practice-2/phase three/snake_env.py`) adds `body_collision` and encodes 12 bits total, so `number_states = 2^12 = 4096`.

If you change the state encoding, you must also update `number_states` in the corresponding `SnakeGame.py` file and retrain.

**Key Files**
- `practice-2/phase three/SnakeGame.py`: Entry point for running/training the agent.
- `practice-2/phase three/q_learning.py`: Q-learning logic and Q-table persistence.
- `practice-2/phase three/snake_env.py`: Environment dynamics, reward shaping, and state encoding.
- `practice-2/phase three/q_table.txt`: Saved Q-table (policy).

Phase two mirrors the same structure inside `practice-2/phase two` with a smaller state space.

**Important Functions (excluding `SnakeGame.py`)**
- `QLearning.__init__` in `practice-2/phase three/q_learning.py`: Initializes hyperparameters and loads the Q-table.
- `QLearning.choose_action`: Epsilon-greedy action choice and epsilon decay per step.
- `QLearning.update_q_table`: Core Q-learning update rule; treats negative reward as terminal.
- `QLearning.save_q_table` / `QLearning.load_q_table`: Persist and restore the table from disk.
- `SnakeGameEnv.reset` in `practice-2/phase three/snake_env.py`: Resets game state and returns the initial encoded state.
- `SnakeGameEnv.step`: Advances the environment one action and returns `(next_state, reward, done)`.
- `SnakeGameEnv.get_state`: Builds the bit-packed state (danger flags, food direction, heading, distance bucket).
- `SnakeGameEnv.calculate_reward`: Reward shaping for food, crashes, distance-to-food, and wall danger.
- `SnakeGameEnv.check_game_over`: Collision and boundary checks.
- `SnakeGameEnv.update_snake_position` / `update_food_position`: Core movement and food spawning.

**Parameters You’ll Likely Change**
In `practice-2/phase three/SnakeGame.py`:
- `training`: `True` to train, `False` to play.
- `render_game`: Disable for faster training.
- `num_episodes`: Training length.
- `difficulty`: FPS cap (higher = faster).
- `FRAME_SIZE_X`, `FRAME_SIZE_Y`: Board size.
- `growing_body`: Whether the snake grows when it eats.
- `number_states`: Must match the state encoding bit count.

In `practice-2/phase three/q_learning.py`:
- `alpha`: Learning rate.
- `gamma`: Discount factor.
- `epsilon`: Initial exploration rate.
- `epsilon_min`: Floor for exploration.
- `epsilon_decay`: Multiplicative decay applied each action.

In `practice-2/phase three/snake_env.py`:
- Reward values in `calculate_reward` (food reward, crash penalty, distance shaping, wall danger penalty).
- State features in `get_state` (adding/removing bits changes the state space size).

**Phase Two vs Phase Three**
- Phase two uses fewer state features and a smaller Q-table (2048 states).
- Phase three adds `body_collision` and increases the state space (4096 states).

If you switch phases, run from `practice-2` and call the desired file:

```bash
cd "practice-2"
python "phase two/SnakeGame.py"
```

**Notes On The Weka Files**
The `practice-1` folder contains Weka models and ARFF datasets from earlier experiments. They are not used by the Q-learning Snake code.
