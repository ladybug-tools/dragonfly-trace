"""Utility functions for organizing TRACE exports."""
from collections import OrderedDict
from honeybee.room import Room


def sort_rooms_for_trace_700(rooms):
    """Sort a list of rooms for TRACE 700 export.

    This sorting accounts for the fact that TRACE 700 wants rooms with the same
    zone to be next to one another in the component tree view.
    """
    # reorder rooms such that those with the same HVAC system are next to one another
    hvac_dict = OrderedDict()
    for room in rooms:
        hvac = room.properties.energy.hvac
        if hvac is None:
            hvac_id = room.story if isinstance(room, Room) else room.parent.display_name
        else:
            hvac_id = hvac.identifier
        try:
            hvac_dict[hvac_id].append(room)
        except KeyError:
            hvac_dict[hvac_id] = [room]
    sorted_rooms = []
    for hvac_id, rooms in hvac_dict.items():
        sorted_rooms.extend(rooms)

    # reorder rooms such that those with the same zone are next to one another
    zone_dict = OrderedDict()
    for room in sorted_rooms:
        zone = room.display_name if room._zone is None else room.zone
        try:
            zone_dict[zone].append(room)
        except KeyError:
            zone_dict[zone] = [room]
    sorted_rooms = []
    for zone, rooms in zone_dict.items():
        sorted_rooms.extend(rooms)

    return sorted_rooms
