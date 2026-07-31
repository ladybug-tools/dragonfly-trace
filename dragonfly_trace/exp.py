"""Methods to generate EXP templates for Trane TRACE."""
from honeybee.typing import readable_short_name
from ladybug.datatype.area import Area
from ladybug.datatype.power import Power
from ladybug.datatype.energyflux import EnergyFlux
from ladybug.datatype.volumeflowrate import VolumeFlowRate
from ladybug.datatype.temperature import Temperature


area_dt = Area()
power_dt = Power()
flux_dt = EnergyFlux()
flow_dt = VolumeFlowRate()
temp_dt = Temperature()


def people_to_trace700_people(people, si_units=False):
    """Get a TRACE 700 "T.LOAD_PEOPLE" entry string from a Honeybee People object.

    Args:
        people: A Honeybee People object.
        si_units: Boolean to note whether the units of the values in the resulting
            matrix are in SI (True) instead of IP (False). (Default: False).

    Returns:
        A text string for a TRACE 700 T.LOAD_PEOPLE library entry.
    """
    description = readable_short_name(people.display_name, max_length=40)
    radiant_pct = people.radiant_fraction * 100.0

    area_unit = 'm2' if si_units else 'ft2'
    power_unit = 'W' if si_units else 'Btu/h'
    amount_unit_code = 2 if si_units else 1  # 1 = sq ft/person, 2 = sq m/person
    load_unit_code = 8 if si_units else 7  # 7 = Btu/h, 8 = W

    people_amount = area_dt.to_unit([people.area_per_person], area_unit, 'm2')[0]
    sensible_ppl = power_dt.to_unit([people.activity_max_sensible], power_unit, 'W')[0]
    latent_ppl = power_dt.to_unit([people.activity_max_latent], power_unit, 'W')[0]

    # People;
    # Description;
    # 1;
    # People amount;
    # People amount unit;
    # Sensible load;
    # Sensible load unit;
    # Latent load;
    # Latent load unit;
    # Longwave radiant %;
    exp_line = (
        f'People;{description};1;{people_amount:.6f};{amount_unit_code};'
        f'{sensible_ppl:.6f};{load_unit_code};{latent_ppl:.6f};{load_unit_code};{radiant_pct:.1f};'
    )
    return exp_line


def lighting_to_trace700_lighting(lighting, fixture_type='SUSFLUOR'):
    """Get a TRACE 700 "T.LOAD_LIGHTS" entry string from a Honeybee Lighting object.

    Args:
        lighting: A Honeybee Lighting object.
        fixture_type: Optional text string for the lighting fixture type.
            (Default: 'SUSFLUOR').

    Returns:
        A text string for a TRACE 700 T.LOAD_LIGHTS library entry.
    """
    description = lighting.display_name

    plenum_pct = lighting.return_air_fraction * 100.0
    radiant_pct = lighting.radiant_fraction * 100.0
    visible_pct = lighting.visible_fraction * 100.0

    # Lighting;
    # Description;
    # 1;
    # Fixture type;
    # Plenum %;
    # Ballast factor;
    # Longwave radiant %;
    # Shortwave radiant %;
    exp_line = (
        f'Lighting;{description};1;{fixture_type};{plenum_pct:.1f};1;'
        f'{radiant_pct:.1f};{visible_pct:.1f};'
    )
    return exp_line


def equipment_to_trace700_miscellaneous(equipment, si_units=False, watts_per_area=None):
    """Get a TRACE 700 "T.LOAD_MISEQUIP" entry string from a Honeybee Equipment object.

    Args:
        equipment: A Honeybee ElectricEquipment or GasEquipment object.
        si_units: Boolean to note whether the units of the values in the resulting
            matrix are in SI (True) instead of IP (False). (Default: False).
        watts_per_area: Optional float for total W/m2 override to represent a combined
            electric + gas equipment load density. If None, equipment.watts_per_area
            will be used. (Default: None).

    Returns:
        A text string for a TRACE 700 T.LOAD_MISEQUIP library entry.
    """
    description = readable_short_name(equipment.display_name, max_length=40)
    sensible_pct = (1.0 - equipment.latent_fraction) * 100.0
    radiant_pct = equipment.radiant_fraction * 100.0
    lost_pct = equipment.lost_fraction * 100.0
    room_pct = 100.0 - lost_pct
    plenum_pct = 0.0

    meter_code = 2 if 'Gas' in equipment.__class__.__name__ else 1
    air_path = 2 if lost_pct > 0 else 1

    flux_unit = 'W/m2' if si_units else 'W/ft2'
    misc_unit_code = 9 if si_units else 8  # 8 = W/sq ft, 9 = W/sq m

    lpd_val = watts_per_area if watts_per_area is not None else equipment.watts_per_area
    energy_value = flux_dt.to_unit([lpd_val], flux_unit, 'W/m2')[0]

    # Miscellaneous;
    # Description;
    # 1;
    # Energy consumption;
    # Energy consumption unit;
    # Sensible %;
    # Room %;
    # Plenum %;
    # Radiant %;
    # Energy meter;
    # Air path;
    exp_line = (
        f'Miscellaneous;{description};1;{energy_value:.6f};{misc_unit_code};{sensible_pct:.1f};'
        f'{room_pct:.1f};{plenum_pct:.1f};{radiant_pct:.1f};{meter_code};{air_path};'
    )
    return exp_line


