from enum import Enum
from sqlalchemy import create_engine, event
from datetime import datetime as dt

import os
from sqlmodel import Field, SQLModel
from app.utils.sys_config import cfg
from app.utils.tools import check_path, format_datetime

cfg = cfg
check_path(cfg.DB_DIR)
db_path = os.path.join(cfg.DB_DIR, cfg.DB_NAME)
engine = create_engine(
    f"sqlite:///{db_path}"
    #    , echo=True
)


def database_int():
    Base.metadata.create_all(engine)


class Base(SQLModel):
    pass


class SportActivity(Base, table=True):
    __tablename__ = "activity"  # pyright: ignore[reportAssignmentType]
    id: int = Field(primary_key=True, default=None)
    platform: str
    sport_device: str = ""  # 佳明为： manufacturer ， 高驰平台为device字段，但是也可能无此字段，但是fit文件中存在 fields.manufacturer 字段
    activity_id: str
    sport_type: str = ""
    mark: str = ""
    is_sync: str = ""
    start_time: str | None = None
    end_time: str | None = None
    distance: str | None = None
    duration: str | None = None
    created_at: str = format_datetime(dt.now())
    updated_at: str = format_datetime(dt.now())


@event.listens_for(SportActivity, "before_update")
def receive_before_update(mapper, connection, target: SportActivity):
    """
    监听 User 模型的 before_update 事件
    :param mapper: 模型映射器
    :param connection: 数据库连接
    :param target: 被更新的模型实例
    """
    # 直接使用update 不会监听到，不会更新
    target.updated_at = format_datetime(dt.now())


class SportPlatform(Enum):
    garminCOM = "garminCOM"
    garminCN = "garminCN"
    coros = "coros"
