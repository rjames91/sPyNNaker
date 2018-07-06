from spinn_utilities.overrides import overrides
from pacman.executor.injection_decorator import inject_items
from spynnaker.pyNN.models.abstract_models import AbstractContainsUnits
from spynnaker.pyNN.models.neuron.synapse_types.synapse_type_exponential \
    import get_exponential_decay_and_init
from spynnaker.pyNN.models.neural_properties import NeuronParameter
from spynnaker.pyNN.utilities.ranged import SpynnakerRangeDictionary
from .abstract_synapse_type import AbstractSynapseType
from data_specification.enums import DataType

from enum import Enum

TAU_SYN_E = 'tau_syn_E'
TAU_SYN_E2 = 'tau_syn_E2'
TAU_SYN_I = 'tau_syn_I'
GSYN_EXC = 'gsyn_exc'
GSYN_INH = 'gsyn_inh'
INITIAL_INPUT_EXC = "initial_input_exc"
INITIAL_INPUT_EXC2 = "initial_input_exc2"
INITIAL_INPUT_INH = "initial_input_inh"


class _DUAL_EXP_TYPES(Enum):

    E_DECAY = (1, DataType.UINT32)
    E_INIT = (2, DataType.UINT32)
    E2_DECAY = (3, DataType.UINT32)
    E2_INIT = (4, DataType.UINT32)
    I_DECAY = (5, DataType.UINT32)
    I_INIT = (6, DataType.UINT32)
    INITIAL_EXC = (7, DataType.S1615)
    INITIAL_EXC2 = (8, DataType.S1615)
    INITIAL_INH = (9, DataType.S1615)

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


class SynapseTypeDualExponential(AbstractSynapseType, AbstractContainsUnits):
    __slots__ = [
        "_data",
        "_n_neurons",
        "_units"]

    def __init__(self, n_neurons, tau_syn_E, tau_syn_E2,
                 tau_syn_I, initial_input_exc, initial_input_exc2,
                 initial_input_inh):
        # pylint: disable=too-many-arguments
        self._units = {
            TAU_SYN_E: "mV",
            TAU_SYN_E2: "mV",
            TAU_SYN_I: 'mV',
            GSYN_EXC: "uS",
            GSYN_INH: "uS"}

        self._n_neurons = n_neurons
        self._data = SpynnakerRangeDictionary(size=n_neurons)
        self._data[TAU_SYN_E] = tau_syn_E
        self._data[TAU_SYN_E2] = tau_syn_E2
        self._data[TAU_SYN_I] = tau_syn_I
        self._data[INITIAL_INPUT_EXC] = initial_input_exc
        self._data[INITIAL_INPUT_EXC2] = initial_input_exc2
        self._data[INITIAL_INPUT_INH] = initial_input_inh

    @property
    def tau_syn_E(self):
        return self._data[TAU_SYN_E]

    @tau_syn_E.setter
    def tau_syn_E(self, tau_syn_E):
        self._data.set_value(key=TAU_SYN_E, _value=tau_syn_E)

    @property
    def tau_syn_E2(self):
        return self._data[TAU_SYN_E2]

    @tau_syn_E2.setter
    def tau_syn_E2(self, tau_syn_E2):
        self._data.set_value(key=TAU_SYN_E2, value=tau_syn_E2)

    @property
    def tau_syn_I(self):
        return self._data[TAU_SYN_I]

    @tau_syn_I.setter
    def tau_syn_I(self, tau_syn_I):
        self._data.set_value(key=TAU_SYN_I, value=tau_syn_I)

    @property
    def isyn_exc(self):
        return self._data[INITIAL_INPUT_EXC]

    @isyn_exc.setter
    def isyn_exc(self, new_value):
        self._data.set_value(key=INITIAL_INPUT_EXC, value=new_value)

    @property
    def isyn_inh(self):
        return self._data[INITIAL_INPUT_INH]

    @isyn_inh.setter
    def isyn_inh(self, new_value):
        self._data.set_value(key=INITIAL_INPUT_INH, value=new_value)

    @property
    def isyn_exc2(self):
        return self._data[INITIAL_INPUT_EXC2]

    @isyn_exc2.setter
    def isyn_exc2(self, new_value):
        self._data.set_value(key=INITIAL_INPUT_EXC2, value=new_value)

    @overrides(AbstractSynapseType.get_n_synapse_types)
    def get_n_synapse_types(self):
        return 3

    @overrides(AbstractSynapseType.get_synapse_id_by_target)
    def get_synapse_id_by_target(self, target):
        if target == "excitatory":
            return 0
        elif target == "excitatory2":
            return 1
        elif target == "inhibitory":
            return 2
        return None

    @overrides(AbstractSynapseType.get_synapse_targets)
    def get_synapse_targets(self):
        return "excitatory", "excitatory2", "inhibitory"

    @overrides(AbstractSynapseType.get_n_synapse_type_parameters)
    def get_n_synapse_type_parameters(self):
        return 9

    @inject_items({"machine_time_step": "MachineTimeStep"})
    def get_synapse_type_parameters(self, machine_time_step):
        # pylint: disable=arguments-differ
        e_decay, e_init = get_exponential_decay_and_init(
            self._data[TAU_SYN_E], machine_time_step)
        e_decay2, e_init2 = get_exponential_decay_and_init(
            self._data[TAU_SYN_E2], machine_time_step)
        i_decay, i_init = get_exponential_decay_and_init(
            self._data[TAU_SYN_I], machine_time_step)

        return [
            NeuronParameter(e_decay, _DUAL_EXP_TYPES.E_DECAY.data_type),
            NeuronParameter(e_init, _DUAL_EXP_TYPES.E_INIT.data_type),
            NeuronParameter(e_decay2, _DUAL_EXP_TYPES.E2_DECAY.data_type),
            NeuronParameter(e_init2, _DUAL_EXP_TYPES.E2_INIT.data_type),
            NeuronParameter(i_decay, _DUAL_EXP_TYPES.I_DECAY.data_type),
            NeuronParameter(i_init, _DUAL_EXP_TYPES.I_INIT.data_type),
            NeuronParameter(
                self._data[INITIAL_INPUT_EXC],
                _DUAL_EXP_TYPES.INITIAL_EXC.data_type),
            NeuronParameter(
                self._data[INITIAL_INPUT_EXC2],
                _DUAL_EXP_TYPES.INITIAL_EXC2.data_type),
            NeuronParameter(
                self._data[INITIAL_INPUT_INH],
                _DUAL_EXP_TYPES.INITIAL_INH.data_type)
        ]

    @overrides(AbstractSynapseType.get_synapse_type_parameter_types)
    def get_synapse_type_parameter_types(self):
        return [item.data_type for item in _DUAL_EXP_TYPES]

    @overrides(AbstractSynapseType.get_n_cpu_cycles_per_neuron)
    def get_n_cpu_cycles_per_neuron(self):

        # A guess
        return 100

    @overrides(AbstractContainsUnits.get_units)
    def get_units(self, variable):
        return self._units[variable]