def program_to_trace700_internal_load_template(program, si_units=False):
    """Get a TRACE 700 "T.InternalLoadTemplate" entry string from a Honeybee ProgramType.

    Args:
        program: A Honeybee ProgramType object.
        si_units: Boolean to note whether the units of the values in the resulting
            matrix are in SI (True) instead of IP (False). (Default: False).

    Returns:
        A text string for a TRACE 700 T.InternalLoadTemplate entry.
    """
    template_name = program.display_name

    area_unit = 'm2' if si_units else 'ft2'
    power_unit = 'W' if si_units else 'Btu/h'
    flux_unit = 'W/m2' if si_units else 'W/ft2'

    ppl_amount_unit = 2 if si_units else 1
    ppl_load_unit = 8 if si_units else 7
    ltg_unit = 4 if si_units else 3
    misc_unit = 9 if si_units else 8

    # Fields 2-9 (People)
    ppl = program.people
    if ppl is not None:
        ppl_type = readable_short_name(ppl.display_name, max_length=40)
        ppl_amount = area_dt.to_unit([ppl.area_per_person], area_unit, 'm2')[0]
        sensible_watts = power_dt.to_unit([ppl.activity_max_sensible], power_unit, 'W')[0]
        latent_watts = power_dt.to_unit([ppl.activity_max_latent], power_unit, 'W')[0]
    else:
        ppl_type = 'None'
        ppl_amount = 0
        # default sensible and latent loads: 250 Btu/h (73.26775 W)
        # unit is hardcoded to IP since the sensible and latent values are converted
        # to Btu/h when importing the template
        sensible_watts = 250
        latent_watts = 250
        ppl_load_unit = 7

    # Fields 10-13 (Lighting)
    ltg = program.lighting
    if ltg is not None:
        ltg_type = ltg.display_name
        ltg_lpd = flux_dt.to_unit([ltg.watts_per_area], flux_unit, 'W/m2')[0] if ltg else 0.0
    else:
        ltg_type = 'Fluorescent, hung below ceiling, 100% load to space'
        ltg_lpd = 0.0

    # Fields 14-18 (Miscellaneous Equipment)
    elec_eq = program.electric_equipment
    gas_eq = program.gas_equipment

    if elec_eq is not None or gas_eq is not None:
        elec_lpd = elec_eq.watts_per_area if elec_eq is not None else 0.0
        gas_lpd = gas_eq.watts_per_area if gas_eq is not None else 0.0
        combined_lpd = elec_lpd + gas_lpd
        if combined_lpd > 0:
            misc_energy = flux_dt.to_unit([combined_lpd], flux_unit, 'W/m2')[0]
            eq_obj = elec_eq if elec_lpd >= gas_lpd else gas_eq
            energy_meter = 1 if elec_lpd >= gas_lpd else 2
            misc_type = readable_short_name(eq_obj.display_name, max_length=40)
        else:
            misc_type = 'None'
            misc_energy = 0
            energy_meter = 0
    else:
        misc_type = 'None'
        misc_energy = 0
        energy_meter = 0

    field_19, field_20 = 1, 2  # workstation, workstation unit

    exp_line = (
        f"{template_name};{ppl_type};Cooling Only (Design);{ppl_amount:.6f};{ppl_amount_unit};"
        f"{sensible_watts:.4f};{ppl_load_unit};{latent_watts:.4f};{ppl_load_unit};"
        f"{ltg_type};Cooling Only (Design);{ltg_lpd:.6f};{ltg_unit};"
        f"{misc_type};Cooling Only (Design);{misc_energy:.6f};{misc_unit};"
        f"{energy_meter};{field_19};{field_20};"
    )
    return exp_line


