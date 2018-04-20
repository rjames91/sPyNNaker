// Spinn_common includes
#include "static-assert.h"

// sPyNNaker neural modelling includes
#include <neuron/synapses.h>
#include <neuron/plasticity/synapse_dynamics.h>

// Plasticity includes
#include "maths.h"
#include "post_events_dv.h"
#include "pre_events_dv.h"
#include "weight_dependence/weight.h"
#include "timing_dependence/timing.h"
#include <string.h>
#include <debug.h>
#include <utils.h>

// #include <neuron/models/neuron_model_lif_dv_impl.h>

static uint32_t _synapse_type_index_bits;
static uint32_t _synapse_index_bits;
static uint32_t _synapse_index_mask;
static uint32_t _synapse_type_index_mask;
static uint32_t _synapse_delay_index_type_bits;

uint32_t num_plastic_pre_synaptic_events = 0;

post_event_history_t *post_event_history;

static neuron_pointer_t neuron_array_plasticity;


//---------------------------------------
// Synapse update loop
//---------------------------------------
static inline final_state_t _plasticity_update_synapse(
        uint32_t time, uint32_t begin_time,
        uint32_t delay, uint32_t post_index, update_state_t current_state,
        const pre_event_history_t *pre_event_history,
        const post_event_history_t *post_event_history) {
    use(begin_time);
    use(delay);
    use(pre_event_history);
    use(post_event_history);
    neuron_pointer_t post_neuron = &neuron_array_plasticity[post_index];

    //'convert' to uint32 so we don't have to change the definition of ..._apply_...
    uint32_t dv_slow = (uint32_t)(*((uint32_t *)&post_neuron->dV_dt_slow));
   // io_printf(IO_BUF, "DW for neuron, t, dw = %012d;%05d;%11.6k\n",
           // time, post_index, post_neuron->dV_dt_slow);

    current_state = timing_apply_pre_spike(time, (pre_trace_t){}, 0,
                    (pre_trace_t){},
                    dv_slow, // changed from last post time
                    (post_trace_t){},
                    current_state);
    // Return final synaptic word and weight
    return synapse_structure_get_final_state(current_state);
}

//---------------------------------------
// Synaptic row plastic-region implementation
//---------------------------------------
static inline plastic_synapse_t* _plastic_synapses(
        address_t plastic_region_address) {
    // const uint32_t pre_event_history_size_words =
        // sizeof(pre_event_history_t) / sizeof(uint32_t);
    // static_assert(pre_event_history_size_words * sizeof(uint32_t)
                  // == sizeof(pre_event_history_t),
                  // "Size of pre_event_history_t structure should be a multiple"
                  // " of 32-bit words");
// 
    // return (plastic_synapse_t*)
        // (&plastic_region_address[pre_event_history_size_words]);

    // TODO: --------------------------------------------------------
    // TODO: FIGURE OUT HOW TO PASS THIS FROM PYTHON, WHICH SIZE SHOULD I CHANGE?
    // TODO: --------------------------------------------------------
    return (plastic_synapse_t*)
        (&plastic_region_address[1]);


}

//---------------------------------------
static inline pre_event_history_t *_plastic_event_history(
        address_t plastic_region_address) {
    return (pre_event_history_t*) (&plastic_region_address[0]);
}

    
//---------------------------------------
address_t synapse_dynamics_initialise(
        address_t address, uint32_t n_neurons,
        uint32_t *ring_buffer_to_input_buffer_left_shifts) {

    // Load timing dependence data
    address_t weight_region_address = timing_initialise(address);
    if (address == NULL) {
        return NULL;
    }

    // Load weight dependence data
    address_t weight_result = weight_initialise(
        weight_region_address, ring_buffer_to_input_buffer_left_shifts);
    if (weight_result == NULL) {
        return NULL;
    }

    post_event_history = post_events_init_buffers(n_neurons);
    if (post_event_history == NULL) {
        return NULL;
    }

    uint32_t n_neurons_power_2 = n_neurons;
    if (!is_power_of_2(n_neurons)) {
        n_neurons_power_2 = next_power_of_2(n_neurons);
    }
    uint32_t log_n_neurons = ilog_2(n_neurons_power_2);

    _synapse_type_index_bits = log_n_neurons + SYNAPSE_TYPE_BITS;
    _synapse_type_index_mask = (1 << _synapse_type_index_bits) - 1;
    _synapse_index_bits = log_n_neurons;
    _synapse_index_mask = (1 << _synapse_index_bits) - 1;
    _synapse_delay_index_type_bits =
                    SYNAPSE_DELAY_BITS + _synapse_type_index_bits;
        
    return weight_result;
}

