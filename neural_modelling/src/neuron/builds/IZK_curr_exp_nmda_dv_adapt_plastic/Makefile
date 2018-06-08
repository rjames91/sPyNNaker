APP = $(notdir $(CURDIR))
BUILD_DIR = build/

NEURON_MODEL = $(SOURCE_DIR)/neuron/models/neuron_model_izh_dv_2c_impl.c
NEURON_MODEL_H = $(SOURCE_DIR)/neuron/models/neuron_model_izh_dv_2c_impl.h
INPUT_TYPE_H = $(SOURCE_DIR)/neuron/input_types/input_type_current_nmda.h
THRESHOLD_TYPE_H = $(SOURCE_DIR)/neuron/threshold_types/threshold_type_adaptive_izk.h
SYNAPSE_TYPE_H = $(SOURCE_DIR)/neuron/synapse_types/synapse_types_exponential_nmda_impl.h
SYNAPSE_DYNAMICS = $(SOURCE_DIR)/neuron/plasticity/stdp/synapse_dynamics_dv_nmda_impl.c
TIMING_DEPENDENCE = $(SOURCE_DIR)/neuron/plasticity/stdp/timing_dependence/timing_dv_nmda_impl.c
TIMING_DEPENDENCE_H = $(SOURCE_DIR)/neuron/plasticity/stdp/timing_dependence/timing_dv_nmda_impl.h
WEIGHT_DEPENDENCE = $(SOURCE_DIR)/neuron/plasticity/stdp/weight_dependence/weight_dv_nmda_impl.c
WEIGHT_DEPENDENCE_H = $(SOURCE_DIR)/neuron/plasticity/stdp/weight_dependence/weight_dv_nmda_impl.h

include ../Makefile.common
