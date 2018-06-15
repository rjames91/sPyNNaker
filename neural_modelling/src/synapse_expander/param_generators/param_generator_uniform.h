#include <stdfix.h>
#include <spin1_api.h>
#include <stdfix-full-iso.h>
#include <synapse_expander/rng.h>

struct param_generator_uniform_params {
    accum low;
    accum high;
};

struct param_generator_uniform {
    struct param_generator_uniform_params params;
    rng_t rng;
};

void *param_generator_uniform_initialize(address_t *region) {
    struct param_generator_uniform *params =
        (struct param_generator_uniform *)
            spin1_malloc(sizeof(struct param_generator_uniform));
    spin1_memcpy(
        &(params->params), *region,
        sizeof(struct param_generator_uniform_params));
    *region += sizeof(struct param_generator_uniform_params) >> 2;
    log_debug("Uniform low = %k, high = %k",
        params->params.low, params->params.high);
    params->rng = rng_init(region);
    return params;
}

void param_generator_uniform_free(void *data) {
    sark_free(data);
}

void param_generator_uniform_generate(
        void *data, uint32_t n_synapses, uint32_t pre_neuron_index,
        uint16_t *indices, accum *values) {
    use(pre_neuron_index);
    use(indices);
    struct param_generator_uniform *params =
        (struct param_generator_uniform *) data;
    accum range = params->params.high - params->params.low;
    for (uint32_t i = 0; i < n_synapses; i++) {
        values[i] =
            params->params.low + (ulrbits(rng_generator(params->rng)) * range);
    }
}