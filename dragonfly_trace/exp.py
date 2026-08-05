"""Methods to generate EXP templates for Trane TRACE."""
from honeybee.typing import readable_short_name
from ladybug.datatype.area import Area
from ladybug.datatype.conductivity import Conductivity
from ladybug.datatype.density import Density
from ladybug.datatype.distance import Distance
from ladybug.datatype.power import Power
from ladybug.datatype.energyflux import EnergyFlux
from ladybug.datatype.volumeflowrate import VolumeFlowRate
from ladybug.datatype.temperature import Temperature
from ladybug.datatype.specificheatcapacity import SpecificHeatCapacity
from ladybug.datatype.rvalue import RValue
from ladybug.datatype.uvalue import UValue
from honeybee_energy.material.opaque import EnergyMaterialNoMass


area_dt = Area()
conductivity_dt = Conductivity()
density_dt = Density()
distance_dt = Distance()
power_dt = Power()
flux_dt = EnergyFlux()
flow_dt = VolumeFlowRate()
temp_dt = Temperature()
specific_heat_capacity_dt = SpecificHeatCapacity()
rvalue_dt = RValue()
uvalue_dt = UValue()


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


def energy_material_to_trace700_material(material, si_units=False, id=999):
    """Converts a Honeybee EnergyMaterial or EnergyMaterialNoMass to a T.MATR_MATERIAL entry."""
    description = readable_short_name(material.display_name, max_length=40)
    material_id = f'M{id}' if not str(id).startswith('M') else str(id)

    thickness_unit = 'm' if si_units else 'in'
    thickness_code = 2 if si_units else 1

    conductivity_unit = 'W/m-K' if si_units else 'Btu/h-ft-F'
    conductivity_code = 0 if si_units else 1

    density_unit = 'kg/m3' if si_units else 'lb/ft3'
    density_code = 1 if si_units else 0

    specific_heat_unit = 'J/kg-K' if si_units else 'Btu/lb-F'
    specific_heat_code = 0 if si_units else 1

    resistance_unit = 'm2-K/W' if si_units else 'h-ft2-F/Btu'
    resistance_unit_code = 1

    category = 'Undefined Material'
    if isinstance(material, EnergyMaterialNoMass):
        resistance = rvalue_dt.to_unit([material.r_value], resistance_unit, 'm2-K/W')[0]
        thickness = 0
        conductivity = 0
        density = 0
        specific_heat = 0
    else:
        thickness = distance_dt.to_unit([material.thickness], thickness_unit, 'm')[0]
        conductivity = conductivity_dt.to_unit([material.conductivity], conductivity_unit, 'W/m-K')[0]
        density = density_dt.to_unit([material.density], density_unit, 'kg/m3')[0]
        thickness = distance_dt.to_unit([material.thickness], thickness_unit, 'm')[0]
        specific_heat = specific_heat_capacity_dt.to_unit(
            [material.specific_heat], specific_heat_unit, 'J/kg-K'
        )[0]
        resistance = 0.0  # this is 0 because the other fields are used

    exp_line = (
        f'0;{material_id};{category};0;{description};{thickness};{thickness_code};'
        f'{conductivity};{conductivity_code};{density};{density_code};'
        f'{specific_heat};{specific_heat_code};{resistance};{resistance_unit_code};'
    )
    return exp_line


