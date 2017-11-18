print(__file__)

from datetime import datetime


# Set up default metadata

RE.md['beamline_id'] = 'developer'  # TODO: NAME YOUR BEAMLINE HERE
RE.md['proposal_id'] = None
RE.md['pid'] = os.getpid()


import socket 
import getpass 
HOSTNAME = socket.gethostname() or 'localhost' 
USERNAME = getpass.getuser() or 'synApps_xxx_user' 
RE.md['login_id'] = USERNAME + '@' + HOSTNAME

#import os
#for key, value in os.environ.items():
#    if key.startswith("EPICS"):
#        RE.md[key] = value
