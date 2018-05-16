#include "timing_nearest_pair_impl.h"

//---------------------------------------
// Globals
//---------------------------------------

//---------------------------------------
// Functions
//---------------------------------------
address_t timing_initialise(address_t address) {

    log_info("timing_initialise: starting");
    log_info("\tdV - NMDA rule");
    // **TODO** assert number of neurons is less than max

    // Copy LUTs from following memory
    log_info("timing_initialise: completed successfully");

//    return lut_address;
    return address;
}