def program_to_trace700_airflow_template(program, si_units=False):
    """Get a TRACE 700 "T.AirflowTemplate" entry string from a Honeybee ProgramType.

    Args:
        program: A Honeybee ProgramType object.
        si_units: Boolean to note whether the units of the values in the resulting
            matrix are in SI (True) instead of IP (False). (Default: False).

    Returns:
        A text string for a TRACE 700 T.AirflowTemplate entry.
    """
    blank_val = '9999.99'
    template_name = program.display_name

    # Fields 4-7 (Ventilation Layout)
    vent = program.ventilation
    vent_flow_unit = 'L/s' if si_units else 'cfm'
    vent_unit = 6 if si_units else 3  # 6 = L/s/sq m, 3 = cfm/sq ft

    vent_val = 0
    if vent is not None:
        vent_val = flow_dt.to_unit([vent.flow_per_area], vent_flow_unit, 'm3/s')[0]
        vent_val = vent_val if si_units else vent_val * 10.7639104  # convert to cfm/ft2

    # Fields 8-13 (Infiltration Layout)
    inf = program.infiltration
    inf_unit = 5 if si_units else 3  # 5 = L/s/sq m, 3 = cfm/sq ft

    inf_val = 0
    if inf is not None:
        inf_val = inf.flow_per_exterior_area_si if si_units else inf.flow_per_exterior_area_ip

    exp_line = (
        f"{template_name};None;Available (100%);{vent_val:.6f};{vent_unit};{vent_val:.6f};{vent_unit};"
        f"None;Available (100%);{inf_val:.6f};{inf_unit};{inf_val:.6f};{inf_unit};"
        f"{blank_val};0;Available (100%);{blank_val};8;{blank_val};9;{blank_val};10;{blank_val};10;0;2;"
        f"Available (100%);0;0;{blank_val};0;{blank_val};1;{blank_val};{blank_val};0;0;{blank_val};0;"
    )
    return exp_line


def program_to_trace700_thermostat_template(program, si_units=False):
    """Get a TRACE 700 "T.ThermostatTemplate" entry string from a Honeybee ProgramType.

    Args:
        program: A Honeybee ProgramType object.
        si_units: Boolean to note whether the units of the values in the resulting
            matrix are in SI (True) instead of IP (False). (Default: False).

    Returns:
        A text string for a TRACE 700 T.ThermostatTemplate entry.
    """
    set_pt = program.setpoint
    template_name = program.display_name

    temp_unit_label = 'C' if si_units else 'F'
    temp_unit_code = 0 if si_units else 1  # 0 = Celsius, 1 = Fahrenheit

    if set_pt is not None:
        clg_db = temp_dt.to_unit([set_pt.cooling_setpoint], temp_unit_label, 'C')[0]
        htg_db = temp_dt.to_unit([set_pt.heating_setpoint], temp_unit_label, 'C')[0]
        clg_drift = temp_dt.to_unit([set_pt.cooling_setback], temp_unit_label, 'C')[0]
        htg_drift = temp_dt.to_unit([set_pt.heating_setback], temp_unit_label, 'C')[0]
        rh_val = set_pt.dehumidifying_setpoint if set_pt.dehumidifying_setpoint is not None else 50.0
    else:
        clg_db = temp_dt.to_unit([75.0], temp_unit_label, 'F')[0]
        htg_db = temp_dt.to_unit([68.0], temp_unit_label, 'F')[0]
        clg_drift = temp_dt.to_unit([90.0], temp_unit_label, 'F')[0]
        htg_drift = temp_dt.to_unit([55.0], temp_unit_label, 'F')[0]
        rh_val = 50.0

    control_fields = '1;0;2;1;'

    exp_line = (
        f"{template_name};{clg_db:.1f};{temp_unit_code};{htg_db:.1f};{temp_unit_code};"
        f"{rh_val:.0f};{clg_drift:.1f};None;{htg_drift:.1f};None;"
        f"{control_fields}"
    )
    return exp_line


