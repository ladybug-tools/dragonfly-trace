# coding=utf-8
"""Methods to write calculations of airflow for Trane TRACE tables."""
from __future__ import division


def calculation_matrix(rooms, si_units=False):
    """Add a matrix with calculations of airflow.

    The fields in this matrix can be linked back to the "Sum of Outdoor Air"
    fields within TRACE 700 so that it is possible to understand how the outdoor
    air values were computed.

    Args:
        rooms: A list of dragonfly Room2Ds and honeybee Rooms for which the
            TRACE 700 "Airflows" matrix will be returned.
        si_units: Boolean to note whether the units of the values in the resulting
            matrix are in SI (True) instead of IP (False). (Default: False).

    Returns:
        A list of list where each sublist represents a row with airflow calculations.
    """
    # set up things for unit conversion
    area_unit = 'm²' if si_units else 'ft²'
    volume_unit = 'm³' if si_units else 'ft³'
    rp_unit = 'L/s/person' if si_units else 'cfm/person'
    ra_unit = 'L/s/m²' if si_units else 'cfm/ft²'
    flow_unit = 'L/s' if si_units else 'cfm'

    # set up the names and abbreviations of the rows
    row_names = [
        'Identifier',
        'Level',
        'Zone',
        'Room',
        'Program',
        'Primary\nOccupancy\nCategory',
        'Secondary\nOccupancy\nCategory',
        'Person Count',
        'Floor Area [{}]'.format(area_unit),
        'Volume [{}]'.format(volume_unit),
        'Outdoor Air\nper Person\n[{}]'.format(rp_unit),
        'Outdoor Air\nper Floor Area\n[{}]'.format(ra_unit),
        'Outdoor Air\nChanges per Hour\n[ACH]',
        'Outdoor Air\nMethod',
        'Effectiveness\nin Cooling',
        'Effectiveness\nin Heating',
        'Secondary\nRecirculation',
        '',
        'Total OA in\nCooling [{}]'.format(flow_unit),
        'Total OA in\nHeating [{}]'.format(flow_unit)
    ]
    row_abbrev = [
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        'Pz',
        'Az',
        'Vz',
        'Rp',
        'Ra',
        'ACH',
        '',
        'Ez Clg',
        'Ez Htg',
        'Er',
        '',
        'Q Clg',
        'Q Htg'
    ]

    # loop through the rooms and add each of the attributes
    calc_mtx = []
    for room in rooms:
        # get the area and volume
        floor_area, volume = room.floor_area, room.volume

        # get the number of people
        ppl_obj = room.properties.energy.people
        person_count = round(ppl_obj.people_per_area * floor_area, 3) \
            if ppl_obj is not None else 0
        if not si_units:
            floor_area = floor_area * 10.7639
            volume = volume * 35.3147
        floor_area = round(floor_area)
        volume = round(volume)

        # get all of the ventilation criteria
        vent_obj = room.properties.energy.ventilation
        if vent_obj is not None:
            if not si_units:
                rp = round(vent_obj.flow_per_person_ip, 3)
                ra = round(vent_obj.flow_per_area_ip, 3)
            else:
                rp = round(vent_obj.flow_per_person_si, 3)
                ra = round(vent_obj.flow_per_area_si, 3)
            r_ach = vent_obj.air_changes_per_hour
            method = vent_obj.method
            clg_ez = vent_obj.effectiveness_cooling
            htg_ez = vent_obj.effectiveness_heating
            er = vent_obj.secondary_recirculation
        else:
            rp, ra, r_ach, method, clg_ez, htg_ez, er = 0, 0, 0, 'Sum', 1, 1, 0

        # compute the total flow
        eval_func = sum if method == 'Sum' else max
        total = eval_func((person_count * rp, floor_area * ra, (r_ach * volume) / 3600))

        # extract attributes for program and occupancy category
        program = room.properties.energy.program_type
        primary_cat, secondary_cat = '', ''
        if program.ventilation is not None:
            vent = program.ventilation
            if vent.user_data:
                if 'primary_occupancy' in vent.user_data:
                    primary_cat = vent.user_data['primary_occupancy']
                if 'secondary_occupancy' in vent.user_data:
                    secondary_cat = vent.user_data['secondary_occupancy']

        # put all attributes into a list
        oa_attr = [
            room.identifier,
            room.story,
            room.zone,
            room.display_name,
            program.display_name,
            primary_cat,
            secondary_cat,
            person_count,
            floor_area,
            volume,
            rp,
            ra,
            r_ach,
            method,
            clg_ez,
            htg_ez,
            er,
            '',
            total / clg_ez,
            total / htg_ez
        ]
        calc_mtx.append(oa_attr)

    # insert the row for column names and column abbreviations
    calc_mtx.insert(0, row_names)
    calc_mtx.insert(0, row_abbrev)
    return calc_mtx
