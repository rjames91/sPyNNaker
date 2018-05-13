from pacman.executor.injection_decorator import inject_items
from spynnaker.pyNN.models.neural_properties import NeuronParameter
from data_specification.enums import DataType
from spynnaker.pyNN.models.neuron.additional_inputs \
    import AbstractAdditionalInput
from spynnaker.pyNN.utilities.ranged.spynakker_ranged_dict import \
    SpynakkerRangeDictionary

import numpy
from enum import Enum

I_H = "I_H"
M = "m"
M_INF = "m_inf"
H = "h"
H_INF = "h_inf"
E_TO_T_ON_TAU_M = "e_to_t_on_tau_m"
E_TO_T_ON_TAU_H = "e_to_t_on_tau_h"
G_H = "g_H"
E_H ="e_H"


class _PACEMAKER_TYPES(Enum):
    I_H = (1, DataType.S1615)
    m = (2, DataType.S1615)
    m_inf = (3, DataType.S1615)
    h = (4, DataType.S1615)
    h_inf = (5, DataType.S1615)
    e_to_t_on_tau_m = (6, DataType.S1615)
    e_to_t_on_tau_h = (7, DataType.S1615)
    g_H = (8, DataType.S1615)
    e_H = (9, DataType.S1615)
    dt = (10, DataType.S1615)


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


class AdditionalInputHTPacemaker(AbstractAdditionalInput):
    __slots__ = [
        "_data",
        "_n_neurons"
        ]

    def __init__(self, n_neurons,
                 I_H,
                 m,
                 m_inf,
                 h,
                 h_inf,
                 e_to_t_on_tau_m,
                 e_to_t_on_tau_h,
                 g_H,
                 e_H
                 ):
        self._n_neurons = n_neurons
        self._data = SpynakkerRangeDictionary(size=n_neurons)

        self._data['I_H'] = I_H
        self._data['m'] = m
        self._data['m_inf'] = m_inf
        self._data['h'] = h
        self._data['h_inf'] = h_inf
        self._data['e_to_t_on_tau_m'] = e_to_t_on_tau_m
        self._data['e_to_t_on_tau_h'] = e_to_t_on_tau_h
        self._data['g_H'] = g_H
        self._data['e_H'] = e_H


    @property
    def I_H(self):
        return self._data[I_H]
    @ I_H.setter
    def I_H(self, new_I_H):
        self._data.set_value(key=I_H, value=new_I_H)

    @property
    def m(self):
        return self._data[M]
    @ m.setter
    def m(self, new_m):
        self._data.set_value(key=M, value=new_m)

    @property
    def m_inf(self):
        return self._data[M_INF]
    @ m_inf.setter
    def m_inf(self, new_m_inf):
        self._data.set_value(key=M_INF, value=new_m_inf)

    @property
    def h(self):
        return self._data[H]
    @ h.setter
    def h(self, new_h):
        self._data.set_value(key=H, value=new_h)

    @property
    def h_inf(self):
        return self._data[H_INF]
    @ h_inf.setter
    def h_inf(self, new_h_inf):
        self._data.set_value(key=H_INF, value=new_h_inf)

    @property
    def e_to_t_on_tau_m(self):
        return self._data[E_TO_T_ON_TAU_M]
    @ e_to_t_on_tau_m.setter
    def e_to_t_on_tau_m(self, new_e_to_t_on_tau_m):
        self._data.set_value(key=E_TO_T_ON_TAU_M, value=new_e_to_t_on_tau_m)

    @property
    def e_to_t_on_tau_h(self):
        return self._data[E_TO_T_ON_TAU_H]
    @ e_to_t_on_tau_h.setter
    def e_to_t_on_tau_h(self, new_e_to_t_on_tau_h):
        self._data.set_value(key=E_TO_T_ON_TAU_H, value=new_e_to_t_on_tau_h)

    @property
    def g_H(self):
        return self._data[G_H]
    @ g_H.setter
    def g_H(self, new_g_H):
        self._data.set_value(key=G_H, value=new_g_H)

    @property
    def e_H(self):
        return self._data[E_H]
    @ e_H.setter
    def e_H(self, new_e_H):
        self._data.set_value(key=E_H, value=new_e_H)


    def get_n_parameters(self):
        return 10

    @inject_items({"machine_time_step": "MachineTimeStep"})
    def get_parameters(self, machine_time_step):
        # pylint: disable=arguments-differ
        return [
            NeuronParameter(self._data[I_H],_PACEMAKER_TYPES.I_H.data_type),
            NeuronParameter(self._data[G_H], _PACEMAKER_TYPES.g_H.data_type),
            NeuronParameter(self._data[E_H], _PACEMAKER_TYPES.e_H.data_type),
            NeuronParameter(0.1, _PACEMAKER_TYPES.dt.data_type),

            NeuronParameter(self._data[M], _PACEMAKER_TYPES.m.data_type),
            NeuronParameter(self._data[M_INF], _PACEMAKER_TYPES.m_inf.data_type),
            NeuronParameter(self._data[E_TO_T_ON_TAU_M], _PACEMAKER_TYPES.e_to_t_on_tau_m.data_type),

            NeuronParameter(self._data[H], _PACEMAKER_TYPES.h.data_type),
            NeuronParameter(self._data[H_INF], _PACEMAKER_TYPES.h_inf.data_type),
            NeuronParameter(self._data[E_TO_T_ON_TAU_H], _PACEMAKER_TYPES.e_to_t_on_tau_h.data_type)]

    def get_parameter_types(self):
        return [item.data_type for item in _PACEMAKER_TYPES]

    def set_parameters(self, parameters, vertex_slice):
        pass
        # Can ignore anything that isn't a state variable
#         self._data[I_CA2][vertex_slice.slice] = parameters[1]

    def get_n_cpu_cycles_per_neuron(self):
        return 3

