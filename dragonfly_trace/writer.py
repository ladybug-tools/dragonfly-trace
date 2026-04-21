# coding=utf-8
"""Methods to write Dragonfly Models to Trane TRACE."""
from __future__ import division

from collections import OrderedDict

from ladybug.datatype.area import Area
from ladybug.datatype.distance import Distance
from ladybug.datatype.temperature import Temperature
from ladybug.datatype.rvalue import RValue
from honeybee.typing import clean_and_number_string
from dragonfly.room2d import Room2D

from .airflows import airflows_trace700_matrix
from .loads import people_and_lights_trace700_matrix, \
    miscellaneous_loads_trace700_matrix


def rooms_to_trace700_matrix(rooms, si_units=False):
    """Get a matrix for the "Rooms" table of the TRACE 700 Component Tree.

    Args:
        rooms: A list of dragonfly Room2Ds and honeybee Rooms for which the
            TRACE 700 "Rooms" matrix will be returned.
        si_units: Boolean to note whether the units of the values in the resulting
            matrix are in SI (True) instead of IP (False). (Default: False).

    Returns:
        A list of list where each sublist represents a row of the Rooms table
        of the TRACE 700 Component Tree.
    """
    # set up things for unit conversion
    dist_unit = 'm' if si_units else 'ft'
    r_unit = 'm2-C/W' if si_units else 'hr-ft2-F/Btu'
    temp_unit = 'C' if si_units else 'F'
    area, distance, temperature, r_value = Area(), Distance(), Temperature(), RValue()

    # set up the names of the rows
    row_names = [
        'Room Description',
        'Assigned to System',
        'Assigned to Zone',
        'Room Template',
        'Thermostat Template',
        'Construction Template',
        'Floor Length ({})'.format(dist_unit),
        'Floor Width ({})'.format(dist_unit),
        'Flr to Flr Height ({})'.format(dist_unit),
        'Plenum Height ({})'.format(dist_unit),
        'Height Above Ground ({})'.format(dist_unit),
        'Acoustic Ceiling Resistance ({})'.format(r_unit),
        'Cooling Dry Bulb ({})'.format(temp_unit),
        'Heating Dry Bulb ({})'.format(temp_unit),
        'Relative Humidity (%)'
        'Cooling Driftpoint ({})'.format(temp_unit),
        'Heating Driftpoint ({})'.format(temp_unit),
        'Thermostat Cooling Schedule',
        'Thermostat Heating Schedule',
        'Thermostat Location',
        'CO2 Sensor Location',
        'Humidity Moisture Capacitance',
        'Humidistat Location',
        'Duplicate Floor Multiplier',
        'Duplicate Rooms per Zone',
        'Room Mass / # of Hours',
        'Slab Construction Type',
        'Room Type',
        'Carpeted Floor'
    ]

    # loop through the rooms and add each of the attributes
    room_mtx = []
    for room in rooms:
        # figure out the values for certain attributes
        f2f = room.floor_to_ceiling_height if isinstance(room, Room2D) \
            else room.volume / room.floor_area
        plenum = room.ceiling_plenum_depth if isinstance(room, Room2D) else 0
        elev = room.floor_elevation if isinstance(room, Room2D) \
            else room.average_floor_height
        multiplier = room.parent.multiplier \
            if isinstance(room, Room2D) and room.has_parent else room.multiplier
        set_pt = room.properties.energy.setpoint
        if room.properties.energy.setpoint is not None:
            room_type = 'Conditioned'
            cool_set_pt = set_pt.cooling_setpoint
            heat_set_pt = set_pt.heating_setpoint
            cool_set_back = set_pt.cooling_setback
            heat_set_back = set_pt.heating_setback
            humid_pt = set_pt.dehumidifying_setpoint \
                if set_pt.dehumidifying_setpoint is not None else 50
        else:
            room_type = 'Unconditioned'
            cool_set_pt = 50
            heat_set_pt = 0
            cool_set_back = 50
            heat_set_back = 0
            humid_pt = 50

        # put all attributes into a list
        room_attr = [
            room.display_name,
            'Default System',
            room.zone,
            'Default',
            'Default',
            'Default',
            room.floor_area,
            1,
            f2f,
            plenum,
            elev,
            0.31451,
            cool_set_pt,
            heat_set_pt,
            humid_pt,
            cool_set_back,
            heat_set_back,
            'None',
            'None',
            'Room',
            'None',
            'Medium',
            'Room',
            multiplier,
            1,
            'Time delay based on actual mass',
            '4" LW Concrete',
            room_type,
            'Yes'
        ]
        room_mtx.append(room_attr)

    # transpose the matrix and convert SI units to IP
    room_matrix = [list(row) for row in zip(*room_mtx)]
    if not si_units:
        room_matrix[6] = area.to_ip(room_matrix[6], 'm2')
        room_matrix[8] = distance.to_ip(room_matrix[8], 'm')
        room_matrix[9] = distance.to_ip(room_matrix[9], 'm')
        room_matrix[10] = distance.to_ip(room_matrix[10], 'm')
        room_matrix[11] = r_value.to_ip(room_matrix[11], 'm2-K/W')
        room_matrix[12] = temperature.to_ip(room_matrix[12], 'C')
        room_matrix[13] = temperature.to_ip(room_matrix[13], 'C')
        room_matrix[15] = temperature.to_ip(room_matrix[15], 'C')
        room_matrix[15] = temperature.to_ip(room_matrix[15], 'C')

    # insert the column for the row names
    for row_name, row in zip(row_names, room_matrix):
        row.insert(0, row_name)
    return room_matrix


