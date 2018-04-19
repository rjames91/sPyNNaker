#ifndef _WEIGHT_ADDITIVE_DV_IMPL_H_
#define _WEIGHT_ADDITIVE_DV_IMPL_H_

// Include generic plasticity maths functions
#include <neuron/plasticity/stdp/maths.h>
#include <neuron/plasticity/stdp/stdp_typedefs.h>
#include <neuron/synapse_row.h>

#include <debug.h>

//---------------------------------------
// Structures
//---------------------------------------
typedef struct {
    int32_t min_weight;
    int32_t max_weight;

    int32_t scale;

} plasticity_weight_region_data_t;

typedef struct {
    int32_t initial_weight;

    int32_t dv_slow;

    const plasticity_weight_region_data_t *weight_region;
} weight_state_t;

#include "weight_dv.h"

//---------------------------------------
// Externals
//---------------------------------------
extern plasticity_weight_region_data_t
    plasticity_weight_region_data[SYNAPSE_TYPE_COUNT];

//---------------------------------------
// STDP weight dependance functions
//---------------------------------------
static inline weight_state_t weight_get_initial(weight_t weight,
                                                index_t synapse_type) {

    return (weight_state_t ) {
        .initial_weight = (int32_t) weight,
        .dv_slow = 0,
        .weight_region = &plasticity_weight_region_data[synapse_type]
    };
}

//---------------------------------------
static inline weight_state_t weight_dv_apply(
        weight_state_t state, int32_t dv_slow) {
    state.dv_slow += dv_slow;
    return state;
}


//---------------------------------------
static inline weight_t weight_get_final(weight_state_t new_state) {

    // Scale potentiation and depression
    // **NOTE** A2+ and A2- are pre-scaled into weight format
    int32_t scaled_dv_slow = STDP_FIXED_MUL_16X16(
        new_state.dv_slow, new_state.weight_region->scale);
//    io_printf("%012d\n", scaled_dv_slow);
//    log_info( "\tscaling: %d * %d = %d",
//        new_state.dv_slow, new_state.weight_region->scale, scaled_dv_slow);
    // Apply all terms to initial weight
    int32_t new_weight = new_state.initial_weight + scaled_dv_slow;
//    log_info( "\tnew w: %d + %d = %d",
//        new_state.initial_weight, scaled_dv_slow, new_weight);


    // Clamp new weight
    new_weight = MIN(new_state.weight_region->max_weight,
                     MAX(new_weight, new_state.weight_region->min_weight));

//    log_info("\told_weight:%u, dv_slow:%d, scaled dv_slow:%d, new_weight:%d",
//              new_state.initial_weight, new_state.dv_slow, scaled_dv_slow,
//              new_weight);

    return (weight_t) new_weight;
}

#endif // _WEIGHT_ADDITIVE_ONE_TERM_IMPL_H_