def program_to_trace700_room_template(program):
    """Get a TRACE 700 "T.RoomTemplate" entry string from a Honeybee ProgramType.

    Args:
        program: A Honeybee ProgramType object.

    Returns:
        A text string for a TRACE 700 T.RoomTemplate entry.
    """
    template_name = program.display_name
    construction_template = 'Default'

    exp_line = f'{template_name};{template_name};{template_name};{template_name};{construction_template};'
    return exp_line


def internal_loads_to_exp(program, si_units=False):
    """Get an EXP string containing internal load library entries and templates for a ProgramType.

    Args:
        program: A Honeybee ProgramType object.
        si_units: Boolean to note whether the units of the values in the resulting
            matrix are in SI (True) instead of IP (False). (Default: False).

    Returns:
        Text string of an EXP file for TRACE 700 containing internal load definitions.
    """
    newline = '\n'
    standalone_blocks = ['EDITORSv6.3.1']

    if program.people:
        standalone_blocks.extend([
            'T.LOAD_PEOPLE',
            people_to_trace700_people(program.people, si_units)
        ])
    if program.lighting:
        standalone_blocks.extend([
            'T.LOAD_LIGHTS',
            lighting_to_trace700_lighting(program.lighting)
        ])

    elec_eq = program.electric_equipment
    gas_eq = program.gas_equipment
    if elec_eq is not None or gas_eq is not None:
        elec_lpd = elec_eq.watts_per_area if elec_eq is not None else 0.0
        gas_lpd = gas_eq.watts_per_area if gas_eq is not None else 0.0
        combined_lpd = elec_lpd + gas_lpd
        if elec_lpd + gas_lpd > 0:
            eq_obj = elec_eq if elec_lpd >= gas_lpd else gas_eq
            standalone_blocks.extend([
                'T.LOAD_MISEQUIP',
                equipment_to_trace700_miscellaneous(eq_obj, si_units, watts_per_area=combined_lpd)
            ])

    internal_load_template = program_to_trace700_internal_load_template(program, si_units)
    standalone_blocks.extend([
        'T.InternalLoadTemplate',
        internal_load_template
    ])

    file_data = newline.join(standalone_blocks) + newline
    return file_data


def airflow_to_exp(program, si_units=False):
    """Get an EXP string containing only the airflow template for a ProgramType.

    Args:
        program: A Honeybee ProgramType object.
        si_units: Boolean to note whether the units of the values in the resulting
            matrix are in SI (True) instead of IP (False). (Default: False).

    Returns:
        Text string of an EXP file for TRACE 700 containing the airflow template.
    """
    newline = '\n'

    airflow_template = program_to_trace700_airflow_template(program, si_units)

    standalone_blocks = [
        'EDITORSv6.3.1',
        'T.AirflowTemplate',
        airflow_template
    ]

    file_data = newline.join([b for b in standalone_blocks if b != '']) + newline
    return file_data


def thermostat_to_exp(program, si_units=False):
    """Get an EXP string containing only the thermostat template for a ProgramType.

    Args:
        program: A Honeybee ProgramType object.
        si_units: Boolean to note whether the units of the values in the resulting
            matrix are in SI (True) instead of IP (False). (Default: False).

    Returns:
        Text string of an EXP file for TRACE 700 containing the thermostat template.
    """
    newline = '\n'

    thermostat_template = program_to_trace700_thermostat_template(program, si_units)

    standalone_blocks = [
        'EDITORSv6.3.1',
        'T.ThermostatTemplate',
        thermostat_template
    ]

    file_data = newline.join([b for b in standalone_blocks if b != '']) + newline
    return file_data


