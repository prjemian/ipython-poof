try:
    import ophyd

    ophyd.EpicsSignal.set_default_timeout(timeout=10, connection_timeout=5)
except RuntimeError:
    pass

from .motors import *
from .scalers import *
from .tune_guard_slits import *
from .issues import *
