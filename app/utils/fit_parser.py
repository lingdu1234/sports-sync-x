import zipfile
import os
from typing import Optional

import fitdecode


def get_device_from_fit(file_path: str) -> Optional[str]:
    """
    仅用户部分无法从返回数据获取设备平台coros fit

    :param file_path: 文件路径
    :type file_path: str
    :return: 设备名称
    :rtype: str | None
    """
    try:
        if not os.path.exists(file_path):
            return None
        with fitdecode.FitReader(file_path) as fit:
            for frame in fit:
                if frame.frame_type == fitdecode.FIT_FRAME_DATA:
                    manufacturer = frame.get_value("manufacturer")  # pyright: ignore[reportAttributeAccessIssue]
                    if manufacturer is not None and type(manufacturer) is str:
                        return str(manufacturer)

    except Exception as e:
        print(f"Error parsing FIT file {file_path}: {e}")
        import traceback

        traceback.print_exc()
        return None

    # class ZipFileHandler:
    #     @staticmethod
    #     def extract_fit_from_zip(zip_path: str, extract_dir: str = None) -> Optional[str]:
    #         try:
    #             if not os.path.exists(zip_path):
    #                 return None

    #             if extract_dir is None:
    #                 extract_dir = os.path.dirname(zip_path)

    #             with zipfile.ZipFile(zip_path, "r") as zip_ref:
    #                 fit_files = [
    #                     f for f in zip_ref.namelist() if f.lower().endswith(".fit")
    #                 ]

    #                 if not fit_files:
    #                     return None

    #                 fit_file = fit_files[0]
    #                 extract_path = os.path.join(extract_dir, os.path.basename(fit_file))

    #                 zip_ref.extract(fit_file, extract_dir)

    #                 extracted_file = os.path.join(extract_dir, fit_file)
    #                 if os.path.exists(extracted_file):
    #                     return extracted_file
    #                 elif os.path.exists(extract_path):
    #                     return extract_path

    #                 return None
    #         except Exception as e:
    #             print(f"Error extracting FIT from ZIP {zip_path}: {e}")
    #             return None


@staticmethod
def extract_all_from_zip(zip_path: str, extract_dir: str | None = None):
    try:
        if not os.path.exists(zip_path):
            return

        if extract_dir is None:
            extract_dir = os.path.dirname(zip_path)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
    except Exception as e:
        print(f"Error extracting all from ZIP {zip_path}: {e}")
        return
