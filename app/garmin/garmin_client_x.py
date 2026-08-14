import os
from pathlib import Path
from typing import Any
import time
from functools import wraps

from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectInvalidFileFormatError,
)

from app.utils.tools import Singleton
from app.utils.sys_config import cfg
from app.utils.const import GarminAuthDomain, SportPlatform


class GarminClient:
    def __init__(self, email, password, auth_domain: GarminAuthDomain, newest_num):
        print(f"正在初始化garmin{auth_domain.value}客户端")
        self.auth_domain = auth_domain
        self.email = email
        self.password = password
        self.newestNum = int(newest_num)
        self._logged_in = False

        # 设置不同的 tokenstore 路径，避免 COM 和 CN 冲突
        token_dir = "garmin_cn" if auth_domain == GarminAuthDomain.CN else "garmin_com"
        self.tokenstore = str(Path.home() / ".garminconnect" / token_dir)
        os.makedirs(self.tokenstore, exist_ok=True)

        # 创建 Garmin 客户端
        self.client = Garmin(
            email=email,
            password=password,
            is_cn=(auth_domain == GarminAuthDomain.CN),
        )

    ## 登录装饰器 - 优化版，使用 try/except 而非预检查
    @staticmethod
    def login(f):
        @wraps(f)
        def wrapTheFunction(self, *args, **kwargs):
            try:
                if not self._logged_in:
                    self.login_fn()
                return f(self, *args, **kwargs)
            except GarminConnectAuthenticationError:
                print(f"garmin{self.auth_domain.value} 会话已过期,重新登录...")
                self.login_fn()
                return f(self, *args, **kwargs)

        return wrapTheFunction

    def login_fn(self):
        try:
            self.client.login(self.tokenstore)
            self._logged_in = True
            print(f"garmin{self.auth_domain.value} 登录成功")
        except GarminConnectTooManyRequestsError:
            print(f"garmin{self.auth_domain.value} 请求过于频繁,稍后重试")
            raise
        except (GarminConnectAuthenticationError, GarminConnectConnectionError) as e:
            print(f"garmin{self.auth_domain.value} 登录失败: {e}")
            self._logged_in = False
            raise

    @login
    def getActivities(self, start: int, limit: int) -> Any:
        """
        获取garmin运动记录
        :param
        start: int
        limit: int"""
        return self.client.get_activities(start=start, limit=limit)

    def getAllActivities(self) -> list[dict]:
        """获取全部garmin运动记录"""
        all_activities = []
        new = int(cfg.GARMIN_NEWEST_NUM)
        start = 0
        limit = new if new < 100 else 100
        while start <= new:
            activities = self.getActivities(start=start, limit=limit)
            if activities and len(activities) > 0:
                all_activities.extend(activities)
            else:
                return all_activities
            start += 100
        return all_activities

    @login
    def downloadActivity(self, id: str):
        """下载garmin运动记录 - 使用原始FIT格式"""
        return self.client.download_activity(
            id, dl_fmt=Garmin.ActivityDownloadFormat.ORIGINAL
        )

    @login
    def deleteActivity(self, id: str, max_retries: int = 3):
        """删除activity，带最大重试限制"""
        try:
            result = self.client.delete_activity(id)
            print(f"删除activity成功:{id}")
            return True
        except Exception as e:
            print(f"删除activity出错:{id} - {e}")
            if max_retries > 0:
                print(f"删除出错,1秒后将进行重试 (剩余{max_retries}次)")
                time.sleep(1)
                return self.deleteActivity(id, max_retries - 1)
            else:
                print(f"删除activity失败,已达到最大重试次数")
                return False

    @login
    def uploadActivity(self, file_path: str) -> bool:
        """Upload activity in fit format from file."""
        try:
            result = self.client.upload_activity(file_path)
            # upload_activity 返回的是服务器响应数据
            # 检查上传是否成功
            if result and isinstance(result, dict):
                detailed_result = result.get("detailedImportResult", {})
                upload_id = detailed_result.get("uploadId")
                if upload_id and upload_id != "":
                    print(f"上传成功: {file_path}, uploadId: {upload_id}")
                    return True
                else:
                    print(f"上传跳过(重复): {file_path}")
                    return True  # 重复也算成功
            elif result is not None:
                # 非dict结果，可能是字符串或其他
                print(f"上传返回非预期格式: {type(result)}")
                return True  # 假设成功
            else:
                print(f"上传失败: {file_path}")
                return False
        except GarminConnectInvalidFileFormatError as e:
            print(f"上传文件格式错误: {e}")
            return False
        except Exception as e:
            print(f"上传出错: {file_path} - {e}")
            return False


class GarminNoLoginException(Exception):
    """Raised when rate limit is exceeded."""

    def __init__(self, status):
        """Initialize."""
        super(GarminNoLoginException, self).__init__(status)
        self.status = status


@Singleton
class GarminClientCOM(GarminClient):
    def __init__(self, email, password, auth_domain: GarminAuthDomain, newest_num):
        super().__init__(email, password, auth_domain, newest_num)


@Singleton
class GarminClientCN(GarminClient):
    def __init__(self, email, password, auth_domain: GarminAuthDomain, newest_num):
        super().__init__(email, password, auth_domain, newest_num)


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
