"""Methods to generate EXP templates for Trane TRACE."""
from ladybug.datatype.area import Area
from ladybug.datatype.conductivity import Conductivity
from ladybug.datatype.density import Density
from ladybug.datatype.distance import Distance
from ladybug.datatype.power import Power
from ladybug.datatype.energyflux import EnergyFlux
from ladybug.datatype.volumeflowrate import VolumeFlowRate
from ladybug.datatype.volumeflowrateintensity import VolumeFlowRateIntensity
from ladybug.datatype.temperature import Temperature
from ladybug.datatype.specificheatcapacity import SpecificHeatCapacity
from ladybug.datatype.rvalue import RValue
from ladybug.datatype.uvalue import UValue
from honeybee.typing import readable_short_name, clean_ep_string

from honeybee_energy.material.opaque import EnergyMaterial, EnergyMaterialNoMass
from honeybee_energy.construction.opaque import OpaqueConstruction
from honeybee_energy.material.glazing import EnergyWindowMaterialSimpleGlazSys
from honeybee_energy.construction.window import WindowConstruction
from honeybee_energy.constructionset import ConstructionSet
from honeybee_energy.schedule.ruleset import ScheduleRuleset
from honeybee_energy.load.people import People
from honeybee_energy.load.lighting import Lighting
from honeybee_energy.load.equipment import ElectricEquipment, GasEquipment
from honeybee_energy.load.ventilation import Ventilation
from honeybee_energy.load.infiltration import Infiltration
from honeybee_energy.load.exhaust import ExhaustAir
from honeybee_energy.load.setpoint import Setpoint
from honeybee_energy.programtype import ProgramType
from honeybee_energy.lib.scheduletypelimits import temperature, activity_level

from .util import transmissivity_from_transmittance

area_dt = Area()
conductivity_dt = Conductivity()
density_dt = Density()
distance_dt = Distance()
power_dt = Power()
flux_dt = EnergyFlux()
flow_dt = VolumeFlowRate()
flow_int_dt = VolumeFlowRateIntensity()
temp_dt = Temperature()
specific_heat_capacity_dt = SpecificHeatCapacity()
rvalue_dt = RValue()
uvalue_dt = UValue()


"""____________TRANSLATORS TO EXP____________"""


def people_to_exp(people, si_units=False):
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
        f'People;{description};1;{people_amount:.1f};{amount_unit_code};'
        f'{sensible_ppl:.0f};{load_unit_code};{latent_ppl:.0f};{load_unit_code};{radiant_pct:.0f};'
    )
    return exp_line


def lighting_to_exp(lighting, fixture_type='SUSFLUOR'):
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
        f'Lighting;{description};1;{fixture_type};{plenum_pct:.0f};1;'
        f'{radiant_pct:.0f};{visible_pct:.0f};'
    )
    return exp_line


def equipment_to_exp(equipment, si_units=False, watts_per_area=None):
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
        f'Miscellaneous;{description};1;{energy_value:.2f};{misc_unit_code};{sensible_pct:.0f};'
        f'{room_pct:.0f};{plenum_pct:.0f};{radiant_pct:.0f};{meter_code};{air_path};'
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
        f"{template_name};{ppl_type};Cooling Only (Design);{ppl_amount:.1f};{ppl_amount_unit};"
        f"{sensible_watts:.0f};{ppl_load_unit};{latent_watts:.0f};{ppl_load_unit};"
        f"{ltg_type};Cooling Only (Design);{ltg_lpd:.2f};{ltg_unit};"
        f"{misc_type};Cooling Only (Design);{misc_energy:.2f};{misc_unit};"
        f"{energy_meter};{field_19};{field_20};"
    )
    return exp_line


