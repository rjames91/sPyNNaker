from six import add_metaclass

from spinn_utilities.abstract_base import AbstractBase


@add_metaclass(AbstractBase)
class AbstractHasScaleAndBoost(object):

    __slots__ = [
        # things
        '_scale',
        '_boost'
    ]

    def __init__(self):
        self._scale = None
        self._boost = None

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, new_value):
        self._scale = new_value

    @property
    def boost(self):
        return self._boost

    @boost.setter
    def boost(self, new_value):
        self._boost = new_value