def model_to_trace700_matrix(
    model, use_multiplier=True, exclude_plenums=True, merge_method=None,
    si_units=False, geometry_names=False, resource_names=False
):
    """Get matrices with TRACE 700 simulation attributes of a Model.

    The resulting matrices can be written to a CSV and then copied into
    the tables that appear in the Component Tree view of TRACE 700. The
    order and organization of rooms in the resulting matrix matches that
    of the gbXML produced from the same model.

    Args:
        model: A dragonfly Model for which a TRACE 700 CSV matrix will be returned.
        use_multiplier: If True, the multipliers on this Model's Stories will be
            passed along to the CSV. If False, full geometry objects will be written
            for each and every floor in the building that are represented through
            multipliers and all resulting multipliers will be 1. (Default: True).
        exclude_plenums: Boolean to indicate whether ceiling/floor plenum depths
            assigned to Room2Ds should be ignored during translation. This
            results in each Room2D translating to a single Honeybee Room at
            the full floor_to_ceiling_height instead of a base Room with (a)
            plenum Room(s). (Default: True).
        merge_method: An optional text string to describe how the Room2Ds should
            be merged into individual Rooms during the translation. Specifying a
            value here can be an effective way to reduce the number of Room
            volumes in the resulting model and, ultimately, yield a faster
            simulation time in the destination engine with fewer results
            to manage. Note that Room2Ds will only be merged if they form a
            continuous volume. Otherwise, there will be multiple Rooms per
            zone or story, each with an integer added at the end of their
            identifiers. Choose from the following options:

            * None - No merging of Room2Ds will occur
            * Zones - Room2Ds in the same zone will be merged
            * PlenumZones - Only plenums in the same zone will be merged
            * Stories - Rooms in the same story will be merged
            * PlenumStories - Only plenums in the same story will be merged

        si_units: Boolean to note whether the units of the values in the resulting
            matrix are in SI (True) instead of IP (False). (Default: False).
        geometry_names: Boolean to note whether a cleaned version of all geometry
            display names should be used instead of identifiers when translating
            the Model to OSM and IDF. Using this flag will affect all Rooms, Faces,
            Apertures, Doors, and Shades. It will generally result in more read-able
            names in the OSM and IDF but this means that it will not be easy to map
            the EnergyPlus results back to the original Honeybee Model. Cases
            of duplicate IDs resulting from non-unique names will be resolved
            by adding integers to the ends of the new IDs that are derived from
            the name. (Default: False).
        resource_names: Boolean to note whether a cleaned version of all resource
            display names should be used instead of identifiers when translating
            the Model to OSM and IDF. Using this flag will affect all Materials,
            Constructions, ConstructionSets, Schedules, Loads, and ProgramTypes.
            It will generally result in more read-able names for the resources
            in the OSM and IDF. Cases of duplicate IDs resulting from non-unique
            names will be resolved by adding integers to the ends of the new IDs
            that are derived from the name. (Default: False).

    Returns:
        A tuple with four items.

        room_matrix -- A list of list where each sublist represents a row of the
            Rooms table of the TRACE 700 Component Tree.

        airflows_matrix -- A list of list where each sublist represents a row of the
            Airflows table of the TRACE 700 Component Tree.

        people_and_lights_matrix -- A list of list where each sublist represents
            a row of the People & Lighting table of the TRACE 700 Component Tree.

        misc_loads_matrix -- A list of list where each sublist represents a row of
            the Miscellaneous Loads table of the TRACE 700 Component Tree.
    """
    # convert the rooms into the format in which it will go off to TRACE
    rooms_for_trace = []  # list to hold the rooms for CSV reporting
    assert len(model.room_2ds) != 0 or len(model.room_3ds) != 0, \
        'Model must have rooms to be able to export to TRACE700 CSV.'

    # scale the model if the units are not meters
    model = model.duplicate()  # duplicate model to avoid mutating it
    if model.units != 'Meters':
        model.convert_to_units('Meters')
    tol = model.tolerance
    # reset the IDs to be derived from the display_names if requested
    if geometry_names:
        model.reset_ids()
    if resource_names:
        model.properties.energy.reset_resource_ids()

    # account for story multipliers, separated room plenums and room merge method
    merge_map = model._extract_merge_map(merge_method, exclude_plenums, tol)
    for building in model.buildings:
        # separate the plenums unless they are excluded
        if not exclude_plenums and building.has_room_2d_plenums:
            building.convert_plenum_depths_to_room_2ds(tol)
        # collect all of the unmerged rooms
        if use_multiplier:
            for story in building.unique_stories:
                rooms_for_trace.extend(story.room_2ds)
        else:
            for story in building.all_stories():
                rooms_for_trace.extend(story.room_2ds)

    # apply the merge map if it exists
    if merge_map is not None:
        # gather the Room objects to be merged
        merge_groups, remove_i = OrderedDict(), set()
        insert_i, insert_count = [], 0
        for i, room in enumerate(rooms_for_trace):
            try:
                merge_name = merge_map[room.identifier]
                try:
                    merge_groups[merge_name].append(room)
                except KeyError:  # first item in the group
                    merge_groups[merge_name] = [room]
                    insert_i.append(insert_count)
                remove_i.add(i)
            except KeyError:  # not a room to be merged
                insert_count += 1
        # create the new rooms and assign them to the model
        new_rooms = [r for i, r in enumerate(rooms_for_trace) if i not in remove_i]
        group_ids = {}
        zip_obj = zip(reversed(insert_i), reversed(merge_groups.items()))
        for ins_i, (group_name, room_group) in zip_obj:
            merged_rooms = Room2D.join_room_2ds(room_group, tol, tol)
            for room in merged_rooms:
                room.identifier = clean_and_number_string(group_name, group_ids)
                room.display_name = group_name
                new_rooms.insert(ins_i, room)
        rooms_for_trace = new_rooms

    # add the 3D Honeybee Rooms to the list
    for building in model.buildings:
        rooms_for_trace.extend(building.room_3ds)

    # sort the rooms alphanumerically based on their identifiers
    rooms_for_trace.sort(key=lambda x: x.identifier)  # this matches the gbXML export

    # create the matrices of data from the model rooms
    room_matrix = rooms_to_trace700_matrix(rooms_for_trace, si_units)
    airflows_matrix = airflows_trace700_matrix(rooms_for_trace, si_units)
    people_and_lights_matrix = people_and_lights_trace700_matrix(rooms_for_trace, si_units)
    misc_loads_matrix = miscellaneous_loads_trace700_matrix(rooms_for_trace, si_units)
    return room_matrix, airflows_matrix, people_and_lights_matrix, misc_loads_matrix


