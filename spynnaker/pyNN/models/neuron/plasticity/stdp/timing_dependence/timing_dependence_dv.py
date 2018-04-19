from spinn_utilities.overrides import overrides
from spynnaker.pyNN.models.neuron.plasticity.stdp.common \
    import plasticity_helpers
from spynnaker.pyNN.models.neuron.plasticity.stdp.synapse_structure \
    import SynapseStructureWeightDvDt
from .abstract_timing_dependence import AbstractTimingDependence

import logging

logger = logging.getLogger(__name__)

# LOOKUP_TAU_PLUS_SIZE = 256
LOOKUP_TAU_PLUS_SIZE = 0
LOOKUP_TAU_PLUS_SHIFT = 0
# LOOKUP_TAU_MINUS_SIZE = 256
LOOKUP_TAU_MINUS_SIZE = 0
LOOKUP_TAU_MINUS_SHIFT = 0


class TimingDependenceDvDt(AbstractTimingDependence):

    def __init__(self):
        AbstractTimingDependence.__init__(self)
        self._synapse_structure = SynapseStructureWeightDvDt()

    def is_same_as(self, timing_dependence):
        # pylint: disable=protected-access
        if not isinstance(timing_dependence, TimingDependenceDvDt):
            return False

    @property
    def vertex_executable_suffix(self):
        return ""

    @property
    def pre_trace_n_bytes(self):
        # Pair rule requires no pre-synaptic trace when only the nearest
        # Neighbours are considered and, a single 16-bit R1 trace
        return 0

    @overrides(AbstractTimingDependence.get_parameters_sdram_usage_in_bytes)
    def get_parameters_sdram_usage_in_bytes(self):
        return 0

    @property
    def n_weight_terms(self):
        return 1

    @overrides(AbstractTimingDependence.write_parameters)
    def write_parameters(self, spec, machine_time_step, weight_scales):
        pass

    @property
    def synaptic_structure(self):
        return self._synapse_structure

    @overrides(AbstractTimingDependence.get_provenance_data)
    def get_provenance_data(self, pre_population_label, post_population_label):
        prov_data = list()
        return prov_data

    def get_parameter_names(self):
        return []
