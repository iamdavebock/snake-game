import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO
from game import SnakeGame

app = Flask(__name__)
app.config["SECRET_KEY"] = "snake-secret-key"
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")

game = SnakeGame()


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("move")
def handle_move(data):
    game.set_direction(data.get("direction", ""))


@socketio.on("restart")
def handle_restart():
    game.reset()


def game_loop():
    while True:
        eventlet.sleep(0.15)
        game.tick()
        socketio.emit("game_state", game.get_state())


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5050))
    socketio.start_background_task(game_loop)
    socketio.run(app, host="0.0.0.0", port=port)
