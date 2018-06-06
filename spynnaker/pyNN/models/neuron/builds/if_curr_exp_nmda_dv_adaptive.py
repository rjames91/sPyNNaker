from spynnaker.pyNN.models.neuron.neuron_models \
    import NeuronModelLeakyIntegrateAndFireDvDtNMDA
from spynnaker.pyNN.models.neuron.synapse_types import SynapseTypeExponentialNMDA
from spynnaker.pyNN.models.neuron.input_types import InputTypeCurrent
from spynnaker.pyNN.models.neuron.threshold_types import ThresholdTypeAdaptive
from spynnaker.pyNN.models.neuron import AbstractPopulationVertex

# global objects
DEFAULT_MAX_ATOMS_PER_CORE = 255
_apv_defs = AbstractPopulationVertex.non_pynn_default_parameters


class IFCurrExpDvDtAdaptiveNMDA(AbstractPopulationVertex):
    """ Leaky integrate and fire neuron with an exponentially decaying \
        current input
    """

    _model_based_max_atoms_per_core = DEFAULT_MAX_ATOMS_PER_CORE

    default_parameters = {
        'tau_m': 20.0, 'cm': 1.0, 'v_rest': -65.0, 'v_reset': -65.0,
        'v_thresh': -50.0, 'tau_syn_E': 5.0, 'tau_syn_I': 5.0,
        'tau_syn_nmda_E': 50.0, 'tau_syn_nmda_I': 50.0,
        'tau_refrac': 0.1, 'i_offset': 0, 
        'isyn_exc': 0.0, 'isyn_inh': 0.0,
        'isyn_nmda_exc': 0.0, 'isyn_nmda_inh': 0.0,
        'tau_low_pass': 20.,
        'min_thresh': -50.0, 'max_thresh': -40.0,
        'up_thresh': 0.1, 'down_thresh': 0.01,
        'v_max': None, 'v_spike': -30.0
    }

    initialize_parameters = {'v_init': None}

    def __init__(
            self, n_neurons, spikes_per_second=_apv_defs['spikes_per_second'],
            ring_buffer_sigma=_apv_defs['ring_buffer_sigma'],
            incoming_spike_buffer_size=_apv_defs['incoming_spike_buffer_size'],
            constraints=_apv_defs['constraints'],
            label=_apv_defs['label'],
            tau_m=default_parameters['tau_m'],
            cm=default_parameters['cm'],
            v_rest=default_parameters['v_rest'],
            v_reset=default_parameters['v_reset'],
            v_thresh=default_parameters['v_thresh'],
            tau_syn_E=default_parameters['tau_syn_E'],
            tau_syn_I=default_parameters['tau_syn_I'],
            tau_syn_nmda_E=default_parameters['tau_syn_nmda_E'],
            tau_syn_nmda_I=default_parameters['tau_syn_nmda_I'],
            tau_refrac=default_parameters['tau_refrac'],
            i_offset=default_parameters['i_offset'],
            v_init=initialize_parameters['v_init'],
            isyn_exc=default_parameters['isyn_exc'],
            isyn_inh=default_parameters['isyn_inh'],
            isyn_nmda_exc=default_parameters['isyn_nmda_exc'],
            isyn_nmda_inh=default_parameters['isyn_nmda_inh'],
            tau_low_pass=default_parameters['tau_low_pass'],
            min_thresh=default_parameters['min_thresh'],
            max_thresh=default_parameters['max_thresh'],
            up_thresh=default_parameters['up_thresh'],
            down_thresh=default_parameters['down_thresh'],
            v_max=default_parameters['v_max'],
            v_spike=default_parameters['v_spike']):

        if v_max is None:
            v_max = max_thresh + 1.
        if v_spike <= max_thresh:
            v_spike = max_thresh + 1.

        neuron_model = NeuronModelLeakyIntegrateAndFireDvDtNMDA(
                        n_neurons, v_init, v_rest, tau_m, cm, i_offset,
                        v_reset, tau_refrac, tau_low_pass, v_max, v_spike)
        synapse_type = SynapseTypeExponentialNMDA(
                        n_neurons, tau_syn_E, tau_syn_I, tau_syn_nmda_E, tau_syn_nmda_I,
                        isyn_exc, isyn_inh, isyn_nmda_exc, isyn_nmda_inh)
        input_type = InputTypeCurrent()
        threshold_type = ThresholdTypeAdaptive(n_neurons, v_thresh,
                            min_thresh, max_thresh, up_thresh, down_thresh)

        AbstractPopulationVertex.__init__(
            self, n_neurons=n_neurons, binary="IF_curr_exp_nmda_dv_adapt.aplx", label=label,
            max_atoms_per_core=IFCurrExpDvDtAdaptiveNMDA._model_based_max_atoms_per_core,
            spikes_per_second=spikes_per_second,
            ring_buffer_sigma=ring_buffer_sigma,
            incoming_spike_buffer_size=incoming_spike_buffer_size,
            model_name="IF_curr_exp_nmda_dv_adapt", neuron_model=neuron_model,
            input_type=input_type, synapse_type=synapse_type,
            threshold_type=threshold_type, constraints=constraints)

    @staticmethod
    def set_model_max_atoms_per_core(new_value=DEFAULT_MAX_ATOMS_PER_CORE):
        IFCurrExpDvDtAdaptiveNMDA._model_based_max_atoms_per_core = new_value

    @staticmethod
    def get_max_atoms_per_core():
        return IFCurrExpDvDtAdaptiveNMDA._model_based_max_atoms_per_core

    @property
    def isyn_exc(self):
        return self.synapse_type.initial_value_exc

    @isyn_exc.setter
    def isyn_exc(self, new_value):
        self.synapse_type.initial_value_exc = new_value

    @property
    def isyn_inh(self):
        return self.synapse_type.initial_value_inh

    @isyn_inh.setter
    def isyn_inh(self, new_value):
        self.synapse_type.initial_value_inh = new_value
        
    # #----------------------------------------------------------------
    # #----------------------------------------------------------------
    # @property
    # def isyn_nmda_exc(self):
        # return self.synapse_type.initial_value_nmda_exc
# 
    # @isyn_nmda_exc.setter
    # def isyn_nmda_exc(self, new_value):
        # self.synapse_type.initial_value_nmda_exc = new_value
# 
    # @property
    # def isyn_nmda_inh(self):
        # return self.synapse_type.initial_value_nmda_inh
# 
    # @isyn_nmda_inh.setter
    # def isyn_nmda_inh(self, new_value):
        # self.synapse_type.isyn_nmda_inh = new_value
