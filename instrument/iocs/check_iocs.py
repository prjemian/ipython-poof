"""
check that our EPICS soft IOCs are running
"""

__all__ = []

from ..session_logs import logger

logger.info(__file__)

import epics
import logging
import os


up = epics.caget("sky:UPTIME", timeout=1)
if up is None:
    logger.info("EPICS IOCs not running.  Starting them now...")
    start_ioc_script = os.path.join(
        os.environ["HOME"], "bin", "start_iocs.sh",
    )
    os.system(start_ioc_script)
    logger.debug("IOCs started")
else:
    logger.info("EPICS IOCs ready...")
