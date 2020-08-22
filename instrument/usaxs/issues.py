
"""
GitHub issues
"""

__all__ = ["issue253", "trim_all"]

from ..session_logs import logger
logger.info(__file__)

from ..framework import bec
from .motors import guard_slit
from .scalers import upd2
from .tune_guard_slits import tune_Gslits, tune_GslitsCenter, tune_GslitsSize
import bluesky.plan_stubs as bps
import bluesky.plans as bp
import matplotlib.pyplot as plt


_tune_number = 0


def select_figure(x, y):
    figure_name = f"{y.name} vs {x.name}"
    if figure_name in plt.get_figlabels():
        print(figure_name)
        return plt.figure(figure_name)


def select_live_plot(bec, signal):
    for live_plot_dict in bec._live_plots.values():
        live_plot = live_plot_dict.get(signal.name)
        if live_plot is not None:
            return live_plot


def trim_plot(bec, n, x, y):
    liveplot = select_live_plot(bec, y)
    assert liveplot is not None
    fig = select_figure(x, y)
    assert fig is not None
    ax = fig.axes[0]
    while len(ax.lines) > n:
        try:
            ax.lines.pop(0).remove()
        except ValueError as exc:
            logger.warning(
                "%s vs %s: mpl remove() error: %s",
                y.name, x.name, str(exc))
    ax.legend()
    liveplot.update_plot()


def trim_all(n=3):
    for axis in "y x top bot outb inb".split():     # in order of tune
        trim_plot(bec, n, getattr(guard_slit, axis), upd2)


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
    trim_all()


def issue253(times=1):
    global _tune_number
    logger.info("# ------- Testing for issue #253 with %d iterations", times)
    _tune_number = 0
    yield from bps.repeat(_full_guard_slits_tune_, num=times)
