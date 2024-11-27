from flask import Flask, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/data', methods=['POST'])
def receive_data():
    """
    Receive sequence information from blossom network controller and pass it to Raspberry Pi.
    """
    data = request.json
    print(f"Received data: {data}")
    socketio.emit('data_update', data)
    return "Data received", 200


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
