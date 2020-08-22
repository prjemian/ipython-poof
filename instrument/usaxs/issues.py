
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
import bluesky.plan_stubs as bps
import bluesky.plans as bp


_tune_number = 0

def _full_guard_slits_tune_():
    global _tune_number
    _tune_number += 1
    _md = dict(
        purpose="test if guard slit motors sometimes stuck in MOVING state",
        URL="https://github.com/APS-USAXS/ipython-usaxs/issues/253",
        tune_number=_tune_number,
    )
    logger.info("# tune number: %d", _tune_number)
    yield from tune_Gslits(md=_md)
    for axis in "y x top bot outb inb".split():     # in order of tune
        bec.plot_prune_fifo(3, upd2, getattr(guard_slit, axis))


def issue253(times=1):
    global _tune_number
    logger.info("# ------- Testing for issue #253 with %d iterations", times)
    _tune_number = 0
    yield from bps.repeat(_full_guard_slits_tune_, num=times)