def model_to_trace700_csv(
    model, use_multiplier=True, exclude_plenums=True, merge_method=None,
    si_units=False, geometry_names=False, resource_names=False
):
    """Generate a CSV string with TRACE 700 load simulation attributes of a Model.

    The resulting CSV tables can be copied into the tables that appear in the
    Component Tree view of TRACE 700. The order and organization of rooms in
    the resulting matrix should match that of the gbXML produced from the same model.

    Args:
        model: A dragonfly Model for which a TRACE 700 CSV matrix will be returned.
        use_multiplier: If True, the multipliers on this Model's Stories will be
            passed along to the CSV. If False, full geometry objects will be written
            for each and every floor in the building that are represented through
            multipliers and all resulting multipliers will be 1. (Default: True).
        exclude_plenums: Boolean to indicate whether ceiling/floor plenum depths
            assigned to Room2Ds should be ignored during translation. This
            results in each Room2D translating to a single Honeybee Room at
            the full floor_to_ceiling_height instead of a base Room with (a)
            plenum Room(s). (Default: True).
        merge_method: An optional text string to describe how the Room2Ds should
            be merged into individual Rooms during the translation. Specifying a
            value here can be an effective way to reduce the number of Room
            volumes in the resulting model and, ultimately, yield a faster
            simulation time in the destination engine with fewer results
            to manage. Note that Room2Ds will only be merged if they form a
            continuous volume. Otherwise, there will be multiple Rooms per
            zone or story, each with an integer added at the end of their
            identifiers. Choose from the following options:

            * None - No merging of Room2Ds will occur
            * Zones - Room2Ds in the same zone will be merged
            * PlenumZones - Only plenums in the same zone will be merged
            * Stories - Rooms in the same story will be merged
            * PlenumStories - Only plenums in the same story will be merged

        si_units: Boolean to note whether the units of the values in the resulting
            matrix are in SI (True) instead of IP (False). (Default: False).
        geometry_names: Boolean to note whether a cleaned version of all geometry
            display names should be used instead of identifiers when translating
            the Model to OSM and IDF. Using this flag will affect all Rooms, Faces,
            Apertures, Doors, and Shades. It will generally result in more read-able
            names in the OSM and IDF but this means that it will not be easy to map
            the EnergyPlus results back to the original Honeybee Model. Cases
            of duplicate IDs resulting from non-unique names will be resolved
            by adding integers to the ends of the new IDs that are derived from
            the name. (Default: False).
        resource_names: Boolean to note whether a cleaned version of all resource
            display names should be used instead of identifiers when translating
            the Model to OSM and IDF. Using this flag will affect all Materials,
            Constructions, ConstructionSets, Schedules, Loads, and ProgramTypes.
            It will generally result in more read-able names for the resources
            in the OSM and IDF. Cases of duplicate IDs resulting from non-unique
            names will be resolved by adding integers to the ends of the new IDs
            that are derived from the name. (Default: False).

    Returns:
        Text string of content to be written into a CSV file containing all tables
        needed to specify room loads in TRACE 700.
    """
    # get the matrices to be written to CSV format
    room_matrix, airflows_matrix, people_and_lights_matrix, misc_loads_matrix = \
        model_to_trace700_matrix(
            model, use_multiplier, exclude_plenums, merge_method,
            si_units, geometry_names, resource_names
        )

    # put all of the matrices into one master matrix for CSV export
    mtx_width = len(room_matrix[0]) - 1
    spacer_row = ',' * mtx_width
    # add the Room table
    csv_matrix = ['Rooms{}'.format(spacer_row)]
    for row in room_matrix:
        csv_matrix.append(','.join([str(val) for val in row]))
    # add the Airflows table
    csv_matrix.append(spacer_row)
    csv_matrix.append('Airflows{}'.format(spacer_row))
    for row in airflows_matrix:
        csv_matrix.append(','.join([str(val) for val in row]))
    # add the People & Lighting table
    csv_matrix.append(spacer_row)
    csv_matrix.append('People & Lighting{}'.format(spacer_row))
    for row in people_and_lights_matrix:
        csv_matrix.append(','.join([str(val) for val in row]))
    # add the Miscellaneous Loads table
    csv_matrix.append(spacer_row)
    csv_matrix.append('Miscellaneous Loads{}'.format(spacer_row))
    for row in misc_loads_matrix:
        csv_matrix.append(','.join([str(val) for val in row]))

    return '\n'.join(csv_matrix)
