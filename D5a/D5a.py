from qcodes import Instrument, VisaInstrument
from qcodes.utils.validators import Numbers, Ints

from .D5a_module import D5a_module

from functools import partial


class D5a(Instrument):
    """
    Qcodes driver for the D5a DAC SPI-rack module.

    functions:
    -   set_dacs_zero   set all DACs to zero voltage

    parameters:
    -   dacN:       get and set DAC voltage
    -   stepsizeN   get the minimum step size corresponding to the span
    -   spanN       get and set the DAC span: '4v uni', '4v bi', or '2.5v bi'

    where N is the DAC number from 1 up to 16
    """
    def __init__(self, name, spi_rack, module, **kwargs):
        super().__init__(name, **kwargs)

        self.d5a = D5a_module(spi_rack, module)

        self._span_set_map = {
           '4v uni':    0,
           '4v bi':     2,
           '2.5v bi':   4,
        }

        self._span_get_map = {v: k for k, v in self._span_set_map.items()}

        self.add_function('set_dacs_zero', call_cmd=self._set_dacs_zero)

        for i in range(16):
            self.add_parameter('dac{}'.format(i + 1),
                               label='DAC {} (V)'.format(i + 1),
                               get_cmd=partial(self._get_dac, i),
                               set_cmd=partial(self._set_dac, i),
                               units='V',
                               delay=0.1)

            self.add_parameter('stepsize{}'.format(i + 1),
                               get_cmd=partial(self._get_stepsize, i),
                               units='V')

            self.add_parameter('span{}'.format(i + 1),
                               get_cmd=partial(self._get_span, i),
                               set_cmd=partial(self._set_span, i))

    def _set_dacs_zero(self):
        for i in range(16):
            self._set_dac(i, 0.0)

    def _get_dac(self, dac):
        return self.d5a.voltages[dac]

    def _set_dac(self, dac, value):
        self.d5a.set_voltage(dac, value)

    def _get_stepsize(self, dac):
        return self.d5a.get_stepsize(dac)

    def _get_span(self, dac):
        return self._span_get_map[self.d5a.span[dac]]

    def _set_span(self, dac, span_str):
        if span_str in self._span_set_map.keys():
            self.d5a.change_span_update(dac, self._span_set_map[span_str])
        else:
            raise KeyError("DAC span of '{}' not recognized.".format(span_str))