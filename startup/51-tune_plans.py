print(__file__)

# Bluesky plans (scans)

from bluesky.utils import Msg, separate_devices


def maximize_signal(
        detectors, signal, motor, 
        start, stop, num_points, min_step, 
        *, md=None):
    """
    tune a motor by maximizing a signal
    """
    assert(isinstance(num_points, int))
    assert(num_points > 1)
    assert(start < stop)
    assert(isinstance(motor, EpicsMotor))
    min_step = max(min_step, epics.caget(motor.prefix+".MRES"))
    _md = {'detectors': [det.name for det in detectors],
           'motors': [motor.name],
           'plan_args': {'detectors': list(map(repr, detectors)),
                         'motor': repr(motor),
                         'start': start,
                         'stop': stop,
                         'num_points': num_points,
                         'min_step': min_step,},
           'plan_name': 'maximize_signal',
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
        max_I = None
        peak_position = None
        cur_I = None
        cur_det = {}
        
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
                    if max_I is None or cur_I > max_I:
                        motor.get()
                        max_I = cur_I
                        peak_position = motor.user_readback.value

            yield Msg('save')

            if next_pos < stop:	# FIXME: "<" assumes sign of scan direction
                next_pos += step
            else:
                # TODO: use COM instead
                start = peak_position - step
                stop = peak_position + step
                step = (stop - start) / (num_points - 1)
                next_pos = start

        # finally, move to peak position
        if peak_position is not None:
            yield from bp.mv(motor, peak_position)

    return (yield from _tune_core(start, stop, num_points, signal))


if False:		# demo & testing code
    RE(maximize_signal([noisy], "noisy", m1, -2, 0, 10, 0.00001))
