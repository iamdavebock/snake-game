# Architecture

Snake Game uses a server-side game loop pattern: all game state lives in Python, and the browser is a stateless renderer that receives and displays state over WebSockets.

---

## Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Browser                                                    │
│                                                             │
│  index.html                                                 │
│  ┌──────────────┐    ┌──────────────────────────────────┐  │
│  │ Socket.IO    │    │ HTML5 Canvas                     │  │
│  │ client       │    │                                  │  │
│  │              │    │  drawGrid(state)                 │  │
│  │ on("game_    │───▶│  - body cells (grey)             │  │
│  │   state")    │    │  - head cell (bright)            │  │
│  │              │    │  - food cell (red)               │  │
│  │ emit("move") │    └──────────────────────────────────┘  │
│  │ emit("        │                                          │
│  │   restart")  │                                          │
│  └──────┬───────┘                                          │
│         │ WebSocket                                         │
└─────────┼───────────────────────────────────────────────────┘
          │
          │  ws://host:5050
          │
┌─────────┼───────────────────────────────────────────────────┐
│  Server │                                                   │
│         ▼                                                   │
│  ┌──────────────────┐                                       │
│  │  Flask-SocketIO  │                                       │
│  │                  │                                       │
│  │  @on("move")     │──▶ game.set_direction(d)             │
│  │  @on("restart")  │──▶ game.reset()                      │
│  │                  │                                       │
│  │  emit("game_     │◀── game_loop() broadcasts state      │
│  │   state", ...)   │                                       │
│  └────────┬─────────┘                                       │
│           │                                                 │
│  ┌────────▼─────────┐    ┌───────────────┐                 │
│  │  game_loop()     │    │  SnakeGame    │                 │
│  │  eventlet bg     │───▶│               │                 │
│  │  task            │    │  .tick()      │                 │
│  │  sleep(0.15s)    │    │  .get_state() │                 │
│  └──────────────────┘    └───────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

---

## The Server-Side Game Loop

`app.py` starts a background task using eventlet before accepting connections:

```python
def game_loop():
    while True:
        eventlet.sleep(0.15)   # ~15 fps tick rate
        game.tick()            # advance game state one step
        socketio.emit("game_state", game.get_state())  # broadcast to all clients
```

This runs in an eventlet greenthread — a lightweight cooperative coroutine. Because eventlet has monkey-patched the standard library, `eventlet.sleep` yields control back to the event loop between ticks, allowing WebSocket I/O to proceed concurrently without threads.

Key characteristics:
- The loop is unconditional — it broadcasts state every 150 ms regardless of whether any clients are connected
- A single `game` instance is shared across all connections (all viewers see the same game)
- `game.tick()` is a no-op when `game.alive == False`, so the loop is safe to run while the game is over

---

## WebSocket Events

### Client → Server

| Event | Payload | Handler |
|---|---|---|
| `move` | `{ "direction": "UP" \| "DOWN" \| "LEFT" \| "RIGHT" }` | `game.set_direction(d)` |
| `restart` | (none) | `game.reset()` |

Direction changes take effect on the next `tick()` call. The game enforces 180-degree reversal prevention server-side — the client cannot force an illegal move.

### Server → Client

| Event | Payload | Rate |
|---|---|---|
| `game_state` | See state structure below | Every 150 ms |

The server always emits to all clients (no rooms). This is intentional — the game is shared and spectatable by multiple browser tabs simultaneously.

---

## Game State Structure

`SnakeGame.get_state()` returns:

```python
{
    "snake": [[10, 10], [10, 11], [10, 12]],  # list of [x, y] from head to tail
    "food":  [5, 7],                           # [x, y] or None if grid full
    "score": 120,                              # integer, +10 per food
    "alive": True,                             # False = game over
    "grid":  [[0, 0, ...], ...]               # 20x20 array, row-major
}
```

The `grid` array encodes cell types numerically:

| Value | Meaning |
|---|---|
| `0` | Empty |
| `1` | Snake body |
| `2` | Snake head |
| `3` | Food |

The grid is derived fresh from `snake` and `food` on every call — it is not stored as internal state. This ensures the grid is always consistent and simplifies the rendering path.

---

## Canvas Rendering Approach

`index.html` receives `game_state` events and redraws the entire Canvas on every frame:

```
socket.on("game_state", (state) => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    for each row in state.grid:
        for each cell in row:
            pick colour based on cell value (0/1/2/3)
            ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize)
    update score display
    if not state.alive: show game over overlay
})
```

The full grid is redrawn every frame rather than diffing changed cells. At 20x20 = 400 cells this is trivially fast, and it keeps the rendering code simple and stateless.

---

## Why This Architecture?

### Versus pure client-side JavaScript

A conventional Snake game runs entirely in the browser. This project deliberately inverts that to demonstrate:

- **Server-authoritative state** — the server is the source of truth. Clients cannot cheat by modifying game state locally.
- **Multi-client observation** — any number of browser tabs can watch the same game instance simultaneously.
- **WebSocket event model** — clean separation between input events (client → server) and state broadcasts (server → all clients).

The tradeoff is latency sensitivity. A 150 ms tick rate masks typical LAN/localhost latency well, but over high-latency connections controls may feel sluggish. For a production game, client-side prediction would be added.

### Versus Pygame / WASM

Running Python game logic natively in the browser via WebAssembly is possible but adds significant complexity (Pyodide, build tooling, large bundle sizes). The WebSocket approach keeps the server stack familiar (plain Python) and the client stack minimal (no build step, no framework).

### Versus a REST API

Polling a REST endpoint for game state would require the client to request updates. At 15 fps that is 15 HTTP requests per second per client — wasteful and higher latency than a persistent WebSocket connection. The push model used here is the correct choice for real-time game state.
