#ifndef _ADDITIONAL_INPUT_SODIUM_
#define _ADDITIONAL_INPUT_SODIUM_

#include "additional_input.h"

//----------------------------------------------------------------------------
//----------------------------------------------------------------------------

typedef struct additional_input_t {

    // Sodium Current
    accum    I_NaP;
    accum    m;  // not used here
    accum    m_inf;
    accum    h;  // not used here
    accum    h_inf;  // not used here
    accum    e_to_t_on_tau_m;  // not used here
    accum    e_to_t_on_tau_h;  // not used here
    accum    g_NaP; // max sodium conductance
    accum    E_NaP; // sodium reversal potential
    accum    dt;

} additional_input_t;

static input_t additional_input_get_input_value_as_current(
        additional_input_pointer_t additional_input,
        state_t membrane_voltage) {

    profiler_write_entry_disable_irq_fiq(PROFILER_ENTER | PROFILER_INTRINSIC_CURRENT);

    additional_input->g_NaP = 0.007k;

	additional_input->m_inf = 1k / (1k + expk(-(membrane_voltage+55.7k)*0.12987k)); // 1/7.7 = 0.12987012987013

	// H is 1 and constant, so ignore - also not sure of activation gating power at present
	additional_input->I_NaP = - // the original code has this as a negative current so a "-" may be here.
	        additional_input->g_NaP *
			additional_input->m_inf *
			additional_input->m_inf *
			additional_input->m_inf *
			(membrane_voltage - 45k); //additional_input->E_H);

/*
	log_info("mem_V: %k, m: %k, m_inf: %k, I_Na = %k",
			membrane_voltage,
			additional_input->m,
			additional_input->m_inf,
			additional_input->I_NaP);
*/

    profiler_write_entry_disable_irq_fiq(PROFILER_EXIT | PROFILER_INTRINSIC_CURRENT);

    return additional_input->I_NaP;
}

static void additional_input_has_spiked(
        additional_input_pointer_t additional_input) {
	// no action to be taken on spiking
}

#endif // _ADDITIONAL_INPUT_SODIUM
