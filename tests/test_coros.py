import os
from app.coros.coros_client import get_coros_client
import unittest


class CorosTest(unittest.TestCase):
    def test_upload(self):
        # 332731032
        path = os.path.join(os.getcwd(), "334815527.zip")
        print(path)
        client = get_coros_client()
        client.uploadActivity(path)


if __name__ == "__main__":
    _ = unittest.main()
