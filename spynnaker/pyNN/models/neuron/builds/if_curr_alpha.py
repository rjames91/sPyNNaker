from spynnaker.pyNN.models.neuron import AbstractPopulationVertex

from spynnaker.pyNN.models.neuron.neuron_models \
    import NeuronModelLeakyIntegrateAndFire
from spynnaker.pyNN.models.neuron.synapse_types import SynapseTypeAlpha
from spynnaker.pyNN.models.neuron.input_types import InputTypeCurrent
from spynnaker.pyNN.models.neuron.threshold_types import ThresholdTypeStatic

# global objects
DEFAULT_MAX_ATOMS_PER_CORE = 255


class IFCurrAlpha(AbstractPopulationVertex):
    """ Leaky integrate and fire neuron with an alpha-shaped current-based\
        input.
    """

    # noinspection PyPep8Naming
    _model_based_max_atoms_per_core = DEFAULT_MAX_ATOMS_PER_CORE

    default_parameters = {
        'tau_m': 20.0,
        'cm': 1.0,
        'v_rest': -65.0,
        'v_reset': -65.0,
        'v_thresh': -50.0,
        'tau_syn_E': 0.5,
        'tau_syn_I': 0.5,
        'tau_refrac': 0.1,
        'i_offset': 0}

    non_pynn_default_parameters = {
        # Internal parameters
        'exc_response': 0,
        'exc_exp_response': 0,
        'inh_response': 0,
        'inh_exp_response': 0}

    initialize_parameters = {'v_init': None}

    def __init__(
            self, n_neurons, spikes_per_second=None, ring_buffer_sigma=None,
            incoming_spike_buffer_size=None, constraints=None, label=None,
            tau_m=default_parameters['tau_m'], cm=default_parameters['cm'],
            v_rest=default_parameters['v_rest'],
            v_reset=default_parameters['v_reset'],
            v_thresh=default_parameters['v_thresh'],
            exc_response=non_pynn_default_parameters['exc_response'],
            exc_exp_response=non_pynn_default_parameters['exc_exp_response'],
            tau_syn_E=default_parameters['tau_syn_E'],
            inh_response=non_pynn_default_parameters['inh_response'],
            inh_exp_response=non_pynn_default_parameters['inh_exp_response'],
            tau_syn_I=default_parameters['tau_syn_I'],
            tau_refrac=default_parameters['tau_refrac'],
            i_offset=default_parameters['i_offset'],
            v_init=initialize_parameters['v_init']):
        # pylint: disable=too-many-arguments, too-many-locals
        neuron_model = NeuronModelLeakyIntegrateAndFire(
            n_neurons, v_init, v_rest, tau_m, cm, i_offset,
            v_reset, tau_refrac)

        synapse_type = SynapseTypeAlpha(
                n_neurons,
                exc_response,
                exc_exp_response,
                tau_syn_E,
                inh_response,
                inh_exp_response,
                tau_syn_I)

        input_type = InputTypeCurrent()
        threshold_type = ThresholdTypeStatic(n_neurons, v_thresh)

        super(IFCurrAlpha, self).__init__(
            n_neurons=n_neurons, binary="IF_curr_alpha.aplx", label=label,
            max_atoms_per_core=IFCurrAlpha._model_based_max_atoms_per_core,
            spikes_per_second=spikes_per_second,
            ring_buffer_sigma=ring_buffer_sigma,
            incoming_spike_buffer_size=incoming_spike_buffer_size,
            model_name="IF_curr_alpha", neuron_model=neuron_model,
            input_type=input_type, synapse_type=synapse_type,
            threshold_type=threshold_type, constraints=constraints)

    @staticmethod
    def get_max_atoms_per_core():
        return IFCurrAlpha._model_based_max_atoms_per_core

    @staticmethod
    def set_model_max_atoms_per_core(new_value=DEFAULT_MAX_ATOMS_PER_CORE):
        IFCurrAlpha._model_based_max_atoms_per_core = new_value
