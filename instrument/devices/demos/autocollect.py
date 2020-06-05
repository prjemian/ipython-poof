
"""
automated data collection

    RE(auto_collect.remote_ops())
"""

__all__ = [
    'AutoCollectDataDevice', 
    'auto_collect',
    ]

from ..session_logs import logger
logger.info(__file__)

from bluesky import plan_stubs as bps
from ophyd import Component, Device, EpicsSignal, EpicsSignalRO
import os


# mock this standard USAXS plan
def preUSAXStune():
    logger.info("running preUSAXStune()")
    yield from bps.null()

# mock this standard USAXS plan
def useModeRadiography():
    logger.info("running useModeRadiography()")
    yield from bps.null()

# mock this standard USAXS plan
def run_command_file(fname):
    logger.info("running run_command_file('%s')", fname)
    yield from bps.null()


class AutoCollectDataDevice(Device):
    acquire = Component(EpicsSignal, "Start", string=True)
    commands = Component(EpicsSignal, "StrInput", string=True)
    permit = Component(EpicsSignal, "Permit", string=True)
    idle_interval = 2       # seconds

    def remote_ops(self, *args, **kwargs):
        yield from bps.mv(self.permit, "enable")
        yield from bps.sleep(1)

        logger.info("waiting for user commands")
        while self.permit.get() in (1, "enable"):
            if self.acquire.get() in (1, "start"):
                logger.debug("starting user commands")
                command = self.commands.get()
                if command == "preUSAXStune":
                    yield from preUSAXStune()
                elif command == "useModeRadiography":
                    yield from useModeRadiography()
                elif os.path.exists(command):
                    yield from run_command_file(command)
                else:
                    logger.warning("unrecognized command: %s", command)
                yield from bps.mv(self.acquire, 0)
                logger.info("waiting for next user command")
            else:
                yield from bps.sleep(self.idle_interval)


auto_collect = AutoCollectDataDevice(
    "9idcLAX:AutoCollection", 
    name="auto_collect")
