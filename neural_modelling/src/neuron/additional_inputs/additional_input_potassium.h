#ifndef _ADDITIONAL_INPUT_POTASSIUM_
#define _ADDITIONAL_INPUT_POTASSIUM_

#include "additional_input.h"

//----------------------------------------------------------------------------
//----------------------------------------------------------------------------

typedef struct additional_input_t {

    // Potassium Current
    accum    I_DK;
    accum    m;         // not used here
    accum    m_inf;
    accum    D;         // instead of h
    accum    NaInflux;  // instead of h_inf
    accum    e_to_t_on_tau;
    accum    e_to_t_on_tau_h;  // not used here
    accum    g_DK;      // max potassium conductance
    accum    E_DK;      // potassium reversal potential
    accum    dt;

} additional_input_t;

static input_t additional_input_get_input_value_as_current(
        additional_input_pointer_t additional_input,
        state_t membrane_voltage) {

    profiler_write_entry_disable_irq_fiq(PROFILER_ENTER | PROFILER_INTRINSIC_CURRENT);

    additional_input->g_DK = 1.25k;

	additional_input->e_to_t_on_tau = 1.00008k;  // exp(0.1/1250)

    additional_input->NaInflux = 1k / (1k + expk(-(membrane_voltage- -10k) * 0.2k)); //1/5=0.2

	// Update D
	additional_input->D = (additional_input->NaInflux +0.0000008k) *   //Deq/tauD=0.001/1250
			(1k - additional_input->e_to_t_on_tau) +
			additional_input->D * additional_input->e_to_t_on_tau;

	additional_input->m_inf = 1k / (1k + 0.015625k * additional_input->D * additional_input->D * additional_input->D); // TODO: Actual exponent is D^3.5.

	// H is 1 and constant, so ignore - also not sure of activation gating power at present
	additional_input->I_DK = - // the original code has this as a negative current so a "-" may be here.
	        additional_input->g_DK *
			additional_input->m_inf *
			(membrane_voltage - -90k); //additional_input->E_H);

/*
	log_info("mem_V: %k, D: %k, m_inf: %k, NaInflux: %k, I_DK = %k",
			membrane_voltage,
			additional_input->D,
			additional_input->m_inf,
			additional_input->NaInflux,
			additional_input->I_DK);
*/
    profiler_write_entry_disable_irq_fiq(PROFILER_EXIT | PROFILER_INTRINSIC_CURRENT);

    return additional_input->I_DK;
}

static void additional_input_has_spiked(
        additional_input_pointer_t additional_input) {
	// no action to be taken on spiking
}

#endif // _ADDITIONAL_INPUT_PACEMAKER_H_
