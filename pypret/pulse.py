""" Provides a class to simulate an ultrashort optical pulse using its envelope
description.

The temporal envelope is denoted as `field` and the spectral envelope as
`spectrum` in the code and the function signatures.
"""
import numpy as np
from . import io
from . import lib
from .frequencies import convert


class Pulse(io.IO):
    """ A class for modelling femtosecond pulses by their envelope.
    """
    _io_store = ['ft', 'wl0', '_field', '_spectrum']

    def __init__(self, ft, wl0, unit='wl'):
        """ Initializes an optical pulse described by its envelope.

        Parameters
        ----------
        ft : FourierTransform
            A ``FourierTransform`` instance that specifies a temporal and
            spectral grid.
        wl0 : float
            The center frequency of the pulse.
        unit : str
            The unit in which the center frequency is specified. Can be either
            of ``wl``, ``om``, ``f``, or ``k``. See ``frequencies`` for more
            information. Default is ``wl``.
        """
        self.ft = ft
        self.wl0 = convert(wl0, unit, 'wl')
        self._field = np.zeros(ft.N, dtype=np.complex128)
        self._spectrum = np.zeros(ft.N, dtype=np.complex128)
        self._post_init()

    def copy(self):
        """ Returns a copy of the pulse object.

        Note that they still reference the same `FourierTransform` instance,
        which is assumed to be immutable.
        """
        p = Pulse(self.ft, self.wl0)
        p.spectrum = self.spectrum
        return p

    def _post_init(self):
        ft = self.ft
        self.t = ft.t
        self.w = ft.w
        self.dt = ft.dt
        self.dw = ft.dw
        self.N = ft.N

        self.w0 = convert(self.wl0, 'wl', 'om')
        self.wl = convert(self.w + self.w0, 'om', 'wl')

    @property
    def field(self):
        """ The complex-valued temporal envelope of the pulse.

        On read access returns a copy of the internal array. On write
        access the spectral envelope is automatically updated.
        """
        return self._field.copy()

    @field.setter
    def field(self, val):
        self._field[:] = val
        self.update_spectrum()

    @property
    def spectrum(self):
        """ The complex-valued spectral envelope of the pulse.

        On read access returns a copy of the internal array. On write
        access the temporal envelope is automatically updated.
        """
        return self._spectrum.copy()

    @spectrum.setter
    def spectrum(self, val):
        self._spectrum[:] = val
        self.update_field()

    def update_field(self):
        """ Manually updates the field from the (modified) spectrum.
        """
        self._field[:] = self.ft.backward(self._spectrum)

    def update_spectrum(self):
        """ Manually updates the spectrum from the (modified) field.
        """
        self._spectrum[:] = self.ft.forward(self._field)

    @property
    def intensity(self):
        """ The temporal intensity profile of the pulse in vacuum.

        Only read access.
        """
        return lib.abs2(self._field)

    @property
    def amplitude(self):
        """ The temporal amplitude profile of the pulse in vacuum.

        Only read access.
        """
        return self._field.abs()

    @property
    def phase(self):
        """ The temporal phase of the pulse.

        Only read access.
        """
        return lib.phase(self._field)

    @property
    def spectral_intensity(self):
        """ The spectral intensity profile of the pulse in vacuum.

        Only read access.
        """
        return lib.abs2(self._spectrum)

    @property
    def spectral_amplitude(self):
        """ The spectral amplitude profile of the pulse in vacuum.

        Only read access.
        """
        return self._spectrum.abs()

    @property
    def spectral_phase(self):
        """ The spectral phase of the pulse.

        Only read access.
        """
        return lib.phase(self._spectrum)

    @property
    def time_bandwidth_product(self):
        """ Calculates the rms time-bandwidth product of the pulse.

            In this definition a transform-limited Gaussian pulse has a
            time-bandwidth product of 0.5. So the number returned by this
            function will always be >= 0.5.
        """
        return (lib.standard_deviation(self.t, self.intensity) *
                lib.standard_deviation(self.w, self.spectral_intensity))

    @property
    def fwhm(self):
        """ The FWHM of the temporal intensity profile.

        Only read access.
        """
        return lib.fwhm(self.t, self.intensity)