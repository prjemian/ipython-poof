print(__file__)

# Bluesky plans (scans)
from APS_BlueSky_tools.plans import *

def demo_tuning():       # demo & testing code

    simulate_peak(calc1, m1, profile="lorentzian")
    RE(bp.tune_centroid([noisy], "noisy", m1, -2, 0, 0.00001, 10))
    
    RE(
        bp.tune_centroid(
            [synthetic_pseudovoigt], "synthetic_pseudovoigt", m1, 
            -2, 0, 0.00001, 10,
            snake=True
        )
    )
    RE(
        bp.adaptive_scan(
            [synthetic_pseudovoigt], 'synthetic_pseudovoigt', m1, 
            start=-2, stop=0, min_step=0.01, max_step=1, 
            target_delta=500, backstep=True
        )
    )
