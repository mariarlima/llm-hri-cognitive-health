import socketio
import os
import json
import dotenv
import logging
import Config.logging_config as logging_config
from ..blossom_interaction import BlossomInterface

logger = logging.getLogger("HRI")
logging_config.configure_logger(logger)
logger.info("Client Started.")

example_data = {
    "function": "do_start_sequence",
    "kwargs": {
        "delay_time": 0.5,
        "audio_length": 20,
        "seq": "reset"
    }
}


class BlossomClient:
    def __init__(self, server_ip, server_port):
        self.bl = BlossomInterface()
        self.sio = socketio.Client()
        self.sio.connect(f"http://{server_ip}:{server_port}")
        self.sio.on('data_update', self.on_data_update)
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)

    def on_data_update(self, data):
        logger.info(f"Received data: {json.dumps(data, indent=2)}")
        if data["function"] == "do_start_sequence":
            self.bl.do_start_sequence(data["kwargs"]["delay_time"])
        elif data["function"] == "do_prompt_sequence":
            self.bl.do_prompt_sequence(data["kwargs"]["delay_time"])
        elif data["function"] == "do_prompt_sequence_matching":
            self.bl.do_prompt_sequence_matching(data["kwargs"]["delay_time"], data["kwargs"]["audio_length"])
        elif data["function"] == "do_end_sequence":
            self.bl.do_end_sequence(data["kwargs"]["delay_time"])
        elif data["function"] == "do_idle_sequence":
            self.bl.do_idle_sequence(data["kwargs"]["delay_time"])
        elif data["function"] == "do_sequence":
            self.bl.do_sequence(data["kwargs"]["seq"], data["kwargs"]["delay_time"])
        elif data["function"] == "reset":
            self.bl.reset()
        else:
            logger.error(f"Function {data['function']} not found.")

    def wait(self):
        self.sio.wait()

    def on_connect(self):
        logger.info("Connected to server.")

    def on_disconnect(self):
        logger.info("Disconnected from server.")


if __name__ == '__main__':
    dotenv.load_dotenv()
    client = BlossomClient(os.getenv("SERVER_IP"), os.getenv("SERVER_PORT"))
    client.wait()
