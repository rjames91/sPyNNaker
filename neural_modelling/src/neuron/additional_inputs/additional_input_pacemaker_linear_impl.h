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

// Variables to control 'patch clamp' tests
static input_t local_v = -65;
static uint32_t n_spikes = 0;

// Variable to set m = m_inf on first timestep.
static uint32_t n_dt = 0;

// Variable to get the V_reset value from other neurons which will be used to clamp the neuron in each new spike arrival.
static neuron_pointer_t clamp_neuron;

static input_t additional_input_get_input_value_as_current(
        additional_input_pointer_t additional_input,
        state_t membrane_voltage) {

    // log_info("membrane potential: %k", membrane_voltage);

        // Hardcode membrane potential during tests:
        membrane_voltage = local_v;
    // log_info("local membrane potential: %k", local_v);

    profiler_write_entry_disable_irq_fiq(
        PROFILER_ENTER | PROFILER_INTRINSIC_CURRENT);

        additional_input->g_H = 0.015k;

        // piece-wise linear approximation to m_inf     
        if (membrane_voltage < -100.27315917574025k) {
                      additional_input->m_inf = 1k;
           } else if (membrane_voltage < -87.60837418258647k) {
                      additional_input->m_inf = 
                      0.2735578393208621k - 
                      0.007244632229108933k * membrane_voltage;
           } else if (membrane_voltage < -82.24326843308661k) {
                      additional_input->m_inf = -1.0442965932124193k - 
                      0.022287194596340095k * membrane_voltage;
           } else if (membrane_voltage < -67.75673208009987k) {
                      additional_input->m_inf = -2.4890698510182734k - 
                      0.03985426464756655k * membrane_voltage;
           } else if (membrane_voltage < -62.39162672916564k) {
                      additional_input->m_inf = -1.2987827262413782k - 
                      0.022287196575721303k * membrane_voltage;
           } else if (membrane_voltage < -49.72684082k) {
                      additional_input->m_inf = -0.3602527019929843k - 
                      0.007244632798334361k * membrane_voltage;
           } else if (membrane_voltage >= -49.72684082k) {
           additional_input->m_inf = 0k;
           }

        // hardcode initial value for m as m_inf
        n_dt += 1; 
        if (n_dt ==1){
        additional_input->m = additional_input->m_inf;
        }

        // piece-wise linear approximation to e_to_t_on_tau_m
        if (membrane_voltage < -110k ){
               additional_input->e_to_t_on_tau_m = 1.0814883341634767k + 0.0007950549506933303k*membrane_voltage;
            } else if (  membrane_voltage < -100k ){
               additional_input->e_to_t_on_tau_m = 1.030644594330175k + 0.0003328391340269521k* membrane_voltage;
            } else if ( membrane_voltage < -90k ){
              additional_input->e_to_t_on_tau_m = 1.0103634650620523k + 0.00013002784134572565k*membrane_voltage;  
            } else if ( membrane_voltage < -80k){
              additional_input->e_to_t_on_tau_m =  1.0015935711016k + 0.000032584575118477234k* membrane_voltage;
            } else if ( membrane_voltage < -70k ){
              additional_input->e_to_t_on_tau_m = 0.9964642185274247k - 0.00003153233205871464k*membrane_voltage;
            } else if ( membrane_voltage < -60k ){
              additional_input->e_to_t_on_tau_m = 0.9913474913574395k - 0.00010462843448707516k * membrane_voltage;
            } else if (  membrane_voltage < -50k   ){
              additional_input->e_to_t_on_tau_m = 0.9839498559815502k - 0.00022792235741856404k*membrane_voltage; 
            } else if (  membrane_voltage >= -50k   ){     // use the same equation for now
              additional_input->e_to_t_on_tau_m = 0.9839498559815502k - 0.00022792235741856404k*membrane_voltage;  
            }

        // Update m
        additional_input->m = additional_input->m_inf +
                (additional_input->m - additional_input->m_inf) *
                additional_input->e_to_t_on_tau_m;
        // h (inactivation) is 1 and constant, so we will just ignore it.
        additional_input->I_H = 
                additional_input->g_H *
                additional_input->m * 
                (membrane_voltage - -43.0k); //additional_input->E_H);
                
                
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

//n      log_info("number of post-synaptic spikes: %u", n_spikes);

}

#endif // _ADDITIONAL_INPUT_PACEMAKER_H_
