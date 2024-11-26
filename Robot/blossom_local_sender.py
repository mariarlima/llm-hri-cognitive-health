import logging
import dotenv
import requests
import os
import json

logger = logging.getLogger("HRI")


class BlossomLocalSender:
    def __init__(self):
        dotenv.load_dotenv()
        self.server_ip = os.getenv("SERVER_IP")
        self.server_port = os.getenv("SERVER_PORT")

        self.url = f"http://{self.server_ip}:{self.server_port}/data"
        self.data = {
            "function": "do_start_sequence",
            "kwargs": {
                "delay_time": 0.5,
                "audio_length": 20,
                "seq": "reset"
            }
        }

    def do_idle_sequence(self, delay_time=0):
        self.data["function"] = "do_idle_sequence"
        self.data["kwargs"]["delay_time"] = delay_time
        response = requests.post(self.url, json=self.data)
        logger.info(f"Sending data to server: {json.dumps(self.data, indent=2)}")
        logger.info(f"Response from server: {response.text}")

    def do_start_sequence(self, delay_time=0):
        self.data["function"] = "do_start_sequence"
        self.data["kwargs"]["delay_time"] = delay_time
        response = requests.post(self.url, json=self.data)
        logger.info(f"Sending data to server: {json.dumps(self.data, indent=2)}")
        logger.info(f"Response from server: {response.text}")

    def do_prompt_sequence(self, delay_time=0):
        self.data["function"] = "do_prompt_sequence"
        self.data["kwargs"]["delay_time"] = delay_time
        response = requests.post(self.url, json=self.data)
        logger.info(f"Sending data to server: {json.dumps(self.data, indent=2)}")
        logger.info(f"Response from server: {response.text}")

    def do_prompt_sequence_matching(self, delay_time=0, audio_length=0):
        self.data["function"] = "do_prompt_sequence_matching"
        self.data["kwargs"]["delay_time"] = delay_time
        self.data["kwargs"]["audio_length"] = audio_length
        response = requests.post(self.url, json=self.data)
        logger.info(f"Sending data to server: {json.dumps(self.data, indent=2)}")
        logger.info(f"Response from server: {response.text}")

    def do_end_sequence(self, delay_time=0):
        self.data["function"] = "do_end_sequence"
        self.data["kwargs"]["delay_time"] = delay_time
        response = requests.post(self.url, json=self.data)
        logger.info(f"Sending data to server: {json.dumps(self.data, indent=2)}")
        logger.info(f"Response from server: {response.text}")

    def do_sequence(self, seq, delay_time=0):
        self.data["function"] = "do_sequence"
        self.data["kwargs"]["seq"] = seq
        self.data["kwargs"]["delay_time"] = delay_time
        response = requests.post(self.url, json=self.data)
        logger.info(f"Sending data to server: {json.dumps(self.data, indent=2)}")
        logger.info(f"Response from server: {response.text}")

    def reset(self):
        self.data["function"] = "reset"
        response = requests.post(self.url, json=self.data)
        logger.info(f"Sending data to server: {json.dumps(self.data, indent=2)}")
        logger.info(f"Response from server: {response.text}")

# bls = BlossomLocalSender()
# # bls.do_sequence("reset")
# # input()
# bls.do_prompt_sequence_matching(0.5, 20)
