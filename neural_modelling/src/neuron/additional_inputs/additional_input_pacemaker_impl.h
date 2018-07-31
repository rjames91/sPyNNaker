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
    long fract const0 = 0.9184876080443717lr;
    long fract const1 = 0.9785719997657578lr;
    long fract const2 = 0.9660152351987441lr;
    long fract const3 = 0.0017983013356693135lr;
    long fract const4 = 0.0005102968729975963lr;
    long fract const5 = 0.0008924324766459653lr;
    long fract const6 = 0.00001009512149614703lr;
    long fract const7 = 0.000003188659896lr;
    long fract const8 = 0.00000609293468lr;

    long fract first_const, mult1, mult2;
    if (membrane_voltage < -92.5k) {
        first_const = const0;
        mult1 = const3 * membrane_voltage;
        mult2 = const6 * membrane_voltage;
    } else if (membrane_voltage > -66k) {
        first_const = const2;
        mult1 = const5 * membrane_voltage;
        mult2 = const8 * membrane_voltage;
    } else {
        first_const = const1;
        mult1 = const4 * membrane_voltage;
        mult2 = const7 * membrane_voltage;
    }
    mult2 *= membrane_voltage;

    // Note: Order of operations to avoid overflow.
    long fract result_fract = first_const - mult2 - mult1;

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
