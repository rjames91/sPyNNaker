from spinn_utilities.overrides import overrides

from spynnaker.pyNN.models.abstract_models import AbstractContainsUnits
from spynnaker.pyNN.models.neural_properties import NeuronParameter
from spynnaker.pyNN.utilities.ranged.spynakker_ranged_dict import \
    SpynakkerRangeDictionary
from .abstract_threshold_type import AbstractThresholdType

from data_specification.enums import DataType

from enum import Enum

V_THRESH = "v_thresh"
MIN_THRESH = "min_thresh"
MAX_THRESH = "max_thresh"
UP_THRESH = "up_thresh"
DOWN_THRESH = "down_thresh"

class _ADAPTIVE_TYPES(Enum):
    V_THRESH = (1, DataType.S1615)
    MIN_THRESH = (2, DataType.S1615)
    MAX_THRESH = (3, DataType.S1615)
    UP_THRESH = (4, DataType.S1615)
    DOWN_THRESH = (5, DataType.S1615)

    def __new__(cls, value, data_type, doc=""):
        # pylint: disable=protected-access
        obj = object.__new__(cls)
        obj._value_ = value
        obj._data_type = data_type
        obj.__doc__ = doc
        return obj

    @property
    def data_type(self):
        return self._data_type


class ThresholdTypeAdaptive(AbstractThresholdType, AbstractContainsUnits):
    """ A threshold that is a linear adaptive value
    """
    __slots__ = [
        "_data",
        "_n_neurons",
        "_units"]

    def __init__(self, n_neurons, v_thresh, min_thresh, max_thresh,
                 up_thresh, down_thresh):
        self._units = {
            V_THRESH: "mV",
            MIN_THRESH: "mV",
            MAX_THRESH: "mV",
            UP_THRESH: "mV",
            DOWN_THRESH: "mV",
        }

        self._n_neurons = n_neurons
        self._data = SpynakkerRangeDictionary(size=n_neurons)
        self._data[V_THRESH] = v_thresh
        self._data[MIN_THRESH] = min_thresh
        self._data[MAX_THRESH] = max_thresh
        self._data[UP_THRESH] = up_thresh
        self._data[DOWN_THRESH] = down_thresh

    @property
    def v_thresh(self):
        return self._data[V_THRESH]

    @v_thresh.setter
    def v_thresh(self, v_thresh):
        self._data.set_value(key=V_THRESH, value=v_thresh)

    @property
    def min_thresh(self):
        return self._data[MIN_THRESH]

    @min_thresh.setter
    def min_thresh(self, value):
        self._data.set_value(key=MIN_THRESH, value=value)

    @property
    def max_thresh(self):
        return self._data[MAX_THRESH]

    @max_thresh.setter
    def max_thresh(self, value):
        self._data.set_value(key=MAX_THRESH, value=value)

    @property
    def up_thresh(self):
        return self._data[UP_THRESH]

    @up_thresh.setter
    def up_thresh(self, value):
        self._data.set_value(key=UP_THRESH, value=value)

    @property
    def down_thresh(self):
        return self._data[DOWN_THRESH]

    @down_thresh.setter
    def down_thresh(self, value):
        self._data.set_value(key=DOWN_THRESH, value=value)

    @overrides(AbstractThresholdType.get_n_threshold_parameters)
    def get_n_threshold_parameters(self):
        return 5

    @overrides(AbstractThresholdType.get_threshold_parameters)
    def get_threshold_parameters(self):
        return [
            NeuronParameter(self._data[V_THRESH],
                            _ADAPTIVE_TYPES.V_THRESH.data_type),
            NeuronParameter(self._data[MIN_THRESH],
                            _ADAPTIVE_TYPES.MIN_THRESH.data_type),
            NeuronParameter(self._data[MAX_THRESH],
                            _ADAPTIVE_TYPES.MAX_THRESH.data_type),
            NeuronParameter(self._data[UP_THRESH],
                            _ADAPTIVE_TYPES.UP_THRESH.data_type),
            NeuronParameter(self._data[DOWN_THRESH],
                            _ADAPTIVE_TYPES.DOWN_THRESH.data_type),

        ]

    @overrides(AbstractThresholdType.get_threshold_parameter_types)
    def get_threshold_parameter_types(self):
        return [item.data_type for item in _STATIC_TYPES]

    @overrides(AbstractThresholdType.get_n_cpu_cycles_per_neuron)
    def get_n_cpu_cycles_per_neuron(self):
        # Just a comparison, but 2 just in case!
        return 5

    @overrides(AbstractContainsUnits.get_units)
    def get_units(self, variable):
        return self._units[variable]
