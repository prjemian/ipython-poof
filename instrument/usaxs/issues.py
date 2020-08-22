
"""
GitHub issues
"""

__all__ = ["issue253",]

from ..session_logs import logger
logger.info(__file__)

from ..framework import bec
from .motors import guard_slit
from .scalers import upd2
from .tune_guard_slits import tune_Gslits, tune_GslitsCenter, tune_GslitsSize
from apstools.utils import plot_prune_fifo
import bluesky.plan_stubs as bps
import bluesky.plans as bp


def issue253(times=1, md=None):
    _md = dict(
        purpose="test if guard slit motors sometimes stuck in MOVING state",
        URL="https://github.com/APS-USAXS/ipython-usaxs/issues/253"
    )
    _md.update(md or {})

    
    logger.info("# ------- Testing for issue #253 with %d iterations", times)
    yield from bps.repeat(tune_Gslits, num=times)
    for axis in "x y top bot inb outb".split():
        plot_prune_fifo(bec, 3, upd2, getattr(guard_slit, axis))
