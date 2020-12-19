"""
Provide a simplified UI for hklpy diffractometer users.

The user must define a diffractometer instance, then
register that instance here calling `selectDiffractometer(instance)`.

FUNCTIONS

.. autosummary::

    ~cahkl
    ~cahkl_table
    ~calcEnergy
    ~calcUB
    ~listSamples
    ~newSample
    ~selectDiffractometer
    ~setEnergy
    ~setor
    ~showSample
    ~showSelectedDiffractometer
    ~updateSample
    ~wh

.. needed

    ~changeSample
    ~hklArray
    ~mvhkl          # move to an hkl
    ~realPosition
    ~scanhkl
    ~scanhkl_array
    ~scanhkl_energy
    ~scanhkl_test
    ~setWavelength
    ~simMove
    ~table2csv      # is duplicate?

EXAMPLES::

    # work with our 4-circle simulator
    selectDiffractometer(fourc)

    # sample is the silicon standard
    a0=5.4310196; newSample("silicon standard", a0, a0, a0, 90, 90, 90)

    listSamples()

    # define the first orientation reflection, specify each motor position
    # motor values given in "diffractometer order"::
    #     print(_geom_.calc.physical_axis_names)
    r1 = setor(4, 0, 0, -145.451, 0, 0, 69.0966, wavelength = 1.54)

    # move to the position of the second reflection: (040)
    %mov fourc.omega -145.451 fourc.chi 90 fourc.phi 0 fourc.tth 69.0966

    # define the second orientation reflection, use current motor positions
    r2 = setor(0, 4, 0)

    calcUB(r1, r2)

    # calculate reflection, record motor positions before and after
    p_before = fourc.real_position
    fourc.forward(4, 0, 0)
    p_after = fourc.real_position

    # show if the motors moved
    if p_before != p_after:
        print("fourc MOVED!")
    else:
        print("fourc did not move.")

    # cubic sample: show r2, the (040)
    fourc.inverse(-145.5, 90, 0, 69)
    # verify that the (0 -4 0) is half a rotation away in chi
    fourc.inverse(-145.5, -90, 0, 69)

"""

__all__ = """
    cahkl
    cahkl_table
    calcEnergy
    calcUB
    changeSample
    listSamples
    newSample
    selectDiffractometer
    setEnergy
    setor
    showSample
    showSelectedDiffractometer
    updateSample
    wh
""".split()

from instrument.session_logs import logger

logger.info(__file__)

import gi
gi.require_version("Hkl", "5.0")
from hkl.diffract import Diffractometer
from hkl.util import Lattice
import pyRestTable


_geom_ = None  # selected diffractometer geometry


def _check_geom_selected_(*args, **kwargs):
    """Raise ValueError i no diffractometer geometry is selected."""
    if _geom_ is None:
        raise ValueError(
            "No diffractometer selected."
            " Call 'selectDiffractometer(diffr)' where"
            " 'diffr' is a diffractometer instance."
        )


def cahkl(h, k, l):
    """
    Calculate motor positions for one reflection.
    
    Returns a namedtuple.
    Does not move motors.
    """
    _check_geom_selected_()
    # TODO: make certain this will not move the motors!
    return _geom_.forward(h, k, l)


def cahkl_table(reflections):
    """Print a table with motor positions for each reflection given."""
    _check_geom_selected_()
    print(_geom_.forwardSolutionsTable(reflections))


def calcUB(r1, r2, wavelength=None):
    """Compute the UB matrix with two reflections."""
    _check_geom_selected_()
    _geom_.calc.sample.compute_UB(r1, r2)
    print(_geom_.calc.sample.UB)


def changeSample(sample):
    """Pick a known sample to be the current selection."""
    _check_geom_selected_()
    if sample not in _geom_.calc._samples:
        raise KeyError(
            f"Sample '{sample}' is unknown."
            f"  Known samples: {list(_geom_.calc._samples.keys())}"
        )
    _geom_.calc.sample = sample
    showSample(sample)


