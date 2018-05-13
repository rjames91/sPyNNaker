from spynnaker.pyNN.models.neuron.neuron_models \
    import NeuronModelLeakyIntegrateAndFire
from spynnaker.pyNN.models.neuron.synapse_types import SynapseTypeHillTononi
from spynnaker.pyNN.models.neuron.input_types import InputTypeCurrent
from spynnaker.pyNN.models.neuron.threshold_types import ThresholdTypeHTDynamic
from spynnaker.pyNN.models.neuron import AbstractPopulationVertex
from spynnaker.pyNN.models.neuron.additional_inputs import AdditionalInputHTPacemaker

# global objects
DEFAULT_MAX_ATOMS_PER_CORE = 128


class HillTononi(AbstractPopulationVertex):
    """
        Hill Tononi Neuron model: leaky integrate and fire neuron, with
        intrinsic HH-like currents, bi-exponential synapses (voltage-dependent
        NMDA), short-term plasticity and dynamic threshold.
    """
    _max_feasible_atoms_per_core = 128
    _model_based_max_atoms_per_core = DEFAULT_MAX_ATOMS_PER_CORE

    default_parameters = {
    # #### Neuron Model ####
        'tau_refrac': 0.1, 'i_offset': 0,
        'tau_m': 20.0, 'cm': 1.0, 'v_rest': -65.0, 'v_reset': -65.0,

    # #### Threshold ####
        'v_thresh': -55, 'v_thresh_resting': -50, 'v_thresh_tau':2,
        'v_thresh_Na_reversal':40,

    # ##### Synapse Type #####
        # AMPA - excitatory
        'exc_a_response': 2, 'exc_a_A': 1, 'exc_a_tau': 0.5,
        'exc_b_response': 2, 'exc_b_B': -1, 'exc_b_tau': 2.4,
        # NMDA - excitatory2
        'exc2_a_response': 1, 'exc2_a_A': 1, 'exc2_a_tau': 4,
        'exc2_b_response': 1, 'exc2_b_B': -1, 'exc2_b_tau': 40,
        # GABA_A - inhibitory
        'inh_a_response': 1, 'inh_a_A': 1, 'inh_a_tau': 1,
        'inh_b_response': 1, 'inh_b_B': -1, 'inh_b_tau': 7,
        # GABA_B - inhibitory2
        'inh2_a_response': 1, 'inh2_a_A': 1, 'inh2_a_tau': 60,
        'inh2_b_response': 1, 'inh2_b_B':-1, 'inh2_b_tau': 200,

    # #### Input Type ####
#         'e_rev_AMPA': 0, 'e_rev_NMDA': 0,
#         'e_rev_GABA_A': -70 , 'e_rev_GABA_B': -90,
#         note that GABA_A_TC connections have a reversal potential of -80 mV

    # ##### Additional Inputs ####
    # Pacemaker
        'I_H': 1,
        'g_H': 9,
        'e_H': 10,
        'm': 5,
        'm_inf': 6,
        'e_to_t_on_tau_m': 7,
        'h': -2,
        'h_inf': -3,
        'e_to_t_on_tau_h': -4
        }

    initialize_parameters = {'v_init': None}

    def __init__(
            self, n_neurons, spikes_per_second=AbstractPopulationVertex.
            non_pynn_default_parameters['spikes_per_second'],
            ring_buffer_sigma=AbstractPopulationVertex.
            non_pynn_default_parameters['ring_buffer_sigma'],
            incoming_spike_buffer_size=AbstractPopulationVertex.
            non_pynn_default_parameters['incoming_spike_buffer_size'],
            constraints=AbstractPopulationVertex.non_pynn_default_parameters[
                'constraints'],
            label=AbstractPopulationVertex.non_pynn_default_parameters[
                'label'],

        # Neuron parameters
            tau_refrac=default_parameters['tau_refrac'],
            tau_m=default_parameters['tau_m'],
            cm=default_parameters['cm'],
            v_rest=default_parameters['v_rest'],
            v_reset=default_parameters['v_reset'],
            i_offset=default_parameters['i_offset'],
            v_init=initialize_parameters['v_init'],



        # Synapse parameters
            # AMPA - excitatory
            exc_a_response=default_parameters['exc_a_response'],
            exc_a_A=default_parameters['exc_a_A'],
            exc_a_tau=default_parameters['exc_a_tau'],
            exc_b_response=default_parameters['exc_b_response'],
            exc_b_B=default_parameters['exc_b_B'],
            exc_b_tau=default_parameters['exc_b_tau'],

            # NMDA - excitatory2
            exc2_a_response=default_parameters['exc2_a_response'],
            exc2_a_A=default_parameters['exc2_a_A'],
            exc2_a_tau=default_parameters['exc2_a_tau'],
            exc2_b_response=default_parameters['exc2_b_response'],
            exc2_b_B=default_parameters['exc2_b_B'],
            exc2_b_tau=default_parameters['exc2_b_tau'],

            # GABA_A - inhibitory
            inh_a_response=default_parameters['inh_a_response'],
            inh_a_A=default_parameters['inh_a_A'],
            inh_a_tau=default_parameters['inh_a_tau'],
            inh_b_response=default_parameters['inh_b_response'],
            inh_b_B=default_parameters['inh_b_B'],
            inh_b_tau=default_parameters['inh_b_tau'],

            # GABA_B - inhibitory2
            inh2_a_response=default_parameters['inh2_a_response'],
            inh2_a_A=default_parameters['inh2_a_A'],
            inh2_a_tau=default_parameters['inh2_a_tau'],
            inh2_b_response=default_parameters['inh2_b_response'],
            inh2_b_B=default_parameters['inh2_b_B'],
            inh2_b_tau=default_parameters['inh2_b_tau'],

        # Input Type
#             e_rev_AMPA=default_parameters['e_rev_AMPA'],
#             e_rev_NMDA=default_parameters['e_rev_NMDA'],
#             e_rev_GABA_A=default_parameters['e_rev_GABA_A'],
#             e_rev_GABA_B=default_parameters['e_rev_GABA_B']


        # additional inputs
            # Pacemaker
            I_H = default_parameters['I_H'],
            m = default_parameters['m'],
            m_inf = default_parameters['m_inf'],
            h = default_parameters['h'],
            h_inf = default_parameters['h_inf'],
            e_to_t_on_tau_m = default_parameters['e_to_t_on_tau_m'],
            e_to_t_on_tau_h = default_parameters['e_to_t_on_tau_h'],
            g_H = default_parameters['g_H'],
            e_H = default_parameters['e_H'],


        # Threshold parameters
            v_thresh=default_parameters['v_thresh'],
            v_thresh_resting=default_parameters['v_thresh_resting'],
            v_thresh_tau=default_parameters['v_thresh_tau'],
            v_thresh_Na_reversal=default_parameters['v_thresh_Na_reversal']
            ):



        neuron_model = NeuronModelLeakyIntegrateAndFire(
            n_neurons, v_init, v_rest, tau_m, cm, i_offset,
            v_reset, tau_refrac)

        synapse_type = SynapseTypeHillTononi(
                n_neurons,

                # AMPA - excitatory
                exc_a_response,
                exc_a_A,
                exc_a_tau,
                exc_b_response,
                exc_b_B,
                exc_b_tau,

                # NMDA - excitatory2
                exc2_a_response,
                exc2_a_A,
                exc2_a_tau,
                exc2_b_response,
                exc2_b_B,
                exc2_b_tau,

                # GABA_A - inhibitory
                inh_a_response,
                inh_a_A,
                inh_a_tau,
                inh_b_response,
                inh_b_B,
                inh_b_tau,

                # GABA_B - inhibitory2
                inh2_a_response,
                inh2_a_A,
                inh2_a_tau,
                inh2_b_response,
                inh2_b_B,
                inh2_b_tau
            )

        input_type = InputTypeCurrent()

        additional_input = AdditionalInputHTPacemaker(
                n_neurons=n_neurons,
                I_H = I_H,
                m = m,
                m_inf = m_inf,
                h = h,
                h_inf = h_inf,
                e_to_t_on_tau_m = e_to_t_on_tau_m,
                e_to_t_on_tau_h = e_to_t_on_tau_h,
                g_H = g_H,
                e_H = e_H
                )

        threshold_type = ThresholdTypeHTDynamic(n_neurons, v_thresh,
                                                v_thresh_resting,
                                                v_thresh_tau,
                                                v_thresh_Na_reversal)

        super(HillTononi, self).__init__(
            n_neurons=n_neurons, binary="Hill_Tononi.aplx", label=label,
            max_atoms_per_core=HillTononi._model_based_max_atoms_per_core,
            spikes_per_second=spikes_per_second,
            ring_buffer_sigma=ring_buffer_sigma,
            incoming_spike_buffer_size=incoming_spike_buffer_size,
            model_name="Hill_Tononi",
            neuron_model=neuron_model,
            input_type=input_type, synapse_type=synapse_type,
            threshold_type=threshold_type,
            additional_input=additional_input,
            constraints=constraints)


    @staticmethod
    def set_model_max_atoms_per_core(new_value=DEFAULT_MAX_ATOMS_PER_CORE):
        HillTononi._model_based_max_atoms_per_core = new_value

    @staticmethod
    def get_max_atoms_per_core():
        return HillTononi._model_based_max_atoms_per_core

#
#
#     @isyn_exc.setter
#     def isyn_exc(self = new_value):
#         self.synapse_type.initial_value_exc = new_value
#
#     @isyn_inh.setter
#     def isyn_inh(self = new_value):
#         self.synapse_type.initial_value_inh = new_value
