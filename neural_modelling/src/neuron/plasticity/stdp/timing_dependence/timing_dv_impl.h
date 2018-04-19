#ifndef _TIMING_DV_IMPL_H_
#define _TIMING_DV_IMPL_H_

//---------------------------------------
// Structures
//---------------------------------------
typedef struct post_trace_t {
} post_trace_t;

typedef struct pre_trace_t {
} pre_trace_t;
#include <neuron/plasticity/stdp/maths.h>
#include <neuron/plasticity/stdp/synapse_structure/synapse_structure_weight_dv_impl.h>
#include <neuron/plasticity/stdp/timing_dependence/timing.h>
#include <neuron/plasticity/stdp/weight_dependence/weight_dv.h>


// Include debug header for log_info etc
#include <debug.h>

// Include generic plasticity maths functions
#include <neuron/plasticity/stdp/maths.h>




//---------------------------------------
// Macros
//---------------------------------------

//---------------------------------------
// Externals
//---------------------------------------

//---------------------------------------
// Timing dependence inline functions
//---------------------------------------
static inline post_trace_t timing_get_initial_post_trace() {
    return (post_trace_t) {};
}

//---------------------------------------
static inline post_trace_t timing_add_post_spike(
        uint32_t time, uint32_t last_time, post_trace_t last_trace) {
    use(&last_time);
    use(&last_trace);

    log_debug("\tdelta_time=%u\n", time - last_time);

    // Return new pre- synaptic event with decayed trace values with energy
    // for new spike added
    return (post_trace_t) {};
}

//---------------------------------------
static inline pre_trace_t timing_add_pre_spike(
        uint32_t time, uint32_t last_time, pre_trace_t last_trace) {
    use(&last_time);
    use(&last_trace);

    log_debug("\tdelta_time=%u\n", time - last_time);

    return (pre_trace_t ) {};
}

//---------------------------------------
static inline update_state_t timing_apply_pre_spike(
        uint32_t time, pre_trace_t trace, uint32_t last_pre_time,
        pre_trace_t last_pre_trace,
        uint32_t dv_slow, // changed from last post time
        post_trace_t last_post_trace, update_state_t previous_state) {
    use(&trace);
    use(&last_pre_time);
    use(&last_pre_trace);
    use(&last_post_trace);
    use(&time);

    // dv is in 32-bit S16.15 format, we need to change it to 16-bit S4.11 format
//    int32_t dv = (((int32_t)dv_slow) >> 4);
    int32_t dv = (int32_t)dv_slow;
//    log_info("in timing_apply_pre_spike time, dv = %u, %11.6k, %d", time, dv, dv);
//    log_info("timing_apply dv full %d", dv);
    dv = dv >> 4;
//    log_info( "in timing_apply_pre_spike time, dv = %u, %d, %d %d\t%d",
//              time, dv, (dv>>12), ((dv>>12)& ((1 << 12) -1)), (dv & ((1 << 12) -1)) );
//    log_info("timing_apply dv half %d", dv);

    return weight_dv_apply(previous_state, dv);

}

//---------------------------------------
static inline update_state_t timing_apply_post_spike(
        uint32_t time, post_trace_t trace, uint32_t last_pre_time,
        pre_trace_t last_pre_trace, uint32_t last_post_time,
        post_trace_t last_post_trace, update_state_t previous_state) {
    use(&trace);
    use(&last_pre_trace);
    use(&last_post_time);
    use(&last_post_trace);
    use(&time);
    use(&last_pre_time);

    return previous_state;

}

#endif	// _TIMING_dV_IMPL_H_
