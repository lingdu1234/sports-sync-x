from app.coros.coros_client import CorosClient, get_coros_client
from app.garmin.garmin_client_x import get_garmin_client
from app.utils.const import SportPlatform
from app.utils.tools import format_datetime
import os
import unittest

from app.utils.fit_parser import get_device_from_fit
from app.utils.sys_config import SysConfig, cfg
from app.utils.msg_tool import send_message, MsgType
from datetime import datetime as dt, timedelta


class MyTestCase(unittest.TestCase):
    @staticmethod
    def test_config():
        print("COROS_EMAIL:", cfg.COROS_EMAIL)  # add assertion here
        print(cfg.GARMIN_EMAIL_COM)  # add assertion here
        print(cfg.GARMIN_NEWEST_NUM)
        print(cfg.COROS_EMAIL)
        print(cfg.GARMIN_FIT_DIR_COM)
        print(cfg.COROS_FIT_DIR)
        print(cfg.DB_DIR)

    # def test_send_message(self):
    #     resp = send_message("测试消息")
    @staticmethod
    def test_send_message2():
        resp = send_message(
            "##测试消息\n* 测试1\n* 测试2", msg_type=MsgType.MARKDOWN_V2
        )

    def test_get_device(self):
        fileList = ["470508240631791915.fit", "475389768654422119.fit"]
        xxx = fileList.__reversed__()
        print(f"xxx={xxx}")
        for file in xxx:
            fit_path = os.path.join(cfg.COROS_FIT_DIR, file)
            x = get_device_from_fit(fit_path)
            print("dddd = ", x)

    def test_time_format(self):
        x = format_datetime(dt.now())
        print(f"time:{x}")

    def test_delete_garmin_activity(self):
        cx = get_garmin_client(SportPlatform.garminCN)
        id = "234930494"
        cx.deleteActivity(id)

    def test_xx(self):
        xxx = [(1, 1), (3, 5)]

        for a, b in xxx:
            x = a == b

    def test_singleton(self):

        a1 = get_garmin_client(SportPlatform.garminCOM)
        a2 = get_garmin_client(SportPlatform.garminCOM)
        a3 = get_garmin_client(SportPlatform.garminCN)
        print(id(a1), id(a2), id(a3))
        print(id(a1) == id(a2))

    def test_singleton3(self):

        a1 = CorosClient(cfg.COROS_EMAIL, cfg.COROS_PASSWORD)
        a2 = CorosClient(cfg.COROS_EMAIL, cfg.COROS_PASSWORD)
        a3 = CorosClient(cfg.COROS_EMAIL, cfg.COROS_PASSWORD)

        print(id(a1), id(a2), id(a3))
        print(id(a1) == id(a2))

    def test_singleton2(self):

        a1 = SysConfig()
        a2 = SysConfig()
        a3 = cfg
        print(id(a1), id(a2), id(a3))
        print(id(a1) == id(a2))

    def test_aaa(self):
        st = dt.now()
        diff = int(cfg.SPORT_DIFF_SECOND)
        print(format_datetime(st - timedelta(seconds=diff)))
        print(format_datetime(st + timedelta(seconds=diff)))

    def test_delete_coros(self):
        cx = get_coros_client()
        cx.deleteActivity("475416904796766510")


if __name__ == "__main__":
    _ = unittest.main()
