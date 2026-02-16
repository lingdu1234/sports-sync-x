from sqlalchemy import update
from sqlmodel import Session, delete, select, col, and_
from app.database.db_api import getUnSyncActivites, getAllActivities
from app.database.db import engine, SportActivity, SportPlatform, Base
from typing import Sequence
from datetime import datetime as dt

import unittest


class DbTest(unittest.TestCase):
    def test_create_db(self):
        Base.metadata.create_all(engine)

    def test_db_add(self):
        data1 = SportActivity(
            activity_id="eretretre", platform="garmin", sport_type="1"
        )
        with Session(engine) as session:
            session.add(data1)
            session.commit()

    def test_db_add2(self):
        data1 = SportActivity(
            activity_id="ere2323tretre",
            platform=SportPlatform.garmin.value,
            sport_type="1",
        )
        data2 = SportActivity(
            activity_id="3242354sefs",
            platform=SportPlatform.garmin.value,
            sport_type="1",
        )
        data3 = SportActivity(
            activity_id="324233354sefs",
            platform=SportPlatform.coros.value,
            sport_type="1",
        )
        with Session(engine) as session:
            session.add(data1)
            session.add_all([data2, data3])
            session.commit()

    def test_update(self):
        with Session(engine) as session:
            stmt = select(SportActivity).where(SportActivity.activity_id == "eretretre")
            data: SportActivity = session.scalars(stmt).one()
            data.is_sync = "5"
            # data.updated_at = format_datetime(dt.now())
            session.commit()
            session.refresh(data)
            print(data)

    def test_select(self):
        with Session(engine) as session:
            stmt = (
                select(SportActivity)
                .where(
                    and_(
                        col(SportActivity.platform) == SportPlatform.garmin.value,
                        col(SportActivity.is_sync).not_like(SportPlatform.coros.value),
                    )
                )
                .limit(1)
            )
            data = session.exec(stmt).one()
            # data.updated_at = format_datetime(dt.now())
            session.commit()
            print(data)

    def test_select2(self):
        with Session(engine) as session:
            stmt = select(SportActivity).where(
                and_(
                    col(SportActivity.platform) == SportPlatform.garmin.value,
                    col(SportActivity.is_sync).not_like(SportPlatform.coros.value),
                )
            )
            data = session.exec(stmt).all()
            # data.updated_at = format_datetime(dt.now())
            session.commit()
            print(data)

    def test_update2(self):
        with Session(engine) as session:
            stmt = (
                update(SportActivity)
                .where(col(SportActivity.activity_id) == "eretretre")
                .values(is_sync="9")
            )

            session.exec(stmt)
            session.commit()
            print(stmt)

    def test_delete(self):
        with Session(engine) as session:
            stmt = select(SportActivity).where(
                SportActivity.activity_id == "3242354sefs"
            )
            data = session.scalars(stmt).one_or_none()
            if data is not None:
                session.delete(data)
                session.commit()

    def test_delete2(self):
        with Session(engine) as session:
            stmt = delete(SportActivity).where(
                col(SportActivity.activity_id) == "3242354sefs"
            )
            session.exec(stmt)

    def test_delete_all(self):
        with Session(engine) as session:
            stmt = select(SportActivity).where(
                SportActivity.activity_id == "3242354sefs"
            )
            data: Sequence[SportActivity] = session.scalars(stmt).all()
            for d in data:
                session.delete(d)
            session.commit()

    def test_getUnSyncActivites(self):
        getUnSyncActivites(SportPlatform.garmin, SportPlatform.coros)

    def test_getAllActivites(self):
        getAllActivities(SportPlatform.garmin)

    def test_enun(self):
        print(SportPlatform.garmin)


if __name__ == "__main__":
    unittest.main()
