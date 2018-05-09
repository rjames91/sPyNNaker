#ifndef _ADDITIONAL_INPUT_PACEMAKER_H_
#define _ADDITIONAL_INPUT_PACEMAKER_H_

#include "additional_input.h"

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

static input_t additional_input_get_input_value_as_current(
        additional_input_pointer_t additional_input,
        state_t membrane_voltage) {

    profiler_write_entry_disable_irq_fiq(PROFILER_ENTER | PROFILER_INTRINSIC_CURRENT);

    additional_input->g_H = 0.015k;

	additional_input->m_inf = 1k / (1k + expk((membrane_voltage+75k)/5.5k));

	additional_input->e_to_t_on_tau_m = expk(-0.1k *
			((expk(-14.59k - 0.086k * membrane_voltage))
			+ expk(-1.87k + 0.0701k * membrane_voltage))
			);

	// Update m
	additional_input->m = additional_input->m_inf +
			(additional_input->m - additional_input->m_inf) *
			additional_input->e_to_t_on_tau_m;

	// H is 1 and constant, so ignore - also not sure of activation gating power at present
	additional_input->I_H =
			additional_input->g_H *
			additional_input->m *
			(membrane_voltage - -65k); //additional_input->E_H);


//    _print_additional_input_params(additional_input);


    profiler_write_entry_disable_irq_fiq(PROFILER_EXIT | PROFILER_INTRINSIC_CURRENT);

    return 0; //additional_input->I_H;
}

static void additional_input_has_spiked(
        additional_input_pointer_t additional_input) {
	// no action to be taken on spiking
}


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

#endif // _ADDITIONAL_INPUT_PACEMAKER_H_
