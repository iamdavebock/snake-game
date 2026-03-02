# Snake Game

A classic Snake game with a twist: the game logic runs entirely server-side in Python, with the browser acting as a pure renderer. Real-time state is streamed to the client over WebSockets using Flask-SocketIO.

```
  ╔══════════════════════════════╗
  ║  Score: 120                  ║
  ║                              ║
  ║        ●●●●                  ║
  ║           ●                  ║
  ║           ●                  ║
  ║           ◎  ★               ║
  ║                              ║
  ║                              ║
  ╚══════════════════════════════╝
  ● = body   ◎ = head   ★ = food
```

---

## How It Works

```
  Browser (HTML5 Canvas)
       │  Arrow keys / R key
       │──── WebSocket "move" / "restart" ────▶  Flask-SocketIO
       │                                               │
       │◀─── WebSocket "game_state" (15 fps) ─────── game_loop()
       │                                          eventlet background task
       │                                               │
       │                                         SnakeGame.tick()
       │                                         (Python game logic)
```

The game loop runs as an eventlet background task, calling `tick()` every 150 ms and broadcasting the full game state to all connected clients. The browser never calculates game logic — it only receives state and draws it on a Canvas.

---

## Features

- Server-side game logic — browser is a pure renderer
- Real-time WebSocket communication at ~15 fps
- 20x20 grid with wall and self-collision detection
- 180-degree reversal prevention
- Food placed randomly on unoccupied cells
- Score tracker (+10 per food)
- Instant restart without page reload
- Dark theme UI

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | Flask |
| WebSocket server | Flask-SocketIO + eventlet |
| Game logic | Pure Python (no dependencies) |
| Frontend rendering | HTML5 Canvas + vanilla JS |
| WebSocket client | Socket.IO JS client |
| Styling | CSS (dark theme) |

---

## Quick Start

**Requirements:** Python 3.8+

```bash
git clone https://github.com/iamdavebock/snake-game.git
cd snake-game
pip install -r requirements.txt
python app.py
```

Visit [http://localhost:5050](http://localhost:5050).

---

## Controls

| Key | Action |
|---|---|
| Arrow Up | Move up |
| Arrow Down | Move down |
| Arrow Left | Move left |
| Arrow Right | Move right |
| R | Restart after game over |

---

## Project Structure

```
snake-game/
├── app.py              # Flask app, SocketIO event handlers, game loop
├── game.py             # SnakeGame class — all game logic, zero dependencies
├── requirements.txt    # flask, flask-socketio, eventlet
├── templates/
│   └── index.html      # HTML5 Canvas + Socket.IO client rendering
├── static/
│   └── style.css       # Dark theme styles
├── docs/
│   ├── architecture.md # Deep dive: server loop, WebSocket events, rendering
│   └── game-logic.md   # Deep dive: SnakeGame class internals
└── LICENSE
```

| File | Purpose |
|---|---|
| `app.py` | Entry point. Wires Flask, SocketIO, and the background game loop. Handles `move` and `restart` events. |
| `game.py` | Self-contained `SnakeGame` class. No Flask or socket knowledge — pure game state machine. |
| `templates/index.html` | Single-page client. Connects via Socket.IO, listens for `game_state`, draws to Canvas. |
| `static/style.css` | Dark background, centred layout, score display. |

---

## Deployment

### Local

```bash
python app.py
# Runs on 0.0.0.0:5050
```

### Railway (recommended for quick deploys)

1. Push to GitHub (already done)
2. Create a new project at [railway.app](https://railway.app)
3. Connect your GitHub repo
4. Railway auto-detects Python — add a `Procfile` if needed:

```
web: python app.py
```

5. Set the `PORT` environment variable if Railway requires it (update `app.py` to read `os.environ.get("PORT", 5050)`)

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

```bash
docker build -t snake-game .
docker run -p 5050:5050 snake-game
```

---

## Documentation

- [Architecture](docs/architecture.md) — server loop, WebSocket events, rendering pipeline
- [Game Logic](docs/game-logic.md) — SnakeGame class, collision, food placement, state representation

---

## Contributing

Pull requests welcome. Keep game logic in `game.py` (no Flask imports), keep rendering in `index.html` (no game logic). This separation is intentional — see [Architecture](docs/architecture.md).

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-thing`)
3. Commit your changes
4. Open a pull request

---

## License

MIT — see [LICENSE](LICENSE).
