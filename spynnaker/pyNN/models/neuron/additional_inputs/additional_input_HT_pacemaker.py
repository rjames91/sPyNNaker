from pacman.executor.injection_decorator import inject_items
from spynnaker.pyNN.models.neural_properties import NeuronParameter
from data_specification.enums import DataType
from spynnaker.pyNN.models.neuron.additional_inputs \
    import AbstractAdditionalInput
from spynnaker.pyNN.utilities.ranged.spynakker_ranged_dict import \
    SpynakkerRangeDictionary

import numpy
from enum import Enum

# Pacemaker Current
I_H = "I_H"
G_H = "g_H"   
E_H = "E_H" 
M_H = "m_H"
M_INF_H = "m_inf_H"
E_TO_T_ON_TAU_M_H = "e_to_t_on_tau_m_H"
H_H = "h_H"
H_INF_H = "h_inf_H"
E_TO_T_ON_TAU_H_H = "e_to_t_on_tau_h_H"
# Voltage Clamp 
V_CLAMP = "v_clamp"
S_CLAMP = "s_clamp"
T_CLAMP = "t_clamp"
# simulation. Maybe more efficient to get them from other parts of the software?
DT = "dt"



class _INTRINSIC_CURRENTS_TYPES(Enum):
    # Pacemaker
    I_H = (1, DataType.S1615)
    g_H = (2, DataType.S1615)
    E_H = (3, DataType.S1615)
    m_H = (4, DataType.S1615)
    m_inf_H = (5, DataType.S1615)
    e_to_t_on_tau_m_H = (6, DataType.S1615)
    h_H = (7, DataType.S1615)
    h_inf_H = (8, DataType.S1615) 
    e_to_t_on_tau_h_H = (9, DataType.S1615)
    # Voltage Clamp
    v_clamp = (10, DataType.S1615) 
    s_clamp = (11, DataType.UINT32) 
    t_clamp = (12, DataType.UINT32)
    dt = (13, DataType.S1615)

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
       # Pacemaker
       I_H, g_H, E_H, m_H, m_inf_H, e_to_t_on_tau_m_H, h_H, h_inf_H, e_to_t_on_tau_h_H,
       # Voltage Clamp
       v_clamp, s_clamp, t_clamp,
       # Other
       dt):
        self._n_neurons = n_neurons
        self._data = SpynakkerRangeDictionary(size=n_neurons)
        self._data['I_H'] = I_H  
        self._data['g_H'] = g_H  
        self._data['E_H'] = E_H  
        self._data['m_H'] = m_H  
        self._data['m_inf_H'] = m_inf_H  
        self._data['e_to_t_on_tau_m_H'] = e_to_t_on_tau_m_H  
        self._data['h_H'] = h_H  
        self._data['h_inf_H'] = h_inf_H  
        self._data['e_to_t_on_tau_h_H'] = e_to_t_on_tau_h_H  
        self._data['v_clamp'] = v_clamp  
        self._data['s_clamp'] = s_clamp  
        self._data['t_clamp'] = t_clamp  
        self._data['dt'] = dt  

    @property
    def I_H(self):
        return self._data[I_H]
    @ I_H.setter
    def I_H(self, new_I_H):
        self._data.set_value(key=I_H, value=new_I_H)
    
    @property
    def g_H(self):
        return self._data[G_H]
    @ g_H.setter
    def g_H(self, new_g_H):
        self._data.set_value(key=G_H, value=new_g_H)
    
    @property
    def E_H(self):
        return self._data[E_H]
    @ E_H.setter
    def E_H(self, new_E_H):
        self._data.set_value(key=E_H, value=new_E_H)

    @property
    def m_H(self):
        return self._data[M_H]
    @ m_H.setter
    def m_H(self, new_m_H):
        self._data.set_value(key=M_H, value=new_m_H)
    
    @property
    def m_inf_H(self):
        return self._data[M_INF_H]
    @ m_inf_H.setter
    def m_inf_H(self, new_m_inf_H):
        self._data.set_value(key=M_INF_H, value=new_m_inf_H)
    
    @property
    def e_to_t_on_tau_m_H(self):
        return self._data[E_TO_T_ON_TAU_M_H]
    @ e_to_t_on_tau_m_H.setter
    def e_to_t_on_tau_m_H(self, new_e_to_t_on_tau_m_H):
        self._data.set_value(key=E_TO_T_ON_TAU_M_H, value=new_e_to_t_on_tau_m_H)

    @property
    def h_H(self):
        return self._data[H_H]
    @ h_H.setter
    def h_H(self, new_h_H):
        self._data.set_value(key=H_H, value=new_h_H)

    @property
    def h_inf_H(self):
        return self._data[H_INF_H]
    @ h_inf_H.setter
    def h_inf_H(self, new_h_inf_H):
        self._data.set_value(key=H_INF_H, value=new_h_inf_H)

    @property
    def e_to_t_on_tau_h_H(self):
        return self._data[E_TO_T_ON_TAU_H_H]
    @ e_to_t_on_tau_h_H.setter
    def e_to_t_on_tau_h_H(self, new_e_to_t_on_tau_h_H):
        self._data.set_value(key=E_TO_T_ON_TAU_H_H, value=new_e_to_t_on_tau_h_H)

    @property
    def v_clamp(self):
        return self._data[V_CLAMP]

    @ v_clamp.setter
    def v_clamp(self, new_v_clamp):
        self._data.set_value(key=V_CLAMP, value=new_v_clamp)
    

    @property
    def s_clamp(self):
        return self._data[S_CLAMP]

    @ s_clamp.setter
    def s_clamp(self, new_s_clamp):
        self._data.set_value(key=S_CLAMP, value=new_s_clamp)
    

    @property
    def t_clamp(self):
        return self._data[T_CLAMP]
    @ t_clamp.setter
    def t_clamp(self, new_t_clamp):
        self._data.set_value(key=T_CLAMP, value=new_t_clamp)
    

    @property
    def dt(self):
        return self._data[DT]
    @ dt.setter
    def dt(self, new_dt):
        self._data.set_value(key=DT, value=new_dt)
      
    def get_n_parameters(self):
        return 10

    @inject_items({"machine_time_step": "MachineTimeStep"})
    def get_parameters(self, machine_time_step):
        # pylint: disable=arguments-differ
        return [NeuronParameter(self._data[I_H],_INTRINSIC_CURRENTS_TYPES.I_H.data_type),
               NeuronParameter(self._data[G_H],_INTRINSIC_CURRENTS_TYPES.g_H.data_type),
               NeuronParameter(self._data[E_H],_INTRINSIC_CURRENTS_TYPES.E_H.data_type),
               NeuronParameter(self._data[M_H],_INTRINSIC_CURRENTS_TYPES.m_H.data_type),
               NeuronParameter(self._data[M_INF_H],_INTRINSIC_CURRENTS_TYPES.m_inf_H.data_type),
               NeuronParameter(self._data[E_TO_T_ON_TAU_M_H],_INTRINSIC_CURRENTS_TYPES.e_to_t_on_tau_m_H.data_type),
               NeuronParameter(self._data[H_H],_INTRINSIC_CURRENTS_TYPES.h_H.data_type),
               NeuronParameter(self._data[H_INF_H],_INTRINSIC_CURRENTS_TYPES.h_inf_H.data_type),
               NeuronParameter(self._data[E_TO_T_ON_TAU_H_H],_INTRINSIC_CURRENTS_TYPES.e_to_t_on_tau_h_H.data_type),
               NeuronParameter(self._data[V_CLAMP],_INTRINSIC_CURRENTS_TYPES.v_clamp.data_type),
               NeuronParameter(self._data[S_CLAMP],_INTRINSIC_CURRENTS_TYPES.s_clamp.data_type),
               NeuronParameter(self._data[T_CLAMP],_INTRINSIC_CURRENTS_TYPES.t_clamp.data_type),
               NeuronParameter(self._data[DT],_INTRINSIC_CURRENTS_TYPES.dt.data_type) 
               ] 

    def get_parameter_types(self):
        return [item.data_type for item in _INTRINSIC_CURRENTS_TYPES]

    def set_parameters(self, parameters, vertex_slice):
        pass
        # Can ignore anything that isn't a state variable
#         self._data[I_CA2][vertex_slice.slice] = parameters[1]

    def get_n_cpu_cycles_per_neuron(self):
        return 3

