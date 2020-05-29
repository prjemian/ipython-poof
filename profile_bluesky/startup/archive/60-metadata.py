print(__file__)

from datetime import datetime
import apstools


# Set up default metadata

RE.md['beamline_id'] = 'developer'  # TODO: NAME YOUR BEAMLINE HERE
RE.md['proposal_id'] = None
RE.md['pid'] = os.getpid()


import socket 
import getpass 
HOSTNAME = socket.gethostname() or 'localhost' 
USERNAME = getpass.getuser() or 'synApps_xxx_user' 
RE.md['login_id'] = USERNAME + '@' + HOSTNAME
RE.md['BLUESKY_VERSION'] = bluesky.__version__
RE.md['OPHYD_VERSION'] = ophyd.__version__
RE.md['APSTOOLS_VERSION'] = apstools.__version__
RE.md['PYEPICS_VERSION'] = epics.__version__

#import os
#for key, value in os.environ.items():
#    if key.startswith("EPICS"):
#        RE.md[key] = value

import pyRestTable
print("Metadata dictionary (RE.md):")
_tbl = pyRestTable.Table()
_tbl.addLabel("key")
_tbl.addLabel("value")
for k, v in sorted(RE.md.items()):
    # print("RE.md['%s']" % k, "=", v)
    _tbl.addRow((k, v))
print(_tbl)
