"""Methods to write EXP files to Trane TRACE."""


def people_to_trace700_people(people):
    """Converts a Honeybee People object to a T.LOAD_PEOPLE entry."""
    description = people.display_name or people.identifier

    people_amount = people.people_per_area_ip

    sensible_ppl = people.activity_max_sensible_ip
    latent_ppl = people.activity_max_latent_ip

    # radiant fraction
    radiant_pct = people.radiant_fraction * 100.0

    # People;Description;1;People amount;People amount unit;Sensible load;Sensible load unit;Latent load;Latent load unit;Longwave radiant %;
    exp_line = (
        f'People;{description};1;{people_amount:.6f};1;'
        f'{sensible_ppl:.6f};7;{latent_ppl:.6f};7;{radiant_pct:.1f};'
    )
    return exp_line


def lighting_to_trace700_lighting(lighting, fixture_type='SUSFLUOR'):
    """Converts a Honeybee Lighting object to a T.LOAD_LIGHTS entry."""
    description = lighting.display_name or lighting.identifier

    plenum_pct = lighting.return_air_fraction * 100.0
    radiant_pct = lighting.radiant_fraction * 100.0
    visible_pct = lighting.visible_fraction * 100.0

    # Lighting;Description;1;Fixture type;Plenum %;Ballast factor;Longwave radiant %;Shortwave radiant %;
    exp_line = f'Lighting;{description};1;{fixture_type};{plenum_pct:.1f};1;{radiant_pct:.1f};{visible_pct:.1f};'
    return exp_line


def equipment_to_trace700_miscellaneous(equipment):
    """Converts a Honeybee Equipment object to a T.LOAD_MISEQUIP entry."""
    description = equipment.display_name or equipment.identifier

    energy_value = equipment.watts_per_area_ip

    sensible_pct = (1.0 - equipment.latent_fraction) * 100.0
    radiant_pct = equipment.radiant_fraction * 100.0
    lost_pct = equipment.lost_fraction * 100.0
    room_pct = 100.0 - lost_pct
    plenum_pct = 0.0

    meter_code = 2 if 'Gas' in equipment.__class__.__name__ else 1
    air_path = 2 if lost_pct > 0 else 1

    # Miscellaneous;Description;1;Energy consumption;Energy consumption unit;Sensible %;Room %;Plenum %;Radiant %;Energy meter;Air path;
    exp_line = (
        f'Miscellaneous;{description};1;{energy_value:.6f};8;{sensible_pct:.1f};'
        f'{room_pct:.1f};{plenum_pct:.1f};{radiant_pct:.1f};{meter_code};{air_path};'
    )
    return exp_line


def program_to_trace700_internal_load_template(program):
    """Translates a Honeybee ProgramType into a TRACE 700 Internal Load Template line."""
    # Field 1
    template_name = program.display_name or program.identifier

    # Fields 2-9 (People)
    ppl = program.people
    if ppl is not None:
        ppl_type = ppl.display_name or ppl.identifier
        ppl_amount = ppl.people_per_area_ip
        sensible_watts = ppl.activity_max_sensible_ip
        latent_watts = ppl.activity_max_latent_ip
        ppl_amount_unit = 1  # sq ft / person
        ppl_load_unit = 7
    else:
        ppl_type = 'None'
        ppl_amount = 0.0
        ppl_amount_unit = 0
        sensible_watts = 0.0
        latent_watts = 0.0
        ppl_load_unit = 8

    # Fields 10-13 (Lighting)
    ltg = program.lighting
    if ltg is not None:
        ltg_type = ltg.display_name or ltg.identifier
        ltg_lpd = ltg.watts_per_area_ip
        ltg_unit = 3  # W/sq ft
    else:
        ltg_type = 'None'
        ltg_lpd = 0.0
        ltg_unit = 4

    # Fields 14-18 (Miscellaneous)
    elec_eq = program.electric_equipment
    gas_eq = program.gas_equipment

    elec_lpd = elec_eq.watts_per_area_ip if elec_eq is not None else 0.0
    gas_lpd = gas_eq.watts_per_area_ip if gas_eq is not None else 0.0
    combined_lpd = elec_lpd + gas_lpd

    if combined_lpd > 0:
        if elec_lpd >= gas_lpd:
            eq_obj = elec_eq
            energy_meter = 1  # Electricity
        else:
            eq_obj = gas_eq
            energy_meter = 2  # Gas
        misc_type = eq_obj.display_name or eq_obj.identifier
    else:
        misc_type = 'None'
        energy_meter = 0

    misc_unit = 8  # W/sq ft

    field_19 = 0  # workstation density
    field_20 = 2  # workstation unit (workstation/person)

    exp_line = (
        f"{template_name};{ppl_type};Cooling Only (Design);{ppl_amount:.6f};{ppl_amount_unit};"
        f"{sensible_watts:.4f};{ppl_load_unit};{latent_watts:.4f};{ppl_load_unit};"
        f"{ltg_type};Cooling Only (Design);{ltg_lpd:.6f};{ltg_unit};"
        f"{misc_type};Cooling Only (Design);{combined_lpd:.6f};{misc_unit};"
        f"{energy_meter};{field_19};{field_20};"
    )

    return exp_line


