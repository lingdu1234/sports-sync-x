from app.garmin.garmin_client_x import get_garmin_client
from app.coros.coros_client import get_coros_client
import os

from app.utils.fit_parser import extract_all_from_zip
from app.utils.sys_config import cfg
from app.database.db import SportActivity, SportPlatform
from typing import Dict
from app.database.db_api import getUnSyncActivites, setActivitySynced
from app.utils.const import get_coros_sport_type
from datetime import datetime as dt

from app.utils.tools import (
    calculate_end_time,
    format_datetime,
)


def process_garmin_activity(
    activity: Dict, garmin_platform: SportPlatform
) -> SportActivity:
    """处理单个 Garmin 活动，提取数据并保存到数据库"""
    activity_id = activity["activityId"]

    start_time_local = activity.get("startTimeLocal")
    start_time_gmt = activity.get("startTimeGMT")
    distance = activity.get("distance")
    # sport_type_id = activity.get("activityType").get("typeId")  # pyright: ignore[reportOptionalMemberAccess]
    sport_type = activity.get("activityType").get("typeKey")  # pyright: ignore[reportOptionalMemberAccess]  # ty:ignore[unresolved-attribute]
    sport_device = activity.get("manufacturer")
    activity_name = activity.get("activityName")

    # 解析 start_time
    start_time = None
    end_time = None
    duration = 0
    if start_time_local and start_time_gmt:
        try:
            start_time = dt.strptime(start_time_local, "%Y-%m-%d %H:%M:%S")
            # 计算 duration（秒）
            duration = round(activity.get("duration", 0), 0)
            end_time = calculate_end_time(start_time_local, start_time_gmt, duration)
        except Exception as e:
            print(f"  ✗ 解析时间失败: {activity_id} - {e}")

    # 保留两位小数
    distance = round(distance, 2) if distance else 0

    # 获取 sport_type
    # sport_type, mark = get_garmin_sport_type(sport_type_id)

    # 组合数据

    return SportActivity(
        platform=garmin_platform.value,
        sport_device=str(sport_device).lower() if sport_device is not None else "",
        activity_id=activity_id,
        sport_type=sport_type if sport_type is not None else "other",
        mark=activity_name if activity_name is not None else "",
        is_sync=f"{garmin_platform.value}@1",
        start_time=format_datetime(start_time),
        end_time=format_datetime(end_time),
        distance=str(distance),
        duration=str(duration),
    )


def process_coros_activity(activity: Dict) -> SportActivity:
    """处理单个 Coros 活动，提取数据并保存到数据库"""
    activity_id = activity["labelId"]
    start_time_timestamp = activity.get("startTime")
    end_time_timestamp = activity.get("endTime")
    distance = activity.get("distance")
    sport_type = activity.get("sportType")
    sport_name = activity.get("name")
    sport_device = activity.get("device")

    # 解析时间戳为 datetime
    start_time = None
    end_time = None
    duration = 0
    if start_time_timestamp and end_time_timestamp:
        try:
            # 时间戳转换（秒）
            start_time = dt.fromtimestamp(start_time_timestamp)
            end_time = dt.fromtimestamp(end_time_timestamp)
            # 计算 duration（秒）
            duration = end_time_timestamp - start_time_timestamp
        except Exception as e:
            print(f"  ✗ 解析时间失败: {activity_id} - {e}")

    # 保留两位小数
    distance = round(distance, 2) if distance else 0

    # # 映射 sport_type
    mark = get_coros_sport_type(sport_type)

    # 保存到数据库
    return SportActivity(
        platform=SportPlatform.coros.value,
        sport_device=str(sport_device).lower() if sport_device is not None else "",
        activity_id=activity_id,
        sport_type=sport_type if sport_type is not None else "other",
        mark=sport_name if sport_name is not None else mark,
        is_sync=f"{SportPlatform.coros.value}@1",
        start_time=format_datetime(start_time),
        end_time=format_datetime(end_time),
        distance=str(distance),
        duration=str(duration),
    )


def sync_to_platform(platform: SportPlatform):
    # 获取没有同步到该平台的记录
    un_sync_activities = getUnSyncActivites(platform)
    for un_sync_activity in un_sync_activities:
        # 下载
        file_path = ""
        match un_sync_activity.platform:
            case SportPlatform.garminCOM.value:
                if download_garmin_activity_fn(un_sync_activity):
                    file_path = os.path.join(
                        cfg.GARMIN_FIT_DIR_COM,
                        f"{un_sync_activity.activity_id}_ACTIVITY.fit",
                    )
            case SportPlatform.garminCN.value:
                if download_garmin_activity_fn(un_sync_activity):
                    file_path = os.path.join(
                        cfg.GARMIN_FIT_DIR_CN,
                        f"{un_sync_activity.activity_id}_ACTIVITY.fit",
                    )
            case SportPlatform.coros.value:
                if download_coros_activity_fn(un_sync_activity):
                    file_path = os.path.join(
                        cfg.COROS_FIT_DIR,
                        f"{un_sync_activity.activity_id}.fit",
                    )
        # 上传
        if file_path == "":
            print(f"{un_sync_activity.activity_id}文件不存在，无法同步")
        else:
            match platform:
                case SportPlatform.garminCOM | SportPlatform.garminCN:
                    client = get_garmin_client(platform)
                    if client.uploadActivity(file_path):
                        setActivitySynced(un_sync_activity, platform.value, True)
                    else:
                        setActivitySynced(un_sync_activity, platform.value, False)
                case SportPlatform.coros:
                    client = get_coros_client()
                    if client.uploadActivity(file_path, un_sync_activity.activity_id):
                        setActivitySynced(un_sync_activity, platform.value, True)
                    else:
                        setActivitySynced(un_sync_activity, platform.value, False)


def download_garmin_activity_fn(activity: SportActivity) -> bool:
    id = activity.activity_id
    FIT_DIR, client = (
        (cfg.GARMIN_FIT_DIR_COM, get_garmin_client(SportPlatform.garminCOM))
        if activity.platform == SportPlatform.garminCOM.value
        else (cfg.GARMIN_FIT_DIR_CN, get_garmin_client(SportPlatform.garminCN))
    )
    try:
        # 下载记录
        file = client.downloadActivity(id)
        zip_file_path = os.path.join(FIT_DIR, f"{id}.zip")
        with open(zip_file_path, "wb") as fb:
            fb.write(file)
        # 解压文件
        extract_all_from_zip(zip_file_path)
        return True
    except Exception:
        print(f"* ✗ 下载 Garmin 活动 {id} 失败")
        return False


def download_coros_activity_fn(activity: SportActivity) -> bool:
    id = activity.activity_id
    sport_type = activity.sport_type
    try:
        client = get_coros_client()
        file = client.downloadActivity(id, sport_type)
        fit_file_path = os.path.join(cfg.COROS_FIT_DIR, f"{id}.fit")
        with open(fit_file_path, "wb") as fb:
            fb.write(file.data)
        return True
    except Exception as err:
        print(err)
        print(f"* ✗ 下载 Coros 活动 {id} 失败")
        return False
