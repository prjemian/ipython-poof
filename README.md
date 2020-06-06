# Instrument Package for Bluesky Development

This package describes the `instrument` configuration
for a Bluesky developer using EPICS synApps.

EPICS base and synApps and areaDetector are running
from docker containers.

IOC prefix | provides
:--- | :---
`sky:` | synApps IOC based on *xxx* module
`adsky:` | AreaDetector IOC using *ADSimDetector*

## INSTALLATION

This will install the package and allow local
modifications of the source files to be used right away.
(Modification of content in this package usually means 
a restart of the ipython session or restart
of the jupyter kernel will be necessary to begin
using the modification.)

    pip install -e .

You may need to install a configuration file for 
the mongodb back end storage for databroker.
An example file is: `instrument/mongodb_config.yml`.

This file should be installed in `~/.config/databroker/mongodb_config.yml` (either by copying the file or making a link).

## USE

To use this instrument package, import as:

    from instrument.collection import *

In an IPython profile directory, put this line in
a python source file in the profile startup directory,
such as `~/.ipython/profile_bluesky/startup/00-instrument.py`.
