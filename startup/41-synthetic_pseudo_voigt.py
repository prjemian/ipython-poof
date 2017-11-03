print(__file__)


import bluesky.examples


class SynPseudoVoigt(bluesky.examples.Reader):
    """
    Evaluate a point on a pseudo-Voigt based on the value of a motor.
    
    :see: https://en.wikipedia.org/wiki/Voigt_profile

    Parameters
    ----------
    name :(str) name of detector signal
    motor_field : (str) name of Mover field
    center : (float) location of maximum value
    eta : (float) 0 <= eta < 1.0: Lorentzian fraction
    scale : (float) scale >= 1 : scale factor
    sigma : (float) sigma > 0 : width

    Example
    -------
    motor = Mover('motor', {'motor': lambda x: x}, {'x': 0})
    det = SynPseudoVoigt('det', motor, 'motor', center=0, eta=0.5, scale=1, sigma=1)
    """

    def __init__(self, name, motor, motor_field, center, 
                eta=0.5, scale=1, sigma=1, **kwargs):
        noise = "poisson"
        assert(0 <= eta < 1.0)
        assert(scale >= 1)
        assert(sigma > 0)

        def f_lorentzian(x, gamma):
            #return gamma / np.pi / (x**2 + gamma**2)
            return 1 / np.pi / gamma / (1 + (x/gamma)**2)

        def f_gaussian(x, sigma):
            numerator = np.exp(-0.5 * (x / sigma) ** 2)
            denominator = sigma * np.sqrt(2 * np.pi)
            return numerator / denominator

        def pvoigt():
            m = motor.read()[motor_field]['value']
            v = eta * f_lorentzian(m - center, sigma)
            v += (1-eta) * f_gaussian(m - center, sigma)
            v *= scale
            v = int(np.random.poisson(np.round(v), None))
            return v

        super().__init__(name, {name: pvoigt}, **kwargs)


synthetic_pseudovoigt = SynPseudoVoigt(
	'synthetic_pseudovoigt', m1, 'm1', 
    center=-1.2, eta=0.5, sigma=0.01, scale=1e5)