bool synapse_dynamics_process_plastic_synapses(
        address_t plastic_region_address, address_t fixed_region_address,
        weight_t *ring_buffers, uint32_t time) {

    // Extract separate arrays of plastic synapses (from plastic region),
    // Control words (from fixed region) and number of plastic synapses
    plastic_synapse_t *plastic_words = _plastic_synapses(
                                              plastic_region_address);
    const control_t *control_words = synapse_row_plastic_controls(
                                                fixed_region_address);

    size_t plastic_synapse = synapse_row_num_plastic_controls(
                                                fixed_region_address);

    num_plastic_pre_synaptic_events += plastic_synapse;

    // Get event history from synaptic row
    pre_event_history_t *event_history = _plastic_event_history(
        plastic_region_address);

    // Get last pre-synaptic event from event history
    // **NOTE** at this level we don't care about individual synaptic delays
    const uint32_t last_pre_time = 0;
//            event_history->times[event_history->count_minus_one];

    // Loop through plastic synapses
    for (; plastic_synapse > 0; plastic_synapse--) {

        // Get next control word (auto incrementing)
        uint32_t control_word = *control_words++;

        // Extract control-word components
        // **NOTE** cunningly, control word is just the same as lower
        // 16-bits of 32-bit fixed synapse so same functions can be used
        uint32_t delay_axonal = 0;
        uint32_t delay_dendritic = synapse_row_sparse_delay(control_word, 
                                                    _synapse_type_index_bits);
        uint32_t type = synapse_row_sparse_type(control_word, 
                                                    _synapse_index_bits);
        uint32_t index = (uint32_t)synapse_row_sparse_index(control_word,
                                                    _synapse_index_mask);
        uint32_t type_index = synapse_row_sparse_type_index(control_word,
                                                    _synapse_type_index_mask);

        // Create update state from the plastic synaptic word
        update_state_t current_state = synapse_structure_get_update_state(
            *plastic_words, type);

        // Update the synapse state
        final_state_t final_state = _plasticity_update_synapse(
            time, last_pre_time, delay_dendritic, index, current_state, event_history,
            &post_event_history[index]);

        // Convert into ring buffer offset
        uint32_t ring_buffer_index = synapses_get_ring_buffer_index_combined(
                            delay_axonal + delay_dendritic + time, type_index,
                            _synapse_type_index_bits);

        // Add weight to ring-buffer entry
        // **NOTE** Dave suspects that this could be a potential location
        // for overflow
        uint32_t accumulation = ring_buffers[ring_buffer_index] +
                                synapse_structure_get_final_weight(final_state);
        uint32_t sat_test = accumulation & 0x10000;
        if (sat_test) {
            accumulation = sat_test - 1;
        }
        ring_buffers[ring_buffer_index] = accumulation;

        // Write back updated synaptic word to plastic region
        *plastic_words++ = synapse_structure_get_final_synaptic_word(
            final_state);
    }

    log_debug("Adding pre-synaptic event to trace at time:%u", time);

    // Add pre-event
//    const pre_trace_t last_pre_trace =
//        event_history->traces[event_history->count_minus_one];
    pre_events_add(time, event_history,
        timing_add_pre_spike(time, last_pre_time,
                            //last_pre_trace
                            (pre_trace_t){})
    );

    return true;
}

