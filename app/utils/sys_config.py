import os

from dotenv import find_dotenv, load_dotenv

_ = load_dotenv(find_dotenv(), override=True)

work_dir = os.getcwd()


def get_sys_config(key: str) -> str:
    v = os.getenv(key)
    return v if v else ""


class SysConfig:
    GARMIN_EMAIL: str = get_sys_config("GARMIN_EMAIL")
    GARMIN_PASSWORD: str = get_sys_config("GARMIN_PASSWORD")
    GARMIN_AUTH_DOMAIN: str = get_sys_config("GARMIN_AUTH_DOMAIN")
    GARMIN_NEWEST_NUM: str = get_sys_config("GARMIN_NEWEST_NUM")

    COROS_EMAIL: str = get_sys_config("COROS_EMAIL")
    COROS_PASSWORD: str = get_sys_config("COROS_PASSWORD")
    QYWX_BOT_KEY: str = get_sys_config("QYWX_BOT_KEY")

    #     系统配置
    GARMIN_FIT_DIR = os.path.join(work_dir, "garmin-fit")
    COROS_FIT_DIR = os.path.join(work_dir, "coros-fit")
    DB_DIR = os.path.join(work_dir, "db")
    DB_NAME = "sports_sync.sqlite"


# 创建全局配置实例（方便其他文件导入使用）
sysConfig = SysConfig()
