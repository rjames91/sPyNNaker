from spinn_utilities.overrides import overrides
from pacman.executor.injection_decorator import inject_items
from spynnaker.pyNN.models.abstract_models import AbstractContainsUnits
from spynnaker.pyNN.models.neural_properties import NeuronParameter
from spynnaker.pyNN.utilities.ranged.spynakker_ranged_dict import \
    SpynakkerRangeDictionary
from .abstract_neuron_model import AbstractNeuronModel
from data_specification.enums import DataType

from enum import Enum
import numpy

A = 'a'
B = 'b'
C = 'c'
D = 'd'
V_INIT = 'v_init'
U_INIT = 'u_init'
I_OFFSET = 'i_offset'
V_PREV = "v_prev"
DV_DT = "dv_dt"
DV_DT_S = "dv_dt_slow"
TAU_LP = "tau_low_pass"
GAMMA = "gamma"
GAMMA_COMP = "gamma_complement"
V_NMDA = "v_nmda"


class _IZH_TYPES(Enum):
    A = (1, DataType.S1615)
    B = (2, DataType.S1615)
    C = (3, DataType.S1615)
    D = (4, DataType.S1615)
    V_INIT = (5, DataType.S1615)
    U_INIT = (6, DataType.S1615)
    I_OFFSET = (7, DataType.S1615)
    THIS_H = (8, DataType.S1615)
    V_PREV = (9, DataType.S1615)
    DV_DT = (10, DataType.S1615)
    DV_DT_SLOW = (11, DataType.S1615)
    GAMMA = (12, DataType.S1615) # history weight for slow dV/dt
    GAMMA_COMP = (13, DataType.S1615)  # 1 - GAMMA
    V_NMDA = (14, DataType.S1615)

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


class _IZH_GLOBAL_TYPES(Enum):
    TIMESTEP = (1, DataType.S1615)

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


