print(__file__)

from ophyd import (EpicsScaler, EpicsSignal, EpicsSignalRO,
                   Device, DeviceStatus)
from ophyd import Component as Cpt

import time
#import bluesky.examples
from APS_BlueSky_tools.examples import SynPseudoVoigt


aps_current = EpicsSignalRO("S:SRcurrentAI", name="aps_current")

## Beam Monitor Counts
#bs_bm2 = EpicsSignalRO('BL14B:Det:BM2', name='bs_bm2')
noisy = EpicsSignalRO('xxx:userCalc1', name='noisy')
scaler = EpicsScaler('xxx:scaler1', name='scaler')

# only read a few of the many channels
scaler.channels.read_attrs = "chan1 chan2 chan3 chan6".split()


synthetic_pseudovoigt = SynPseudoVoigt(
    'synthetic_pseudovoigt', m1, 'm1', 
    center=-1.5 + 0.5*np.random.uniform(), 
    eta=0.3 + 0.5*np.random.uniform(), 
    sigma=0.001 + 0.05*np.random.uniform(), 
    scale=1e5)
