"""
"""

__all__ = []

from ..session_logs import logger

logger.info(__file__)

import gi

gi.require_version("Hkl", "5.0")

import apstools
import bluesky
import databroker
from datetime import datetime
import epics
import event_model
import getpass
import h5py
import hkl
import matplotlib
import numpy
import ophyd
import os
import pyRestTable
import socket
import spec2nexus

from .initialize import RE

# Set up default metadata

RE.md["beamline_id"] = "poof"
RE.md["proposal_id"] = "testing"
RE.md["pid"] = os.getpid()

HOSTNAME = socket.gethostname() or "localhost"
USERNAME = getpass.getuser() or "APS poof user"
RE.md["login_id"] = USERNAME + "@" + HOSTNAME

# useful diagnostic to record with all data
RE.md["versions"] = dict(
    apstools=apstools.__version__,
    bluesky=bluesky.__version__,
    databroker=databroker.__version__,
    epics=epics.__version__,
    event_model=event_model.__version__,
    h5py=h5py.__version__,
    hkl=hkl.__version__,
    matplotlib=matplotlib.__version__,
    numpy=numpy.__version__,
    ophyd=ophyd.__version__,
    pyRestTable=pyRestTable.__version__,
    spec2nexus=spec2nexus.__version__,
)
