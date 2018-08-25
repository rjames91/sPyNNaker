#ifndef _ADDITIONAL_INPUT_PACEMAKER_H_
#define _ADDITIONAL_INPUT_PACEMAKER_H_

#include "additional_input.h"
#include "../profile_tags.h"
#include <profiler.h>

//----------------------------------------------------------------------------
typedef struct additional_input_t {
    // Pacemaker Current
    accum    I_H;
    accum    g_H;         // max pacemaker conductance
    accum    E_H;         // reversal potential
    accum    m_H;
    accum    m_inf_H;
    accum    e_to_t_on_tau_m_H;
    // Calcium Current
    accum    I_T;
    accum    g_T;         // max pacemaker conductance
    accum    E_T;         // reversal potential
    accum    m_T;
    accum    m_inf_T;
    accum    e_to_t_on_tau_m_T;
    accum    h_T;
    accum    h_inf_T;
    accum    e_to_t_on_tau_h_T;
    // Sodium Current
    accum    I_NaP;
    accum    g_NaP;       // max sodium conductance
    accum    E_NaP;       // sodium reversal potential
    accum    m_inf_NaP;
    // Potassium Current
    accum    I_DK;
    accum    g_DK;        // max potassium conductance
    accum    E_DK;        // potassium reversal potential
    accum    m_inf_DK;
    accum    e_to_t_on_tau_m_DK;
    accum    D;           
    accum    D_infinity; 
    // Voltage Clamp 
    accum      v_clamp;   // voltage for voltage clamp [mV], hold voltage is just V_rest
    uint32_t  s_clamp;    // clamp starting time [timesteps]
    uint32_t  t_clamp;    // clamp duration [timesteps] 
    //TODO:  maybe more efficient to get dt from other part of the software?
    accum    dt;
} additional_input_t;

// Variables to control 'patch clamp' tests
static input_t local_v;

// Variable to set m = m_inf on first timestep.
static uint32_t n_dt = 0;


static input_t additional_input_get_input_value_as_current(
        additional_input_pointer_t additional_input,
        state_t membrane_voltage) {

	if (n_dt >= additional_input->s_clamp &&
            n_dt < additional_input->s_clamp + additional_input->t_clamp){
        // local_v +=1;
        // membrane_voltage = local_v;
        local_v = additional_input->v_clamp;
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

/////////// piece-wise linear approximation to m_inf  /////////
/*        if (membrane_voltage < -100.27315917574025k) {
                      additional_input->m_inf_H = 1k;
           } else if (membrane_voltage < -87.60837418258647k) {
                      additional_input->m_inf_H =
                      0.2735578393208621k -
                      0.007244632229108933k * membrane_voltage;
           } else if (membrane_voltage < -82.24326843308661k) {
                      additional_input->m_inf_H = -1.0442965932124193k -
                      0.022287194596340095k * membrane_voltage;
           } else if (membrane_voltage < -67.75673208009987k) {
                      additional_input->m_inf_H = -2.4890698510182734k -
                      0.03985426464756655k * membrane_voltage;
           } else if (membrane_voltage < -62.39162672916564k) {
                      additional_input->m_inf_H = -1.2987827262413782k -
                      0.022287196575721303k * membrane_voltage;
           } else if (membrane_voltage < -49.72684082k) {
                      additional_input->m_inf_H = -0.3602527019929843k -
                      0.007244632798334361k * membrane_voltage;
           } else if (membrane_voltage >= -49.72684082k) {
           additional_input->m_inf_H = 0k;
           }
*/
////////////////////////////////////////////

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

/////////// Mixed format experiment /////////
/////////// for piece-wise quadratic approximation for e_to_t_on_tau_m 
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
    additional_input->e_to_t_on_tau_m_H = result_fract;

*/
////////////////////////////////////////////

	// Update m
	additional_input->m_H = additional_input->m_inf_H +
		(additional_input->m_H - additional_input->m_inf_H) *
         	additional_input->e_to_t_on_tau_m_H;

	// h (inactivation) is 1 and constant, so we will just ignore it.
	additional_input->I_H = 
		additional_input->g_H *
		additional_input->m_H *
		(membrane_voltage - additional_input->E_H); 
                                             //it was set to -65 but needs to be -43 to reproduce the results 
                                             //of Huguenard, not sure about the value used by Hans.

        //    _print_additional_input_params(additional_input);
//------------------------------------------------------------------------
    profiler_write_entry_disable_irq_fiq(
        PROFILER_EXIT | PROFILER_INTRINSIC_CURRENT);
//------------------------------------------------------------------------
    return additional_input->I_H;
}

static void additional_input_has_spiked(
        additional_input_pointer_t additional_input) {
        // Do nothing.
}

static inline void _print_additional_input_params(additional_input_t* additional_input){

                 log_info("Pacemaker Current \n"
                       " I_H: %k, g_H: %k, E_H: %k,   \n"
                       " m_H: %k,m_inf_H: %k,e_to_t_on_tau_m_H: %k, \n"
                       " Calcium Current: \n"
                       "I_T: %k, g_T: %k, E_T: %k,\n"
                       "m_T: %k,m_inf_T: %k, e_to_t_on_tau_m_T: %k,\n"
                       "h_T: %k, h_inf_T: %k, e_to_t_on_tau_h_T: %k,\n"
                       " Sodium Current:  \n"
                       "I_NaP: %k, g_NaP: %k,E_NaP: %k,\n"
                       "m_inf_NaP: %k,\n"
                       " Potassium Current:   \n"
                       "I_DK: %k, g_DK: %k, E_DK: %k, \n"
                       " m_inf_DK: %k,e_to_t_on_tau_m_DK: %k,\n"
                       " D: %k, D_infinity: %k,\n"
                       " Voltage Clamp:      \n"
                       " v_clamp: %k, s_clamp: %k, t_clamp: %k, dt: %k",
                       // Pacemaker Current
                       additional_input->I_H,
                       additional_input->g_H,
                       additional_input->E_H,
                       additional_input->m_H,
                       additional_input->m_inf_H,
                       additional_input->e_to_t_on_tau_m_H,
                       // Calcium Current
                       additional_input->I_T,
                       additional_input->g_T,
                       additional_input->E_T,
                       additional_input->m_T,
                       additional_input->m_inf_T,
                       additional_input->e_to_t_on_tau_m_T,
                       additional_input->h_T,
                       additional_input->h_inf_T,
                       additional_input->e_to_t_on_tau_h_T,
                       // Sodium Current
                       additional_input->I_NaP,
                       additional_input->g_NaP,
                       additional_input->E_NaP,
                       additional_input->m_inf_NaP,
                       // Potassium Current
                       additional_input->I_DK,
                       additional_input->g_DK,
                       additional_input->E_DK,
                       additional_input->m_inf_DK,
                       additional_input->e_to_t_on_tau_m_DK,
                       additional_input->D,
                       additional_input->D_infinity,
                       // Voltage Clamp 
                       additional_input->v_clamp,
                       additional_input->s_clamp,
                       additional_input->t_clamp,
                       additional_input->dt);
}

#endif // _ADDITIONAL_INPUT_PACEMAKER_H_
