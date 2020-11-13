#!/usr/bin/env python

"""
See https://github.com/APS-USAXS/ipython-usaxs/issues/366 issue.
"""

from instrument.session_logs import logger
logger.info(__file__)

from bluesky import plan_stubs as bps
from instrument.devices import calcs
from ophyd import EpicsMotor
import datetime

m9 = EpicsMotor("sky:m9", name="m9")


class Watcher:

    idle = None
    idle_interval = 2       # seconds
    permit = None
    trigger_signal = None

    def idle_reporter(self):
        ts = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
        print(
            f"{ts}: auto_collect is waiting for next command from EPICS ...",
            end="\r"
        )

    def remote_ops(self):
        """
        Bluesky plan to report when motor is idle.

        similar to https://github.com/APS-USAXS/ipython-usaxs/issues/366
        """
        logger.info("starting watcher")
        yield from bps.null()
        if self.permit is not None and self.trigger_signal is not None:

            yield from bps.mv(
                self.permit, 1,
                self.trigger_signal, 0,
            )
            while self.permit.get() in (1, "yes"):
                if self.trigger_signal.get() in (1, "start"):
                    print()
                    logger.info("triggered")
                    yield from bps.mv(
                        m9, -m9.position
                    )
                    yield from bps.mv(self.trigger_signal, 0)
                    logger.info("trigger complete")
                else:
                    yield from bps.sleep(self.idle_interval)
                    self.idle_reporter()

        print()
        logger.info("ending watcher")

watcher = Watcher()
watcher.idle = m9.motor_done_move
watcher.permit = calcs.calc9.channels.A.input_value
watcher.trigger_signal = calcs.calc9.channels.B.input_value
