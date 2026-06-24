# coding=utf-8
"""Methods to write room airflows to matrices for Trane TRACE tables."""
from __future__ import division

from ladybug.datatype.volumeflowrate import VolumeFlowRate

# formatting for each attribute in the airflows table
AIRFLOW_TABLE_FORMAT = (
    'user',
    'default',
    'default',
    'default',
    'default',
    'user',
    'user',
    'user',
    'user',
    'locked',
    'locked',
    'locked',
    'locked',
    'default',
    'locked',
    'locked',
    'locked',
    'locked',
    'locked',
    'locked',
    'locked',
    'locked',
    'default',
    'user',
    'user',
    'user',
    'user',
    'default',
    'locked',
    'default',
    'locked',
    'default',
    'locked',
    'default',
    'locked',
    'default',
    'default',
    'default',
    'default',
    'default',
    'default',
    'default',
    'default',
    'default',
    'default'
)

AIRFLOW_TABLE_FORMAT_62_1 = (
    'user',
    'default',
    'default',
    'user',
    'user',
    'locked',
    'locked',
    'locked',
    'locked',
    'user',
    'user',
    'user',
    'user',
    'default',
    'default',
    'user',
    'default',
    'user',
    'user',
    'user',
    'locked',
    'default',
    'default',
    'user',
    'user',
    'user',
    'user',
    'default',
    'locked',
    'default',
    'locked',
    'default',
    'locked',
    'default',
    'locked',
    'default',
    'default',
    'default',
    'default',
    'default',
    'default',
    'default',
    'default',
    'default',
    'default'
)


