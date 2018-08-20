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

    accum    m_H;
    accum    m_inf_H;
    accum    e_to_t_on_tau_m_H;

    accum    h_H;      // not used here
    accum    h_inf_H;  // not used here
    accum    e_to_t_on_tau_h_H;  // not used here

    // Voltage Clamp 
    REAL      V_clamp;    // voltage for voltage clamp [mV], hold voltage is just V_rest
    uint32_t  S_clamp;    // clamp starting time [timesteps]
    uint32_t  T_clamp;    // clamp duration [timesteps] 
    accum    dt;
} additional_input_t;

// Variables to control 'patch clamp' tests
static input_t local_v;

// Variable to set m = m_inf on first timestep.
static uint32_t n_dt = 0;

static inline void _print_additional_input_params(additional_input_t* additional_input){
	log_info("\n"
			"m: %k, m_inf: %k, tau_m: %k, \n"
			"h: %k, h_inf: %k, tau_h: %k, \n"
			"g_H: %k, E_H: %k, dt = %k, \n"
			" I_H = %k",
			additional_input->m_H,
			additional_input->m_inf_H,
			additional_input->e_to_t_on_tau_m_H,
			additional_input->h_H,
			additional_input->h_inf_H,
			additional_input->e_to_t_on_tau_h_H,
			additional_input->g_H,
			additional_input->E_H,
			additional_input->dt,
			additional_input->I_H);
}

static input_t additional_input_get_input_value_as_current(
        additional_input_pointer_t additional_input,
        state_t membrane_voltage) {
//------------------------------------------------------------------------
         if (n_dt >= additional_input->S_clamp &&
            n_dt < additional_input->S_clamp + additional_input->T_clamp){
        // local_v +=1;
        // membrane_voltage = local_v;
        local_v = additional_input->V_clamp;
         } else {
        local_v = -55;
        }

        membrane_voltage = local_v;
        // log_info("membrane potential: %k", membrane_voltage);

//------------------------------------------------------------------------
    profiler_write_entry_disable_irq_fiq(
        PROFILER_ENTER | PROFILER_INTRINSIC_CURRENT);
//------------------------------------------------------------------------
        additional_input->g_H = 0.015k;

	additional_input->m_inf_H = 1k / (1k + expk((membrane_voltage+75k)/5.5k));
        
        // hardcode initial value for m as m_inf may cause an overhead on the profiling
        n_dt += 1; 
        if (n_dt ==1){
        additional_input->m_H = additional_input->m_inf_H;
        }

	additional_input->e_to_t_on_tau_m_H = 
                  expk(
                 -1.0k *
	          (expk(-14.59k - 0.086k * membrane_voltage)
		 + expk(-1.87k + 0.0701k * membrane_voltage)));

	// Update m
	additional_input->m_H = additional_input->m_inf_H +
		(additional_input->m_H - additional_input->m_inf_H) *
         	additional_input->e_to_t_on_tau_m_H;

	// h (inactivation) is 1 and constant, so we will just ignore it.
	additional_input->I_H = 
		additional_input->g_H *
		additional_input->m_H *
		(membrane_voltage - -43.0k); //additional_input->E_H); 
                                             //it was set to -65 but needs to be -43 to reproduce the results 
                                             //of Huguenard, not sure about the value used by Hans.

        //    _print_additional_input_params(additional_input);
//------------------------------------------------------------------------
    profiler_write_entry_disable_irq_fiq(
        PROFILER_EXIT | PROFILER_INTRINSIC_CURRENT);
//------------------------------------------------------------------------
    return additional_input->I_H;
}

//static void
static void additional_input_has_spiked(
        additional_input_pointer_t additional_input) {
//      log_info("number of post-synaptic spikes: %u", n_spikes);
}

#endif // _ADDITIONAL_INPUT_PACEMAKER_H_
