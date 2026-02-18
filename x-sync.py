import time
from app.database.db_api import saveActivity, checkSynced
from app.coros.coros_client import get_coros_client
from app.database.db import database_int, SportActivity, SportPlatform
from app.garmin.garmin_client import get_garmin_client
from app.sync_fn.sync_fn import (
    process_coros_activity,
    process_garmin_activity,
    sync_to_platform,
)
from app.utils.sys_config import cfg


def sync_data():
    print("=" * 60)
    print("Garmin - Coros 双向运动数据同步工具")
    print("=" * 60)

    if not cfg.check_cfg():
        print("错误: 请确保在 .env 文件中填写了所有必需的配置信息:")
        return
    try:
        print("初始化数据库...")
        database_int()

        print("开始运行同步任务...")
        run_sync_task()

    except Exception as e:
        print(f"错误: {e}")
        import traceback

        traceback.print_exc()


def run_sync_task():
    print("=" * 60)
    print("开始双向同步和对比分析")
    print("=" * 60)
    print("获取 GarminCN 运动记录...")
    print("获取 GarminCOM 运动记录...")
    deal_with_garmin_activity(SportPlatform.garminCN)
    deal_with_garmin_activity(SportPlatform.garminCOM)
    print("获取 Coros 运动记录...")
    # deal_with_coros_activity()

    # checkSynced(SportPlatform.garminCN)
    # checkSynced(SportPlatform.garminCOM)
    # checkSynced(SportPlatform.coros)

    # sync_to_platform(SportPlatform.garminCOM)
    # sync_to_platform(SportPlatform.garminCN)
    # sync_to_platform(SportPlatform.coros)


def deal_with_garmin_activity(garmin_platform: SportPlatform):
    client = get_garmin_client(garmin_platform)
    print(id(client))
    activities_raw = client.getAllActivities()
    print(f"{garmin_platform.value} 运动记录总数: {len(activities_raw)}")
    sports: list[SportActivity] = []
    for activity in activities_raw:
        data = process_garmin_activity(activity, garmin_platform)
        sports.append(data)
    # 将数据排序，入库排除重复数据，正向排序，自己平台先上传，id应该更小
    sports_sorted = sorted(sports, key=lambda x: int(x.activity_id))
    for activity in sports_sorted:
        is_DUPLICATE = saveActivity(activity)
        if is_DUPLICATE and cfg.DELETE_DUPLICATE == "1":
            print(
                f"{garmin_platform.value}activity重复,1秒后将删除:{activity.activity_id}"
            )
            time.sleep(1)  # 等待10秒，防止api报错
            # client.deleteActivity(activity.activity_id)


def deal_with_coros_activity():
    client = get_coros_client()
    activities_raw = client.getAllActivities()
    print(f"Coros 运动记录总数: {len(activities_raw)}")
    sports: list[SportActivity] = []
    for activity in activities_raw:
        data = process_coros_activity(activity)
        sports.append(data)
    # 将数据排序，入库排除重复数据，正向排序，自己平台先上传，id应该更小
    sports_sorted = sorted(sports, key=lambda x: int(x.activity_id))
    for activity in sports_sorted:
        is_DUPLICATE = saveActivity(activity)
        if is_DUPLICATE and cfg.DELETE_DUPLICATE == "1":
            print(f"Coros平台 activity重复,1秒后将删除:{activity.activity_id}")
            # time.sleep(1)  # 等待10秒，防止api报错
            client.deleteActivity(activity.activity_id)


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == "__main__":
    sync_data()
