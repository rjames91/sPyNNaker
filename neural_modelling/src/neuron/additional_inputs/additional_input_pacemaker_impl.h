#ifndef _ADDITIONAL_INPUT_PACEMAKER_H_
#define _ADDITIONAL_INPUT_PACEMAKER_H_

#include "additional_input.h"
#include "../profile_tags.h"
#include <profiler.h>
//----------------------------------------------------------------------------
//----------------------------------------------------------------------------

typedef struct additional_input_t {
    // Pacemaker Current
    accum    I_H;
    accum    g_H; // max pacemaker conductance
    accum    E_H; // reversal potential
    accum    dt;

    accum    m;
    accum    m_inf;
    accum    e_to_t_on_tau_m;

    accum    h;      // not used here
    accum    h_inf;  // not used here
    accum    e_to_t_on_tau_h;  // not used here
} additional_input_t;

// Variables to control 'patch clamp' tests
static input_t local_v = -65;
static uint32_t n_spikes = 0;

// Variable to set m = m_inf on first timestep.
static uint32_t n_dt = 0;

// Variable to get the V_reset value from other neurons which will be used to clamp the neuron in each new spike arrival.
static neuron_pointer_t clamp_neuron;

static inline void _print_additional_input_params(additional_input_t* additional_input){
	log_info("\n"
			"m: %k, m_inf: %k, tau_m: %k, \n"
			"h: %k, h_inf: %k, tau_h: %k, \n"
			"g_H: %k, E_H: %k, dt = %k, \n"
			" I_H = %k",
			additional_input->m,
			additional_input->m_inf,
			additional_input->e_to_t_on_tau_m,
			additional_input->h,
			additional_input->h_inf,
			additional_input->e_to_t_on_tau_h,
			additional_input->g_H,
			additional_input->E_H,
			additional_input->dt,
			additional_input->I_H);
}

static input_t additional_input_get_input_value_as_current(
        additional_input_pointer_t additional_input,
        state_t membrane_voltage) {

    // log_info("membrane potential: %k", membrane_voltage);

	// Hardcode membrane potential during tests:
	membrane_voltage = local_v;

    //	log_info("local membrane potential: %k", local_v);

    profiler_write_entry_disable_irq_fiq(
        PROFILER_ENTER | PROFILER_INTRINSIC_CURRENT);

        additional_input->g_H = 0.015k;

	additional_input->m_inf = 1k / (1k + expk((membrane_voltage+75k)/5.5k));
        
        // hardcode initial value for m as m_inf may cause an overhead on the profiling
        n_dt += 1; 
        if (n_dt ==1){
        additional_input->m = additional_input->m_inf;
        }

/////////// Mixed format experiment /////////
/*
    // Constants
    // NOTE: Smallest value (and a length of the gap between any two
    // neighbouring values) in long fract is 2^(-31) = 0.000000000465661.
    long fract const0 = 0.909733lr;
    long fract const1 = 0.00415872lr;
    long fract const2 = 0.00007531lr;
    long fract const3 = 0.000000630055lr;
    long fract const4 = 0.00000000205212lr;

    // Note: Membrane voltage cannot get higher than 1/const1, otherwise the
    // following mutliplication result will produce overflow.
    long fract mult1 = const1 * membrane_voltage;
    // Note: Membrane voltage cannot get higher than SQRT(1/const2), etc.
    long fract mult2 = const2 * membrane_voltage;
    mult2 *= membrane_voltage;
    long fract mult3 = const3 * membrane_voltage;
    mult3 *= membrane_voltage;
    mult3 *= membrane_voltage;
    // Note: Order of operations is strictly controlled, using brackets, in order to
    // avoid large powers of membrane voltage, which would quickly overflow
    // the accum type.
    long fract mult4 = const4 * membrane_voltage;
    mult4 *= membrane_voltage;
    mult4 *= membrane_voltage;
    mult4 *= membrane_voltage;

    // Note: Order of operations to avoid overflow.
    long fract result_fract = const0 + (- mult1 - mult2) + (- mult3 - mult4);

    // This converts result_fract to accum (Note that likely GCC does not
    // implement any rounding on this conversion, so that can be added later
    // to improve accuracy).
    additional_input->e_to_t_on_tau_m = result_fract;
*/
////////////////////////////////////////////

	additional_input->e_to_t_on_tau_m = 
                  expk(
                 -1.0k *
	          (expk(-14.59k - 0.086k * membrane_voltage)
		 + expk(-1.87k + 0.0701k * membrane_voltage)));

	// Update m
	additional_input->m = additional_input->m_inf +
		(additional_input->m - additional_input->m_inf) *
         	additional_input->e_to_t_on_tau_m;

	// h (inactivation) is 1 and constant, so we will just ignore it.
	additional_input->I_H = 
		additional_input->g_H *
		additional_input->m *
		(membrane_voltage - -43.0k); //additional_input->E_H); //it was set to -65 but needs to be -43 to reproduce the results of Huguenard, not sure about the value used by Hans.

//    _print_additional_input_params(additional_input);

    profiler_write_entry_disable_irq_fiq(
        PROFILER_EXIT | PROFILER_INTRINSIC_CURRENT);
    
//    return additional_input->m;
//    return additional_input->e_to_t_on_tau_m;
//    return additional_input-> m_inf;
    return additional_input->I_H;
//    return local_v ; 
}

//static void
static additional_input_has_spiked(
        additional_input_pointer_t additional_input, neuron_pointer_t neuron, neuron_pointer_t neuron_array, uint32_t n_neurons) {
        
//      log_info("number of post-synaptic spikes: %u", n_spikes);

        n_spikes += 1;
        clamp_neuron = &neuron_array[n_spikes/n_neurons];
        local_v = clamp_neuron->V_reset;

//	log_info("number of post-synaptic spikes: %u", n_spikes);

}



#endif // _ADDITIONAL_INPUT_PACEMAKER_H_
