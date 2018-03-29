#ifndef _ADDITIONAL_INPUT_PACEMAKER_H_
#define _ADDITIONAL_INPUT_PACEMAKER_H_

#include "additional_input.h"

//----------------------------------------------------------------------------
//----------------------------------------------------------------------------

typedef struct additional_input_t {

    // Pacemaker Current
    accum    I_int;
    accum    m;
    accum    m_inf;
    accum    e_to_t_on_tau_m_approx;
    accum    h;
    accum	 h_inf;
    accum    e_to_t_on_tau_h_approx;
    accum    g_H; // max pacemaker conductance
    accum    E_H; // reversal potential
    accum    dt;
} additional_input_t;

static input_t additional_input_get_input_value_as_current(
        additional_input_pointer_t additional_input,
        state_t membrane_voltage) {

    profiler_write_entry_disable_irq_fiq(PROFILER_ENTER | PROFILER_INTRINSIC_CURRENT);

	REAL m_inf_V_shift = (membrane_voltage >> 7) + 0.7421875k;
	REAL tau_m_V_shift = (membrane_voltage >> 7) - 0.234375k;
//	log_info("m_V: %k, tau_m: %k", m_inf_V_shift, tau_m_V_shift);

	// **** Update pacemeaker current ****
	if (membrane_voltage <= -138k){
		additional_input->m_inf = 1.0k;

	} else if (membrane_voltage >= -12k){
		additional_input->m_inf = 0.0k;

	} else{
	// Update m_inf (Substitute polynomial approximation)
	additional_input->m_inf = 0.783385k + (-m_inf_V_shift) *
							(1.42433k + (-m_inf_V_shift) *
							(-3.00206k + (-m_inf_V_shift) *
							(-3.70779k + (-m_inf_V_shift) *
							(12.1412k + 15.3091k * (-m_inf_V_shift)))));
    }

	if (membrane_voltage <= -12k){
		additional_input->e_to_t_on_tau_m_approx = 1.0k;

	} else if (membrane_voltage >= 112k) {
		additional_input->e_to_t_on_tau_m_approx = 0.0k;

	} else {
    // Update exp(t/tau_m) (Substitute polynomial approximation)
	additional_input->e_to_t_on_tau_m_approx = 0.783385k + (-tau_m_V_shift) *
							(1.42433k + (-tau_m_V_shift) *
							(-3.00206k + (-tau_m_V_shift) *
							(-3.70779k + (-tau_m_V_shift) *
							(12.1412k + 15.3091k * (-tau_m_V_shift)))));
	}

	// Update m
	additional_input->m = additional_input->m_inf +
			(additional_input->m - additional_input->m_inf) *
			additional_input->e_to_t_on_tau_m_approx;

	// H is 1 and constant, so ignore - also not sure of activation gating power at present
	additional_input->I_int = // additional_input->g_H *
			0.001k *
			additional_input->m *
			(membrane_voltage - -65k); //additional_input->E_H);

    profiler_write_entry_disable_irq_fiq(PROFILER_EXIT | PROFILER_INTRINSIC_CURRENT);

//	log_info("mem_V: %k, m: %k, m_inf: %k, tau_m: %k, I_H = %k",
//			membrane_voltage,
//			additional_input->m,
//			additional_input->m_inf,
//			additional_input->e_to_t_on_tau_m_approx,
//			additional_input->I_H);

//    return additional_input->I_H;
    return additional_input->I_int;
}

static void additional_input_has_spiked(
        additional_input_pointer_t additional_input) {
	// no action to be taken on spiking
}

#endif // _ADDITIONAL_INPUT_PACEMAKER_H_
