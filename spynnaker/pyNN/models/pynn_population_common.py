from pacman.model.constraints import AbstractConstraint
from pacman.model.constraints.placer_constraints\
    import ChipAndCoreConstraint

from spynnaker.pyNN.models.abstract_models \
    import AbstractReadParametersBeforeSet, AbstractContainsUnits
from spynnaker.pyNN.models.abstract_models \
    import AbstractPopulationInitializable, AbstractPopulationSettable
from spynnaker.pyNN.models.neuron.input_types import InputTypeConductance

from spinn_front_end_common.utilities import globals_variables
from spinn_front_end_common.utilities.exceptions import ConfigurationException
from spinn_front_end_common.abstract_models import AbstractChangableAfterRun

import numpy
import logging
from six import iteritems, string_types
logger = logging.getLogger(__file__)


class PyNNPopulationCommon(object):
    __slots__ = [
        "_all_ids",
        "_change_requires_mapping",
        "_delay_vertex",
        "_first_id",
        "_has_read_neuron_parameters_this_run",
        "_last_id",
        "_positions",
        "_record_gsyn_file",
        "_record_spike_file",
        "_record_v_file",
        "_size",
        "_spinnaker_control",
        "_structure",
        "_vertex",
        "_vertex_changeable_after_run",
        "_vertex_contains_units",
        "_vertex_has_set_max_atoms_per_core",
        "_vertex_population_initializable",
        "_vertex_population_settable",
        "_vertex_read_parameters_before_set"]

    def __init__(
            self, spinnaker_control, size, vertex, structure, initial_values):
        # pylint: disable=too-many-arguments
        if size is not None and size <= 0:
            raise ConfigurationException(
                "A population cannot have a negative or zero size.")

        self._vertex = vertex

        # copy the parameters so that the end users are not exposed to the
        # additions placed by SpiNNaker.
        if initial_values is not None:
            for name, value in iteritems(initial_values):
                self._vertex.set_value(name, value)

        # Introspect properties of the vertex
        self._vertex_population_settable = \
            isinstance(self._vertex, AbstractPopulationSettable)
        self._vertex_population_initializable = \
            isinstance(self._vertex, AbstractPopulationInitializable)
        self._vertex_changeable_after_run = \
            isinstance(self._vertex, AbstractChangableAfterRun)
        self._vertex_read_parameters_before_set = \
            isinstance(self._vertex, AbstractReadParametersBeforeSet)
        self._vertex_contains_units = \
            isinstance(self._vertex, AbstractContainsUnits)
        self._vertex_has_set_max_atoms_per_core = \
            hasattr(self._vertex, "set_model_max_atoms_per_core")

        self._spinnaker_control = spinnaker_control
        self._delay_vertex = None

        # Internal structure now supported 23 November 2014 ADR
        # structure should be a valid Space.py structure type.
        # generation of positions is deferred until needed.
        if structure:
            self._structure = structure
            self._positions = None
        else:
            self._structure = None

        # add objects to the SpiNNaker control class
        self._spinnaker_control.add_population(self)
        self._spinnaker_control.add_application_vertex(self._vertex)

        # initialise common stuff
        self._size = size
        self._record_spike_file = None
        self._record_v_file = None
        self._record_gsyn_file = None

        # parameter
        self._change_requires_mapping = True
        self._has_read_neuron_parameters_this_run = False

        # things for pynn demands
        self._all_ids = numpy.arange(
            globals_variables.get_simulator().id_counter,
            globals_variables.get_simulator().id_counter + size)
        self._first_id = self._all_ids[0]
        self._last_id = self._all_ids[-1]

        # update the simulators id_counter for giving a unique ID for every
        # atom
        globals_variables.get_simulator().id_counter += size

    @property
    def first_id(self):
        return self._first_id

    @property
    def last_id(self):
        return self._last_id

    @property
    def requires_mapping(self):
        return self._change_requires_mapping

    @requires_mapping.setter
    def requires_mapping(self, new_value):
        self._change_requires_mapping = new_value

    def mark_no_changes(self):
        self._change_requires_mapping = False
        self._has_read_neuron_parameters_this_run = False

    def __add__(self, other):
        """ Merges populations
        """
        # TODO: Make this add the neurons from another population to this one
        raise NotImplementedError

    def all(self):
        """ Iterator over cell IDs on all nodes.
        """
        # TODO: Return the cells when we have such a thing
        raise NotImplementedError

    @property
    def conductance_based(self):
        """ True if the population uses conductance inputs
        """
        return isinstance(self._vertex.input_type, InputTypeConductance)

    def __getitem__(self, index_or_slice):
        # Note: This is supported by sPyNNaker8
        # TODO: Used to get a single cell - not yet supported
        raise NotImplementedError

    def get(self, parameter_names, gather=False):
        """ Get the values of a parameter for every local cell in the\
            population.

        :param parameter_names: Name of parameter. This is either a single\
            string or a list of strings
        :return: A single list of values (or possibly a single value) if\
            paramter_names is a string, or a dict of these if parameter names\
            is a list.
        :rtype: str or list(str) or dict(str,str) or dict(str,list(str))
        """
        if not self._vertex_population_settable:
            raise KeyError("Population does not support setting")
        if isinstance(parameter_names, string_types):
            return self._vertex.get_value(parameter_names)
        results = dict()
        for parameter_name in parameter_names:
            results[parameter_name] = self._vertex.get_value(parameter_name)
        return results

    # NON-PYNN API CALL
    def get_by_selector(self, selector, parameter_names):
        """ Get the values of a parameter for the selected cell in the\
            population.

        :param parameter_names: Name of parameter. This is either a\
            single string or a list of strings
        :param selector: a description of the subrange to accept. \
            Or None for all. \
            See: _selector_to_ids in \
            SpiNNUtils.spinn_utilities.ranged.abstract_sized.py
        :return: A single list of values (or possibly a single value) if\
            paramter_names is a string or a dict of these if parameter names\
            is a list.
        :rtype: str or list(str) or dict(str,str) or dict(str,list(str))
        """
        if not self._vertex_population_settable:
            raise KeyError("Population does not support setting")
        if isinstance(parameter_names, string_types):
            return self._vertex.get_value_by_selector(
                selector, parameter_names)
        results = dict()
        for parameter_name in parameter_names:
            results[parameter_name] = self._vertex.get_value_by_selector(
                selector, parameter_name)
        return results

    def id_to_index(self, id):  # @ReservedAssignment
        """ Given the ID(s) of cell(s) in the Population, return its (their)\
            index (order in the Population).
        """
        # pylint: disable=redefined-builtin
        if not numpy.iterable(id):
            if not self._first_id <= id <= self._last_id:
                raise ValueError(
                    "id should be in the range [{},{}], actually {}".format(
                        self._first_id, self._last_id, id))
            return int(id - self._first_id)  # this assumes IDs are consecutive
        return id - self._first_id

    def index_to_id(self, index):
        """ Given the index (order in the Population) of cell(s) in the\
            Population, return their ID(s)
        """
        if not numpy.iterable(index):
            if index > self._last_id - self._first_id:
                raise ValueError(
                    "indexes should be in the range [{},{}], actually {}"
                    "".format(0, self._last_id - self._first_id, index))
            return int(index + self._first_id)
        # this assumes IDs are consecutive
        return index + self._first_id

    def id_to_local_index(self, cell_id):
        """ Given the ID(s) of cell(s) in the Population, return its (their)\
            index (order in the Population), counting only cells on the local\
            MPI node.
        """
        # TODO: Need __getitem__
        raise NotImplementedError

    def initialize(self, variable, value):
        """ Set the initial value of one of the state variables of the neurons\
            in this population.
        """
        if not self._vertex_population_initializable:
            raise KeyError(
                "Population does not support the initialisation of {}".format(
                    variable))
        if globals_variables.get_not_running_simulator().has_ran \
                and not self._vertex_changeable_after_run:
            raise Exception("Population does not support changes after run")
        self._vertex.initialize(variable, value)

    def can_record(self, variable):
        """ Determine whether `variable` can be recorded from this population.

        Note: This is supported by sPyNNaker8
        """

        # TODO: Needs a more precise recording mechanism (coming soon)
        raise NotImplementedError

    def inject(self, current_source):
        """ Connect a current source to all cells in the Population.
        """

        # TODO:
        raise NotImplementedError

    def __iter__(self):
        """ Iterate over local cells

        Note: This is supported by sPyNNaker8
        """

        # TODO:
        raise NotImplementedError

    def __len__(self):
        """ Get the total number of cells in the population.
        """
        return self._size

    @property
    def label(self):
        """ The label of the population
        """
        return self._vertex.label

    @label.setter
    def label(self, new_value):
        self._vertex.label = new_value

    @property
    def local_size(self):
        """ The number of local cells
        """

        # Doesn't make much sense on SpiNNaker
        return self._size

    def _set_check(self, parameter, value):
        """ Checks for various set methods.
        """
        if not self._vertex_population_settable:
            raise KeyError("Population does not have property {}".format(
                parameter))

        if globals_variables.get_not_running_simulator().has_ran \
                and not self._vertex_changeable_after_run:
            raise Exception(
                " run has been called")

        if isinstance(parameter, string_types):
            if value is None:
                raise Exception("A value (not None) must be specified")
        elif type(parameter) is not dict:
            raise Exception(
                "Parameter must either be the name of a single parameter to"
                " set, or a dict of parameter: value items to set")

        self._read_parameters_before_set()

    def set(self, parameter, value=None):
        """ Set one or more parameters for every cell in the population.

        param can be a dict, in which case value should not be supplied, or a\
        string giving the parameter name, in which case value is the parameter\
        value. value can be a numeric value, or list of such\
        (e.g. for setting spike times)::

            p.set("tau_m", 20.0).
            p.set({'tau_m':20, 'v_rest':-65})

        :param parameter: the parameter to set
        :type parameter: str or dict
        :param value: the value of the parameter to set.
        """
        self._set_check(parameter, value)

        # set new parameters
        if isinstance(parameter, string_types):
            if value is None:
                raise Exception("A value (not None) must be specified")
            self._read_parameters_before_set()
            self._vertex.set_value(parameter, value)
            return
        for (key, value) in parameter.iteritems():
            self._vertex.set_value(key, value)

    # NON-PYNN API CALL
    def set_by_selector(self, selector, parameter, value=None):
        """ Set one or more parameters for selected cell in the population.

        param can be a dict, in which case value should not be supplied, or a\
        string giving the parameter name, in which case value is the parameter\
        value. value can be a numeric value, or list of such
        (e.g. for setting spike times)::

            p.set("tau_m", 20.0).
            p.set({'tau_m':20, 'v_rest':-65})

        :param selector: See RangedList.set_value_by_selector as this is just \
            a pass through method
        :param parameter: the parameter to set
        :param value: the value of the parameter to set.
        """
        self._set_check(parameter, value)

        # set new parameters
        if type(parameter) is str:
            self._vertex.set_value_by_selector(selector, parameter, value)
            return
        for (key, value) in parameter.iteritems():
            self._vertex.set_value_by_selector(selector, key, value)
        if not isinstance(parameter, dict):
            raise Exception(
                "Parameter must either be the name of a single parameter to"
                " set, or a dict of parameter: value items to set")

        # set new parameters
        self._read_parameters_before_set()
        for _key, _value in iteritems(parameter):
            self._vertex.set_value(_key, _value)

    def _read_parameters_before_set(self):
        """ Reads parameters from the machine before "set" completes

        :return: None
        """

        # If the tools have run before, and not reset, and the read
        # hasn't already been done, read back the data
        if globals_variables.get_simulator().has_ran \
                and not globals_variables.get_simulator().has_reset_last \
                and self._vertex_read_parameters_before_set \
                and not self._has_read_neuron_parameters_this_run \
                and not globals_variables.get_simulator().use_virtual_board:
            # locate machine vertices from the application vertices
            machine_vertices = globals_variables.get_simulator().graph_mapper\
                .get_machine_vertices(self._vertex)

            # go through each machine vertex and read the neuron parameters
            # it contains
            for machine_vertex in machine_vertices:

                # tell the core to rewrite neuron params back to the
                # SDRAM space.
                placement = globals_variables.get_simulator().placements.\
                    get_placement_of_vertex(machine_vertex)

                self._vertex.read_parameters_from_machine(
                    globals_variables.get_simulator().transceiver, placement,
                    globals_variables.get_simulator().graph_mapper.get_slice(
                        machine_vertex))

            self._has_read_neuron_parameters_this_run = True

    def get_spike_counts(self, spikes, gather=True):
        """ Return the number of spikes for each neuron.
        """
        n_spikes = {}
        counts = numpy.bincount(spikes[:, 0].astype(dtype=numpy.int32),
                                minlength=self._vertex.n_atoms)
        for i in range(self._vertex.n_atoms):
            n_spikes[i] = counts[i]
        return n_spikes

    @property
    def structure(self):
        """ Return the structure for the population.
        """
        return self._structure

    # NON-PYNN API CALL
    def set_constraint(self, constraint):
        """ Apply a constraint to a population that restricts the processor\
            onto which its atoms will be placed.
        """
        globals_variables.get_simulator().verify_not_running()
        if not isinstance(constraint, AbstractConstraint):
            raise ConfigurationException(
                "the constraint entered is not a recognised constraint")

        self._vertex.add_constraint(constraint)
        # state that something has changed in the population,
        self._change_requires_mapping = True

    # NON-PYNN API CALL
    def add_placement_constraint(self, x, y, p=None):
        """ Add a placement constraint

        :param x: The x-coordinate of the placement constraint
        :type x: int
        :param y: The y-coordinate of the placement constraint
        :type y: int
        :param p: The processor ID of the placement constraint (optional)
        :type p: int
        """
        globals_variables.get_simulator().verify_not_running()
        self._vertex.add_constraint(ChipAndCoreConstraint(x, y, p))

        # state that something has changed in the population,
        self._change_requires_mapping = True

    # NON-PYNN API CALL
    def set_mapping_constraint(self, constraint_dict):
        """ Add a placement constraint - for backwards compatibility

        :param constraint_dict: A dictionary containing "x", "y" and\
            optionally "p" as keys, and ints as values
        :type constraint_dict: dict(str, int)
        """
        globals_variables.get_simulator().verify_not_running()
        self.add_placement_constraint(**constraint_dict)

        # state that something has changed in the population,
        self._change_requires_mapping = True

    # NON-PYNN API CALL
    def set_model_based_max_atoms_per_core(self, new_value):
        """ Supports the setting of each models max atoms per core parameter

        :param new_value: the new value for the max atoms per core.
        """
        if not self._vertex_has_set_max_atoms_per_core:
            raise ConfigurationException(
                "This population does not support its max_atoms_per_core "
                "variable being adjusted by the end user")

        globals_variables.get_simulator().verify_not_running()
        self._vertex.set_model_max_atoms_per_core(new_value)
        # state that something has changed in the population,
        self._change_requires_mapping = True

    @property
    def size(self):
        """ The number of neurons in the population
        """
        return self._vertex.n_atoms

    @property
    def _get_vertex(self):
        return self._vertex

    @property
    def _internal_delay_vertex(self):
        return self._delay_vertex

    @_internal_delay_vertex.setter
    def _internal_delay_vertex(self, delay_vertex):
        self._delay_vertex = delay_vertex
        self._change_requires_mapping = True

    @staticmethod
    def create_label(model_label, pop_level_label):
        """ Helper method for choosing a label from model and population levels

        :param model_label: the model level label
        :param pop_level_label: the pop level label
        :return: the new model level label
        """
        cell_label = None
        if model_label is None and pop_level_label is None:
            cell_label = "Population {}".format(
                globals_variables.get_simulator().none_labelled_vertex_count)
            globals_variables.get_simulator(). \
                increment_none_labelled_vertex_count()
        elif model_label is None and pop_level_label is not None:
            cell_label = pop_level_label
        elif model_label is not None and pop_level_label is None:
            cell_label = model_label
        elif model_label is not None and pop_level_label is not None:
            cell_label = pop_level_label
            logger.warning("Don't know which label to use. Will use pop "
                           "label and carry on")
        return cell_label

    def _get_variable_unit(self, parameter_name):
        """ Helper method for getting units from a parameter used by the vertex

        :param parameter_name: the parameter name to find the units for
        :return: the units in string form
        """
        if self._vertex_contains_units:
            return self._vertex.get_units(parameter_name)
        raise ConfigurationException(
            "This population does not support describing its units")

    def _roundsize(self, size, label):
        if isinstance(size, int):
            return size
        # External device population can have a size of None so accept for now
        if size is None:
            return None
        if label is None:
            label = "None"
        # Allow a float which has a near int value
        temp = int(round(size))
        if abs(temp - size) < 0.001:
            logger.warning("Size of the population with label %s rounded "
                           "from %s to %d. Please use int values for size",
                           label, size, temp)
            return temp
        raise ConfigurationException(
            "Size of a population with label {} must be an int,"
            " received {}".format(label, size))