void synapse_dynamics_process_post_synaptic_event(
        uint32_t time, index_t neuron_index) {
    log_debug("Adding post-synaptic event to trace at time:%u", time);

    // Add post-event
    post_event_history_t *history = &post_event_history[neuron_index];
    const uint32_t last_post_time = history->times[history->count_minus_one];
    const post_trace_t last_post_trace = (post_trace_t){};

    post_events_add(time, history, timing_add_post_spike(time, last_post_time,
                                                         last_post_trace));
}

input_t synapse_dynamics_get_intrinsic_bias(uint32_t time, index_t neuron_index) {
    use(time);
    use(neuron_index);
    return 0.0k;
}

void synapse_dynamics_print_plastic_synapses(
        address_t plastic_region_address, address_t fixed_region_address,
        uint32_t *ring_buffer_to_input_buffer_left_shifts) {
    use(plastic_region_address);
    use(fixed_region_address);
    use(ring_buffer_to_input_buffer_left_shifts);
#if LOG_LEVEL >= LOG_DEBUG

    // Extract separate arrays of weights (from plastic region),
    // Control words (from fixed region) and number of plastic synapses
    weight_t *plastic_words = _plastic_synapses(plastic_region_address);
    const control_t *control_words = synapse_row_plastic_controls(
        fixed_region_address);
    size_t plastic_synapse = synapse_row_num_plastic_controls(
        fixed_region_address);
    const pre_event_history_t *event_history = _plastic_event_history(
        plastic_region_address);

    log_debug(
        "Plastic region %u synapses pre-synaptic event buffer count:%u:\n",
        plastic_synapse, event_history->count_minus_one + 1);

    // Loop through plastic synapses
    for (uint32_t i = 0; i < plastic_synapse; i++) {

        // Get next weight and control word (auto incrementing control word)
        uint32_t weight = *plastic_words++;
        uint32_t control_word = *control_words++;
        uint32_t synapse_type = synapse_row_sparse_type(control_word);

        log_debug("%08x [%3d: (w: %5u (=", control_word, i, weight);
        synapses_print_weight(
            weight, ring_buffer_to_input_buffer_left_shifts[synapse_type]);
        log_debug("nA) d: %2u, %s, n = %3u)] - {%08x %08x}\n",
                  synapse_row_sparse_delay(control_word),
                  synapse_types_get_type_char(synapse_row_sparse_type(
                                             control_word)),
                  synapse_row_sparse_index(control_word), SYNAPSE_DELAY_MASK,
                  SYNAPSE_TYPE_INDEX_BITS);
    }
#endif // LOG_LEVEL >= LOG_DEBUG
}

//! \brief returns the counters for plastic pre synaptic events based
//!        on (if the model was compiled with SYNAPSE_BENCHMARK parameter) or
//!        returns 0
//! \return counters for plastic pre synaptic events or 0
uint32_t synapse_dynamics_get_plastic_pre_synaptic_events(){
    return num_plastic_pre_synaptic_events;
}

void synapse_dynamics_set_neuron_array(neuron_pointer_t neuron_array){
    neuron_array_plasticity = neuron_array;
}

#if SYNGEN_ENABLED == 1