def opaque_construction_to_trace700_construction(
    construction, const_type='Wall', si_units=False, starting_material_id=500, material_id_map=None
):
    """Converts a Honeybee OpaqueConstruction to a TRACE 700 construction entry."""
    description = readable_short_name(construction.display_name, max_length=40)

    film_map = {
        'Wall': ('A0', 'E0'),
        'Roof': ('A0', 'E0'),
        'Floor': ('E0', 'E0'),
        'Partition': ('A0', 'E0'),
        'Exposed Floor': ('A0', 'E0')
    }
    out_film, in_film = film_map.get(const_type, ('A0', 'E0'))

    layers_ids = ['None'] * 10
    layers_ids[0] = out_film

    material_lines = []
    id_counter = starting_material_id

    for idx, mat in enumerate(construction.materials):
        if idx >= 8:
            break
        mat_key = mat.identifier
        if material_id_map is not None and mat_key in material_id_map:
            mat_tag = material_id_map[mat_key]
        else:
            mat_tag = f'M{id_counter}'
            mat_line = energy_material_to_trace700_material(mat, si_units=si_units, id=id_counter)
            material_lines.append(mat_line)
            if material_id_map is not None:
                material_id_map[mat_key] = mat_tag
            id_counter += 1

        layers_ids[idx + 1] = mat_tag

    layers_ids[len(construction.materials) + 1] = in_film
    layers_str = ';'.join(layers_ids)

    b_coeffs = ';'.join([''] * 7)
    d_coeffs = ';'.join([''] * 7)

    u_factor_unit = 'W/m2-K' if si_units else 'Btu/h-ft2-F'
    u_factor = uvalue_dt.to_unit([construction.u_factor], u_factor_unit, 'W/m2-K')[0]
    u_code = 0 if si_units else 1

    hc_si = construction.area_heat_capacity
    heat_capacity = hc_si if si_units else (hc_si * 0.000048919)
    hc_code = 0 if si_units else 1

    wt_si = sum(
        m.density * m.thickness
        for m in construction.materials
        if hasattr(m, 'density') and hasattr(m, 'thickness')
    )
    if si_units:
        area_density = wt_si
        ad_code = 0
    else:
        area_density = wt_si * 0.20481614
        ad_code = 1

    out_mat = construction.outside_material
    in_mat = construction.inside_material

    sol_abs_out = getattr(out_mat, 'solar_absorptance', 0.9)
    therm_abs_out = getattr(out_mat, 'thermal_absorptance', 0.9)
    sol_abs_in = getattr(in_mat, 'solar_absorptance', 0.65)
    therm_abs_in = getattr(in_mat, 'thermal_absorptance', 0.9)
    vis_refl_in = getattr(in_mat, 'visible_reflectance', 0.20)

    roughness_map = {
        'VeryRough': 0, 'Rough': 1, 'MediumRough': 2, 'MediumSmooth': 3,
        'Smooth': 4, 'VerySmooth': 5
    }
    roughness = roughness_map.get(getattr(out_mat, 'roughness', 'Rough'), 1)

    comment = ''
    zero_padding_block = ';'.join(['0'] * 10)

    exp_line = (
        f'{const_type};{description};1;0;{layers_str};'
        f'{b_coeffs};{d_coeffs};'
        f'0;0;1;'
        f'{area_density};{ad_code};{heat_capacity};{hc_code};{u_factor};{u_code};'
        f'0;{comment};{sol_abs_out:.8f};'
        f'{zero_padding_block};'
        f'{therm_abs_out:.8f};{sol_abs_in:.8f};{therm_abs_in:.8f};{vis_refl_in:.8f};{roughness};1;'
    )
    return exp_line, material_lines


def window_construction_to_trace700_glass(construction, si_units=False, is_door=False):
    """Converts a Honeybee WindowConstruction object to a T.GLAS_GLASS entry."""
    description = construction.display_name
    if is_door and not description.lower().endswith('door'):
        description = f'{description} Door'
    description = readable_short_name(description, max_length=40)

    u_value_unit = 'W/m2-K' if si_units else 'Btu/h-ft2-F'
    u_value = uvalue_dt.to_unit([construction.u_value], u_value_unit, 'W/m2-K')[0]
    u_value_code = 0 if si_units else 1

    shgc = getattr(construction, 'shgc', 0.0)
    vt = getattr(construction, 'visible_transmittance', 0.5)
    panes = getattr(construction, 'glazing_count', 1)

    inside_vis_refl = construction.inside_solar_reflectance
    inside_sol_refl = construction.inside_solar_reflectance

    solar_transmissivity = getattr(construction, 'solar_transmittance', 0.0)

    outside_emissivity = construction.outside_emissivity
    inside_emissivity = construction.inside_emissivity

    # Field 179: 1 for standard glass, 2 for glass doors
    glass_type_code = 2 if is_door else 1

    # TRACE 700 custom glass data (213 fields)
    # This is copied from an exported default glass material in TRACE 700
    glass_tail = (
        "0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;"
        "0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;"
        "0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;"
        "0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;"
        f"0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;{glass_type_code};0;0;"
        "0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;57.1500015258789063;"
        "25.3999996185302734;25.3999996185302734;4.59999990463256836;1.10099995136260986;"
        ".89999997615814209;.89999997615814209;.89999997615814209;0;0;0;0;0;0;0;0;0;0;0;0;"
    )

    exp_line = (
        f'{description};Glass;1;{shgc:.6f};{u_value:.6f};{u_value_code};{panes};0;'
        f'{vt:.4f};{inside_vis_refl:.4f};{solar_transmissivity:.4f};{inside_sol_refl:.4f};'
        f'{outside_emissivity:.4f};{inside_emissivity:.4f};{glass_tail}'
    )
    return exp_line