def airflows_trace700_matrix(rooms, si_units=False, ventilation_method='Sum of Outdoor Air'):
    """Get a matrix for the "Airflows" table of the TRACE 700 Component Tree.

    Args:
        rooms: A list of dragonfly Room2Ds and honeybee Rooms for which the
            TRACE 700 "Airflows" matrix will be returned.
        si_units: Boolean to note whether the units of the values in the resulting
            matrix are in SI (True) instead of IP (False). (Default: False).
        ventilation_method: Optional text for the ventilation method to be used in the
            resulting matrix. Choose from the following.

            * Sum of Outdoor Air
            * ASHRAE 62.1

    Returns:
        A list of list where each sublist represents a row of the Airflows
        table of the TRACE 700 Component Tree.
    """
    # set up things for unit conversion
    flow_unit = 'L/s' if si_units else 'cfm'
    flow_intensity_unit = 'L/s/sq m' if si_units else 'cfm/sq ft of wall'
    ach_unit = 'air changes/hr'
    rp_unit = 'L/s/person' if si_units else 'cfm/person'
    ra_unit = 'L/s/sq m' if si_units else 'cfm/sq ft'
    flow = VolumeFlowRate()

    # set up the names of the rows
    row_names = [
        'Room Description',
        'Adjacent Air Transfer from Room',
        'Airflow Template',
        'Ventilation Method',
        'Ventilation Type',
        'Ventilation Cooling',
        'Ventilation Cooling Units',
        'Ventilation Heating',
        'Ventilation Heating Units',
        'People-based Rate (Rp)',
        'People-based Unit',
        'Area-based Rate (Ra)',
        'Area-based Unit',
        'Ventilation Schedule',
        'Std62.1-2004-2010 Clg Ez',
        'Std62.1-2004-2010 Clg Ez Pct',
        'Std62.1-2004-2010 Htg Ez',
        'Std62.1-2004-2010 Htg Ez Pct',
        'Std62.1-2004-2010 Er',
        'Std62.1-2004-2010 Er Pct',
        'DCV Min OA Intake',
        'DCV Min OA Intake Unit',
        'Infiltration Type',
        'Infiltration Cooling',
        'Infiltration Cooling Units',
        'Infiltration Heating',
        'Infiltration Heating Units',
        'Infiltration Schedule',
        'Main Supply Cooling',
        'Main Supply Cooling Units',
        'Main Supply Heating',
        'Main Supply Heating Units',
        'Aux Supply Cooling',
        'Aux Supply Cooling Units',
        'Aux Supply Heating',
        'Aux Supply Heating Units',
        'Cooling VAV Min Airflow',
        'Cooling VAV Min Airflow Units',
        'Heating VAV Max Airflow',
        'Heating VAV Max Airflow Units',
        'VAV Airflow Schedule',
        'VAV Type',
        'Room Exhaust',
        'Room Exhaust Units',
        'Room Exhaust Schedule'
    ]

    # define all of the fields that get filled after TRACE calculation
    calculated_fields = [
        'Available (100%)',
        '',
        'To be calculated',
        '',
        'To be calculated',
        '',
        'To be calculated',
        '',
        'To be calculated',
        '',
        '% Clg Airflow',
        '',
        '% Clg Airflow',
        'Available (100%)',
        'Default',
        '0',
        'air changes/hr',
        'Available (100%)'
    ]

    # loop through the rooms and add each of the attributes
    airflow_mtx = []
    for room in rooms:
        # calculate the infiltration fields for the room
        inf_flow, inf_unit = 0, ach_unit
        inf_obj = room.properties.energy.infiltration
        if inf_obj is not None:
            if room.properties.energy._person_count is not None:
                inf_flow = room.properties.energy.infiltration_ach
            else:
                inf_flow = inf_obj.flow_per_exterior_area_si if si_units else \
                    inf_obj.flow_per_exterior_area_ip
                inf_unit = flow_intensity_unit

        # calculate the total outdoor air fields using the ventilation_method
        vent_obj = room.properties.energy.ventilation
        if ventilation_method == 'Sum of Outdoor Air':
            if vent_obj is not None:
                vent_flow = vent_obj.room_absolute_flow(room)
                v_eff = min(vent_obj.effectiveness_cooling, vent_obj.effectiveness_heating)
                total_flow = vent_flow * v_eff
                vent_flow_cool = total_flow * vent_obj.effectiveness_cooling
                vent_flow_heat = total_flow * vent_obj.effectiveness_heating
            else:
                vent_flow_cool, vent_flow_heat = 0, 0

            # put all attributes into a list
            airflow_attr = [
                room.display_name,
                '<<No adjacent room>>',
                'Default',
                'Sum of Outdoor Air',
                'None',
                vent_flow_cool,
                flow_unit,
                vent_flow_heat,
                flow_unit,
                '',
                '',
                '',
                '',
                'Available (100%)',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                'None',
                inf_flow,
                inf_unit,
                inf_flow,
                inf_unit
            ]
            airflow_mtx.append(airflow_attr + calculated_fields)

        else:  # assume we are using ASHRAE 62.1
            if vent_obj is not None:
                if not si_units:
                    rp = vent_obj.flow_per_person_ip
                    ra = vent_obj.flow_per_area_ip
                else:
                    rp = vent_obj.flow_per_person_si
                    ra = vent_obj.flow_per_area_si
                clg_ez = vent_obj.effectiveness_cooling * 100
                htg_ez = vent_obj.effectiveness_heating * 100
                er = vent_obj.secondary_recirculation * 100
            else:
                rp, ra, clg_ez, htg_ez, er = 0, 0, 100, 100, 0

            # put all attributes into a list
            airflow_attr = [
                room.display_name,
                '<<No adjacent room>>',
                'Default',
                'ASHRAE 62.1',
                'Default Std62',
                '',
                '',
                '',
                '',
                rp,
                rp_unit,
                ra,
                ra_unit,
                'Available (100%)',
                'Custom',
                int(clg_ez),
                'Custom',
                int(htg_ez),
                'Custom',
                int(er),
                '',
                'None',
                'None',
                inf_flow,
                inf_unit,
                inf_flow,
                inf_unit
            ]
            airflow_mtx.append(airflow_attr + calculated_fields)

    # transpose the matrix and round the numbers so that they display nicely
    airflow_matrix = [list(row) for row in zip(*airflow_mtx)]
    if ventilation_method == 'Sum of Outdoor Air':
        if not si_units:
            airflow_matrix[5] = list(flow.to_unit(airflow_matrix[5], 'cfm', 'm3/s'))
            airflow_matrix[7] = list(flow.to_unit(airflow_matrix[7], 'cfm', 'm3/s'))
        else:
            airflow_matrix[5] = list(flow.to_unit(airflow_matrix[5], 'L/s', 'm3/s'))
            airflow_matrix[7] = list(flow.to_unit(airflow_matrix[7], 'L/s', 'm3/s'))

        # round the numbers so that they display nicely
        for row_i in (5, 7):
            airflow_matrix[row_i] = [round(val, 1) for val in airflow_matrix[row_i]]
    else:
        for row_i in (9, 11):
            airflow_matrix[row_i] = [round(val, 3) for val in airflow_matrix[row_i]]
    # round the infiltration number so that they display nicely
    for row_i in (23, 25):
        airflow_matrix[row_i] = [round(val, 3) for val in airflow_matrix[row_i]]

    # insert the column for the row names
    for row_name, row in zip(row_names, airflow_matrix):
        row.insert(0, row_name)
    return airflow_matrix


def outdoor_air_calculation_matrix(rooms, si_units=False):
    """Add a matrix with calculations of outdoor air.

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
        'Level',
        'Zone',
        'Room',
        'Program',
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
    oa_mtx = []
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

        # put all attributes into a list
        oa_attr = [
            room.story,
            room.zone,
            room.display_name,
            room.properties.energy.program_type.display_name,
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
        oa_mtx.append(oa_attr)

    # insert the row for column names and column abbreviations
    oa_mtx.insert(0, row_names)
    oa_mtx.insert(0, row_abbrev)
    return oa_mtx
