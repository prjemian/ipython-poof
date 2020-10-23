
"""
configure for data collection in a console session
"""

from .session_logs import logger
logger.info(__file__)

from . import mpl

logger.info("Start soft IOC dockers if PVs not available")
from .iocs import check_iocs

logger.info("bluesky framework")

from .framework import *
from .devices import *
from .callbacks import *
from .plans import *
from .utils import *

from apstools.utils import *

from .session_logs import logger
