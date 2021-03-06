import numpy
import math

from spinn_front_end_common.abstract_models import AbstractChangableAfterRun
from spinn_utilities.overrides import overrides
from spynnaker.pyNN.models.abstract_models import AbstractSettable
from .abstract_static_synapse_dynamics import AbstractStaticSynapseDynamics
from spynnaker.pyNN.exceptions import InvalidParameterType
from .abstract_synapse_dynamics import AbstractSynapseDynamics


class SynapseDynamicsStatic(
        AbstractStaticSynapseDynamics, AbstractSettable,
        AbstractChangableAfterRun):
    __slots__ = [
        # ??????????
        "_change_requires_mapping",
        # padding to add to a synaptic row for synaptic rewiring
        "_pad_to_length"]

    def __init__(self, pad_to_length=None):
        self._change_requires_mapping = True
        self._pad_to_length = pad_to_length

    @overrides(AbstractSynapseDynamics.is_same_as)
    def is_same_as(self, synapse_dynamics):
        return isinstance(synapse_dynamics, SynapseDynamicsStatic)

    @overrides(AbstractSynapseDynamics.are_weights_signed)
    def are_weights_signed(self):
        return False

    @overrides(AbstractSynapseDynamics.get_vertex_executable_suffix)
    def get_vertex_executable_suffix(self):
        return ""

    @overrides(AbstractSynapseDynamics.get_parameters_sdram_usage_in_bytes)
    def get_parameters_sdram_usage_in_bytes(self, n_neurons, n_synapse_types):
        return 0

    @overrides(AbstractSynapseDynamics.write_parameters)
    def write_parameters(self, spec, region, machine_time_step, weight_scales):
        # Nothing to do here
        pass

    @overrides(
        AbstractStaticSynapseDynamics.get_n_words_for_static_connections)
    def get_n_words_for_static_connections(self, n_connections):
        if (self._pad_to_length is not None and
                n_connections < self._pad_to_length):
            n_connections = self._pad_to_length
        return n_connections

    @overrides(AbstractStaticSynapseDynamics.get_static_synaptic_data)
    def get_static_synaptic_data(
            self, connections, connection_row_indices, n_rows,
            post_vertex_slice, n_synapse_types):
        # pylint: disable=too-many-arguments
        n_neuron_id_bits = int(
            math.ceil(math.log(post_vertex_slice.n_atoms, 2)))
        n_synapse_type_bits = int(math.ceil(math.log(n_synapse_types, 2)))

        fixed_fixed = (
            ((numpy.rint(numpy.abs(connections["weight"])).astype("uint32") &
              0xFFFF) << 16) |
            ((connections["delay"].astype("uint32") & 0xF) <<
             (n_neuron_id_bits + n_synapse_type_bits)) |
            (connections["synapse_type"].astype(
                "uint32") << n_neuron_id_bits) |
            ((connections["target"] - post_vertex_slice.lo_atom) & 0xFF))
        fixed_fixed_rows = self.convert_per_connection_data_to_rows(
            connection_row_indices, n_rows,
            fixed_fixed.view(dtype="uint8").reshape((-1, 4)))
        ff_size = self.get_n_items(fixed_fixed_rows, 4)
        if self._pad_to_length is not None:
            # Pad the data
            fixed_fixed_rows = self._pad_row(fixed_fixed_rows, 4)
        ff_data = [fixed_row.view("uint32") for fixed_row in fixed_fixed_rows]

        return ff_data, ff_size

    def _pad_row(self, rows, no_bytes_per_connection):
        padded_rows = []
        for row in rows:  # Row elements are (individual) bytes
            padded_rows.append(
                numpy.concatenate((
                    row, numpy.zeros(numpy.clip(
                        no_bytes_per_connection * self._pad_to_length -
                        row.size, 0, None)).astype(
                            dtype="uint8"))).view(dtype="uint8"))

        return padded_rows

    @overrides(AbstractStaticSynapseDynamics.get_n_static_words_per_row)
    def get_n_static_words_per_row(self, ff_size):

        # The sizes are in words, so just return them
        return ff_size

    @overrides(AbstractStaticSynapseDynamics.get_n_synapses_in_rows)
    def get_n_synapses_in_rows(self, ff_size):

        # Each word is a synapse and sizes are in words, so just return them
        return ff_size

    @overrides(AbstractStaticSynapseDynamics.read_static_synaptic_data)
    def read_static_synaptic_data(
            self, post_vertex_slice, n_synapse_types, ff_size, ff_data):

        n_synapse_type_bits = int(math.ceil(math.log(n_synapse_types, 2)))
        n_neuron_id_bits = int(
            math.ceil(math.log(post_vertex_slice.n_atoms, 2)))

        data = numpy.concatenate(ff_data)
        connections = numpy.zeros(data.size, dtype=self.NUMPY_CONNECTORS_DTYPE)
        connections["source"] = numpy.concatenate(
            [numpy.repeat(i, ff_size[i]) for i in range(len(ff_size))])
        connections["target"] = (data & 0xFF) + post_vertex_slice.lo_atom
        connections["weight"] = (data >> 16) & 0xFFFF
        connections["delay"] = (data >> (n_neuron_id_bits +
                                         n_synapse_type_bits)) & 0xF
        connections["delay"][connections["delay"] == 0] = 16

        return connections

    @overrides(AbstractChangableAfterRun.requires_mapping)
    def requires_mapping(self):
        """ True if changes that have been made require that mapping be\
            performed.  Note that this should return True the first time it\
            is called, as the vertex must require mapping as it has been\
            created!
        """
        return self._change_requires_mapping

    @overrides(AbstractChangableAfterRun.mark_no_changes)
    def mark_no_changes(self):
        """ Marks the point after which changes are reported.  Immediately\
            after calling this method, requires_mapping should return False.
        """
        self._change_requires_mapping = False

    @overrides(AbstractSettable.get_value)
    def get_value(self, key):
        """ Get a property
        """
        if hasattr(self, key):
            return getattr(self, key)
        raise InvalidParameterType(
            "Type {} does not have parameter {}".format(type(self), key))

    @overrides(AbstractSettable.set_value)
    def set_value(self, key, value):
        """ Set a property

        :param key: the name of the parameter to change
        :param value: the new value of the parameter to assign
        """
        if hasattr(self, key):
            setattr(self, key, value)
            self._change_requires_mapping = True
        raise InvalidParameterType(
            "Type {} does not have parameter {}".format(type(self), key))

    @overrides(AbstractStaticSynapseDynamics.get_parameter_names)
    def get_parameter_names(self):
        return ['weight', 'delay']

    @overrides(AbstractStaticSynapseDynamics.get_max_synapses)
    def get_max_synapses(self, n_words):
        return n_words
