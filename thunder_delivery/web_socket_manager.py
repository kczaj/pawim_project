from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, leave_room, emit, send
from flask_cors import CORS, cross_origin

app = Flask(__name__, static_url_path="")
# cors = CORS(app)
socket_io = SocketIO(app, cors_allowed_origins="*")

USER_AGENT = "useragent"
ROOM_ID = "room_id"
MESSAGE = "message"


@app.route("/")
def index():
    return "Hello World!"


@socket_io.on("connect")
def handle_on_connect():
    app.logger.debug("Connected -> OK")
    emit("connection response", {"data": "Correctly connected"})


@socket_io.on("disconnect")
def handle_on_disconnect():
    app.logger.debug("Disconnected -> Bye")


@socket_io.on("join")
def handle_on_join(data):
    useragent = data[USER_AGENT]
    room_id = data[ROOM_ID]
    join_room(room_id)
    emit("joined_room", {"room_id": room_id})
    app.logger.debug("Useragent: %s added to the room: %s" %
                     (useragent, room_id))


@socket_io.on("leave")
def handle_on_leave(data):
    useragent = data[USER_AGENT]
    room_id = data[ROOM_ID]
    leave_room(room_id)
    emit("left_room", {"room_id": room_id})
    app.logger.debug("Useragent: %s is no longer in the room: %s" %
                     (useragent, room_id))


@socket_io.on("change_state")
def handle_new_message(data):
    app.logger.debug(f"Received data: {data}.")
    emit("change_state_message", {"state": data["state"], "id": data["id"]}, room=data[ROOM_ID])


@socket_io.on("package_remove")
def package_remove(data):
    app.logger.debug(f"Received data: {data}.")
    emit("change_package", {"state": data["state"], "id": data["id"]}, room=data[ROOM_ID])