class NeuronModelIzhDvDtNMDA(AbstractNeuronModel, AbstractContainsUnits):
    __slots__ = [
        "_data",
        "_n_neurons",
        "_units"]

    def __init__(self, n_neurons, a, b, c, d, v_init, u_init, i_offset,
                tau_low_pass, v_nmda=0.):
        # pylint: disable=too-many-arguments
        self._units = {
            A: "ms",
            B: "ms",
            C: "mV",
            D: "mV/ms",
            V_INIT: "mV",
            U_INIT: "mV/ms",
            I_OFFSET: "nA",
            V_PREV: 'mV', 
            TAU_LP: 'ms',
            DV_DT: 'mV/ms', DV_DT_S: 'mV/ms',
}

        self._n_neurons = n_neurons
        self._data = SpynakkerRangeDictionary(size=n_neurons)
        self._data[A] = a
        self._data[B] = b
        self._data[C] = c
        self._data[D] = d
        self._data[V_INIT] = v_init
        self._data[U_INIT] = u_init
        self._data[I_OFFSET] = i_offset
        self._data[V_PREV] = v_init
        self._data[DV_DT] = 0
        self._data[DV_DT_S] = 0
        self._data[TAU_LP] = tau_low_pass
        gamma = numpy.exp(-1.0/tau_low_pass)
        self._data[GAMMA] = gamma
        self._data[GAMMA_COMP] = 1. - gamma
        self._data[V_NMDA] = v_nmda

    @property
    def a(self):
        return self._data[A]

    @a.setter
    def a(self, a):
        self._data.set_value(key=A, value=a)

    @property
    def b(self):
        return self._data[B]

    @b.setter
    def b(self, b):
        self._data.set_value(key=B, value=b)

    @property
    def c(self):
        return self._data[C]

    @c.setter
    def c(self, c):
        self._data.set_value(key=C, value=c)

    @property
    def d(self):
        return self._data[D]

    @d.setter
    def d(self, d):
        self._data.set_value(key=D, value=d)



    @property
    def v_prev(self):
        return self._data[V_PREV]

    @v_prev.setter
    def v_prev(self, value):
        self._data.set_value(key=V_PREV, value=value)

    @property
    def dv_dt(self):
        return self._data[DV_DT]

    @dv_dt.setter
    def dv_dt(self, value):
        self._data.set_value(key=DV_DT, value=value)

    @property
    def dv_dt_slow(self):
        return self._data[DV_DT_S]

    @dv_dt_slow.setter
    def dv_dt_slow(self, value):
        self._dv_dt_slow = self._data.set_value(key=DV_DT_S, value=value)

    @property
    def tau_low_pass(self):
        return self._data[TAU_LP]

    @tau_low_pass.setter
    def tau_low_pass(self, value):
        self._data.set_value(key=TAU_LP, value=value)
        self.gamma = numpy.exp(-1.0/value)
        self.gamma_complement(1.0 - self.gamma)

    @property
    def gamma(self):
        return self._data[GAMMA]

    @gamma.setter
    def gamma(self, value):
        self._data.set_value(key=GAMMA, value=value)

    @property
    def gamma_complement(self):
        return self._data[GAMMA_COMP]

    @gamma.setter
    def gamma_complement(self, value):
        self._data.set_value(key=GAMMA_COMP, value=value)

    @property
    def v_nmda(self):
        return self._data[V_NMDA]

    @v_nmda.setter
    def v_nmda(self, value):
        self._data.set_value(key=V_NMDA, value=value)



    @property
    def i_offset(self):
        return self._data[I_OFFSET]

    @i_offset.setter
    def i_offset(self, i_offset):
        self._data.set_value(key=I_OFFSET, value=i_offset)

    @property
    def v_init(self):
        return self._data[V_INIT]

    @v_init.setter
    def v_init(self, v_init):
        self._data.set_value(key=V_INIT, value=v_init)

    @property
    def u_init(self):
        return self._data[U_INIT]

    @u_init.setter
    def u_init(self, u_init):
        self._data.set_value(key=U_INIT, value=u_init)

    def initialize_v(self, v_init):
        self._data.set_value(key=V_INIT, value=v_init)

    def initialize_u(self, u_init):
        self._data.set_value(key=U_INIT, value=u_init)

    @overrides(AbstractNeuronModel.get_n_neural_parameters)
    def get_n_neural_parameters(self):
        return 14

    @inject_items({"machine_time_step": "MachineTimeStep"})
    @overrides(AbstractNeuronModel.get_neural_parameters,
               additional_arguments={'machine_time_step'})
    def get_neural_parameters(self, machine_time_step):
        # pylint: disable=arguments-differ
        return [
            # REAL A
            NeuronParameter(self._data[A], _IZH_TYPES.A.data_type),

            # REAL B
            NeuronParameter(self._data[B], _IZH_TYPES.B.data_type),

            # REAL C
            NeuronParameter(self._data[C], _IZH_TYPES.C.data_type),

            # REAL D
            NeuronParameter(self._data[D], _IZH_TYPES.D.data_type),

            # REAL V
            NeuronParameter(self._data[V_INIT], _IZH_TYPES.V_INIT.data_type),

            # REAL U
            NeuronParameter(self._data[U_INIT], _IZH_TYPES.U_INIT.data_type),

            # offset current [nA]
            # REAL I_offset;
            NeuronParameter(self._data[I_OFFSET],
                            _IZH_TYPES.I_OFFSET.data_type),

            # current timestep - simple correction for threshold
            # REAL this_h;
            NeuronParameter(
                machine_time_step / 1000.0, _IZH_TYPES.THIS_H.data_type),

            # Voltage in previous time step
            # REAL     V_prev;
            NeuronParameter(self._data[V_PREV],
                            _IZH_TYPES.V_PREV.data_type),

            # voltage change per time step
            # REAL     dV_dt;
            NeuronParameter(self._data[DV_DT], 
                            _IZH_TYPES.DV_DT.data_type),

            # low-pass filtered version of voltage change per time step
            # REAL     dV_dt_slow;
            NeuronParameter(self._data[DV_DT_S], 
                            _IZH_TYPES.DV_DT_SLOW.data_type),

            # History weight to filter dV_dt into dV_dt_slow
            # REAL     gamma;
            NeuronParameter(self._data[GAMMA], 
                            _IZH_TYPES.GAMMA.data_type),
            NeuronParameter(self._data[GAMMA_COMP], 
                            _IZH_TYPES.GAMMA_COMP.data_type),

            NeuronParameter(self._data[V_NMDA],
                            _IZH_TYPES.V_NMDA.data_type),
        ]

    @overrides(AbstractNeuronModel.get_neural_parameter_types)
    def get_neural_parameter_types(self):
        return [item.data_type for item in _IZH_TYPES]

    @overrides(AbstractNeuronModel.get_n_global_parameters)
    def get_n_global_parameters(self):
        return 1

    @inject_items({"machine_time_step": "MachineTimeStep"})
    @overrides(AbstractNeuronModel.get_global_parameters,
               additional_arguments={'machine_time_step'})
    def get_global_parameters(self, machine_time_step):
        # pylint: disable=arguments-differ
        return [NeuronParameter(
            machine_time_step / 1000.0,
            _IZH_GLOBAL_TYPES.TIMESTEP.data_type)]

    @overrides(AbstractNeuronModel.get_global_parameter_types)
    def get_global_parameter_types(self):
        return [item.data_type for item in _IZH_GLOBAL_TYPES]

    @overrides(AbstractNeuronModel.set_neural_parameters)
    def set_neural_parameters(self, neural_parameters, vertex_slice):
        self._data[V_INIT][vertex_slice.as_slice] = neural_parameters[4]
        self._data[U_INIT][vertex_slice.as_slice] = neural_parameters[5]
        self._data[V_PREV][vertex_slice.as_slice] = neural_parameters[4]

    def get_n_cpu_cycles_per_neuron(self):

        # A bit of a guess
        return 180

    @overrides(AbstractContainsUnits.get_units)
    def get_units(self, variable):
        return self._units[variable]