def program_to_trace700_airflow_template(program):
    """Translates a Honeybee ProgramType into a TRACE 700 Airflow Template line."""
    blank_val = '9999.990234375'

    # Field 1
    template_name = program.display_name or program.identifier

    # Fields 4-7
    vent = program.ventilation
    if vent is not None:
        vent_val = vent.flow_per_area_ip
        vent_unit = 3  # cfm/sq ft
    else:
        vent_val = 0.0
        vent_unit = 3

    # Fields 8-13
    inf = program.infiltration
    if inf is not None:
        inf_val = inf.flow_per_exterior_area_ip
        inf_unit = 3
    else:
        inf_val = 0.0
        inf_unit = 3

    exp_line = (
        f"{template_name};None;Available (100%);{vent_val:.6f};{vent_unit};{vent_val:.6f};{vent_unit};"
        f"None;Available (100%);{inf_val:.6f};{inf_unit};{inf_val:.6f};{inf_unit};"
        f"{blank_val};0;Available (100%);{blank_val};8;{blank_val};9;{blank_val};10;{blank_val};10;0;2;"
        f"Available (100%);0;0;{blank_val};0;{blank_val};1;{blank_val};{blank_val};0;0;{blank_val};0;"
    )

    return exp_line


def program_to_trace700_thermostat_template(program):
    """Translates a Honeybee ProgramType (Setpoint) into a TRACE 700 Thermostat Template line."""
    set_pt = program.setpoint

    # Field 1
    template_name = program.display_name or program.identifier

    temp_unit = 1  # 1 = Fahrenheit

    # Fields 2-10: Design thermostat settings
    if set_pt is not None:
        clg_db = set_pt.cooling_setpoint_ip
        htg_db = set_pt.heating_setpoint_ip
        clg_drift = set_pt.cooling_setback_ip
        htg_drift = set_pt.heating_setback_ip
        rh_val = set_pt.dehumidifying_setpoint \
            if set_pt.dehumidifying_setpoint is not None else 50.0
    else:
        clg_db = 75.0
        htg_db = 68.0
        clg_drift = 90.0
        htg_drift = 55.0
        rh_val = 50.0

    # Fields 10-13: Sensor Locations, Humidity
    # 1 = Room, 0 = None, 2 = Medium, 1 = Room
    control_fields = '1;0;2;1;'

    exp_line = (
        f"{template_name};{clg_db:.1f};{temp_unit};{htg_db:.1f};{temp_unit};"
        f"{rh_val:.0f};{clg_drift:.1f};None;{htg_drift:.1f};None;"
        f"{control_fields}"
    )

    return exp_line


def program_to_trace700_room_template(program):
    """Translates a Honeybee ProgramType into a TRANE TRACE 700 Room Template line."""
    template_name = program.display_name or program.identifier

    construction_template = 'Default'

    exp_line = f'{template_name};{template_name};{template_name};{template_name};{construction_template};'

    return exp_line


def internal_loads_to_exp(program, output_path):
    """Compiles and writes only the Internal Loads to a standalone EXP file."""
    newline = '\r\n'

    people_line = people_to_trace700_people(program.people) if program.people else ''
    lighting_line = lighting_to_trace700_lighting(program.lighting) if program.lighting else ''

    eq_obj = program.electric_equipment or program.gas_equipment
    equip_line = equipment_to_trace700_miscellaneous(eq_obj) if eq_obj else ''

    template_line = program_to_trace700_internal_load_template(program)

    standalone_blocks = [
        'EDITORSv6.3.1',
        'T.LOAD_PEOPLE', people_line,
        'T.LOAD_LIGHTS', lighting_line,
        'T.LOAD_MISEQUIP', equip_line,
        'T.InternalLoadTemplate', template_line
    ]

    filtered_blocks = [block for block in standalone_blocks if block != '']
    file_data = newline.join(filtered_blocks) + newline

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        f.write(file_data)

    return output_path


def airflow_to_exp(program, output_path):
    """Compiles and writes only the Airflow Template section to a standalone EXP file."""
    newline = '\r\n'

    airflow_line = program_to_trace700_airflow_template(program)

    standalone_blocks = [
        'EDITORSv6.3.1',
        'T.AirflowTemplate', airflow_line
    ]

    filtered_blocks = [block for block in standalone_blocks if block != '']
    file_data = newline.join(filtered_blocks) + newline

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        f.write(file_data)

    return output_path


def thermostat_to_exp(program, output_path):
    """Compiles and writes only the Thermostat Template section to a standalone EXP file."""
    newline = '\r\n'

    thermostat_line = program_to_trace700_thermostat_template(program)

    standalone_blocks = [
        'EDITORSv6.3.1',
        'T.ThermostatTemplate', thermostat_line
    ]

    filtered_blocks = [block for block in standalone_blocks if block != '']
    file_data = newline.join(filtered_blocks) + newline

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        f.write(file_data)

    return output_path


def program_to_exp(program, output_path):
    """Compiles a complete TRACE library structure and writes a standalone EXP file."""
    newline = '\r\n'

    people_line = people_to_trace700_people(program.people) if program.people else ''
    lighting_line = lighting_to_trace700_lighting(program.lighting) if program.lighting else ''

    eq_obj = program.electric_equipment or program.gas_equipment
    equip_line = equipment_to_trace700_miscellaneous(eq_obj) if eq_obj else ''

    template_line = program_to_trace700_internal_load_template(program)
    airflow_line = program_to_trace700_airflow_template(program)
    thermostat_line = program_to_trace700_thermostat_template(program)
    room_template_line = program_to_trace700_room_template(program)

    standalone_blocks = [
        'EDITORSv6.3.1',
        'T.LOAD_PEOPLE', people_line,
        'T.LOAD_LIGHTS', lighting_line,
        'T.LOAD_MISEQUIP', equip_line,
        'T.InternalLoadTemplate', template_line,
        'T.AirflowTemplate', airflow_line,
        'T.ThermostatTemplate', thermostat_line,
        'T.RoomTemplate', room_template_line
    ]

    filtered_blocks = [block for block in standalone_blocks if block != '']
    file_data = newline.join(filtered_blocks) + newline

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        f.write(file_data)

    return output_path
