"""
USAXS scaler0 (only)
"""

__all__ = """
    scaler0
    clock  I0  I00  upd2  trd  I000
    CLOCK_SIGNAL
    I0_SIGNAL
    I00_SIGNAL
    I000_SIGNAL
    UPD_SIGNAL
    TRD_SIGNAL
""".split()

from ..session_logs import logger

logger.info(__file__)

from ophyd import Component, EpicsSignal, EpicsScaler, EpicsSignalRO
from ophyd.scaler import ScalerCH


class myScalerCH(ScalerCH):
    display_rate = Component(EpicsSignal, ".RATE")


scaler0 = myScalerCH("lax:scaler1", name="scaler0", labels=["detectors",])

CLOCK_SIGNAL = scaler0.channels.chan01
I0_SIGNAL = scaler0.channels.chan02
I00_SIGNAL = scaler0.channels.chan03
UPD_SIGNAL = scaler0.channels.chan04
TRD_SIGNAL = scaler0.channels.chan05
I000_SIGNAL = scaler0.channels.chan06

clock = CLOCK_SIGNAL.s
I0 = I0_SIGNAL.s
I00 = I00_SIGNAL.s
upd2 = UPD_SIGNAL.s
trd = TRD_SIGNAL.s
I000 = I000_SIGNAL.s

CLOCK_SIGNAL.chname.put("clock")
I0_SIGNAL.chname.put("I0")
I00_SIGNAL.chname.put("I00")
I000_SIGNAL.chname.put("I000")
UPD_SIGNAL.chname.put("upd2")
TRD_SIGNAL.chname.put("trd")

scaler0.select_channels(None)

for item in (clock, I0, I00, upd2, trd, I000):
    item._ophyd_labels_ = set(["channel", "counter",])
