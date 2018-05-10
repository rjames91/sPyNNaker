#ifndef _THRESHOLD_TYPE_ADAPTIVE_H_
#define _THRESHOLD_TYPE_ADAPTIVE_H_
#include <debug.h>

#include "threshold_type.h"

typedef struct threshold_type_t {

    // The value of the static threshold
    REAL threshold_value;
    REAL threshold_min;
    REAL threshold_max;
    REAL threshold_up;
    REAL threshold_down;

} threshold_type_t;

static inline bool threshold_type_is_above_threshold(state_t value,
                        threshold_type_pointer_t threshold_type) {

    bool did_it_spike =  REAL_COMPARE(value, >, threshold_type->threshold_value);
    if (did_it_spike){
        // make threshold higher
        threshold_type->threshold_value += threshold_type->threshold_up;

        // cap if greater tha maximum
        if (REAL_COMPARE(threshold_type->threshold_value, >,
                         threshold_type->threshold_max)){
            threshold_type->threshold_value = threshold_type->threshold_max;
        }
    }else{
        // reduce threshold
        threshold_type->threshold_value -= threshold_type->threshold_down;

        // cap if lower than lowest
        if (REAL_COMPARE(threshold_type->threshold_value, <,
            threshold_type->threshold_min)){
            threshold_type->threshold_value = threshold_type->threshold_min;
        }
    }
//    log_info("thresh %4.4k\t%4.4k\t%4.4k",
//        threshold_type->threshold_min, threshold_type->threshold_value,
//        threshold_type->threshold_max);

    return did_it_spike;
}

#endif // _THRESHOLD_TYPE_STATIC_H_