def construction_set_to_trace700_template(construction_set, si_units=False):
    """Translates a Honeybee ConstructionSet into a TRACE 700 Construction Template line."""
    template_name = readable_short_name(construction_set.display_name, max_length=40)
    u_code = 0 if si_units else 1

    def _get_opaque_info(cnst):
        if cnst is None:
            return 'None', 0.0
        u_value_unit = 'W/m2-K' if si_units else 'Btu/h-ft2-F'
        u_value = uvalue_dt.to_unit([cnst.u_value], u_value_unit, 'W/m2-K')[0]
        return readable_short_name(cnst.display_name, max_length=40), u_value

    def _get_window_info(cnst, is_door=False):
        if cnst is None:
            return 'None', 0.0, 0.0
        u_value_unit = 'W/m2-K' if si_units else 'Btu/h-ft2-F'
        u_value = uvalue_dt.to_unit([cnst.u_value], u_value_unit, 'W/m2-K')[0]
        desc = cnst.display_name
        if is_door and not desc.lower().endswith('door'):
            desc = f'{desc} Door'
        return readable_short_name(desc, max_length=40), u_value, cnst.shgc

    def _get_door_info(cnst):
        if cnst is None:
            return 'None', 0.0, 0.0
        is_glass = hasattr(cnst, 'shgc')
        if is_glass:
            return _get_window_info(cnst, is_door=True)
        else:
            desc, u_val = _get_opaque_info(cnst)
            return readable_short_name(desc, max_length=40), u_val, 0.0

    roof_cnst = construction_set.roof_ceiling_set.exterior_construction
    roof_name, roof_u = _get_opaque_info(roof_cnst)

    floor_cnst = (
        construction_set.floor_set.ground_construction or
        construction_set.floor_set.exterior_construction or
        construction_set.floor_set.interior_construction
    )
    floor_name, floor_u = _get_opaque_info(floor_cnst)

    skylight_cnst = construction_set.aperture_set.skylight_construction
    skylight_name, skylight_u, skylight_shgc = _get_window_info(skylight_cnst)

    wall_cnst = construction_set.wall_set.exterior_construction
    wall_name, wall_u = _get_opaque_info(wall_cnst)

    window_cnst = construction_set.aperture_set.window_construction
    window_name, window_u, window_shgc = _get_window_info(window_cnst)

    partition_cnst = construction_set.wall_set.interior_construction
    partition_name, partition_u = _get_opaque_info(partition_cnst)

    # resolve door construction priority (glass door if set, otherwise opaque door)
    if getattr(construction_set.door_set, '_exterior_glass_construction', None) is not None:
        door_cnst = construction_set.door_set.exterior_glass_construction
    elif getattr(construction_set.door_set, '_exterior_construction', None) is not None:
        door_cnst = construction_set.door_set.exterior_construction
    else:
        door_cnst = (
            construction_set.door_set.exterior_construction or
            construction_set.door_set.exterior_glass_construction
        )

    door_name, door_u, door_shgc = _get_door_info(door_cnst)
    tail_fields = '0;0;'

    exp_line = (
        f'{template_name};'
        f'{floor_name};{floor_u:.6f};{u_code};'
        f'{roof_name};{roof_u:.6f};{u_code};'
        f'{skylight_name};{skylight_u:.6f};{u_code};{skylight_shgc:.6f};'
        f'{wall_name};{wall_u:.6f};{u_code};'
        f'{window_name};{window_u:.6f};{u_code};{window_shgc:.6f};'
        f'{partition_name};{partition_u:.6f};{u_code};'
        f'10;0;2;0;10;0;'
        f'{door_name};{door_u:.6f};{u_code};{door_shgc:.6f};'
        f'{tail_fields}'
    )
    return exp_line


