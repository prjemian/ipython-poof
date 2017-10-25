print(__file__)

# Bluesky plans (scans)

from bluesky.utils import Msg, separate_devices


def tune_centroid(
        detectors, signal, motor, 
        start, stop, num_points, min_step, 
        step_factor = 2,
        *, md=None):
    """
    plan: tune a motor by maximizing a signal
    
    Initially, traverse the range from start to stop with
    the number of points specified.  Repeat with progressively
    smaller step size until the minimum step size is reached.
    Rescans will be centered on the signal centroid
    (for $I(x)$, centroid$= \sum{I}/\sum{x*I}$)
    with a scan range of 2*step_factor*step of current scan.

    Parameters
    ----------
    detectors : (Signal) list of signals
    signal : (str) name of signal to maximize
    motor : (Mover) positioner to be moved
    start : (float) start of range
    stop : (float) end of range, note: start < stop
    num_points : (int) number of points with each step size
    min_step : (float) smallest step size to use.
        note: For EpicsMotors, ``min_step=min(min_step,motor.MRES)``
        is used.
    step_factor : (float) used in calculating range when 
        maximum is found, note: step_factor > 0

    Example
    -------
    motor = Mover('motor', {'motor': lambda x: x}, {'x': 0})
    det = SynGauss('det', m1, 'm1', center=-1.3, Imax=1e5, sigma=0.021)
    RE(tune_centroid([det], "det", motor, -1.5, -0.5, 10, 0.01))

    m1 = EpicsMotor('xxx:m1', name='m1')
    synthetic_pseudovoigt = SynPseudoVoigt(
            'synthetic_pseudovoigt', m1, 'm1',
            center=-1.5 + 0.5*np.random.uniform(),
            eta=0.3 + 0.5*np.random.uniform(),
            sigma=0.001 + 0.05*np.random.uniform(),
            scale=1e5)
    RE(
        tune_centroid(
            [synthetic_pseudovoigt], "synthetic_pseudovoigt", 
            motor, 
            -2, 0, 10, 0.001
        )
    )
    """
    assert(isinstance(num_points, int))
    assert(num_points > 1)
    assert(start < stop)
    assert(step_factor > 0)
    # assert(isinstance(motor, EpicsMotor))
    if isinstance(motor, EpicsMotor):
        min_step = max(min_step, epics.caget(motor.prefix+".MRES"))
    _md = {'detectors': [det.name for det in detectors],
           'motors': [motor.name],
           'plan_args': {'detectors': list(map(repr, detectors)),
                         'motor': repr(motor),
                         'start': start,
                         'stop': stop,
                         'num_points': num_points,
                         'min_step': min_step,},
           'plan_name': 'tune_centroid',
           'hints': {},
          }
    _md.update(md or {})
    try:
        dimensions = [(motor.hints['fields'], 'primary')]
    except (AttributeError, KeyError):
        pass
    else:
        _md['hints'].setdefault('dimensions', dimensions)

    @bp.stage_decorator(list(detectors) + [motor])
    @bp.run_decorator(md=_md)
    def _tune_core(start, stop, num_points, signal):
        next_pos = start
        step = (stop - start) / (num_points - 1)
        peak_position = None
        cur_I = None
        cur_det = {}
        sum_I = 0		# for peak centroid calculation, I(x)
        sum_xI = 0
        
        while step >= min_step:
            yield Msg('checkpoint')
            yield from bp.mv(motor, next_pos)
            yield Msg('create', None, name='primary')
            for det in detectors:
                yield Msg('trigger', det, group='B')
            yield Msg('wait', None, 'B')
            for det in separate_devices(detectors + [motor]):
                cur_det = yield Msg('read', det)
                if signal in cur_det:
                    cur_I = cur_det[signal]['value']
                    sum_I += cur_I
                    position = motor.read()[motor.name]["value"]
                    sum_xI += position * cur_I

            yield Msg('save')

            if next_pos < stop: # FIXME: "<" assumes sign of scan direction
                next_pos += step
            else:
                if sum_I == 0:
                    return
                peak_position = sum_xI / sum_I  # centroid
                # TODO: report current peak_position in metadata
                RE.md["peak_position"] = str(peak_position)
                start = peak_position - step_factor*step
                stop = peak_position + step_factor*step
                step = (stop - start) / (num_points - 1)
                next_pos = start

        # finally, move to peak position
        if peak_position is not None:
            RE.md["peak_position"] = peak_position
            yield from bp.mv(motor, peak_position)

    yield from _tune_core(start, stop, num_points, signal)
    print("Peak at ", RE.md["peak_position"])
    return


if False:       # demo & testing code
    simulate_peak(calc1, m1, profile="lorentzian")
    RE(tune_centroid([noisy], "noisy", m1, -2, 0, 10, 0.00001))
    
    RE(
        tune_centroid(
            [synthetic_pseudovoigt], "synthetic_pseudovoigt", m1, 
            -2, 0, 10, 0.00001
        )
    )
    RE(
        bp.adaptive_scan(
            [synthetic_pseudovoigt], 'synthetic_pseudovoigt', m1, 
            start=-2, stop=0, min_step=0.01, max_step=1, 
            target_delta=500, backstep=True
        )
    )