def program_to_exp(program, si_units=False):
    """Get a complete EXP string for a Honeybee ProgramType.

    Args:
        program: A Honeybee ProgramType object for which the TRACE 700 EXP string
            will be generated.
        si_units: Boolean to note whether the units of the values in the resulting
            matrix are in SI (True) instead of IP (False). (Default: False).

    Returns:
        Text string of a complete EXP file for TRACE 700.
    """
    newline = '\n'
    standalone_blocks = ['EDITORSv6.3.1']

    if program.people:
        standalone_blocks.extend([
            'T.LOAD_PEOPLE',
            people_to_trace700_people(program.people, si_units)
        ])

    if program.lighting:
        standalone_blocks.extend([
            'T.LOAD_LIGHTS',
            lighting_to_trace700_lighting(program.lighting)
        ])

    elec_eq = program.electric_equipment
    gas_eq = program.gas_equipment
    if elec_eq is not None or gas_eq is not None:
        elec_lpd = elec_eq.watts_per_area if elec_eq is not None else 0.0
        gas_lpd = gas_eq.watts_per_area if gas_eq is not None else 0.0
        combined_lpd = elec_lpd + gas_lpd
        if elec_lpd + gas_lpd > 0:
            eq_obj = elec_eq if elec_lpd >= gas_lpd else gas_eq
            standalone_blocks.extend([
                'T.LOAD_MISEQUIP',
                equipment_to_trace700_miscellaneous(eq_obj, si_units, watts_per_area=combined_lpd)
            ])

    internal_load_template = program_to_trace700_internal_load_template(program, si_units)
    airflow_template = program_to_trace700_airflow_template(program, si_units)
    thermostat_template = program_to_trace700_thermostat_template(program, si_units)
    room_template = program_to_trace700_room_template(program)

    standalone_blocks.extend([
        'T.InternalLoadTemplate', internal_load_template,
        'T.AirflowTemplate', airflow_template,
        'T.ThermostatTemplate', thermostat_template,
        'T.RoomTemplate', room_template
    ])

    file_data = newline.join(standalone_blocks) + newline
    return file_data


def programs_to_exp(programs, si_units=False):
    """Get a single combined EXP string for a list of Honeybee ProgramTypes.

    Args:
        programs: A list of Honeybee ProgramType objects.
        si_units: Boolean to note whether the units of the values in the resulting
            matrix are in SI (True) instead of IP (False). (Default: False).

    Returns:
        Text string of a combined EXP file for TRACE 700.
    """
    newline = '\n'

    people_templates = []
    lighting_templates = []
    equip_templates = []
    internal_load_templates = []
    airflow_templates = []
    thermostat_templates = []
    room_templates = []

    seen_people = set()
    seen_lighting = set()
    seen_equip = set()

    for program in programs:
        if program.people and program.people.identifier not in seen_people:
            people_templates.append(people_to_trace700_people(program.people, si_units))
            seen_people.add(program.people.identifier)

        if program.lighting and program.lighting.identifier not in seen_lighting:
            lighting_templates.append(lighting_to_trace700_lighting(program.lighting))
            seen_lighting.add(program.lighting.identifier)

        elec_eq = program.electric_equipment
        gas_eq = program.gas_equipment
        if elec_eq is not None or gas_eq is not None:
            elec_lpd = elec_eq.watts_per_area if elec_eq is not None else 0.0
            gas_lpd = gas_eq.watts_per_area if gas_eq is not None else 0.0
            combined_lpd = elec_lpd + gas_lpd

            if combined_lpd > 0:
                eq_obj = elec_eq if elec_lpd >= gas_lpd else gas_eq
                if eq_obj.identifier not in seen_equip:
                    equip_templates.append(
                        equipment_to_trace700_miscellaneous(
                            eq_obj, si_units=si_units, watts_per_area=combined_lpd
                        )
                    )
                    seen_equip.add(eq_obj.identifier)

        internal_load_templates.append(
            program_to_trace700_internal_load_template(program, si_units))
        airflow_templates.append(program_to_trace700_airflow_template(program, si_units))
        thermostat_templates.append(program_to_trace700_thermostat_template(program, si_units))
        room_templates.append(program_to_trace700_room_template(program))

    standalone_blocks = ['EDITORSv6.3.1']

    if people_templates:
        standalone_blocks.append('T.LOAD_PEOPLE')
        standalone_blocks.extend(people_templates)

    if lighting_templates:
        standalone_blocks.append('T.LOAD_LIGHTS')
        standalone_blocks.extend(lighting_templates)

    if equip_templates:
        standalone_blocks.append('T.LOAD_MISEQUIP')
        standalone_blocks.extend(equip_templates)

    if internal_load_templates:
        standalone_blocks.append('T.InternalLoadTemplate')
        standalone_blocks.extend(internal_load_templates)

    if airflow_templates:
        standalone_blocks.append('T.AirflowTemplate')
        standalone_blocks.extend(airflow_templates)

    if thermostat_templates:
        standalone_blocks.append('T.ThermostatTemplate')
        standalone_blocks.extend(thermostat_templates)

    if room_templates:
        standalone_blocks.append('T.RoomTemplate')
        standalone_blocks.extend(room_templates)

    file_data = newline.join(standalone_blocks) + newline
    return file_data
