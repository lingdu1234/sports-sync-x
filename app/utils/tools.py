import os
from datetime import datetime as dt
import logging

myLogger = logging.getLogger(__name__)


def check_path(path):
    if not os.path.exists(path):
        os.mkdir(path)


def format_datetime(data_time: dt):
    return data_time.strftime("%Y-%m-%d %H:%M:%S")
