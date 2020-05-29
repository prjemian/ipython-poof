print(__file__)

"""various detectors and other signals"""

from apstools.signals import SynPseudoVoigt


## Beam Monitor Counts
#bs_bm2 = EpicsSignalRO('BL14B:Det:BM2', name='bs_bm2')
noisy = EpicsSignalRO('sky:userCalc1', name='noisy')
scaler = EpicsScaler('sky:scaler1', name='scaler')

# only read a few of the many channels
scaler.channels.read_attrs = "chan1 chan2 chan3 chan6".split()

m1.wait_for_connection()
synthetic_pseudovoigt = SynPseudoVoigt(
    'synthetic_pseudovoigt', m1, 'm1', 
    center=-1.5 + 0.5*np.random.uniform(), 
    eta=0.3 + 0.5*np.random.uniform(), 
    sigma=0.001 + 0.05*np.random.uniform(), 
    scale=1e5)
