from six import add_metaclass

from spinn_utilities.abstract_base import AbstractBase


@add_metaclass(AbstractBase)
class AbstractHasSingleScale(object):

    __slots__ = [
        # things
        '_scale',
    ]

    def __init__(self):
        self._scale = None

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, new_value):
        self._scale = new_value
