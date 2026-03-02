# Game Logic

`game.py` contains the `SnakeGame` class — a self-contained state machine with no Flask, SocketIO, or rendering dependencies. It is designed to be testable and reusable independently of the web layer.

---

## SnakeGame Class Overview

```python
class SnakeGame:
    def __init__(self): self.reset()
    def reset(self)          # initialise/restart game state
    def set_direction(d)     # queue a direction change
    def tick(self)           # advance game one step
    def _place_food(self)    # find a random empty cell for food
    def get_state(self)      # return serialisable snapshot of current state
```

Internal state fields after `reset()`:

| Field | Type | Description |
|---|---|---|
| `self.snake` | `list[list[int, int]]` | Ordered list of `[x, y]` cells, head first |
| `self.direction` | `str` | Current direction: `"UP"`, `"DOWN"`, `"LEFT"`, `"RIGHT"` |
| `self.score` | `int` | Current score |
| `self.alive` | `bool` | `False` after a collision |
| `self.food` | `list[int, int]` or `None` | Current food position |

---

## Grid Coordinate System

The grid is 20x20 (`GRID_SIZE = 20`). Coordinates are `[x, y]` where:

```
  (0,0) ──────────────▶ x  (19,0)
    │
    │
    │
    ▼
  y
  (0,19)                  (19,19)
```

- `x` increases to the right
- `y` increases downward
- `UP` means decrementing `y`
- `DOWN` means incrementing `y`

This matches screen/canvas coordinate conventions where the origin is top-left.

Direction vectors defined in `DIRECTIONS`:

```python
DIRECTIONS = {
    "UP":    (0, -1),
    "DOWN":  (0,  1),
    "LEFT":  (-1, 0),
    "RIGHT": (1,  0),
}
```

---

## Direction Handling and 180-Degree Reversal Prevention

`set_direction()` is called when the browser sends a `move` event. It validates the requested direction and ignores it if it would reverse the snake into itself:

```python
OPPOSITES = {
    "UP": "DOWN",
    "DOWN": "UP",
    "LEFT": "RIGHT",
    "RIGHT": "LEFT",
}

def set_direction(self, d):
    d = d.upper()
    if d not in DIRECTIONS:       # ignore unknown directions
        return
    if d == OPPOSITES.get(self.direction):  # ignore 180-degree reversal
        return
    self.direction = d
```

For example, if the snake is moving `RIGHT`, a `LEFT` input is silently discarded. The snake continues `RIGHT` until a valid direction is given.

This check happens at input time, not at tick time, which means rapid inputs between ticks cannot cause a reversal via buffering. Only the last valid direction before a tick fires takes effect.

---

## Collision Detection

`tick()` advances the game one step. Collision checks happen before any state mutation:

### Wall Collision

```python
if not (0 <= new_head[0] < GRID_SIZE and 0 <= new_head[1] < GRID_SIZE):
    self.alive = False
    return
```

The new head position is checked against grid boundaries. Any out-of-bounds coordinate ends the game immediately.

### Self Collision

```python
if new_head in self.snake:
    self.alive = False
    return
```

The new head is checked against every cell in `self.snake` (including the current tail). This uses Python's `in` operator on a list, which is O(n) where n is the snake length.

Note: at the point of the self-collision check, the tail has not yet been removed. This means the snake cannot legally move into the cell its tail currently occupies — even though that cell will be vacated this tick. This is standard Snake behaviour and prevents a class of edge-case bugs near the tail.

---

## Movement and Growth

If both collision checks pass, the snake moves:

```python
self.snake.insert(0, new_head)      # prepend new head
if new_head == self.food:
    self.score += 10
    self._place_food()              # grow: tail NOT removed
else:
    self.snake.pop()                # no food: remove tail (net length unchanged)
```

The "grow by eating" mechanism is elegant: the snake always gains a head cell, but only loses its tail cell when food is not eaten. Eating food simply skips the `pop()`.

---

## Food Placement Algorithm

```python
def _place_food(self):
    occupied = set(map(tuple, self.snake))
    empty = [[x, y] for x in range(GRID_SIZE) for y in range(GRID_SIZE)
             if (x, y) not in occupied]
    if empty:
        self.food = random.choice(empty)
    else:
        self.food = None
```

Steps:
1. Convert `self.snake` (list of lists) to a set of tuples for O(1) membership testing
2. Build the list of all 400 grid cells that are not occupied by the snake
3. Choose one at random with `random.choice`
4. If no empty cell exists (snake fills entire grid), `self.food` is set to `None`

The `None` food state is handled gracefully throughout: `get_state()` skips placing food in the grid, and `tick()` will never match `new_head == self.food` when food is `None`.

---

## State Representation

`get_state()` returns a snapshot suitable for JSON serialisation:

```python
def get_state(self):
    grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    for i, (x, y) in enumerate(self.snake):
        if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
            grid[y][x] = 2 if i == 0 else 1   # head = 2, body = 1
    if self.food:
        fx, fy = self.food
        grid[fy][fx] = 3
    return {
        "snake": self.snake,
        "food": self.food,
        "score": self.score,
        "alive": self.alive,
        "grid": grid,
    }
```

The `grid` is a 20x20 2D array indexed `grid[y][x]` (row-major, y-first). Cell values:

| Value | Cell type |
|---|---|
| `0` | Empty |
| `1` | Snake body |
| `2` | Snake head (index 0 in `self.snake`) |
| `3` | Food |

The grid is reconstructed on every call — it is not stored as internal state. This keeps `reset()`, `tick()`, and `set_direction()` simple (they only modify `self.snake`, `self.direction`, `self.score`, `self.alive`, and `self.food`), and guarantees the emitted grid is always consistent with the canonical snake list.

The `snake` list is included alongside `grid` so the client has access to ordered segment positions if needed (e.g. for animating the head differently from the body, or computing movement direction per segment).

---

## Score System

- Score starts at `0` on `reset()`
- Each food item eaten adds `10` points
- Score is never decremented
- Score is included in every `get_state()` emission so the client always has the current value without needing to track it locally