def program_to_trace700_airflow_template(
    program, si_units=False, ventilation_method='Sum of Outdoor Air'
):
    """Get a TRACE 700 "T.AirflowTemplate" entry string from a Honeybee ProgramType.

    Args:
        program: A Honeybee ProgramType object.
        si_units: Boolean to note whether the units of the values in the resulting
            matrix are in SI (True) instead of IP (False). (Default: False).
        ventilation_method: Optional text for the ventilation method to be used in the
            airflow template. Choose from the following.

            * Sum of Outdoor Air
            * ASHRAE 62.1

    Returns:
        A text string for a TRACE 700 T.AirflowTemplate entry.
    """
    blank_val = '9999.99'
    template_name = program.display_name

    # Fields 4-7 (Ventilation Layout)
    vent = program.ventilation
    vent_flow_unit = 'L/s' if si_units else 'cfm'
    vent_unit = 6 if si_units else 3  # 6 = L/s/sq m, 3 = cfm/sq ft
    ppl_unit = 7 if si_units else 2  # 7 = L/s/person m, 2 = cfm/person

    vent_val, ppl, ez_cool, ez_heat = 0, 0, 100, 100
    if vent is not None and ventilation_method == 'ASHRAE 62.1':
        vent_val = flow_dt.to_unit([vent.flow_per_area], vent_flow_unit, 'm3/s')[0]
        vent_val = vent_val if si_units else vent_val * 10.7639104  # convert to cfm/ft2
        ppl = flow_dt.to_unit([vent.flow_per_person], vent_flow_unit, 'm3/s')[0]
        ez_cool = int(vent.effectiveness_cooling * 100)
        ez_cool = 100 if ez_cool > 100 else ez_cool
        ez_heat = int(vent.effectiveness_heating * 100)
        ez_heat = 100 if ez_heat > 100 else ez_heat

    # Fields 25-26 (Exhaust Air Layout)
    exhaust = program.exhaust
    ea_unit = 10 if si_units else 4  # 10 = L/s, 4 = cfm
    ea_val = 0
    if exhaust is not None:
        if exhaust.flow_per_area != 0:
            ea_unit = 14 if si_units else 8  # 14 = L/s/sq m, 8 = cfm/sq ft
            ea_val = exhaust.flow_per_area_si if si_units else exhaust.flow_per_area_ip
            ea_val = round(ea_val, 3)
        elif exhaust.flow_per_fixture != 0:
            ea_val = exhaust.flow_per_fixture_si if si_units else exhaust.flow_per_fixture_ip
            ea_val = round(ea_val * exhaust.fixture_count)

    # Fields 8-13 (Infiltration Layout)
    inf = program.infiltration
    inf_unit = 5 if si_units else 3  # 5 = L/s/sq m, 3 = cfm/sq ft

    inf_val = 0
    if inf is not None:
        inf_val = inf.flow_per_exterior_area_si if si_units else inf.flow_per_exterior_area_ip

    if ventilation_method == 'ASHRAE 62.1':
        exp_line = (
            f"{template_name};Default Std62;Available (100%);{ppl:.3f};{ppl_unit};{vent_val:.3f};{vent_unit};"
            f"None;Available (100%);{inf_val:.3f};{inf_unit};{inf_val:.3f};{inf_unit};"
            f"{blank_val};0;Available (100%);{blank_val};8;{blank_val};9;{blank_val};10;{blank_val};10;"
            f"{ea_val};{ea_unit};Available (100%);"
            f"1;0;{ez_cool};0;{ez_heat};1;{blank_val};{blank_val};0;0;{blank_val};0;"
        )
    else:
        exp_line = (
            f"{template_name};None;Available (100%);{vent_val:.3f};{vent_unit};{vent_val:.3f};{vent_unit};"
            f"None;Available (100%);{inf_val:.3f};{inf_unit};{inf_val:.3f};{inf_unit};"
            f"{blank_val};0;Available (100%);{blank_val};8;{blank_val};9;{blank_val};10;{blank_val};10;"
            f"{ea_val};{ea_unit};Available (100%);0;0;"
            f"{blank_val};0;{blank_val};1;{blank_val};{blank_val};0;0;{blank_val};0;"
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
            people_to_exp(program.people, si_units)
        ])
    if program.lighting:
        standalone_blocks.extend([
            'T.LOAD_LIGHTS',
            lighting_to_exp(program.lighting)
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
                equipment_to_exp(eq_obj, si_units, watts_per_area=combined_lpd)
            ])

    internal_load_template = program_to_trace700_internal_load_template(program, si_units)
    standalone_blocks.extend([
        'T.InternalLoadTemplate',
        internal_load_template
    ])

    file_data = newline.join(standalone_blocks) + newline
    return file_data


def airflow_to_exp(program, si_units=False, ventilation_method='Sum of Outdoor Air'):
    """Get an EXP string containing only the airflow template for a ProgramType.

    Args:
        program: A Honeybee ProgramType object.
        si_units: Boolean to note whether the units of the values in the resulting
            matrix are in SI (True) instead of IP (False). (Default: False).
        ventilation_method: Optional text for the ventilation method to be used in the
            airflow template. Choose from the following.

            * Sum of Outdoor Air
            * ASHRAE 62.1

    Returns:
        Text string of an EXP file for TRACE 700 containing the airflow template.
    """
    newline = '\n'

    airflow_template = program_to_trace700_airflow_template(
        program, si_units, ventilation_method
    )

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


def program_to_exp(program, si_units=False, ventilation_method='Sum of Outdoor Air'):
    """Get a complete EXP string for a Honeybee ProgramType.

    Args:
        program: A Honeybee ProgramType object for which the TRACE 700 EXP string
            will be generated.
        si_units: Boolean to note whether the units of the values in the resulting
            matrix are in SI (True) instead of IP (False). (Default: False).
        ventilation_method: Optional text for the ventilation method to be used in the
            airflow template. Choose from the following.

            * Sum of Outdoor Air
            * ASHRAE 62.1

    Returns:
        Text string of a complete EXP file for TRACE 700.
    """
    newline = '\n'
    standalone_blocks = ['EDITORSv6.3.1']

    if program.people:
        standalone_blocks.extend([
            'T.LOAD_PEOPLE',
            people_to_exp(program.people, si_units)
        ])

    if program.lighting:
        standalone_blocks.extend([
            'T.LOAD_LIGHTS',
            lighting_to_exp(program.lighting)
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
                equipment_to_exp(eq_obj, si_units, watts_per_area=combined_lpd)
            ])

    internal_load_template = program_to_trace700_internal_load_template(program, si_units)
    airflow_template = program_to_trace700_airflow_template(program, si_units, ventilation_method)
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


