from pathlib import Path
import os
from app.oss.ali_oss_client import AliOssClient
from app.oss.aws_oss_client import AwsOssClient
from app.utils.md5_utils import calculate_md5_file
from app.utils.sys_config import cfg
import time
from typing import Any
import urllib3
import json
import hashlib

import certifi


from app.coros.region_config import REGIONCONFIG
from app.coros.sts_config import STS_CONFIG
from app.utils.tools import Singleton


@Singleton
class CorosClient:
    def __init__(self, email, password) -> None:
        print("正在初始化coros客户端")
        self.email = email
        self.password = password
        self.req = urllib3.PoolManager(
            cert_reqs="CERT_REQUIRED", ca_certs=certifi.where()
        )

        accessToken, userId, regionId, teamapi = self.login()

        self.accessToken = accessToken
        self.userId = userId
        self.regionId = regionId
        self.teamapi = teamapi

    ## 登录接口
    def login(self):
        ## default use com login url
        login_url = "https://teamcnapi.coros.com/account/login"

        login_data = {
            "account": self.email,
            "pwd": hashlib.md5(self.password.encode()).hexdigest(),  ##MD5加密密码
            "accountType": 2,
        }
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.39 Safari/537.36",
            "referer": "https://teamcnapi.coros.com/",
            "origin": "https://teamcnapi.coros.com/",
        }

        login_body = json.dumps(login_data)
        response = self.req.request("POST", login_url, body=login_body, headers=headers)

        login_response = json.loads(response.data)
        login_result = login_response["result"]
        if login_result != "0000":
            raise CorosLoginError(
                "Coros login anomaly, the reason for the anomaly is:"
                + login_response["message"]
            )

        accessToken = login_response["data"]["accessToken"]
        userId = login_response["data"]["userId"]
        regionId = login_response["data"]["regionId"]
        self.accessToken = accessToken
        self.userId = userId
        self.regionId = regionId
        teamapi = REGIONCONFIG[self.regionId]["teamapi"]
        self.teamapi = teamapi
        return accessToken, userId, regionId, teamapi

    def deleteActivity(self, id: str):
        self.checkToken()
        delete_url = f"{self.teamapi}/activity/delete?labelId={id}"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "accesstoken": self.accessToken,
        }
        try:
            response = self.req.request(method="GET", url=delete_url, headers=headers)
            if response.status == 200:
                print(response.data)
                print(f"删除activity成功:{id}")
            else:
                print(f"删除activity出错:{id}")
        except Exception:
            print("删除出错,1秒后将进行重试")
            time.sleep(1)
            return self.deleteActivity(id)

    ## 上传运动
    def uploadActivityFn(self, oss_object, md5, fileName, size):
        ## 检查token
        self.checkToken()

        upload_url = f"{self.teamapi}/activity/fit/import"

        headers = {
            "Accept": "application/json, text/plain, */*",
            "accesstoken": self.accessToken,
        }

        try:
            bucket = STS_CONFIG[self.regionId]["bucket"]
            serviceName = STS_CONFIG[self.regionId]["service"]
            data = {
                "source": 1,
                "timezone": 32,
                "bucket": f"{bucket}",
                "md5": f"{md5}",
                "size": size,
                "object": f"{oss_object}",
                "serviceName": f"{serviceName}",
                "oriFileName": f"{fileName}",
            }
            json_data = json.dumps(data)
            json_str = str(json_data)
            print(json_str)
            response = self.req.request(
                method="POST",
                url=upload_url,
                fields={"jsonParameter": json_str},
                headers=headers,
            )
            upload_response = json.loads(response.data)
            print(upload_response)
            if (
                upload_response["data"].get("status") == 2
                and upload_response["result"] == "0000"
            ):
                return True
            else:
                return False
        except Exception:
            exit()

    def uploadActivity(self, file_path: str) -> bool:
        """
        从 Garmin 同步你上传的活动到 Coros
        :param file_path: fit 文件路径
        :param un_sync_id: 未同步id
        :return:
        """
        try:
            client = None
            ## 中国区使用阿里云OSS
            if self.regionId == 2:
                client = AliOssClient()
            elif self.regionId == 1 or self.regionId == 3:
                client = AwsOssClient()
            file_name = Path(file_path).name
            _oss_obj = client.multipart_upload(  # pyright: ignore[reportOptionalMemberAccess]  # ty:ignore[unresolved-attribute]
                file_path, f"{self.userId}/{calculate_md5_file(file_path)}.zip"
            )
            size = os.path.getsize(file_path)
            upload_result = self.uploadActivityFn(
                f"fit_zip/{self.userId}/{calculate_md5_file(file_path)}.zip",
                calculate_md5_file(file_path),
                file_name,
                size,
            )
            if upload_result:
                return True
            else:
                return False
        except Exception as err:
            print(err)
            return False

    def getActivities(self, size: int, page: int) -> Any:
        self.checkToken()
        activitys_url = f"{self.teamapi}/activity/query?size={size}&pageNumber={page}"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "accesstoken": self.accessToken,
        }
        try:
            response = self.req.request(
                method="GET", url=activitys_url, headers=headers
            )
            response = json.loads(response.data)
            return response
        except Exception:
            exit()

    ## 获取所有运动
    def getAllActivities(self) -> list[dict]:
        all_activities = []
        size = 200
        page = 1
        while True:
            activities = self.getActivities(size, page)
            totalPage = activities["data"]["totalPage"]
            if totalPage >= page:
                all_activities.extend(activities["data"]["dataList"])
            else:
                return all_activities
            page += 1

    def downloadActivity(self, id: str, sport_type):
        self.checkToken()
        ## 文件下载链接
        get_activity_download_url = f"{self.teamapi}/activity/detail/download?labelId={id}&sportType={sport_type}&fileType=4"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "accesstoken": self.accessToken,
        }
        try:
            get_activity_download_url_response = self.req.request(
                method="POST", url=get_activity_download_url, headers=headers
            )
            get_activity_download_url_response_json = json.loads(
                get_activity_download_url_response.data
            )
            download_url = get_activity_download_url_response_json["data"]["fileUrl"]
            return self.req.request(method="GET", url=download_url, headers=headers)
        except Exception:
            exit()
        pass

    ## 检查token是否有效
    def checkToken(self):
        ## 判断Token 是否为空
        if self.accessToken is None:
            self.login()


def get_coros_client() -> CorosClient:
    return CorosClient(cfg.COROS_EMAIL, cfg.COROS_PASSWORD)


class CorosLoginError(Exception):
    def __init__(self, status):
        """Initialize."""
        super(CorosLoginError, self).__init__(status)
        self.status = status


class CorosActivityUploadError(Exception):
    def __init__(self, status):
        """Initialize."""
        super(CorosActivityUploadError, self).__init__(status)
        self.status = status
