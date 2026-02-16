from enum import Enum
from sqlalchemy import create_engine
from datetime import datetime as dt

# from sqlmodel import SQLModel, Field
import os
from sqlmodel import Field, SQLModel

from app.utils.sys_config import sysConfig
from app.utils.tools import check_path, format_datetime

cfg = sysConfig
check_path(cfg.DB_DIR)
db_path = os.path.join(cfg.DB_DIR, cfg.DB_NAME)
engine = create_engine(f"sqlite:///{db_path}", echo=True)


class Base(SQLModel):
    pass


class SportActivity(Base, table=True):
    __tablename__ = "activity"  # pyright: ignore[reportAssignmentType]
    id: int = Field(primary_key=True, default=None)
    platform: str
    activity_id: str
    is_sync: str = ""
    sport_type: str = ""
    start_time: str | None = None
    end_time: str | None = None
    distance: str | None = None
    distance: str | None = None
    created_at: str = format_datetime(dt.now())
    updated_at: str = format_datetime(dt.now())


class SportPlatform(Enum):
    garmin = "garmin"
    coros = "coros"
