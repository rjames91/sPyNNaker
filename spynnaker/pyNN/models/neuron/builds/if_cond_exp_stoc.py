from spynnaker.pyNN.models.neuron import AbstractPopulationVertex
from spynnaker.pyNN.models.neuron.neuron_models \
    import NeuronModelLeakyIntegrateAndFire
from spynnaker.pyNN.models.neuron.synapse_types import SynapseTypeExponential
from spynnaker.pyNN.models.neuron.input_types import InputTypeConductance
from spynnaker.pyNN.models.neuron.threshold_types \
    import ThresholdTypeMaassStochastic

# global objects
DEFAULT_MAX_ATOMS_PER_CORE = 255


class IFCondExpStoc(AbstractPopulationVertex):
    """ Leaky integrate and fire neuron with a stochastic threshold.
    """

    _model_based_max_atoms_per_core = DEFAULT_MAX_ATOMS_PER_CORE

    default_parameters = {
        'tau_m': 20.0, 'cm': 1.0, 'e_rev_E': 0.0, 'e_rev_I': -70.0,
        'v_rest': -65.0, 'v_reset': -65.0,
        'v_thresh': -50.0, 'tau_syn_E': 5.0, 'tau_syn_I': 5.0,
        'tau_refrac': 0.1, 'i_offset': 0, "du_th": 0.5, "tau_th": 20.0,
        'isyn_exc': 0.0, 'isyn_inh': 0.0}

    initialize_parameters = {'v_init': None}

    def __init__(
            self, n_neurons,
            spikes_per_second=AbstractPopulationVertex.
            non_pynn_default_parameters['spikes_per_second'],
            ring_buffer_sigma=AbstractPopulationVertex.
            non_pynn_default_parameters['ring_buffer_sigma'],
            incoming_spike_buffer_size=AbstractPopulationVertex.
            non_pynn_default_parameters['incoming_spike_buffer_size'],
            constraints=AbstractPopulationVertex.non_pynn_default_parameters[
                'constraints'],
            label=AbstractPopulationVertex.non_pynn_default_parameters[
                'label'],
            tau_m=default_parameters['tau_m'], cm=default_parameters['cm'],
            v_rest=default_parameters['v_rest'],
            v_reset=default_parameters['v_reset'],
            v_thresh=default_parameters['v_thresh'],
            tau_syn_E=default_parameters['tau_syn_E'],
            tau_syn_I=default_parameters['tau_syn_I'],
            tau_refrac=default_parameters['tau_refrac'],
            i_offset=default_parameters['i_offset'],
            e_rev_E=default_parameters['e_rev_E'],
            e_rev_I=default_parameters['e_rev_I'],
            du_th=default_parameters['du_th'],
            tau_th=default_parameters['tau_th'],
            v_init=initialize_parameters['v_init'],
            isyn_exc=default_parameters['isyn_exc'],
            isyn_inh=default_parameters['isyn_inh']):
        # pylint: disable=too-many-arguments, too-many-locals
        neuron_model = NeuronModelLeakyIntegrateAndFire(
            n_neurons, v_init, v_rest, tau_m, cm, i_offset,
            v_reset, tau_refrac)
        synapse_type = SynapseTypeExponential(
            n_neurons, tau_syn_E, tau_syn_I, initial_input_exc=isyn_exc,
            initial_input_inh=isyn_inh)
        input_type = InputTypeConductance(n_neurons, e_rev_E, e_rev_I)
        threshold_type = ThresholdTypeMaassStochastic(
            n_neurons, du_th, tau_th, v_thresh)

        super(IFCondExpStoc, self).__init__(
            n_neurons=n_neurons, binary="IF_cond_exp_stoc.aplx", label=label,
            max_atoms_per_core=IFCondExpStoc._model_based_max_atoms_per_core,
            spikes_per_second=spikes_per_second,
            ring_buffer_sigma=ring_buffer_sigma,
            incoming_spike_buffer_size=incoming_spike_buffer_size,
            model_name="IF_cond_exp_stoc", neuron_model=neuron_model,
            input_type=input_type, synapse_type=synapse_type,
            threshold_type=threshold_type, constraints=constraints)

    @staticmethod
    def get_max_atoms_per_core():
        return IFCondExpStoc._model_based_max_atoms_per_core

    @staticmethod
    def set_max_atoms_per_core(new_value):
        IFCondExpStoc._model_based_max_atoms_per_core = new_value
