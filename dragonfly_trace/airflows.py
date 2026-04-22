# coding=utf-8
"""Methods to write room airflows to matrices for Trane TRACE tables."""
from __future__ import division

from ladybug.datatype.volumeflowrate import VolumeFlowRate
from ladybug.datatype.volumeflowrateintensity import VolumeFlowRateIntensity


def airflows_trace700_matrix(rooms, si_units=False):
    """Get a matrix for the "Airflows" table of the TRACE 700 Component Tree.

    Args:
        rooms: A list of dragonfly Room2Ds and honeybee Rooms for which the
            TRACE 700 "Airflows" matrix will be returned.
        si_units: Boolean to note whether the units of the values in the resulting
            matrix are in SI (True) instead of IP (False). (Default: False).

    Returns:
        A list of list where each sublist represents a row of the Airflows
        table of the TRACE 700 Component Tree.
    """
    # set up things for unit conversion
    flow_unit = 'L/s' if si_units else 'cfm'
    flow_intensity_unit = 'L/s/sq m' if si_units else 'cfm/sq ft of wall'
    flow, fi = VolumeFlowRate(), VolumeFlowRateIntensity()

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

    # loop through the rooms and add each of the attributes
    airflow_mtx = []
    for room in rooms:
        # calculate the total outdoor air ventilation and infiltration
        vent_obj = room.properties.energy.ventilation
        vent_flow = vent_obj.room_absolute_flow(room) if vent_obj is not None else 0
        inf_obj = room.properties.energy.infiltration
        inf_flow = inf_obj.flow_per_exterior_area if inf_obj is not None else 0

        # put all attributes into a list
        airflow_attr = [
            room.display_name,
            '<<No adjacent room>>',
            'Default',
            'Sum of Outdoor Air',
            'None',
            vent_flow,
            flow_unit,
            vent_flow,
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
            flow_intensity_unit,
            inf_flow,
            flow_intensity_unit,
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
        airflow_mtx.append(airflow_attr)

    # transpose the matrix and convert SI units to IP
    airflow_matrix = [list(row) for row in zip(*airflow_mtx)]
    if not si_units:
        airflow_matrix[5] = list(flow.to_unit(airflow_matrix[5], 'cfm', 'm3/s'))
        airflow_matrix[7] = list(flow.to_unit(airflow_matrix[7], 'cfm', 'm3/s'))
        airflow_matrix[23] = list(fi.to_unit(airflow_matrix[23], 'cfm/ft2', 'm3/s-m2'))
        airflow_matrix[25] = list(fi.to_unit(airflow_matrix[25], 'cfm/ft2', 'm3/s-m2'))
    else:
        airflow_matrix[5] = list(flow.to_unit(airflow_matrix[5], 'L/s', 'm3/s'))
        airflow_matrix[7] = list(flow.to_unit(airflow_matrix[7], 'L/s', 'm3/s'))
        airflow_matrix[23] = list(fi.to_unit(airflow_matrix[23], 'L/s-m2', 'm3/s-m2'))
        airflow_matrix[25] = list(fi.to_unit(airflow_matrix[25], 'L/s-m2', 'm3/s-m2'))

    # round the numbers so that they display nicely
    for row_i in (5, 7):
        airflow_matrix[row_i] = [round(val, 1) for val in airflow_matrix[row_i]]
    for row_i in (23, 25):
        airflow_matrix[row_i] = [round(val, 3) for val in airflow_matrix[row_i]]

    # insert the column for the row names
    for row_name, row in zip(row_names, airflow_matrix):
        row.insert(0, row_name)
    return airflow_matrix
