from spynnaker.pyNN.exceptions import SpynnakerException
from spynnaker.pyNN.models.neuron import AbstractPopulationVertex


class IFCondAlpha(AbstractPopulationVertex):
    """ Leaky integrate and fire neuron with an alpha-shaped current input.
    """

    # noinspection PyPep8Naming
    def __init__(
            self, n_neurons, spikes_per_second=None, ring_buffer_sigma=None,
            incoming_spike_buffer_size=None, constraints=None, label=None,
            tau_m=20, cm=1.0, e_rev_E=0.0, e_rev_I=-70.0, v_rest=-65.0,
            v_reset=-65.0, v_thresh=-50.0, tau_syn_E=0.3, tau_syn_I=0.5,
            tau_refrac=0.1, i_offset=0, v_init=None):
        # pylint: disable=too-many-arguments, too-many-locals, unused-argument
        raise SpynnakerException(
            "This neuron model is currently not supported by the tool chain")

    @staticmethod
    def set_model_max_atoms_per_core(new_value):
        """ ???
        """
