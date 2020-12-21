"""
details of the sky IOC from iocStats
"""

__all__ = [
    "iocsky",
]

from ..session_logs import logger

logger.info(__file__)

from apstools.synApps import IocStatsDevice

iocsky = IocStatsDevice("sky:", name="iocsky")