def programs_to_exp(programs, si_units=False, ventilation_method='Sum of Outdoor Air'):
    """Get a single combined EXP string for a list of Honeybee ProgramTypes.

    Args:
        programs: A list of Honeybee ProgramType objects.
        si_units: Boolean to note whether the units of the values in the resulting
            matrix are in SI (True) instead of IP (False). (Default: False).
        ventilation_method: Optional text for the ventilation method to be used in the
            airflow template. Choose from the following.

            * Sum of Outdoor Air
            * ASHRAE 62.1

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
            people_templates.append(people_to_exp(program.people, si_units))
            seen_people.add(program.people.identifier)

        if program.lighting and program.lighting.identifier not in seen_lighting:
            lighting_templates.append(lighting_to_exp(program.lighting))
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
                        equipment_to_exp(
                            eq_obj, si_units=si_units, watts_per_area=combined_lpd
                        )
                    )
                    seen_equip.add(eq_obj.identifier)

        internal_load_templates.append(
            program_to_trace700_internal_load_template(program, si_units)
        )
        airflow_templates.append(
            program_to_trace700_airflow_template(program, si_units, ventilation_method)
        )
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


def material_to_exp(material, si_units=False, id=999):
    """Converts a Honeybee EnergyMaterial or EnergyMaterialNoMass to a T.MATR_MATERIAL entry."""
    description = readable_short_name(material.display_name, max_length=40)
    material_id = f'M{id}' if not str(id).startswith('M') else str(id)

    thickness_unit = 'm' if si_units else 'in'
    thickness_code = 2 if si_units else 1

    conductivity_unit = 'W/m-K' if si_units else 'Btu/h-ft-F'
    conductivity_code = 0 if si_units else 1

    density_unit = 'kg/m3' if si_units else 'lb/ft3'
    density_code = 1 if si_units else 0

    specific_heat_unit = 'kJ/kg-K' if si_units else 'Btu/lb-F'
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


def opaque_construction_to_exp(
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
            mat_line = material_to_exp(mat, si_units=si_units, id=id_counter)
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


def window_construction_to_exp(construction, si_units=False, is_door=False):
    """Converts a Honeybee WindowConstruction object to a T.GLAS_GLASS entry."""
    description = construction.display_name
    if is_door and not description.lower().endswith('door'):
        description = f'{description} Door'
    description = readable_short_name(description, max_length=40)

    # get the summertime U-Value
    u_value_unit = 'W/m2-K' if si_units else 'Btu/h-ft2-F'
    if isinstance(construction, OpaqueConstruction):  # same between winter and summer
        u_factor = construction.u_factor
    else:  # get the U-Value specifically for summertime
        u_factor = construction.u_factor_summer
    u_value = uvalue_dt.to_unit([u_factor], u_value_unit, 'W/m2-K')[0]
    u_value_code = 0 if si_units else 1

    # get shading coefficient
    # defined as the ratio of solar heat compared to a standard 3mm clear float glass
    sc = getattr(construction, 'shading_coefficient', 0.0)

    # get the solar and optical properties
    # TRACE asks for hemispherical transmissivity, which is challenging to compute
    # we will use transmittance at normal incidence in the hope that
    # transmissivity is higher than transmittance and this will cancel out the
    # fact that hemispherical values are lower than those at normal incidence
    vt = getattr(construction, 'visible_transmittance', 0.5)
    panes = getattr(construction, 'glazing_count', 1)
    inside_vis_refl = construction.inside_solar_reflectance
    inside_sol_refl = construction.inside_solar_reflectance
    solar_transmittance = getattr(construction, 'solar_transmittance', 0.0)
    solar_transmissivity = transmissivity_from_transmittance(solar_transmittance)

    # get the emissivity of the inside and outside
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
        f'{description};Glass;1;{sc:.6f};{u_value:.6f};{u_value_code};{panes};0;'
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

    # resolve door construction priority
    if getattr(construction_set.door_set, '_exterior_construction', None) is not None:
        door_cnst = construction_set.door_set.exterior_construction
    elif getattr(construction_set.door_set, '_exterior_glass_construction', None) is not None:
        door_cnst = construction_set.door_set.exterior_glass_construction
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
            line, mat_lines = opaque_construction_to_exp(
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
                line = window_construction_to_exp(cnst, si_units=si_units, is_door=is_door)
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

        d_ovh = _process_glass(c_set.door_set.overhead_construction, is_door=True)
        if d_ovh:
            glass_templates.append(d_ovh)

        d_int = _process_glass(c_set.door_set.interior_construction, is_door=True)
        if d_int:
            glass_templates.append(d_int)

        d_int_gls = _process_glass(c_set.door_set.interior_glass_construction, is_door=True)
        if d_int_gls:
            glass_templates.append(d_int_gls)

        d_ext_gls = _process_glass(c_set.door_set.exterior_glass_construction, is_door=True)
        if d_ext_gls:
            glass_templates.append(d_ext_gls)

        d_ext = _process_glass(c_set.door_set.exterior_construction, is_door=True)
        if d_ext:
            glass_templates.append(d_ext)

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


"""____________TRANSLATORS FROM EXP____________"""


def internal_loads_from_exp(exp_str):
    """Get Honeybee People, Lighting and Equipment from a TRACE 700 InternalLoadTemplate.

    Args:
        exp_str: A TRACE 700 InternalLoadTemplate entry string.

    Returns:
        A tuple with three elements.

        -   people: A Honeybee People object if people are non-zero and defined
            per floor area. None otherwise.

        -   lighting: A Honeybee Lighting object if lights are non-zero and defined
            per floor area. None otherwise.

        -   equipment: A Honeybee ElectricEquipment or GasEquipment object if
            miscellaneous loads are non-zero and defined per floor area. None otherwise.
    """
    # deconstruct the string and get the identifiers
    exp_vals = exp_str.split(';')
    load_id = clean_ep_string(exp_vals[0])
    people_id = clean_ep_string(exp_vals[1]) \
        if exp_vals[1] != 'None' else '{} People'.format(load_id)
    lights_id = clean_ep_string(exp_vals[9]) \
        if exp_vals[9] != 'None' else '{} Lighting'.format(load_id)
    equip_id = clean_ep_string(exp_vals[13]) \
        if exp_vals[13] != 'None' else '{} Equipment'.format(load_id)

    # process the people
    people = None
    ppl_val, ppl_unit = float(exp_vals[3]), int(exp_vals[4])
    if ppl_val != 0 and ppl_unit in (1, 2):
        if ppl_unit == 1:
            ppl_val = area_dt.to_unit([ppl_val], 'm2', 'ft2')[0]
        people = People(people_id, 1 / ppl_val)
        sens_val, sens_unit = float(exp_vals[5]), int(exp_vals[6])
        lat_val, lat_unit = float(exp_vals[7]), int(exp_vals[8])
        if sens_unit in (7, 8) and sens_unit == lat_unit:
            total = sens_val + lat_val
            latent_fraction = lat_val / total
            act_unit = 'Btu/h' if sens_unit == 7 else 'W'
            sch_id = 'People Activity - {} [{}]'.format(total, act_unit)
            if sens_unit == 7:
                total = power_dt.to_unit([total], 'W', 'Btu/h')[0]
            people.activity_schedule = \
                ScheduleRuleset.from_constant_value(sch_id, total, activity_level)
            people.latent_fraction = latent_fraction

    # process the lighting
    lighting = None
    lgt_val, lgt_unit = float(exp_vals[11]), int(exp_vals[12])
    if lgt_val != 0 and lgt_unit in (1, 3, 4):
        if lgt_unit == 1:
            lgt_val = flux_dt.to_unit([lgt_val], 'W/m2', 'Btu/h-ft2')[0]
        elif lgt_unit == 3:
            lgt_val = flux_dt.to_unit([lgt_val], 'W/m2', 'W/ft2')[0]
        lighting = Lighting(lights_id, lgt_val)

    # process the miscellaneous loafs
    equipment = None
    equip_val, equip_unit = float(exp_vals[15]), int(exp_vals[16])
    if equip_val != 0 and equip_unit in (1, 8, 9):
        equip_type = int(exp_vals[17])
        if equip_unit == 1:
            equip_val = flux_dt.to_unit([equip_val], 'W/m2', 'Btu/h-ft2')[0]
        elif equip_unit == 8:
            equip_val = flux_dt.to_unit([equip_val], 'W/m2', 'W/ft2')[0]
        if equip_type == 2:
            equipment = GasEquipment(equip_id, equip_val)
        else:
            equipment = ElectricEquipment(equip_id, equip_val)

    return people, lighting, equipment


def airflow_from_exp(exp_str):
    """"Get Infiltration, Ventilation and ExhaustAir from TRACE 700 AirflowTemplate.

    Args:
        exp_str: A TRACE 700 AirflowTemplate entry string.

    Returns:
        A tuple with three elements.

        -   infiltration: A Honeybee Infiltration object if the infiltration is
            non-zero and defined per exterior area. None otherwise.

        -   ventilation: A Honeybee Ventilation object if ventilation is non-zero
            and is either "Sum of Outdoor Air" or "ASHRAE 62.1." None otherwise.

        -   exhaust: A Honeybee ExhaustAir object if exhaust air is non-zero and
            defined per floor area or as an absolute flow rate. None otherwise.
    """
    blank_val = '9999.99'
    # deconstruct the string and get the identifier
    exp_vals = exp_str.split(';')
    airflow_id = clean_ep_string(exp_vals[0])
    vent_id = clean_ep_string(exp_vals[1]) \
        if exp_vals[1] != 'None' else '{} Ventilation'.format(airflow_id)
    inf_id = clean_ep_string(exp_vals[7]) \
        if exp_vals[7] != 'None' else '{} Infiltration'.format(airflow_id)
    exhaust_id = '{} ExhaustAir'.format(airflow_id)

    # process the ventilation
    ventilation = None
    vent_method = exp_vals[27]
    if vent_method == 0:  # Sum of Outdoor Air
        v_cool_unit, v_heat_unit = int(exp_vals[4]), int(exp_vals[6])
        vc_val, vh_val = float(exp_vals[3]), float(exp_vals[5])
        if vc_val != 0 and vh_val != 0 and v_cool_unit != 4:
            ventilation = Ventilation(vent_id)
            if v_cool_unit == 0:  # ACH
                ventilation.air_changes_per_hour = vc_val
            elif v_cool_unit == 1:  # cfm
                vc_val = flow_dt.to_unit([vc_val], 'm3/s', 'cfm')[0]
                ventilation.flow_per_zone = vc_val
            elif v_cool_unit == 2:  # cfm/person
                vc_val = flow_dt.to_unit([vc_val], 'm3/s', 'cfm')[0]
                ventilation.flow_per_person = vc_val
            elif v_cool_unit == 3:  # cfm/ft2
                vc_val = flow_int_dt.to_unit([vc_val], 'm3/s-m2', 'cfm/ft2')[0]
                ventilation.flow_per_area = vc_val
            elif v_cool_unit == 5:  # L/s
                vc_val = flow_dt.to_unit([vc_val], 'm3/s', 'L/s')[0]
                ventilation.flow_per_zone = vc_val
            elif v_cool_unit == 6:  # L/s-m2
                vc_val = flow_int_dt.to_unit([vc_val], 'm3/s-m2', 'L/s-m2')[0]
                ventilation.flow_per_area = vc_val
            elif v_cool_unit == 7:  # L/s-person
                vc_val = flow_dt.to_unit([vc_val], 'm3/s', 'L/s')[0]
                ventilation.flow_per_person = vc_val
            if v_cool_unit == v_heat_unit:
                ventilation.effectiveness_heating = round(vc_val / vh_val, 3)
    elif vent_method == 1:  # ASHRAE 62.1
        ppl_unit, area_unit = int(exp_vals[4]), int(exp_vals[6])
        ppl_val, area_val = float(exp_vals[3]), float(exp_vals[5])
        if (ppl_val != 0 or area_val != 0) and ppl_unit in (2, 7) and area_unit in (3, 6):
            ventilation = Ventilation(vent_id)
            if ppl_unit == 2:  # cfm/person
                ppl_val = flow_dt.to_unit([ppl_val], 'm3/s', 'cfm')[0]
            else:
                ppl_val = flow_dt.to_unit([ppl_val], 'm3/s', 'L/s')[0]
            ventilation.flow_per_person = ppl_val
            if area_unit == 3:  # cfm/ft2
                area_val = flow_int_dt.to_unit([area_val], 'm3/s-m2', 'cfm/ft2')[0]
            else:
                area_val = flow_int_dt.to_unit([area_val], 'm3/s-m2', 'L/s-m2')[0]
            ventilation.flow_per_area = area_val
            if exp_vals[29] != blank_val and float(exp_vals[29]) != 100:
                ventilation.effectiveness_cooling = float(exp_vals[29]) / 100
            if exp_vals[31] != blank_val and float(exp_vals[31]) != 100:
                ventilation.effectiveness_heating = float(exp_vals[31]) / 100
            if int(exp_vals[32]) != 1 and exp_vals[33] != blank_val:
                ventilation.secondary_recirculation = float(exp_vals[33]) / 100

    # process the infiltration
    infiltration = None
    inf_val, inf_unit = float(exp_vals[9]), int(exp_vals[10])
    if inf_val != 0 and inf_unit in (3, 5):
        if inf_unit == 3:  # cfm/ft2
            inf_val = flow_int_dt.to_unit([inf_val], 'm3/s-m2', 'cfm/ft2')[0]
        else:
            inf_val = flow_int_dt.to_unit([inf_val], 'm3/s-m2', 'L/s-m2')[0]
        infiltration = Infiltration(inf_id, inf_val)

    # process the exhaust air
    exhaust = None
    ea_val, ea_unit = float(exp_vals[24]), int(exp_vals[25])
    if ea_val != 0 and ea_unit in (4, 5, 8, 9, 10, 11, 14, 15):
        exhaust = ExhaustAir(exhaust_id)
        if ea_unit in (4, 5):  # cfm
            ea_val = flow_dt.to_unit([ea_val], 'm3/s', 'cfm')[0]
            exhaust.flow_per_fixture = ea_val
        elif ea_unit in (8, 9):  # cfm/ft2
            ea_val = flow_int_dt.to_unit([ea_val], 'm3/s-m2', 'cfm/ft2')[0]
            exhaust.flow_per_area = ea_val
        elif ea_unit in (10, 11):  # L/s
            ea_val = flow_dt.to_unit([ea_val], 'm3/s', 'L/s')[0]
            exhaust.flow_per_fixture = ea_val
        else:  # L/s-m2
            ea_val = flow_int_dt.to_unit([ea_val], 'm3/s-m2', 'L/s-m2')[0]
            exhaust.flow_per_area = ea_val

    return infiltration, ventilation, exhaust


def setpoint_from_exp(exp_str):
    """Get a Honeybee Setpoint from a TRACE 700 ThermostatTemplate.

    Args:
        exp_str: A TRACE 700 ThermostatTemplate entry string.

    Returns:
        A Honeybee Setpoint object.
    """
    # deconstruct the string and get the identifier
    exp_vals = exp_str.split(';')
    set_id = clean_ep_string(exp_vals[0])

    # process the thermostat setpoints
    setpoint = None
    clg_set, htg_set = float(exp_vals[1]), float(exp_vals[3])
    c_set_unit, h_set_unit = int(exp_vals[2]), int(exp_vals[4])
    if clg_set >= htg_set:
        if c_set_unit == 1:  # F
            clg_set = temp_dt.to_unit([clg_set], 'C', 'F')[0]
        if h_set_unit == 1:  # F
            htg_set = temp_dt.to_unit([htg_set], 'C', 'F')[0]
        heat_sch = ScheduleRuleset.from_constant_value(
            '{} Heating Setpoint'.format(set_id), htg_set, temperature
        )
        cool_sch = ScheduleRuleset.from_constant_value(
            '{} Cooling Setpoint'.format(set_id), clg_set, temperature
        )
        setpoint = Setpoint(set_id, heat_sch, cool_sch)

    return setpoint


def program_from_exp(room_exp_str, internal_loads, airflows, setpoints):
    """Get a complete Honeybee ProgramType from the EXP string of a RoomTemplate.

    Args:
        exp_str: A TRACE 700 RoomTemplate entry string.
        internal_loads: A dictionary of Honeybee internal loads objects with the
            identifiers of the TRACE 700 InternalLoadTemplate as keys and
            tuples of 3 Honeybee load objects as values (people, lighting, equipment).
        airflows: A dictionary of Honeybee airflow objects with the identifiers
            of the TRACE 700 AirflowTemplate as keys and tuples of 3
            airflow objects as values (infiltration, ventilation, exhaust).
        setpoints: A dictionary of Honeybee Setpoint objects with the identifiers
            of the TRACE 700 ThermostatTemplate as keys and Honeybee Setpoint
            objects as values.

    Returns:
        A Honeybee ProgramType object from the RoomTemplate string.
    """
    # deconstruct the string and get the identifier
    exp_vals = room_exp_str.split(';')
    program = ProgramType(clean_ep_string(exp_vals[0]))
    def_templates = ('Default', 'Metric Default')
    msg_t = 'Failed to find {} "{}" in the EXP file.'

    # get the internal loads
    if exp_vals[1] not in def_templates:
        try:
            people, lighting, equipment = internal_loads[exp_vals[1]]
            program.people = people
            program.lighting = lighting
            if isinstance(equipment, ElectricEquipment):
                program.electric_equipment = equipment
            elif isinstance(equipment, GasEquipment):
                program.gas_equipment = equipment
        except KeyError:
            raise ValueError(msg_t.format('InternalLoadTemplate', exp_vals[1]))

    # get the airflows
    if exp_vals[2] not in def_templates:
        try:
            infiltration, ventilation, exhaust = airflows[exp_vals[2]]
            program.infiltration = infiltration
            program.ventilation = ventilation
            program.exhaust = exhaust
        except KeyError:
            raise ValueError(msg_t.format('AirflowTemplate', exp_vals[2]))

    # get the setpoint
    if exp_vals[3] not in def_templates:
        try:
            program.setpoint = setpoints[exp_vals[3]]
        except KeyError:
            raise ValueError(msg_t.format('ThermostatTemplate', exp_vals[3]))

    return program


def programs_from_exp(exp_file_content):
    """Get a list of Honeybee ProgramTypes from the content of an EXP file.

    Args:
        exp_file_content: Text string for the contents of an EXP file.

    Returns:
        A list of Honeybee ProgramTypes.
    """
    # load the individual templates from the file contents
    file_lines = exp_file_content.split('\n')
    internal_loads, airflows, setpoints = {}, {}, {}
    loads_section, airflows_section, setpoints_section = False, False, False
    for line in file_lines:
        if line.startswith('T.InternalLoadTemplate'):
            loads_section, airflows_section, setpoints_section = True, False, False
            continue
        elif line.startswith('T.AirflowTemplate'):
            loads_section, airflows_section, setpoints_section = False, True, False
            continue
        elif line.startswith('T.ThermostatTemplate'):
            loads_section, airflows_section, setpoints_section = False, False, True
            continue
        elif line.startswith('T.'):
            loads_section, airflows_section, setpoints_section = False, False, False

        if loads_section:
            internal_loads[line.split(';')[0]] = internal_loads_from_exp(line)
        elif airflows_section:
            airflows[line.split(';')[0]] = airflow_from_exp(line)
        elif setpoints_section:
            setpoints[line.split(';')[0]] = setpoint_from_exp(line)

    # create the individual programs from the templates
    programs = []
    programs_section = False
    for line in file_lines:
        if line.startswith('T.RoomTemplate'):
            programs_section = True
            continue
        elif programs_section and len(line.split(';')) != 6:
            programs_section = False
        if programs_section:
            programs.append(program_from_exp(line, internal_loads, airflows, setpoints))

    return programs


def material_from_exp(exp_str):
    """Get an EnergyMaterial or EnergyMaterialNoMass from a TRACE 700 MATR_MATERIAL.

    Args:
        exp_str: A TRACE 700 MATR_MATERIAL entry string.

    Returns:
        A Honeybee EnergyMaterial or EnergyMaterialNoMass object.
    """
    # deconstruct the string and get the identifier
    exp_vals = exp_str.split(';')
    mat_id = clean_ep_string(exp_vals[1])

    # first check if the material has no mass
    r_value, r_unit = float(exp_vals[12]), int(exp_vals[13])
    if r_value != 0:
        if r_unit == 1:
            r_value = rvalue_dt.to_unit([r_value], 'm2-K/W', 'h-ft2-F/Btu')[0]
        return EnergyMaterialNoMass(mat_id, r_value)

    # it is a material with mass
    # get the thickness and convert it to the correct units
    thickness, t_unit = float(exp_vals[4]), int(exp_vals[5])
    if t_unit == 0:
        thickness = distance_dt.to_unit([thickness], 'm', 'ft')[0]
    elif t_unit == 1:
        thickness = distance_dt.to_unit([thickness], 'm', 'in')[0]
    elif t_unit == 3:
        thickness = distance_dt.to_unit([thickness], 'm', 'cm')[0]
    elif t_unit == 4:
        thickness = distance_dt.to_unit([thickness], 'm', 'mm')[0]

    # get the conductivity and convert it to the correct units
    conductivity, c_unit = float(exp_vals[6]), int(exp_vals[7])
    if c_unit == 1:
        conductivity = conductivity_dt.to_unit([conductivity], 'W/m-K', 'Btu/h-ft-F')[0]

    # get the density and convert it to the correct units
    density, d_unit = float(exp_vals[8]), int(exp_vals[9])
    if d_unit == 0:
        density = density_dt.to_unit([density], 'kg/m3', 'lb/ft3')[0]
    elif d_unit == 2:
        density = density_dt.to_unit([density], 'kg/m3', 'g/cm3')[0]

    # get the specific_heat and convert it to the correct units
    sht, s_unit = float(exp_vals[10]), int(exp_vals[11])
    if s_unit == 1:
        sht = specific_heat_capacity_dt.to_unit([sht], 'J/kg-K', 'Btu/lb-F')[0]
    elif s_unit == 0:
        sht = specific_heat_capacity_dt.to_unit([sht], 'J/kg-K', 'kJ/kg-K')[0]

    return EnergyMaterial(mat_id, thickness, conductivity, density, sht)


def opaque_construction_from_exp(exp_str, materials):
    """Get an OpaqueConstruction from a TRACE 700 CNST_WALL, CNST_ROOF, CNST_FLOOR, etc.

    Args:
        exp_str: A TRACE 700 CNST_WALL, CNST_ROOF, CNST_FLOOR, CNST_EXFLOOR,
            or CNST_PART entry string.
        materials: A dictionary with identifiers of materials as keys and Python
            material objects as values.

    Returns:
        A Honeybee OpaqueConstruction object.
    """
    # deconstruct the string and get the identifier
    exp_vals = exp_str.split(';')
    con_id = clean_ep_string(exp_vals[1])

    # collect all of the material layers
    mat_layers = []
    for mat_id in exp_vals[4:14]:
        if mat_id != 'None':
            mat_layers.append(materials[mat_id])

    # get the exterior and interior layers
    ext_mat = mat_layers[0]
    int_mat = mat_layers[-1]
    ext_mat.unlock()
    int_mat.unlock()

    # assign the properties of solar and visible absorption
    int_mat.solar_absorptance = float(exp_vals[51])
    int_mat.visible_reflectance = float(exp_vals[53])
    ext_mat.solar_absorptance = float(exp_vals[39])

    # assign the properties of infrared absorption
    int_mat.thermal_absorptance = float(exp_vals[52])
    ext_mat.thermal_absorptance = float(exp_vals[50])

    # assign the exterior roughness
    roughness_map = {
        0: 'VeryRough', 1: 'Rough', 2: 'MediumRough', 3: 'MediumSmooth',
        4: 'Smooth', 5: 'VerySmooth'
    }
    ext_mat.roughness = roughness_map[int(exp_vals[55])]

    return OpaqueConstruction(con_id, mat_layers)


def window_construction_from_exp(exp_str):
    """Get a WindowConstruction (or OpaqueConstruction) from a TRACE 700 GLAS_GLASS.

    Args:
        exp_str: A TRACE 700 GLAS_GLASS entry string.

    Returns:
        A Honeybee WindowConstruction object (or an OpaqueConstruction object if
        the GLAS_GLASS refers to a door construciton with zero solar transmittance).
    """
    # deconstruct the string and get the critical properties
    exp_vals = exp_str.split(';')
    con_id = clean_ep_string(exp_vals[1])
    mat_id = '{} Material'.format(con_id)
    u_factor, u_unit = float(exp_vals[4]), int(exp_vals[5])
    if u_unit == 1:
        u_factor = uvalue_dt.to_unit([u_factor], 'W/m2-K', 'Btu/h-ft2-F')[0]
    sc = float(exp_vals[3])
    is_door = int(exp_vals[178])

    # sense whether we will be returning an OpaqueConstruction for a door
    if is_door == 2 and sc == 0:  # it's an opaque construction
        r_val = 1 / u_factor
        _ext_r = 1 / OpaqueConstruction.out_h_simple()  # exterior heat coefficient in m2-K/W
        _int_r = 1 / OpaqueConstruction.in_h_simple()  # interior film
        r_val = r_val - _ext_r - _int_r
        r_val = 0.001 if r_val < 0.001 else r_val  # odd assumption about air films
        door_mat = EnergyMaterialNoMass(mat_id, r_val)
        door_mat.thermal_absorptance = float(exp_vals[12])
        door_mat.solar_reflectance = float(exp_vals[11])
        door_mat.visible_reflectance = float(exp_vals[9])
        return OpaqueConstruction(con_id, [door_mat])

    # create a simple galzing material from the proeprties
    shgc = sc * 0.87  # convert from SC to SHGC
    win_mat = EnergyWindowMaterialSimpleGlazSys(mat_id, u_factor, shgc)
    win_mat.vt = float(exp_vals[9])
    return WindowConstruction(con_id, [win_mat])


def construction_set_from_exp(exp_str, constructions):
    """Get a ConstructionSet from a TRACE 700 ConstructionTemplate.

    Args:
        exp_str: A TRACE 700 ConstructionTemplate entry string.
        constructions: A dictionary with identifiers of constructions as keys
            and Pythonconstruction objects as values.

    Returns:
        A Honeybee ConstructionSet object.
    """
    # deconstruct the string and create a base ConstructionSet with defaults
    exp_vals = exp_str.split(';')
    cs_id = clean_ep_string(exp_vals[0])
    con_set = ConstructionSet(cs_id)

    # get all of the standard constructions
    con_set.floor_set.ground_construction = constructions[exp_vals[1]]
    con_set.floor_set.exterior_construction = constructions[exp_vals[1]]
    con_set.roof_ceiling_set.exterior_construction = constructions[exp_vals[4]]
    con_set.aperture_set.skylight_construction = constructions[exp_vals[7]]
    con_set.wall_set.exterior_construction = constructions[exp_vals[11]]
    con_set.aperture_set.window_construction = constructions[exp_vals[14]]
    con_set.aperture_set.operable_construction = constructions[exp_vals[14]]
    con_set.wall_set.interior_construction = constructions[exp_vals[18]]

    # assign the door construction depending on whether its glass or not
    door_con = constructions[exp_vals[21]]
    if isinstance(door_con, OpaqueConstruction):
        con_set.door_set.exterior_construction = door_con
    else:
        con_set.door_set.exterior_glass_construction = door_con

    return con_set


def construction_set_from_exp(exp_file_content):
    """Get a list of Honeybee ConstructionSet from the content of an EXP file.

    Args:
        exp_file_content: Text string for the contents of an EXP file.

    Returns:
        A tuple with three elements.

        -   materials: A list of Honeybee materials.

        -   constructions: A list of Honeybee OpaqueConstructions and WindowConstructions.

        -   construction_sets: A list of Honeybee ConstructionSets.
    """
    file_lines = exp_file_content.split('\n')

    # load the individual materials from the file contents
    materials, mat_section = {}, False
    for line in file_lines:
        if line.startswith('T.MATR_MATERIAL'):
            mat_section = True
            continue
        elif line.startswith('T.'):
            mat_section = False
        if mat_section:
            materials[line.split(';')[1]] = material_from_exp(line)

    # load the individual opaque constructions from the file contents
    con_types = ('T.CNST_EXFLOOR', 'T.CNST_FLOOR', 'T.CNST_PART', 'T.CNST_ROOF', 'T.CNST_WALL')
    constructions, con_section = {}, False
    for line in file_lines:
        if any(line.startswith(ct) for ct in con_types):
            con_section = True
            continue
        elif line.startswith('T.'):
            con_section = False
        if con_section:
            constructions[line.split(';')[1]] = opaque_construction_from_exp(line, materials)

    # load the individual window constructions from the file contents
    w_con_section = False
    for line in file_lines:
        if line.startswith('T.GLAS_GLASS'):
            w_con_section = True
            continue
        elif line.startswith('T.'):
            w_con_section = False
        if w_con_section:
            w_con = window_construction_from_exp(line)
            constructions[line.split(';')[0]] = w_con
            for mat in w_con.materials:
                materials[mat.identifier] = mat

    # create the construction sets
    construction_sets = []

    return list(materials.values), list(constructions.values()), construction_sets
