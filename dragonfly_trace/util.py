"""Utility functions for organizing TRACE exports."""
from collections import OrderedDict


def sort_rooms_for_trace_700(rooms):
    """Sort a list of rooms for TRACE 700 export.

    This sorting accounts for the fact that TRACE 700 wants rooms with the same
    zone to be next to one another in the component tree view.
    """
    # sort the rooms alphanumerically based on their identifiers
    rooms.sort(key=lambda x: x.identifier)  # this matches the gbXML export

    # reorder rooms such that those with the same zone are next to one another
    zone_dict = OrderedDict()
    for room in rooms:
        zone = room.display_name if room._zone is None else room.zone
        try:
            zone_dict[zone].append(room)
        except KeyError:
            zone_dict[zone] = [room]
    sorted_rooms = []
    for zone, rooms in zone_dict.items():
        sorted_rooms.extend(rooms)

    return sorted_rooms
