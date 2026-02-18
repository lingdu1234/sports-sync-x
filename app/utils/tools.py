import os
from datetime import datetime as dt, timedelta

from app.utils.const import GARMIN_SPORT_TYPE_MAP


def Singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def check_path(path):
    if not os.path.exists(path):
        os.makedirs(path)


def format_datetime(data_time: dt | None):
    return data_time.strftime("%Y-%m-%d %H:%M:%S") if data_time is not None else ""


def get_datetime(dt_str: str) -> dt:
    return dt.strptime(dt_str, "%Y-%m-%d %H:%M:%S")


def calculate_end_time(start_time_local, start_time_gmt, duration):
    """Calculate end_time by adjusting for timezone differences"""
    try:
        # Parse start times
        local_dt = dt.strptime(start_time_local, "%Y-%m-%d %H:%M:%S")
        gmt_dt = dt.strptime(start_time_gmt, "%Y-%m-%d %H:%M:%S")

        # Calculate timezone offset in seconds
        timezone_offset = (local_dt - gmt_dt).total_seconds()

        # Calculate end time in GMT
        end_time_gmt = gmt_dt + timedelta(seconds=duration)

        # Convert back to local time using the same offset
        end_time_local = end_time_gmt + timedelta(seconds=timezone_offset)

        return end_time_local
    except Exception:
        # Fallback: use start_time_local + duration
        try:
            local_dt = dt.strptime(start_time_local, "%Y-%m-%d %H:%M:%S")
            return local_dt + timedelta(seconds=duration)
        except:  # noqa: E722
            return None


def get_garmin_sport_type(sport_type_id) -> tuple[str, str]:
    sport_type, mark = GARMIN_SPORT_TYPE_MAP.get(sport_type_id, ("other", "其他"))
    return sport_type, mark
