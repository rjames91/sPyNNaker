from data_specification.enums import DataType
from spinn_utilities.overrides import overrides
from .abstract_has_a_plus_a_minus import AbstractHasAPlusAMinus
from .abstract_weight_dependence import AbstractWeightDependence
import math

class WeightDependenceAdditive(
        AbstractHasAPlusAMinus, AbstractWeightDependence):
    __slots__ = [
        "_w_max",
        "_w_min"]

    # noinspection PyPep8Naming
    def __init__(self, w_min=0.0, w_max=1.0):
        super(WeightDependenceAdditive, self).__init__()
        self._w_min = w_min
        self._w_max = w_max

    @property
    def w_min(self):
        return self._w_min

    @property
    def w_max(self):
        return self._w_max

    @overrides(AbstractWeightDependence.is_same_as)
    def is_same_as(self, weight_dependence):
        if not isinstance(weight_dependence, WeightDependenceAdditive):
            return False
        return (
            (self._w_min == weight_dependence.w_min) and
            (self._w_max == weight_dependence.w_max) and
            (self._a_plus == weight_dependence.A_plus) and
            (self._a_minus == weight_dependence.A_minus))

    @property
    def vertex_executable_suffix(self):
        return "additive"

    @overrides(AbstractWeightDependence.get_parameters_sdram_usage_in_bytes)
    def get_parameters_sdram_usage_in_bytes(
            self, n_synapse_types, n_weight_terms):
        if n_weight_terms != 1:
            raise NotImplementedError(
                "Additive weight dependence only supports one term")
        return (4 * 4) * n_synapse_types

    @overrides(AbstractWeightDependence.write_parameters)
    def write_parameters(
            self, spec, machine_time_step, weight_scales, n_weight_terms):
        # Loop through each synapse type's weight scale
        for w in weight_scales:

            # Scale the weights
            scaled_max = int(round(self._w_max * w))
            scaled_min = int(round(self._w_min * w))

            if scaled_max == 0:
                raise ArithmeticError("STDP max weight constant (w_max={} weight_scale={})"
                                      " has been scaled to 0!".format(self._w_max, w))
            if scaled_min == 0 and self._w_min!=0:
                raise ArithmeticError("STDP min weight constant (w_min={} weight_scale={})"
                                      " has been scaled to 0!".format(self._w_min, w))
            if scaled_max & int(0x10000):
                raise ArithmeticError("STDP max weight constant (w_max={} weight_scale={})"
                                      " has been scaled to a value too big for an int16!({})".format(self._w_max, w,hex(scaled_max)))
            spec.write_value(
                #data=int(round(self._w_min * w)), data_type=DataType.INT32)
                data=scaled_min, data_type=DataType.INT32)
            spec.write_value(
                #data=int(round(self._w_max * w)), data_type=DataType.INT32)
                data=scaled_max, data_type=DataType.INT32)
            # Based on http://data.andrewdavison.info/docs/PyNN/_modules/pyNN
            #                /standardmodels/synapses.html
            # Pre-multiply A+ and A- by Wmax
            scaled_a_plus = int(round(self._a_plus *self._w_max * w))
            scaled_a_minus = int(round(self._a_minus *self._w_max * w))

            # scaled_a_plus = int(abs(round(math.log(self._a_plus,2.))))
            # scaled_a_minus = int(abs(round(math.log(self._a_minus,2.))))

            if scaled_a_minus == 0 or scaled_a_plus == 0:
                raise ArithmeticError("STDP alpha constants (a_plus={} a_minus={} weight_scale={})"
                                      " have been scaled to 0!".format(self._a_plus,self._a_minus,w))
            spec.write_value(
                data= scaled_a_plus,
                data_type=DataType.INT32)
            spec.write_value(
                data=scaled_a_minus,
                data_type=DataType.INT32)

    @property
    def weight_maximum(self):
        return self._w_max

    @overrides(AbstractWeightDependence.get_parameter_names)
    def get_parameter_names(self):
        return ['w_min', 'w_max', 'A_plus', 'A_minus']
