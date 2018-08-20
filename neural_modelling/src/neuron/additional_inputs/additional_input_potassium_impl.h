#ifndef _ADDITIONAL_INPUT_POTASSIUM_
#define _ADDITIONAL_INPUT_POTASSIUM_

#include "additional_input.h"

//----------------------------------------------------------------------------
//----------------------------------------------------------------------------

typedef struct additional_input_t {

    // Potassium Current
    accum    I_DK;
    accum    m_DK;         // not used here
    accum    m_inf_DK;

    accum    D;         // instead of h
    accum    D_infinity;  // instead of h_inf
    accum    e_to_t_on_tau_m_DK;

    accum    e_to_t_on_tau_h_DK;  // not used here
    accum    g_DK;      // max potassium conductance
    accum    E_DK;      // potassium reversal potential

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
//                        additional_input->I_DK);
//}

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
//------------------------------------------------------------------------
    profiler_write_entry_disable_irq_fiq(
        PROFILER_ENTER | PROFILER_INTRINSIC_CURRENT);
//------------------------------------------------------------------------

        additional_input->g_DK = 1.25k;

	additional_input->e_to_t_on_tau_m_DK = 0.367879k; // exp(-0.1/1250)

        additional_input->D_infinity = 0.001k + 1250.0k *0.025k
                                       / (1.0k + expk(-(membrane_voltage - -10.0k) * 0.2k)); //1/5 = 0.2

        // hardcode initial value for D as D_infinity
        if (n_dt == 0){
        additional_input->D = additional_input->D_infinity; 
        }
        n_dt += 1;
        
	// Update D (Same form as LIF dV/dt solution)
	additional_input->D = additional_input->D_infinity +
                              (additional_input->D 
                             - additional_input->D_infinity) 
                             * additional_input->e_to_t_on_tau_m_DK;
       
        accum D_cube = (additional_input->D-0.05) * (additional_input->D-0.05) *  (additional_input->D-0.05); 
         // the 0.05 factor above was added to compensate the difference from 3.5 to 3.0 exponent, in this way 
         // the error is minimal. BUTVERIFY IF THIS IS STILL NEEDED.

	additional_input->m_inf_DK = 1k / (1k + (0.0078125k /  // 0.25^3.5 = 0.0078125
                                  (0.00001+ D_cube  // the 0.00001 factor was added to avoid divergence of the type 1/0.
                                  )));              // TODO: Actual exponent is D^3.5.

	additional_input->I_DK = - additional_input->g_DK 
                                 * additional_input->m_inf_DK 
                                 * (membrane_voltage - -90.0k); //additional_input->E_H);

/*
	log_info("mem_V: %k, D: %k, m_inf: %k, NaInflux: %k, I_DK = %k",
			membrane_voltage,
			additional_input->D,
			additional_input->m_inf,
			additional_input->NaInflux,
			additional_input->I_DK);
*/
//------------------------------------------------------------------------
     profiler_write_entry_disable_irq_fiq(
          PROFILER_EXIT | PROFILER_INTRINSIC_CURRENT);
//------------------------------------------------------------------------
     return additional_input->I_DK;
}

//static void
static additional_input_has_spiked(
        additional_input_pointer_t additional_input) {

//      log_info("number of post-synaptic spikes: %u", n_spikes);
        }

#endif // _ADDITIONAL_INPUT_PACEMAKER_H_
