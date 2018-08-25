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
        'v_thresh': 0, 'v_thresh_resting': -50, 'v_thresh_tau':50,
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
        'I_H':-0.2,
        'g_H':2.0,
        'E_H':-40.0, # 40 in Synthesis code and 43.0 in Huguenard's paper. Was 65.0 in OR code
        'm_H':4.0,
        'm_inf_H':5.0,
        'e_to_t_on_tau_m_H':6.0,
   # Calcium 
        'I_T':0.02,
        'g_T':11.0,
        'E_T':120.0, # 0.0 in synthesis but experimental value is around 120.0.
        'm_T':13.0,
        'm_inf_T':14.0,
        'e_to_t_on_tau_m_T':15.0,
        'h_T':16.0,
        'h_inf_T':17.0,
        'e_to_t_on_tau_h_T':18.0,
    # Sodium
        'I_NaP':19.0,
        'g_NaP':20.0,
        'E_NaP':45.0,  # 30.0 in Synthesis 45.0 in OR code.
        'm_inf_NaP':23.0,
    # Potassium
        'I_DK':28.0,
        'g_DK':29.0,
        'E_DK':-90.0,
        'm_inf_DK':32.0,
        'e_to_t_on_tau_m_DK':33.0,
        'D':34.0,
        'D_infinity':35.0,
    # Voltage Clamp
        'v_clamp': -75.0,
        's_clamp': 3.0,
        't_clamp': 1.0,
        'dt':1.0
        }

    initialize_parameters = {'v_init': -65}

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
            g_H = default_parameters['g_H'],
            E_H = default_parameters['E_H'],
            m_H = default_parameters['m_H'],
            m_inf_H = default_parameters['m_inf_H'],
            e_to_t_on_tau_m_H = default_parameters['e_to_t_on_tau_m_H'],
        # Calcium 
            I_T=default_parameters['I_T'],
            g_T=default_parameters['g_T'],
            E_T=default_parameters['E_T'],
            m_T=default_parameters['m_T'],
            m_inf_T=default_parameters['m_inf_T'],
            e_to_t_on_tau_m_T=default_parameters['e_to_t_on_tau_m_T'],
            h_T=default_parameters['h_T'],
            h_inf_T=default_parameters['h_inf_T'],
            e_to_t_on_tau_h_T=default_parameters['e_to_t_on_tau_h_T'],
        # Sodium
            I_NaP = default_parameters['I_NaP'],
            g_NaP = default_parameters['g_NaP'],
            E_NaP = default_parameters['E_NaP'],
            m_inf_NaP = default_parameters['m_inf_NaP'],
        # Potassium
            I_DK = default_parameters['I_DK'],
            g_DK = default_parameters['g_DK'],
            E_DK = default_parameters['E_DK'],
            m_inf_DK = default_parameters['m_inf_DK'],
            e_to_t_on_tau_m_DK = default_parameters['e_to_t_on_tau_m_DK'],
            D = default_parameters['D'],
            D_infinity = default_parameters['D_infinity'],
        # Voltage Clamps
            v_clamp = default_parameters['v_clamp'],
            s_clamp = default_parameters['s_clamp'],
            t_clamp = default_parameters['t_clamp'],
        # Other 
            dt = default_parameters['dt'],
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
                n_neurons,
                I_H,
                g_H,
                E_H,
                m_H,
                m_inf_H,
                e_to_t_on_tau_m_H,
                I_T,
                g_T,
                E_T,
                m_T,
                m_inf_T,
                e_to_t_on_tau_m_T,
                h_T,
                h_inf_T,
                e_to_t_on_tau_h_T,
                I_NaP,
                g_NaP,
                E_NaP,
                m_inf_NaP,
                I_DK,
                g_DK,
                E_DK,
                m_inf_DK,
                e_to_t_on_tau_m_DK,
                D,
                D_infinity,
                v_clamp,
                s_clamp,
                t_clamp,
                dt
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
