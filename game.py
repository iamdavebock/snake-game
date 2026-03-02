import random

GRID_SIZE = 20

DIRECTIONS = {
    "UP":    (0, -1),
    "DOWN":  (0,  1),
    "LEFT":  (-1, 0),
    "RIGHT": (1,  0),
}

OPPOSITES = {
    "UP": "DOWN",
    "DOWN": "UP",
    "LEFT": "RIGHT",
    "RIGHT": "LEFT",
}


class SnakeGame:
    def __init__(self):
        self.reset()

    def reset(self):
        mid = GRID_SIZE // 2
        self.snake = [[mid, mid], [mid, mid + 1], [mid, mid + 2]]
        self.direction = "UP"
        self.score = 0
        self.alive = True
        self._place_food()

    def set_direction(self, d):
        d = d.upper()
        if d not in DIRECTIONS:
            return
        # Prevent 180-degree reversals
        if d == OPPOSITES.get(self.direction):
            return
        self.direction = d

    def tick(self):
        if not self.alive:
            return

        dx, dy = DIRECTIONS[self.direction]
        head = self.snake[0]
        new_head = [head[0] + dx, head[1] + dy]

        # Wall collision
        if not (0 <= new_head[0] < GRID_SIZE and 0 <= new_head[1] < GRID_SIZE):
            self.alive = False
            return

        # Self collision
        if new_head in self.snake:
            self.alive = False
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 10
            self._place_food()
        else:
            self.snake.pop()

    def _place_food(self):
        occupied = set(map(tuple, self.snake))
        empty = [
            [x, y]
            for x in range(GRID_SIZE)
            for y in range(GRID_SIZE)
            if (x, y) not in occupied
        ]
        if empty:
            self.food = random.choice(empty)
        else:
            self.food = None

    def get_state(self):
        grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        for i, (x, y) in enumerate(self.snake):
            if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                grid[y][x] = 2 if i == 0 else 1
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
