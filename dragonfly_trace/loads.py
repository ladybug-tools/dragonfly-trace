# coding=utf-8
"""Methods to write room loads to matrices for Trane TRACE tables."""
from __future__ import division

from ladybug.datatype.power import Power
from ladybug.datatype.energyflux import EnergyFlux


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
    # set up things for unit conversion
    power_unit = 'kW' if si_units else 'Btu/h'
    flux_unit = 'W/sq m' if si_units else 'W/sq ft'
    power, flux = Power(), EnergyFlux()

    # set up the names of the rows
    row_names = [
        'Room Description',
        'Internal Loads Template',
        'People Activity',
        'People Schedule',
        'People Value',
        'People Value Units',
        'People Sensible ({})'.format(power_unit),
        'People Latent ({})'.format(power_unit),
        'Workstation Density',
        'Workstation Density Units',
        'Lighting Type',
        'ASHRAE Space/Area Type',
        'Lighting Value',
        'Lighting Value Units',
        'Lighting Schedule'
    ]

    # loop through the rooms and add each of the attributes
    load_mtx = []
    for room in rooms:
        # calculate the total number of people
        ppl_obj = room.properties.energy.people
        if ppl_obj is not None:
            ppl_count = room.floor_area * ppl_obj.people_per_area
            sensible_ppl = ppl_obj.activity_max_sensible
            latent_ppl = ppl_obj.activity_max_latent
        else:
            ppl_count = 0
            sensible_ppl = 73.26775
            latent_ppl = 73.26775
        # get the lighting power density
        light_obj = room.properties.energy.lighting
        if light_obj is not None:
            lpd = light_obj.watts_per_area
            light_type = r'LED Lighting 100% load to space'

        # put all attributes into a list
        load_attr = [
            room.display_name,
            'Default',
            'None',
            'Cooling Only (Design)',
            ppl_count,
            'People',
            sensible_ppl,
            latent_ppl,
            1,
            'workstation/person',
            light_type,
            '',
            lpd,
            flux_unit,
            'Cooling Only (Design)'
        ]
        load_mtx.append(load_attr)

    # transpose the matrix and convert SI units to IP
    load_matrix = [list(row) for row in zip(*load_mtx)]
    if not si_units:
        load_matrix[6] = list(power.to_unit(load_matrix[6], 'Btu/h', 'W'))
        load_matrix[7] = list(power.to_unit(load_matrix[7], 'Btu/h', 'W'))
        load_matrix[12] = list(flux.to_unit(load_matrix[12], 'W/ft2', 'W/m2'))
    else:
        load_matrix[6] = list(power.to_unit(load_matrix[6], 'kW', 'W'))
        load_matrix[7] = list(power.to_unit(load_matrix[7], 'kW', 'W'))

    # round the numbers so that they display nicely
    for row_i in (6, 7):
        load_matrix[row_i] = [round(val) for val in load_matrix[row_i]]
    for row_i in (4, 12):
        load_matrix[row_i] = [round(val, 3) for val in load_matrix[row_i]]

    # insert the column for the row names
    for row_name, row in zip(row_names, load_matrix):
        row.insert(0, row_name)
    return load_matrix


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
    # set up things for unit conversion
    power_unit = 'W'
    flux_unit = 'W/sq m' if si_units else 'W/sq ft'
    flux = EnergyFlux()

    # set up the names of the rows
    row_names = [
        'Misc Load Description',
        'Room Description',
        'Type',
        'Schedule',
        'Value',
        'Units',
        'Energy Meter',
        'Data Center Equipment'
    ]

    # loop through the rooms and add each of the attributes
    load_mtx = []
    for room in rooms:
        # calculate the total density of equipment
        epd, e_type = 0, 'None'
        ele_obj = room.properties.energy.electric_equipment
        if ele_obj is not None:
            epd += (ele_obj.watts_per_area * (1 - ele_obj.lost_fraction))
            e_type = 'Electricity'
        gas_obj = room.properties.energy.gas_equipment
        if gas_obj is not None:
            epd += (gas_obj.watts_per_area * (1 - gas_obj.lost_fraction))
            e_type = 'Gas'

        # if there are process loads assigned, specify load in absolute Watts
        process_load = sum(load.watts * (1 - load.lost_fraction)
                           for load in room.properties.energy.process_loads)
        if process_load != 0:
            load_value = process_load + (epd * room.floor_area)
            load_unit = power_unit
        else:
            load_value = epd
            load_unit = flux_unit

        # put all attributes into a list
        load_attr = [
            '{} Misc Load'.format(room.display_name),
            room.display_name,
            'None',
            'Cooling Only (Design)',
            load_value,
            load_unit,
            e_type,
            'No'
        ]
        load_mtx.append(load_attr)

    # transpose the matrix and convert SI units to IP
    load_matrix = [list(row) for row in zip(*load_mtx)]
    if load_unit == flux_unit:
        if not si_units:
            load_matrix[4] = list(flux.to_unit(load_matrix[4], 'W/ft2', 'W/m2'))
        load_matrix[4] = [round(val, 2) for val in load_matrix[4]]
    else:
        load_matrix[4] = [round(val) for val in load_matrix[4]]

    # insert the column for the row names
    for row_name, row in zip(row_names, load_matrix):
        row.insert(0, row_name)
    return load_matrix
