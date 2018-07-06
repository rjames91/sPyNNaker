from spinn_utilities.ranged.range_dictionary import RangeDictionary
from .spynnaker_ranged_list import SpynnakerRangedList


class SpynnakerRangeDictionary(RangeDictionary):

    def list_factory(self, size, value, key):
        """
        Defines which class or subclass of RangedList to use

        Main purpose is for subclasses to use a subclass or RangedList
        All parameters are pass through ones to the List constructor

        :param size: Fixed length of the list
        :param value: value to given to all elements in the list
        :param key: The dict key this list covers.
        :return: AbstractList in this case a RangedList
        """
        return SpynnakerRangedList(size, value, key)
