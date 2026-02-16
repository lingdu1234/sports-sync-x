from sqlmodel import select, and_, Session, col
from typing import Sequence
from app.utils.tools import myLogger
from app.database.db import SportActivity, SportPlatform, engine


def is_exist(activity: SportActivity):
    """
    检查activity是否存在

    :param activity: 运动数据
    :type activity: SportActivity
    """
    with Session(engine) as session:
        stmt = (
            select(SportActivity)
            .where(
                and_(
                    col(SportActivity.start_time) == activity.start_time,
                    col(SportActivity.platform) == activity.platform,
                )
            )
            .limit(1)
        )
        data = session.exec(stmt).one_or_none()
        return data is not None


def saveActivity(activity: SportActivity):
    """
    保存运动记录到数据库

    :param activity: 运动数据
    :type activity: SportActivity
    """
    with Session(engine) as session:
        if not is_exist(activity):
            session.add(activity)
            session.commit()
        else:
            myLogger.info(f"该记录已经重复,将不再入库:{activity.activity_id}")


def getAllActivities(platform: SportPlatform) -> Sequence[SportActivity]:
    """
    获取指定平台的所有记录

    :param platform: 运动平台
    :type platform: SportPlatform
    """
    with Session(engine) as session:
        stmt = select(SportActivity).where(SportActivity.platform == platform.value)
        data = session.scalars(stmt).all()
        return data


def getUnSyncActivites(
    platform: SportPlatform, target_plaform: SportPlatform
) -> Sequence[SportActivity]:
    """
    过去指定平台所有的未同步记录

    :param platform: 查询平台
    :type platform: SportPlatform
    :param platform: 未同步平台
    :type platform: SportPlatform
    :return: 说明
    :rtype: Sequence[SportActivity]
    """
    with Session(engine) as session:
        stmt = select(SportActivity).where(
            and_(
                col(SportActivity.platform) == platform.value,
                col(SportActivity.is_sync).not_like(target_plaform.value),
            )
        )
        data = session.scalars(stmt).all()
        return data
