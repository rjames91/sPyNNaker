#ifndef _WEIGHT_ADDITIVE_DV_NMDA_IMPL_H_
#define _WEIGHT_ADDITIVE_DV_NMDA_IMPL_H_

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
    int32_t boost;
    int32_t boost_thresh;

} plasticity_weight_region_data_t;

typedef struct {
    int32_t initial_weight;

    int32_t dv_slow;
    int32_t nmda;

    const plasticity_weight_region_data_t *weight_region;
} weight_state_t;

#include "weight_dv_nmda.h"

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
        .nmda = 0,
        .weight_region = &plasticity_weight_region_data[synapse_type]
    };
}

//---------------------------------------
static inline weight_state_t weight_dv_apply(
        weight_state_t state, int32_t dv_slow, int32_t nmda) {
    state.dv_slow += dv_slow;
    state.nmda += nmda;
    return state;
}


//---------------------------------------
static inline weight_t weight_get_final(weight_state_t new_state) {

    // Scale potentiation and depression
    // **NOTE** A2+ and A2- are pre-scaled into weight format
    int32_t scale = new_state.weight_region->scale;
    
    // int32_t pre_scale = scale;
    
    if (new_state.dv_slow > 0){
        if (new_state.nmda > new_state.weight_region->boost_thresh){
        // when lateral neurons sent sufficient spikes, add boost to LTP
        // scale += new_state.weight_region->boost;
            scale = new_state.weight_region->boost;
        }
        // else{
            // scale = 0;
        // }
    }
    
    // dv_slow needs to be scaled to STDP proportions
    int32_t scaled_dw = STDP_FIXED_MUL_16X16(new_state.dv_slow >> 4, scale);
    
//    io_printf("%012d\n", scaled_dv_slow);
//    log_info( "\tscaling: %d * %d = %d",
//        new_state.dv_slow, new_state.weight_region->scale, scaled_dv_slow);
    // Apply all terms to initial weight
    int32_t new_weight = new_state.initial_weight + scaled_dw;
//    log_info( "\tnew w: %d + %d = %d",
//        new_state.initial_weight, scaled_dv_slow, new_weight);


    // Clamp new weight
    new_weight = MIN(new_state.weight_region->max_weight,
                     MAX(new_weight, new_state.weight_region->min_weight));

   // log_info("\told_weight:%u, dv_slow:%d, scaled dv_slow:%d, new_weight:%d",
             // new_state.initial_weight, new_state.dv_slow, scaled_dw,
             // new_weight);

    // log_info(
        // "FINAL = scale:%d, boost:%d, scale-post:%d, nmda:%d, thr:%d, "
        // "dvSlow:%d, dw:%d, old_w:%d, new_w:%d",
        // pre_scale, new_state.weight_region->boost, scale,
        // new_state.nmda, new_state.weight_region->boost_thresh,
        // new_state.dv_slow, scaled_dw, new_state.initial_weight, new_weight);

    return (weight_t) new_weight;
}

#endif // _WEIGHT_ADDITIVE_ONE_TERM_IMPL_H_
