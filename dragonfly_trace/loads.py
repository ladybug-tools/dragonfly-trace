# coding=utf-8
"""Methods to write room loads to matrices for Trane TRACE tables."""
from __future__ import division


def people_and_lights_trace700_matrix(rooms, si_units=False):
    """Get a matrix for the "People & Lighting" table of the TRACE 700 Component Tree.

    Args:
        rooms: A list of dragonfly Room2Ds and honeybee Rooms for which the
            TRACE 700 "People & Lighting" matrix will be returned.
        si_units: Boolean to note whether the units of the values in the resulting
            matrix are in SI (True) instead of IP (False). (Default: False).

    Returns:
        A list of list where each sublist represents a row of the People & Lighting
        table of the TRACE 700 Component Tree.
    """


def miscellaneous_loads_trace700_matrix(rooms, si_units=False):
    """Get a matrix for the "People & Lighting" table of the TRACE 700 Component Tree.

    Args:
        rooms: A list of dragonfly Room2Ds and honeybee Rooms for which the
            TRACE 700 "People & Lighting" matrix will be returned.
        si_units: Boolean to note whether the units of the values in the resulting
            matrix are in SI (True) instead of IP (False). (Default: False).

    Returns:
        A list of list where each sublist represents a row of the People & Lighting
        table of the TRACE 700 Component Tree.
    """
