
"""
USAXS motors
"""

__all__ = """
    guard_h_size
    guard_slit
    guard_v_size
    move_motors
    usaxs_slit
""".split()

from ..session_logs import logger
logger.info(__file__)

from ..framework import sd
from apstools.utils import pairwise
from bluesky import plan_stubs as bps
from ophyd import Component, EpicsMotor, EpicsSignal, MotorBundle, Signal
import ophyd


guard_h_size = Signal(name="guard_h_size", value=.5, labels=["terms",])
guard_v_size = Signal(name="guard_v_size", value=.5, labels=["terms",])


def move_motors(*args):
    """
    move one or more motors at the same time, returns when all moves are done

    move_motors(m1, 0)
    move_motors(m2, 0, m3, 0, m4, 0)
    """
    status = []
    for m, v in pairwise(args):
        status.append(m.move(v, wait=False))

    for st in status:
        ophyd.status.wait(st)


class UsaxsSlitDevice(MotorBundle):
    """
    USAXS slit just before the sample

    * center of slit: (x, y)
    * aperture: (h_size, v_size)
    """
    h_size = Component(EpicsMotor, 'lax:m11', labels=("uslit", "motor"))
    x      = Component(EpicsMotor, 'lax:m12', labels=("uslit", "motor"))
    v_size = Component(EpicsMotor, 'lax:m13', labels=("uslit", "motor"))
    y      = Component(EpicsMotor, 'lax:m14', labels=("uslit", "motor"))

    def set_size(self, *args, h=None, v=None):
        """move the slits to the specified size"""
        if h is None:
            raise ValueError("must define horizontal size")
        if v is None:
            raise ValueError("must define vertical size")
        move_motors(self.h_size, h, self.v_size, v)


class GuardSlitMotor(EpicsMotor):
    status_update = Component(EpicsSignal, ".STUP")


class GSlitDevice(MotorBundle):
    """
    guard slit
    * aperture: (h_size, v_size)
    """
    bot  = Component(GuardSlitMotor, 'lax:m6', labels=("gslit", "motor"))
    inb  = Component(GuardSlitMotor, 'lax:m4', labels=("gslit", "motor"))
    outb = Component(GuardSlitMotor, 'lax:m3', labels=("gslit", "motor"))
    top  = Component(GuardSlitMotor, 'lax:m5', labels=("gslit", "motor"))
    x    = Component(EpicsMotor, 'lax:m1', labels=("gslit", "motor"))
    y    = Component(EpicsMotor, 'lax:m2', labels=("gslit", "motor"))

    h_size = Component(EpicsSignal, 'lax:Slit1Hsize')
    v_size = Component(EpicsSignal, 'lax:Slit1Vsize')

    h_sync_proc = Component(EpicsSignal, 'lax:Slit1Hsync.PROC')
    v_sync_proc = Component(EpicsSignal, 'lax:Slit1Vsync.PROC')

    gap_tolerance = 0.02        # actual must be this close to desired
    scale_factor = 1.2    # 1.2x the size of the beam should be good guess for guard slits.
    h_step_away = 0.2     # 0.2mm step away from beam
    v_step_away = 0.1     # 0.1mm step away from beam
    h_step_into = 1.1     # 1.1mm step into the beam (blocks the beam)
    v_step_into = 0.4     # 0.4mm step into the beam (blocks the beam)
    tuning_intensity_threshold = 500

    def set_size(self, *args, h=None, v=None):
        """move the slits to the specified size"""
        if h is None:
            raise ValueError("must define horizontal size")
        if v is None:
            raise ValueError("must define vertical size")
        move_motors(self.h_size, h, self.v_size, v)

    @property
    def h_gap_ok(self):
        gap = self.outb.position - self.inb.position
        return abs(gap - guard_h_size.get()) <= self.gap_tolerance

    @property
    def v_h_gap_ok(self):
        gap = self.top.position - self.bot.position
        return abs(gap - guard_v_size.get()) <= self.gap_tolerance

    @property
    def gap_ok(self):
        return self.h_gap_ok and self.v_h_gap_ok

    def status_update(self):
        yield from bps.abs_set(self.top.status_update, 1)
        yield from bps.sleep(0.05)
        yield from bps.abs_set(self.bot.status_update, 1)
        yield from bps.sleep(0.05)
        yield from bps.abs_set(self.outb.status_update, 1)
        yield from bps.sleep(0.05)
        yield from bps.abs_set(self.inb.status_update, 1)
        yield from bps.sleep(0.05)

        # clear a problem for now
        # TODO: fix the root cause
        # https://github.com/APS-USAXS/ipython-usaxs/issues/253#issuecomment-678503301
        # https://github.com/bluesky/ophyd/issues/757#issuecomment-678524271
        self.top.status_update._set_thread = None
        self.bot.status_update._set_thread = None
        self.outb.status_update._set_thread = None
        self.inb.status_update._set_thread = None


guard_slit = GSlitDevice('', name='guard_slit')
usaxs_slit = UsaxsSlitDevice('', name='usaxs_slit')