def listSamples(verbose=True):
    """List all defined crystal samples."""
    _check_geom_selected_()
    # always show the default sample first
    current_name = _geom_.calc.sample_name
    showSample(current_name, verbose=verbose)

    # now, show any other samples
    for sample in _geom_.calc._samples.keys():
        if sample != current_name:
            if verbose:
                print("")
            showSample(sample, verbose=verbose)


def newSample(nm, a, b, c, alpha, beta, gamma):
    """Define a new crystal sample."""
    _check_geom_selected_()
    if nm in _geom_.calc._samples:
        logger.warning(
            (
                "Sample '%s' is already defined."
                "  Use 'updateSample()' to change lattice parameters"
                " on the *current* sample."
            ),
            nm
        )
    else:
        lattice=Lattice(
                a=a, b=b, c=c, alpha=alpha, beta=beta, gamma=gamma)
        _geom_.calc.new_sample(nm, lattice=lattice)
    showSample()


def selectDiffractometer(instrument=None):
    """Name the diffractometer to be used."""
    global _geom_
    if instrument is None or isinstance(instrument, Diffractometer):
        _geom_ = instrument
    else:
        raise TypeError(
            f"{instrument} must be a 'Diffractometer' subclass"
        )


def setEnergy(value, units=None):
    """
    Set the energy (thus wavelength) to be used.

    Also known as ``calcE`` or ``calcEnergy``
    """
    _check_geom_selected_()
    if units is not None:
        _geom_.energy_units.put("eV")
    _geom_._energy_changed(value)

# synonym
calcEnergy = setEnergy


def setor(h, k, l, *args, wavelength=None, **kwargs):
    """Define a crystal reflection and its motor positions."""
    _check_geom_selected_()
    if len(args) == 0:
        if len(kwargs) == 0:
            pos = _geom_.real_position
        else:
            pos = [
                kwargs[m]
                for m in _geom_.calc.physical_axis_names
                if m in kwargs
            ]
    else:
        pos = args
    # TODO: How does libhkl get the wavelength on a reflection?
    if wavelength not in (None, 0):
        _geom_.calc.wavelength = wavelength
    refl = _geom_.calc.sample.add_reflection(h, k, l, position=pos)
    return refl


def showSample(sample_name = None, verbose=True):
    """Print the default sample name and crystal lattice."""
    _check_geom_selected_()
    sample_name = sample_name or _geom_.calc.sample_name
    sample = _geom_.calc._samples[sample_name]

    title = sample_name
    if sample_name == _geom_.calc.sample.name:
        title += " (current)"

    # Print Lattice more simply (than as a namedtuple).
    lattice = [
        getattr(sample.lattice, parm)
        for parm in sample.lattice._fields
    ]
    if verbose:
        tbl = pyRestTable.Table()
        tbl.addLabel("key")
        tbl.addLabel("value")
        tbl.addRow(("name", sample_name))
        tbl.addRow(("lattice", lattice))
        for i, r in enumerate(sample.reflections):
            tbl.addRow((f"reflection {i+1}", r))
        tbl.addRow(("U", sample.U))
        tbl.addRow(("UB", sample.UB))

        print(f"Sample: {title}\n")
        print(tbl)
    else:
        print(f"{title}: {lattice}")


def showSelectedDiffractometer(instrument=None):
    """Print the name of the selected diffractometer."""
    if _geom_ is None:
        print("No diffractometer selected.")
    print(_geom_.name)


def updateSample(a,b,c,alpha,beta,gamma):
    """Update current sample lattice."""
    _check_geom_selected_()
    _geom_.calc.sample.lattice = (a,b,c,alpha,beta,gamma) # define the current sample
    showSample(_geom_.calc.sample.name, verbose=False)


def wh():
    """Print a table describing the selected diffractometer."""
    _check_geom_selected_()
    _geom_.wh()
