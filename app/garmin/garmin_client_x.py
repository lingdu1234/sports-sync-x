from app.utils.tools import Singleton
from app.utils.sys_config import cfg
from typing import Any
import time
from functools import wraps
import os
from enum import Enum, auto
import requests


from garth import Client as gmClient
#  不要直接使用garth 要使用Client,否则两个数据会串

from app.utils.const import GARMIN_URL_DICT, GarminAuthDomain, SportPlatform


class GarminClient:
    def __init__(self, email, password, auth_domain: GarminAuthDomain, newest_num):
        print(f"正在初始化garmin{auth_domain.value}客户端")
        self.auth_domain = auth_domain
        self.email = email
        self.password = password
        self.garthClient = gmClient()
        self.newestNum = int(newest_num)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
            "origin": GARMIN_URL_DICT.get("SSO_URL_ORIGIN"),
            "nk": "NT",
        }

    ## 登录装饰器
    @staticmethod
    def login(f):
        @wraps(f)
        def wrapTheFunction(self, *args, **kwargs):
            session_path = f"_token_data/garmin{self.auth_domain.value}"
            if os.path.exists(session_path):
                # garth.resume(session_path)
                self.garthClient.load(session_path)
                try:
                    if os.path.exists(session_path):
                        try:
                            self.garthClient.username
                        except Exception as e:
                            print(f"读取session错误:{e}")
                            self.login_fn(session_path)
                except Exception:
                    print(f"garmin{self.auth_domain.value} is not loggin,re login...")
                    self.login_fn(session_path)
            else:
                print(f"garmin{self.auth_domain.value} token is not exist,re login...")
                self.login_fn(session_path)

            return f(self, *args, **kwargs)

        return wrapTheFunction

    def login_fn(self, session_path):
        if self.auth_domain and self.auth_domain == GarminAuthDomain.CN:
            self.garthClient.configure(domain="garmin.cn")
        self.garthClient.login(self.email, self.password)
        del self.garthClient.sess.headers["User-Agent"]
        # garth.save(session_path)
        self.garthClient.dump(session_path)

    @login
    def download(self, path, **kwargs):
        return self.garthClient.download(path, **kwargs)

    @login
    def connectapi(self, path, **kwargs):
        return self.garthClient.connectapi(path, **kwargs)

    def getActivities(self, start: int, limit: int) -> Any:
        """
        获取gaming运动记录
        :param
        start: int
        limit: int"""
        params = {"start": str(start), "limit": str(limit)}
        activities = self.connectapi(
            path=GARMIN_URL_DICT["garmin_connect_activities"], params=params
        )
        return activities

    def getAllActivities(self) -> list[dict]:
        """获取全部garmin运动记录"""
        all_activities = []
        start = 0
        while True:
            activities = self.getActivities(start=start, limit=100)
            if len(activities) > 0:  # pyright: ignore[reportArgumentType]
                all_activities.extend(activities)  # pyright: ignore[reportArgumentType]
            else:
                return all_activities
            start += 100

    def downloadActivity(self, id: str):
        """下载garmin运动记录"""
        download_fit_activity_url_prefix = GARMIN_URL_DICT[
            "garmin_connect_fit_download"
        ]
        download_fit_activity_url = f"{download_fit_activity_url_prefix}/{id}"
        response = self.download(download_fit_activity_url)
        return response

    @login
    def deleteActivity(self, id: str):
        url_path = GARMIN_URL_DICT["garmin_connect_delete"]
        delete_url = f"https://connectapi.{self.garthClient.domain}{url_path}/{id}"
        try:
            self.headers["Authorization"] = str(self.garthClient.oauth2_token)
            resp = requests.delete(delete_url, headers=self.headers)
            res_code = resp.status_code
            if res_code == 204:
                print(f"删除activity成功:{id}")
            else:
                print(f"删除activity出错:{id}")
        except Exception:
            print("删除出错,1秒后将进行重试")
            time.sleep(1)
            return self.deleteActivity(id)

    @login
    def uploadActivity(self, file_path: str) -> bool:
        """Upload activity in fit format from file."""
        # This code is borrowed from python-garminconnect-enhanced ;-)
        file_base_name = os.path.basename(file_path)
        file_extension = file_base_name.split(".")[-1]
        allowed_file_extension = (
            file_extension.upper() in ActivityUploadFormat.__members__
        )

        if allowed_file_extension:
            try:
                with open(file_path, "rb") as file:
                    file_data = file.read()
                    fields = {"file": (file_base_name, file_data, "text/plain")}

                    url_path = GARMIN_URL_DICT["garmin_connect_upload"]
                    upload_url = (
                        f"https://connectapi.{self.garthClient.domain}{url_path}"
                    )
                    self.headers["Authorization"] = str(self.garthClient.oauth2_token)
                    response = requests.post(
                        upload_url, headers=self.headers, files=fields
                    )
                    res_code = response.status_code
                    result = response.json()
                    uploadId = result.get("detailedImportResult").get("uploadId")
                    isDuplicateUpload = uploadId is None or uploadId == ""
                    if res_code == 202 and not isDuplicateUpload:
                        return True
                    elif (
                        res_code == 409
                        and result.get("detailedImportResult")
                        .get("failures")[0]
                        .get("messages")[0]
                        .get("content")
                        == "Duplicate Activity."
                    ):
                        return True
            except Exception as e:
                print(e)

                return False
            finally:
                pass
            return False
        else:
            return False


class ActivityUploadFormat(Enum):
    FIT = auto()
    GPX = auto()
    TCX = auto()


class GarminNoLoginException(Exception):
    """Raised when rate limit is exceeded."""

    def __init__(self, status):
        """Initialize."""
        super(GarminNoLoginException, self).__init__(status)
        self.status = status


@Singleton
class GarminClientCOM(GarminClient):
    def __init__(self, email, password, auth_domain: GarminAuthDomain, newest_num):
        print(f"正在初始化garmin{auth_domain.value}客户端")
        self.auth_domain = auth_domain
        self.email = email
        self.password = password
        self.garthClient = gmClient()
        self.newestNum = int(newest_num)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
            "origin": GARMIN_URL_DICT.get("SSO_URL_ORIGIN"),
            "nk": "NT",
        }


@Singleton
class GarminClientCN(GarminClient):
    def __init__(self, email, password, auth_domain: GarminAuthDomain, newest_num):
        print(f"正在初始化garmin{auth_domain.value}客户端")
        self.auth_domain = auth_domain
        self.email = email
        self.password = password
        self.garthClient = gmClient()
        self.newestNum = int(newest_num)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
            "origin": GARMIN_URL_DICT.get("SSO_URL_ORIGIN"),
            "nk": "NT",
        }


def get_garmin_client(platform: SportPlatform) -> GarminClient:
    email, password, auth_domain = (
        (cfg.GARMIN_EMAIL_COM, cfg.GARMIN_PASSWORD_COM, GarminAuthDomain.COM)
        if platform == SportPlatform.garminCOM
        else (cfg.GARMIN_EMAIL_CN, cfg.GARMIN_PASSWORD_CN, GarminAuthDomain.CN)
    )
    return (
        GarminClientCOM(email, password, auth_domain, cfg.GARMIN_NEWEST_NUM)
        if platform == SportPlatform.garminCOM
        else GarminClientCN(email, password, auth_domain, cfg.GARMIN_NEWEST_NUM)
    )
