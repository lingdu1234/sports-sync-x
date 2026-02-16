import unittest

from app.utils.sys_config import sysConfig
from app.utils.msg_tool import send_message, MsgType


class MyTestCase(unittest.TestCase):
    @staticmethod
    def test_config():
        cfg = sysConfig
        print("COROS_EMAIL:", cfg.COROS_EMAIL)  # add assertion here
        print(cfg.GARMIN_EMAIL)  # add assertion here
        print(cfg.GARMIN_AUTH_DOMAIN)
        print(cfg.GARMIN_NEWEST_NUM)
        print(cfg.COROS_EMAIL)
        print(cfg.GARMIN_FIT_DIR)
        print(cfg.COROS_FIT_DIR)
        print(cfg.DB_DIR)

    # def test_send_message(self):
    #     resp = send_message("测试消息")
    @staticmethod
    def test_send_message2():
        resp = send_message(
            "##测试消息\n* 测试1\n* 测试2", msg_type=MsgType.MARKDOWN_V2
        )


if __name__ == "__main__":
    _ = unittest.main()
