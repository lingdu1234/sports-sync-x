from app.utils.sys_config import cfg
import os
from app.utils.const import SportPlatform
from app.garmin.garmin_client_x import get_garmin_client
import unittest


class GarminTest(unittest.TestCase):
    def test_garminCN_upload(self):
        client = get_garmin_client(SportPlatform.garminCN)
        path = "465929716908458004"
        file = os.path.join(cfg.COROS_FIT_DIR, f"{path}.fit")
        client.uploadActivity(file)


if __name__ == "__main__":
    _ = unittest.main()
