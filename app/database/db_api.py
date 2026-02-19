from app.utils.const import SportPlatform
from app.utils.sys_config import cfg
from app.utils.tools import get_datetime, format_datetime
from sqlmodel import select, and_, Session, col
from typing import Sequence
from app.database.db import SportActivity, engine
from datetime import datetime as dt, timedelta
from app.utils.msg_tool import msg


def is_exist_x(activity: SportActivity) -> tuple[bool, bool]:
    """
    检查同平台是否存在重复数据
    检查activity是否存在,宽容模式，在第一条记录的基础上，开始时间加减一定时间

    :param activity: 运动数据
    :type activity: SportActivity
    """
    s_t = (
        get_datetime(activity.start_time)
        if activity.start_time is not None
        else dt.now()
    )

    diff = int(cfg.SPORT_DIFF_SECOND)
    stmt = (
        (
            select(SportActivity)
            .where(
                and_(
                    col(SportActivity.start_time) == activity.start_time,
                    col(SportActivity.platform) == activity.platform,
                )
            )
            .limit(1)
        )
        if diff <= 0
        else (
            select(SportActivity)
            .where(
                and_(
                    col(SportActivity.start_time)
                    >= format_datetime(s_t - timedelta(seconds=diff)),
                    col(SportActivity.start_time)
                    <= format_datetime(s_t + timedelta(seconds=diff)),
                    col(SportActivity.platform) == activity.platform,
                )
            )
            .limit(1)
        )
    )

    with Session(engine) as session:
        data = session.exec(stmt).one_or_none()
        if data is not None:
            return True, int(activity.activity_id) != int(data.activity_id)
        else:
            return False, False


def saveActivity(activity: SportActivity) -> bool:
    """
    保存运动记录到数据库

    :param activity: 运动数据
    :type activity: SportActivity
    """
    is_repeat, is_not_equal = is_exist_x(activity)
    if not is_repeat:
        with Session(engine) as session:
            session.add(activity)
            session.commit()
            return False
    else:
        return is_repeat and is_not_equal


def getAllActivities(platform: SportPlatform) -> Sequence[SportActivity]:
    """
    获取指定平台的所有记录

    :param platform: 运动平台
    :type platform: SportPlatform
    """
    with Session(engine) as session:
        stmt = select(SportActivity).where(SportActivity.platform == platform.value)
        data = session.exec(stmt).all()
        return data


def getUnSyncActivites(platform: SportPlatform) -> Sequence[SportActivity]:
    """
    获取未同步到该平台的记录

    :param platform: 查询平台
    :type platform: SportPlatform
    :return: 说明
    :rtype: Sequence[SportActivity]
    """
    with Session(engine) as session:
        stmt = select(SportActivity).where(
            col(SportActivity.is_sync).not_like(f"%{platform.value}%")
        )
        data = session.exec(stmt).all()
        return data


def checkSynced(platform: SportPlatform):
    """
    检查平台已经同步的数据，并标记

    :param platform: 运动平台
    :type platform: SportPlatform
    """
    # 第一步：获取未同步到该 platform 的数据
    un_sync_activities = getUnSyncActivites(platform)
    # 第二步：对未同步的数据进行遍历
    for un_sync_activity in un_sync_activities:
        # 获取重复的数据
        duplicate_activities = getSyncedActivities(un_sync_activity)

        if duplicate_activities:
            # 对重复的数据进行分析
            for duplicate_activity in duplicate_activities:
                # 如果重复数据的 platform 不在 un_sync_activity 的 is_sync 内
                if duplicate_activity.platform not in un_sync_activity.is_sync:
                    setActivitySynced(
                        un_sync_activity, duplicate_activity.platform, True
                    )

                # 做反向标记：如果 un_sync_activity 的 platform 不在 duplicate_activity 的 is_sync 内
                if un_sync_activity.platform not in duplicate_activity.is_sync:
                    setActivitySynced(
                        duplicate_activity, un_sync_activity.platform, True
                    )

    # 再次获取未同步数据，用于统计
    un_sync_activities_2 = getUnSyncActivites(platform)
    msg.add_message(
        f"检测到 {len(un_sync_activities)} 条未同步到 {platform.value},验证后共 {len(un_sync_activities_2)} 条未同步..."
    )


def setActivitySynced(activity: SportActivity, synced_platform: str, is_success: bool):

    v = f"{synced_platform}@1" if is_success else f"{synced_platform}@0"

    with Session(engine) as session:
        stmt = select(SportActivity).where(col(SportActivity.id) == activity.id)
        data: SportActivity = session.exec(stmt).one()
        if synced_platform not in data.is_sync:
            is_sync = v if data.is_sync == "" else f"{data.is_sync},{v}"
            data.is_sync = is_sync
            session.commit()


def getSyncedActivities(activity: SportActivity) -> Sequence[SportActivity]:
    """
    获取其他平台，重复数据

    :param activity: 说明
    :type activity: SportActivity
    """
    s_t = (
        get_datetime(activity.start_time)
        if activity.start_time is not None
        else dt.now()
    )

    diff = int(cfg.SPORT_DIFF_SECOND)
    stmt = (
        (
            select(SportActivity).where(
                and_(
                    col(SportActivity.start_time) == activity.start_time,
                    col(SportActivity.platform) != activity.platform,
                )
            )
        )
        if diff <= 0
        else (
            select(SportActivity).where(
                and_(
                    col(SportActivity.start_time)
                    >= format_datetime(s_t - timedelta(seconds=diff)),
                    col(SportActivity.start_time)
                    <= format_datetime(s_t + timedelta(seconds=diff)),
                    col(SportActivity.platform) != activity.platform,
                )
            )
        )
    )
    with Session(engine) as session:
        data = session.exec(stmt).all()
        return data
