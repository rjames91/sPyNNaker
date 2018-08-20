#ifndef _ADDITIONAL_INPUT_SODIUM_
#define _ADDITIONAL_INPUT_SODIUM_

#include "additional_input.h"

//----------------------------------------------------------------------------
//----------------------------------------------------------------------------

typedef struct additional_input_t {

    // Sodium Current
    accum    I_NaP;
    accum    m_NaP;  // not used here
    accum    m_inf_NaP;

    accum    h_NaP;  // not used here
    accum    h_inf_NaP;  // not used here
    accum    e_to_t_on_tau_m_NaP;  // not used here

    accum    e_to_t_on_tau_h_NaP;  // not used here
    accum    g_NaP; // max sodium conductance
    accum    E_NaP; // sodium reversal potential

    // Voltage Clamp 
    REAL      V_clamp;    // voltage for voltage clamp [mV], hold voltage is just V_rest
    uint32_t  S_clamp;    // clamp starting time [timesteps]
    uint32_t  T_clamp;    // clamp duration [timesteps] 
    accum    dt;
} additional_input_t;


// Variables to control 'patch clamp' tests
static input_t local_v = -65;

// Variable to set m = m_inf on first timestep.
static uint32_t n_dt = 0;

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
//
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
        local_v = -65;
        }
        
        membrane_voltage = local_v;
        // log_info("membrane potential: %k", membrane_voltage);
        n_dt += 1;
//------------------------------------------------------------------------
    profiler_write_entry_disable_irq_fiq(
        PROFILER_ENTER | PROFILER_INTRINSIC_CURRENT);
//------------------------------------------------------------------------

        additional_input->g_NaP = 0.007k;

	additional_input->m_inf_NaP = 1k / (1k
                                  + expk(-(membrane_voltage+55.7k)*0.12987k)); // 1/7.7 = 0.129870129

        // h (inactivation) is 1 and constant, so we will just ignore it.
	additional_input->I_NaP =
                 additional_input->g_NaP *
		 additional_input->m_inf_NaP *
		 additional_input->m_inf_NaP *
		 additional_input->m_inf_NaP *
		(membrane_voltage - 45.0k); //additional_input->E_H);

/*
	log_info("mem_V: %k, m: %k, m_inf: %k, I_Na = %k",
			membrane_voltage,
			additional_input->m,
			additional_input->m_inf,
			additional_input->I_NaP);
*/
//------------------------------------------------------------------------
    profiler_write_entry_disable_irq_fiq(
        PROFILER_EXIT | PROFILER_INTRINSIC_CURRENT);
    return additional_input->I_NaP;
}

//static void

static additional_input_has_spiked(
        additional_input_pointer_t additional_input ) {

//      log_info("number of post-synaptic spikes: %u", n_spikes);

}

#endif // _ADDITIONAL_INPUT_SODIUM
