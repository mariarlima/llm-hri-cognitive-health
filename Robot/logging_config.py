# https://stackoverflow.com/questions/22612913/python3-pycharm-debug-logging-levels-in-run-debug
import logging
import datetime

def configure_logger(logger):
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(f'Robot/log/{datetime.datetime.now().isoformat().replace(":", "-")}.log',
                                       encoding='utf-8')
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

# logger = logging.getLogger(__name__)
