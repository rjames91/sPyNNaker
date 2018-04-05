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

static input_t additional_input_get_input_value_as_current(
        additional_input_pointer_t additional_input,
        state_t membrane_voltage) {

    profiler_write_entry_disable_irq_fiq(PROFILER_ENTER | PROFILER_INTRINSIC_CURRENT);

    additional_input->g_H = 0.003k;

	additional_input->m_inf = 1k / (1k + expk(-(membrane_voltage+59k) * 0.16129k)); //1/6.2=0.16129032258

	additional_input->h_inf = 1k / (1k + expk((v + 83.0k)*0.25k)); //1/4=0.25

	additional_input->e_to_t_on_tau_m = expk(-0.1k /
	        (0.13k +
	         0.22 * expk(0.05988k * (membrane_voltage+132k)) // 1/16.7=0.05988023952
	        + expk(0.054945 * (membrane_voltage + 16.8k)))); // 1/18.2=0.05494505494

    aditional_input->e_to_t_on_tau_h = expk(-0.1k /
	        (8.2k +
	        (56.6k + 0.27k * expk((membrane_voltage + 115.2k) * 0.2k)) / // 1/5.0=0.2
	        (1.0k + expk((membrane_voltage + 86.0k) * 0.3125))));        // 1/3.2=0.3125

	// Update m
	additional_input->m = additional_input->m_inf +
			(additional_input->m - additional_input->m_inf) *
			additional_input->e_to_t_on_tau_m;

	// Update h
	additional_input->h = additional_input->h_inf +
			(additional_input->h - additional_input->h_inf) *
			additional_input->e_to_t_on_tau_h;

	// H is 1 and constant, so ignore - also not sure of activation gating power at present
	additional_input->I_H =
	        additional_input->g_H *
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

    profiler_write_entry_disable_irq_fiq(PROFILER_EXIT | PROFILER_INTRINSIC_CURRENT);

    return additional_input->I_T;
}

static void additional_input_has_spiked(
        additional_input_pointer_t additional_input) {
	// no action to be taken on spiking
}

#endif // _ADDITIONAL_INPUT_CALCIUM_