def construction_sets_to_exp(construction_sets, si_units=False):
    """Get a single combined EXP string for a list of Honeybee ConstructionSets."""
    newline = '\n'

    exfloor_templates = []
    floor_templates = []
    partition_templates = []
    roof_templates = []
    wall_templates = []
    glass_templates = []
    material_templates = []
    construction_templates = []

    seen_constructions = set()
    seen_materials = set()
    material_id_map = {}
    material_counter = 500

    def _process_opaque(cnst, category):
        nonlocal material_counter
        if cnst is not None and cnst.identifier not in seen_constructions:
            line, mat_lines = opaque_construction_to_trace700_construction(
                cnst, const_type=category, si_units=si_units,
                starting_material_id=material_counter, material_id_map=material_id_map
            )
            material_counter += len(mat_lines)
            seen_constructions.add(cnst.identifier)

            for ml in mat_lines:
                mat_id = ml.split(';')[1]
                if mat_id not in seen_materials:
                    material_templates.append(ml)
                    seen_materials.add(mat_id)

            return line
        return None

    def _process_glass(cnst, is_door=False):
        if cnst is not None:
            key = (cnst.identifier, is_door)
            if key not in seen_constructions:
                line = window_construction_to_trace700_glass(cnst, si_units=si_units, is_door=is_door)
                seen_constructions.add(key)
                return line
        return None

    for c_set in construction_sets:
        w_ext = _process_opaque(c_set.wall_set.exterior_construction, 'Wall')
        if w_ext:
            wall_templates.append(w_ext)

        w_grd = _process_opaque(c_set.wall_set.ground_construction, 'Wall')
        if w_grd:
            wall_templates.append(w_grd)

        w_int = _process_opaque(c_set.wall_set.interior_construction, 'Partition')
        if w_int:
            partition_templates.append(w_int)

        r_ext = _process_opaque(c_set.roof_ceiling_set.exterior_construction, 'Roof')
        if r_ext:
            roof_templates.append(r_ext)

        r_grd = _process_opaque(c_set.roof_ceiling_set.ground_construction, 'Roof')
        if r_grd:
            roof_templates.append(r_grd)

        r_int = _process_opaque(c_set.roof_ceiling_set.interior_construction, 'Floor')
        if r_int:
            floor_templates.append(r_int)

        f_ext = _process_opaque(c_set.floor_set.exterior_construction, 'Exposed Floor')
        if f_ext:
            exfloor_templates.append(f_ext)

        f_grd = _process_opaque(c_set.floor_set.ground_construction, 'Floor')
        if f_grd:
            floor_templates.append(f_grd)

        f_int = _process_opaque(c_set.floor_set.interior_construction, 'Floor')
        if f_int:
            floor_templates.append(f_int)

        for ap_cnst in (
            c_set.aperture_set.window_construction,
            c_set.aperture_set.interior_construction,
            c_set.aperture_set.skylight_construction,
            c_set.aperture_set.operable_construction,
        ):
            g_line = _process_glass(ap_cnst, is_door=False)
            if g_line:
                glass_templates.append(g_line)

        d_ext = _process_glass(c_set.door_set.exterior_construction, is_door=True)
        if d_ext:
            glass_templates.append(d_ext)

        d_ovh = _process_glass(c_set.door_set.overhead_construction, is_door=True)
        if d_ovh:
            glass_templates.append(d_ovh)

        d_int = _process_glass(c_set.door_set.interior_construction, is_door=True)
        if d_int:
            glass_templates.append(d_int)

        d_ext_gls = _process_glass(c_set.door_set.exterior_glass_construction, is_door=True)
        if d_ext_gls:
            glass_templates.append(d_ext_gls)

        d_int_gls = _process_glass(c_set.door_set.interior_glass_construction, is_door=True)
        if d_int_gls:
            glass_templates.append(d_int_gls)

        construction_templates.append(construction_set_to_trace700_template(c_set, si_units=si_units))

    standalone_blocks = ['EDITORSv6.3.1']

    if exfloor_templates:
        standalone_blocks.append('T.CNST_EXFLOOR')
        standalone_blocks.extend(exfloor_templates)

    if floor_templates:
        standalone_blocks.append('T.CNST_FLOOR')
        standalone_blocks.extend(floor_templates)

    if partition_templates:
        standalone_blocks.append('T.CNST_PART')
        standalone_blocks.extend(partition_templates)

    if roof_templates:
        standalone_blocks.append('T.CNST_ROOF')
        standalone_blocks.extend(roof_templates)

    if wall_templates:
        standalone_blocks.append('T.CNST_WALL')
        standalone_blocks.extend(wall_templates)

    if glass_templates:
        standalone_blocks.append('T.GLAS_GLASS')
        standalone_blocks.extend(glass_templates)

    if material_templates:
        standalone_blocks.append('T.MATR_MATERIAL')
        standalone_blocks.extend(material_templates)

    if construction_templates:
        standalone_blocks.append('T.ConstructionTemplate')
        standalone_blocks.extend(construction_templates)

    file_data = newline.join(standalone_blocks) + newline
    return file_data