//! \brief  Searches the synaptic row for the the connection with the
//!         specified post-synaptic id
//! \param[in] id: the (core-local) id of the neuron to search for in the
//! synaptic row
//! \param[in] row: the core-local address of the synaptic row
//! \param[out] sp_data: the address of a struct through which to return
//! weight, delay information
//! \return bool: was the search successful?
bool find_plastic_neuron_with_id(uint32_t id, address_t row,
                                 structural_plasticity_data_t *sp_data){
    address_t fixed_region = synapse_row_fixed_region(row);
    address_t plastic_region_address = synapse_row_plastic_region(row);
    plastic_synapse_t *plastic_words =
        _plastic_synapses(plastic_region_address);
    control_t *control_words = synapse_row_plastic_controls(fixed_region);
    int32_t plastic_synapse = synapse_row_num_plastic_controls(fixed_region);
    plastic_synapse_t weight;
    uint32_t delay;

    // Loop through plastic synapses
    bool found = false;
    for (; plastic_synapse > 0; plastic_synapse--) {

        // Get next control word (auto incrementing)
        weight = *plastic_words++;
        uint32_t control_word = *control_words++;

        // Check if index is the one I'm looking for
        delay = synapse_row_sparse_delay(control_word, _synapse_type_index_bits);
        if (synapse_row_sparse_index(control_word, _synapse_index_mask)==id) {
            found = true;
            break;
        }
    }

    if (found){
        sp_data -> weight = weight;
        sp_data -> offset = synapse_row_num_plastic_controls(fixed_region) -
            plastic_synapse;
        sp_data -> delay  = delay;
        return true;
        }
    else{
        sp_data -> weight = -1;
        sp_data -> offset = -1;
        sp_data -> delay  = -1;
        return false;
        }
}

//! \brief  Remove the entry at the specified offset in the synaptic row
//! \param[in] offset: the offset in the row at which to remove the entry
//! \param[in] row: the core-local address of the synaptic row
//! \return bool: was the removal successful?
bool remove_plastic_neuron_at_offset(uint32_t offset, address_t row){
    address_t fixed_region = synapse_row_fixed_region(row);
    plastic_synapse_t *plastic_words =
        _plastic_synapses(synapse_row_plastic_region(row));
    control_t *control_words = synapse_row_plastic_controls(fixed_region);
    int32_t plastic_synapse = synapse_row_num_plastic_controls(fixed_region);

    // Delete weight at offset
    plastic_words[offset] =  plastic_words[plastic_synapse-1];
    plastic_words[plastic_synapse-1] = 0;

   // Delete control word at offset
    control_words[offset] = control_words[plastic_synapse-1];
    control_words[plastic_synapse-1] = 0;

    // Decrement FP
    fixed_region[1] = fixed_region[1] - 1;

    return true;
}

//! ensuring the weight is of the correct type and size
static inline plastic_synapse_t _weight_conversion(uint32_t weight){
    return (plastic_synapse_t)(0xFFFF & weight);
}

//! packing all of the information into the required plastic control word
static inline control_t _control_conversion(uint32_t id, uint32_t delay,
                                            uint32_t type){
    control_t new_control =
        ((delay & ((1<<SYNAPSE_DELAY_BITS) - 1)) << _synapse_type_index_bits);
    new_control |= (type & ((1<<_synapse_type_index_bits) - 1)) << _synapse_index_bits;
    new_control |= (id & ((1<<_synapse_index_bits) - 1));
    return new_control;
}

//! \brief  Add a plastic entry in the synaptic row
//! \param[in] is: the (core-local) id of the post-synaptic neuron to be added
//! \param[in] row: the core-local address of the synaptic row
//! \param[in] weight: the initial weight associated with the connection
//! \param[in] delay: the delay associated with the connection
//! \param[in] type: the type of the connection (e.g. inhibitory)
//! \return bool: was the addition successful?
bool add_plastic_neuron_with_id(uint32_t id, address_t row,
        uint32_t weight, uint32_t delay, uint32_t type){
    plastic_synapse_t new_weight = _weight_conversion(weight);
    control_t new_control = _control_conversion(id, delay, type);

    address_t fixed_region = synapse_row_fixed_region(row);
    plastic_synapse_t *plastic_words =
        _plastic_synapses(synapse_row_plastic_region(row));
    control_t *control_words = synapse_row_plastic_controls(fixed_region);
    int32_t plastic_synapse = synapse_row_num_plastic_controls(fixed_region);

    // Add weight at offset
    plastic_words[plastic_synapse] = new_weight;

    // Add control word at offset
    control_words[plastic_synapse] = new_control;

    // Increment FP
    fixed_region[1] = fixed_region[1] + 1;
    return true;
}
#endif //SYNGEN_ENABLED
