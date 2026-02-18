from app.garmin.gamin_client_cn import GarminClientCN
from app.garmin.gamin_client_com import GarminClientCOM
from app.utils.const import GarminAuthDomain
from app.utils.sys_config import cfg
from app.database.db import SportPlatform


def get_garmin_client(platform: SportPlatform) -> GarminClientCN | GarminClientCOM:
    email, password, auth_domain = (
        (cfg.GARMIN_EMAIL, cfg.GARMIN_PASSWORD, GarminAuthDomain.COM)
        if platform == SportPlatform.garminCOM
        else (cfg.GARMIN_EMAIL_CN, cfg.GARMIN_PASSWORD_CN, GarminAuthDomain.CN)
    )
    return (
        GarminClientCOM(email, password, auth_domain, cfg.GARMIN_NEWEST_NUM)
        if platform == SportPlatform.garminCOM
        else GarminClientCN(email, password, auth_domain, cfg.GARMIN_NEWEST_NUM)
    )
