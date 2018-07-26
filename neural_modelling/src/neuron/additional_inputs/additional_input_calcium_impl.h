#ifndef _ADDITIONAL_INPUT_CALCIUM_
#define _ADDITIONAL_INPUT_CALCIUM_

#include "additional_input.h"

//----------------------------------------------------------------------------
//----------------------------------------------------------------------------

typedef struct additional_input_t {

    // Pacemaker Current
    accum    I_T;
    accum    m;
    accum    m_inf;
    accum    h;
    accum    h_inf;
    accum    e_to_t_on_tau_m;
    accum    e_to_t_on_tau_h;
    accum    g_T; // max pacemaker conductance
    accum    E_T; // reversal potential
    accum    dt;

} additional_input_t;

// Variables to control 'patch clamp' tests
static input_t local_v = -65;
static uint32_t n_spikes = 0;

// Variable to set m = m_inf on first timestep.
static uint32_t n_dt = 0;

// Variable to get the V_reset value from other neurons which will be used to clamp the neuron in each new spike arrival.
static neuron_pointer_t clamp_neuron;

//static inline void _print_additional_input_params(additional_input_t* additional_input){
//        log_info("\n"
//                        "m: %k, m_inf: %k, tau_m: %k, \n"
//                        "h: %k, h_inf: %k, tau_h: %k, \n"
//                        "g_H: %k, E_H: %k, dt = %k, \n"
//                        " I_H = %k",
//                        additional_input->m,
//                        additional_input->m_inf,
//                        additional_input->e_to_t_on_tau_m,
//                        additional_input->h,
//                        additional_input->h_inf,
//                        additional_input->e_to_t_on_tau_h,
//                        additional_input->g_H,
//                        additional_input->E_H,
//                        additional_input->dt,
//                        additional_input->I_H);
//}

static input_t additional_input_get_input_value_as_current(
        additional_input_pointer_t additional_input,
        state_t membrane_voltage) {

        // Hardcode membrane potential during tests:
        membrane_voltage = local_v;

    profiler_write_entry_disable_irq_fiq(
        PROFILER_ENTER | PROFILER_INTRINSIC_CURRENT);

        additional_input->g_T = 0.003k;

	additional_input->m_inf = 1k
        / (1k + expk(-(membrane_voltage+59k) * 0.16129k)); //1/6.2=0.161290322

	additional_input->h_inf = 1k
        / (1k + expk((membrane_voltage + 83.0k)*0.25k)); //1/4=0.25

        // hardcode initial value for m as m_inf and for h as h_inf
        n_dt += 1;
        if (n_dt ==1){
        additional_input->m = additional_input->m_inf;
        additional_input->h = additional_input->h_inf;
        }


	additional_input->e_to_t_on_tau_m = expk(
           -1.0k /
	   (0.13k + 0.22k / (expk(-0.05988k * (membrane_voltage+132k))             // 1/16.7=0.05988023952
	                      + expk(0.054945k * (membrane_voltage + 16.8k)))));    // 1/18.2=0.05494505494

        additional_input->e_to_t_on_tau_h = expk(
            -1.0k /
	    (8.2k +
	    (56.6k + 0.27k * expk((membrane_voltage + 115.2k) * 0.2k)) /            // 1/5.0=0.2
	    (1.0k + expk((membrane_voltage + 86.0k) * 0.3125k))));                  // 1/3.2=0.3125

	// Update m
	additional_input->m = additional_input->m_inf +
		(additional_input->m - additional_input->m_inf) *
	       	 additional_input->e_to_t_on_tau_m;

	// Update h
	additional_input->h = additional_input->h_inf +
		(additional_input->h - additional_input->h_inf) *
		 additional_input->e_to_t_on_tau_h;

	additional_input->I_T =
	         additional_input->g_T *
	 	 additional_input->m *
		 additional_input->m *
		 additional_input->h *
		(membrane_voltage - 120k); //additional_input->E_H);

/*
	log_info("mem_V: %k, m: %k, h: %k, m_inf: %k, h_inf: %k, tau_m: %k, tau_h, I_T = %k",
			membrane_voltage,
			additional_input->m,
			additional_input->h,
			additional_input->m_inf,
			additional_input->h_inf,
			additional_input->e_to_t_on_tau_m,
			additional_input->e_to_t_on_tau_h,
			additional_input->I_H);
*/

    profiler_write_entry_disable_irq_fiq(
        PROFILER_EXIT | PROFILER_INTRINSIC_CURRENT);

//    return additional_input->m;
//    return additional_input->e_to_t_on_tau_m;
//    return additional_input-> m_inf;
    return additional_input->I_T;
}

//static void
static additional_input_has_spiked(
        additional_input_pointer_t additional_input, neuron_pointer_t neuron, neuron_pointer_t neuron_array, uint32_t n_neurons) {

//     log_info("number of post-synaptic spikes: %u", n_spikes);

        n_spikes += 1;
//        clamp_neuron = &neuron_array[n_spikes/n_neurons];
//        local_v = clamp_neuron->V_reset;


        if (n_spikes==1){
                local_v = neuron->V_reset;
        } else if (n_spikes==2){
                local_v = -65;
        }


}

#endif // _ADDITIONAL_INPUT_CALCIUM_
