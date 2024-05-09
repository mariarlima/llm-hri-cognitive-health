# https://stackoverflow.com/questions/22612913/python3-pycharm-debug-logging-levels-in-run-debug
import logging
import datetime


def configure_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)8.8s] %(message)s",
        handlers=[logging.StreamHandler(),
                  logging.FileHandler(f'log/{datetime.datetime.now().isoformat().replace(":", "-")}.log',
                                      encoding='utf-8')],
    )
# logger = logging.getLogger(__name__)
