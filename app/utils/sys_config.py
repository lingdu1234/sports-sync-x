from app.utils.const import SportPlatform
from app.utils.tools import check_path, Singleton
import os

from dotenv import find_dotenv, load_dotenv

_ = load_dotenv(find_dotenv(), override=True)

work_dir = os.getcwd()


def get_sys_config(key: str) -> str:
    v = os.getenv(key)
    return v if v else ""


@Singleton
class SysConfig:
    SYNC_PLATFORM: str = get_sys_config("SYNC_PLATFORM")

    GARMIN_EMAIL_COM: str = get_sys_config("GARMIN_EMAIL_COM")
    GARMIN_PASSWORD_COM: str = get_sys_config("GARMIN_PASSWORD_COM")

    GARMIN_EMAIL_CN: str = get_sys_config("GARMIN_EMAIL_CN")
    GARMIN_PASSWORD_CN: str = get_sys_config("GARMIN_PASSWORD_CN")

    GARMIN_NEWEST_NUM: str = get_sys_config("GARMIN_NEWEST_NUM")

    COROS_EMAIL: str = get_sys_config("COROS_EMAIL")
    COROS_PASSWORD: str = get_sys_config("COROS_PASSWORD")

    DELETE_DUPLICATE: str = get_sys_config("DELETE_DUPLICATE")
    SPORT_DIFF_SECOND: str = get_sys_config("SPORT_DIFF_SECOND")

    QYWX_BOT_KEY: str = get_sys_config("QYWX_BOT_KEY")

    #     系统配置
    GARMIN_FIT_DIR_COM = os.path.join(work_dir, "fit", "garmin_com")
    GARMIN_FIT_DIR_CN = os.path.join(work_dir, "fit", "garmin_cn")
    COROS_FIT_DIR = os.path.join(work_dir, "fit", "coros")
    DB_DIR = os.path.join(work_dir, "db")
    DB_NAME = "sports_sync.sqlite"

    def check_cfg(self) -> bool:
        if SportPlatform.garminCOM.value.upper() in self.SYNC_PLATFORM.upper():
            if check_null(self.GARMIN_EMAIL_COM) or check_null(
                self.GARMIN_PASSWORD_COM
            ):
                return False
            else:
                check_path(self.GARMIN_FIT_DIR_COM)
        if SportPlatform.garminCN.value.upper() in self.SYNC_PLATFORM.upper():
            if check_null(self.GARMIN_EMAIL_CN) or check_null(self.GARMIN_PASSWORD_CN):
                return False
            else:
                check_path(self.GARMIN_FIT_DIR_CN)
        if SportPlatform.coros.value.upper() in self.SYNC_PLATFORM.upper():
            if check_null(self.COROS_EMAIL) or check_null(self.COROS_EMAIL):
                return False
            else:
                check_path(self.COROS_FIT_DIR)
        return True


def check_null(data: str) -> bool:
    return data is None or data == ""


# 创建全局配置实例（方便其他文件导入使用）
cfg = SysConfig()
