"""dragonfly trace translation commands."""
import click
import sys
import logging
import io
import base64

from ladybug.commandutil import process_content_to_output
from dragonfly.model import Model
from dragonfly_trace.writer import model_to_trace700_csv as model_to_csv
from dragonfly_trace.writer import model_to_trace700_workbook as model_to_workbook
from dragonfly_trace.writer import model_to_trace700_gbxml as model_to_gbxml
from dragonfly_trace.writer import model_to_exp, model_to_trace700_zip_bytes


_logger = logging.getLogger(__name__)


@click.group(help='Commands for translating URBANopt systems to OSM/IDF.')
def translate():
    pass


@translate.command('model-to-trace700-csv')
@click.argument('model-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('--imperial/--metric', '-ip/-si', help='Flag to note whether imperial '
              'or metric units should be used for values in the output CSV.',
              default=True, show_default=True)
@click.option('--ventilation-method', '-v', help='Text for the ventilation method to be '
              'used to calculate outdoor air. Choose from: Sum of Outdoor Air, ASHRAE 62.1',
              type=str, default='Sum of Outdoor Air', show_default=True)
@click.option('--multiplier/--full-geometry', ' /-fg', help='Flag to note if the '
              'multipliers on each Building story will be passed along to the '
              'generated Honeybee Room objects or if full geometry objects should be '
              'written for each story in the building.', default=True, show_default=True)
@click.option('--plenum/--separate-plenum', '-p/-sp', help='Flag to indicate whether '
              'ceiling/floor plenum depths assigned to Room2Ds should simply be '
              'reported as plenum depths in the CSV or they should be used to generate '
              'distinct separated plenum rooms in the translation.',
              default=True, show_default=True)
@click.option('--merge-method', '-m', help='Text to describe how the Room2Ds should '
              'be merged into individual Rooms during the translation. Specifying a '
              'value here can be an effective way to reduce the number of Room '
              'volumes in the resulting Model and, ultimately, yield a faster simulation '
              'time with less results to manage. Choose from: None, Zones, PlenumZones, '
              'Stories, PlenumStories.', type=str, default='None', show_default=True)
@click.option('--geometry-ids/--geometry-names', ' /-gn', help='Flag to note whether a '
              'cleaned version of all geometry display names should be used instead '
              'of identifiers when translating the Model.',
              default=True, show_default=True)
@click.option('--output-file', '-f', help='Optional CSV file to output the string '
              'of the translation. By default it printed out to stdout.',
              type=click.File('w'), default='-', show_default=True)
def model_to_trace700_csv_cli(
    model_file, imperial, ventilation_method,
    multiplier, plenum, merge_method, geometry_ids, output_file
):
    """Translate a Dragonfly Model to a CSV with tables for TRACE 700 attributes.

    The resulting CSV tables can be copied into the tables that appear in the
    Component Tree view of TRACE 700. The order and organization of rooms in
    the resulting matrix should match that of the gbXML produced from the same model.

    \b
    Args:
        model_file: Full path to a Dragonfly Model file (DFJSON or DFpkl).
    """
    try:
        full_geometry = not multiplier
        separate_plenum = not plenum
        metric = not imperial
        geo_names = not geometry_ids
        model_to_trace700_csv(
            model_file, full_geometry, separate_plenum, merge_method,
            metric, geo_names, ventilation_method, output_file
        )
    except Exception as e:
        _logger.exception('System translation failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


def model_to_trace700_csv(
    model_file, metric=False, ventilation_method='Sum of Outdoor Air',
    full_geometry=False, separate_plenum=False, merge_method='None',
    geometry_names=False, output_file=None,
    imperial=True, multiplier=True, plenum=True, geometry_ids=True
):
    """Translate a Dragonfly Model to a CSV with tables for TRACE 700 attributes.

    The resulting CSV tables can be copied into the tables that appear in the
    Component Tree view of TRACE 700. The order and organization of rooms in
    the resulting matrix should match that of the gbXML produced from the same model.

    Args:
        model: A dragonfly Model for which a TRACE 700 CSV matrix will be returned.
        metric: Boolean to note whether the units of the values in the resulting
            matrix are in SI (True) instead of IP (False). (Default: False).
        ventilation_method: Optional text for the ventilation method to be used in the
            resulting matrix. Choose from the following.

            * Sum of Outdoor Air
            * ASHRAE 62.1

        full_geometry: If False, the multipliers on this Model's Stories will be
            passed along to the CSV. If True, full geometry objects will be written
            for each and every floor in the building that are represented through
            multipliers and all resulting multipliers will be 1. (Default: True).
        separate_plenum: Boolean to indicate whether ceiling/floor plenum depths
            assigned to Room2Ds should simply be reported as plenum depths in the
            CSV or they should be used to generate distinct separated plenum
            rooms in the translation. (Default: False).
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

        geometry_names: Boolean to note whether a cleaned version of all geometry
            display names should be used instead of identifiers when translating
            the Model to OSM and IDF. Using this flag will affect all Rooms, Faces,
            Apertures, Doors, and Shades. It will generally result in more read-able
            names in the OSM and IDF but this means that it will not be easy to map
            the EnergyPlus results back to the original Honeybee Model. Cases
            of duplicate IDs resulting from non-unique names will be resolved
            by adding integers to the ends of the new IDs that are derived from
            the name. (Default: False).
        output_file: Optional CSV file to output the CSV string of the translation.
            By default this string will be returned from this method.
    """
    # load the model and translate it to a CSV
    model = Model.from_file(model_file)
    exclude_plenums = not separate_plenum
    csv_str = model_to_csv(
        model, metric, ventilation_method,
        multiplier, exclude_plenums, merge_method, geometry_names
    )
    return process_content_to_output(csv_str, output_file)


@translate.command('model-to-trace700-xlsx')
@click.argument('model-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('--imperial/--metric', '-ip/-si', help='Flag to note whether imperial '
              'or metric units should be used for values in the output XLSX.',
              default=True, show_default=True)
@click.option('--ventilation-method', '-v', help='Text for the ventilation method to be '
              'used to calculate outdoor air. Choose from: Sum of Outdoor Air, ASHRAE 62.1',
              type=str, default='Sum of Outdoor Air', show_default=True)
@click.option('--multiplier/--full-geometry', ' /-fg', help='Flag to note if the '
              'multipliers on each Building story will be passed along to the '
              'generated Honeybee Room objects or if full geometry objects should be '
              'written for each story in the building.', default=True, show_default=True)
@click.option('--plenum/--separate-plenum', '-p/-sp', help='Flag to indicate whether '
              'ceiling/floor plenum depths assigned to Room2Ds should simply be '
              'reported as plenum depths in the tables or they should be used to generate '
              'distinct separated plenum rooms in the translation.',
              default=True, show_default=True)
@click.option('--merge-method', '-m', help='Text to describe how the Room2Ds should '
              'be merged into individual Rooms during the translation. Specifying a '
              'value here can be an effective way to reduce the number of Room '
              'volumes in the resulting Model and, ultimately, yield a faster simulation '
              'time with less results to manage. Choose from: None, Zones, PlenumZones, '
              'Stories, PlenumStories.', type=str, default='None', show_default=True)
@click.option('--geometry-ids/--geometry-names', ' /-gn', help='Flag to note whether a '
              'cleaned version of all geometry display names should be used instead '
              'of identifiers when translating the Model.',
              default=True, show_default=True)
@click.option('--output-file', '-f', help='Optional XLSX file to output the content '
              'of the translation. By default it printed out to stdout.',
              type=click.File('wb'), default='-', show_default=True)
def model_to_trace700_xlsx_cli(
    model_file, imperial, ventilation_method,
    multiplier, plenum, merge_method, geometry_ids, output_file
):
    """Translate a Dragonfly Model to an Excel file with tables for TRACE 700 attributes.

    The resulting Excel tables can be copied into the tables that appear in the
    Component Tree view of TRACE 700. The order and organization of rooms in
    the resulting matrix should match that of the gbXML produced from the same model.

    \b
    Args:
        model_file: Full path to a Dragonfly Model file (DFJSON or DFpkl).
    """
    try:
        full_geometry = not multiplier
        separate_plenum = not plenum
        metric = not imperial
        geo_names = not geometry_ids
        model_to_trace700_xlsx(
            model_file, metric, ventilation_method,
            full_geometry, separate_plenum, merge_method, geo_names, output_file
        )
    except Exception as e:
        _logger.exception('System translation failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


def model_to_trace700_xlsx(
    model_file, metric=False, ventilation_method='Sum of Outdoor Air',
    full_geometry=False, separate_plenum=False, merge_method='None',
    geometry_names=False, output_file=None,
    imperial=True, multiplier=True, plenum=True, geometry_ids=True
):
    """Translate a Dragonfly Model to an Excel file with tables for TRACE 700 attributes.

    The resulting Excel tables can be copied into the tables that appear in the
    Component Tree view of TRACE 700. The order and organization of rooms in
    the resulting matrix should match that of the gbXML produced from the same model.

    Args:
        model: A dragonfly Model for which a TRACE 700 XLSX file will be returned.
        metric: Boolean to note whether the units of the values in the resulting
            matrix are in SI (True) instead of IP (False). (Default: False).
        ventilation_method: Optional text for the ventilation method to be used in the
            resulting matrix. Choose from the following.

            * Sum of Outdoor Air
            * ASHRAE 62.1

        full_geometry: If False, the multipliers on this Model's Stories will be
            passed along to the XLSX. If True, full geometry objects will be written
            for each and every floor in the building that are represented through
            multipliers and all resulting multipliers will be 1. (Default: True).
        separate_plenum: Boolean to indicate whether ceiling/floor plenum depths
            assigned to Room2Ds should simply be reported as plenum depths in the
            tables or they should be used to generate distinct separated plenum
            rooms in the translation. (Default: False).
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

        geometry_names: Boolean to note whether a cleaned version of all geometry
            display names should be used instead of identifiers when translating
            the Model to OSM and IDF. Using this flag will affect all Rooms, Faces,
            Apertures, Doors, and Shades. It will generally result in more read-able
            names in the OSM and IDF but this means that it will not be easy to map
            the EnergyPlus results back to the original Honeybee Model. Cases
            of duplicate IDs resulting from non-unique names will be resolved
            by adding integers to the ends of the new IDs that are derived from
            the name. (Default: False).
        output_file: Optional XLSX file to output the XLSX content of the translation.
            By default this content will be returned from this method as a
            base64 string.
    """
    # load the model and translate it to a Workbook
    model = Model.from_file(model_file)
    exclude_plenums = not separate_plenum
    workbook = model_to_workbook(
        model, metric, ventilation_method,
        multiplier, exclude_plenums, merge_method, geometry_names
    )
    if isinstance(output_file, str):
        workbook.save(output_file)
    else:
        # save workbook to a byte stream
        out = io.BytesIO()
        workbook.save(out)
        workbook.close()
        out.seek(0)  # reset stream position to the beginning
        excel_bytes = out.getvalue()
        if output_file is not None and output_file.name != '<stdout>' and \
                output_file.mode == 'wb':
            output_file.write(excel_bytes)
        else:  # convert the bytes to a base64 string
            b = base64.b64encode(excel_bytes)
            if output_file is None:
                f_contents = b.decode('utf-8')
                return f_contents
            elif output_file.mode == 'w':
                f_contents = b.decode('utf-8')
                output_file.write(f_contents)
            else:
                output_file.write(b)


@translate.command('model-to-trace700-gbxml')
@click.argument('model-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('--imperial/--metric', '-ip/-si', help='Flag to note whether imperial '
              'or metric units should be used for values in the output CSV.',
              default=True, show_default=True)
@click.option('--opening-simplification', '-s', help='Text string for the type of '
              'simplification to perform on windows and doors in the dragonfly model. '
              'Choose from: None, MergeAdjWindows, SingleWindow.',
              type=str, default='MergeAdjWindows', show_default=True)
@click.option('--program-name', '-p', help='Optional text to set the name of the '
              'software that will appear under the programId and ProductName tags '
              'of the DocumentHistory section. This can be set things like "Ladybug '
              'Tools" or "Pollination" or some other software in which this gbXML '
              'export capability is being run. If None, "OpenStudio" will be used.',
              type=str, default=None, show_default=True)
@click.option('--program-version', '-v', help='Optional text to set the version of '
              'the software that will appear under the DocumentHistory section. '
              'If None, and the program_name is also unspecified, only the version '
              'of OpenStudio will appear. Otherwise, this will default to "0.0.0" '
              'given that the version field is required.',
              type=str, default=None, show_default=True)
@click.option('--output-file', '-f', help='Optional gbXML file to output the string '
              'of the translation. By default it printed out to stdout', default='-',
              type=click.Path(file_okay=True, dir_okay=False, resolve_path=True))
def model_to_trace700_gbxml_cli(
    model_file, imperial, opening_simplification,
    program_name, program_version, output_file
):
    """Translate a Dragonfly Model to a gbXML file.

    \b
    Args:
        model_file: Path to either a DFJSON or DFpkl file. This can also be a
            HBJSON or a HBpkl from which a Dragonfly model should be derived.
    """
    try:
        metric = not imperial
        model_to_trace700_gbxml(
            model_file, metric, opening_simplification,
            program_name, program_version, output_file
        )
    except Exception as e:
        _logger.exception('Model translation failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


def model_to_trace700_gbxml(
    model_file, metric=False, opening_simplification='MergeAdjWindows',
    program_name=None, program_version=None, output_file=None,
    imperial=True
):
    """Translate a Dragonfly Model to a gbXML file suitable for TRACE 700.

    Args:
        model_file: Path to either a DFJSON or DFpkl file. This can also be a
            HBJSON or a HBpkl from which a Dragonfly model should be derived.
        metric: Boolean to note whether the units of the values in the resulting
            matrix are in SI (True) instead of IP (False). (Default: False).
        opening_simplification: Optional text to note the method by which openings
            are simplified as part of the translation to gbXML. (Default: MergeAdjWindows).
            Choose from the following options.

            * None - No sub-face simplification will occur
            * MergeAdjWindows - Adjacent windows are merged; doors are left as is
            * SingleWindow - All doors removed; windows are merged into one per wall

        program_name: Optional text to set the name of the software that will
            appear under the programId and ProductName tags of the DocumentHistory
            section. This can be set things like "Ladybug Tools" or "Pollination"
            or some other software in which this gbXML export capability is being
            run. If None, the "OpenStudio" will be used. (Default: None).
        program_version: Optional text to set the version of the software that
            will appear under the DocumentHistory section. If None, and the
            program_name is also unspecified, only the version of OpenStudio will
            appear. Otherwise, this will default to "0.0.0" given that the version
            field is required. (Default: None).
        output_file: Optional gbXML file to output the string of the translation.
            By default it will be returned from this method.
    """
    # re-serialize the Dragonfly Model and translate it
    model = Model.from_file(model_file)
    gbxml_str = model_to_gbxml(
        model, metric, opening_simplification, program_name, program_version
    )
    # write out the gbXML file
    return process_content_to_output(gbxml_str, output_file)


@translate.command('model-to-trace700-exp')
@click.argument('model-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('--imperial/--metric', '-ip/-si', help='Flag to note whether imperial '
              'or metric units should be used for values in the output EXP file.',
              default=True, show_default=True)
@click.option('--output-file', '-f', help='Optional EXP file to output the string '
              'of the translation. By default it is printed out to stdout.',
              type=click.File('w'), default='-', show_default=True)
def model_to_trace700_exp_cli(model_file, imperial, output_file):
    """Translate all unique ProgramTypes in a Dragonfly Model file into a single TRACE 700 EXP file.

    \b
    Args:
        model_file: Full path to a Dragonfly Model file (DFJSON or DFpkl).
    """
    try:
        metric = not imperial
        model = Model.from_file(model_file)
        process_content_to_output(model_to_exp(model, si_units=metric), output_file)
    except Exception as e:
        _logger.exception('Model EXP translation failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@translate.command('model-to-trace700-zip')
@click.argument('model-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('--imperial/--metric', '-ip/-si', help='Flag to note whether imperial '
              'or metric units should be used for values in the output CSV.',
              default=True, show_default=True)
@click.option('--opening-simplification', '-s', help='Text string for the type of '
              'simplification to perform on windows and doors in the dragonfly model. '
              'Choose from: None, MergeAdjWindows, SingleWindow.',
              type=str, default='MergeAdjWindows', show_default=True)
@click.option('--ventilation-method', '-v', help='Text for the ventilation method to be '
              'used to calculate outdoor air. Choose from: Sum of Outdoor Air, ASHRAE 62.1',
              type=str, default='Sum of Outdoor Air', show_default=True)
@click.option('--program-name', '-p', help='Optional text to set the name of the '
              'software that will appear under the programId and ProductName tags '
              'of the DocumentHistory section. This can be set things like "Ladybug '
              'Tools" or "Pollination" or some other software in which this gbXML '
              'export capability is being run. If None, "OpenStudio" will be used.',
              type=str, default=None, show_default=True)
@click.option('--program-version', '-v', help='Optional text to set the version of '
              'the software that will appear under the DocumentHistory section. '
              'If None, and the program_name is also unspecified, only the version '
              'of OpenStudio will appear. Otherwise, this will default to "0.0.0" '
              'given that the version field is required.',
              type=str, default=None, show_default=True)
@click.option('--output-file', '-f', help='Optional ,zip file to output the content '
              'of the translation. By default it printed out to stdout.',
              type=click.File('wb'), default='-', show_default=True)
def model_to_trace700_zip_cli(
    model_file, imperial, opening_simplification, ventilation_method,
    program_name, program_version, output_file
):
    """Translate a Dragonfly Model to a gbXML file.

    \b
    Args:
        model_file: Path to either a DFJSON or DFpkl file. This can also be a
            HBJSON or a HBpkl from which a Dragonfly model should be derived.
    """
    try:
        metric = not imperial
        model_to_trace700_zip(
            model_file, metric, opening_simplification, ventilation_method,
            program_name, program_version, output_file
        )
    except Exception as e:
        _logger.exception('Model translation failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


def model_to_trace700_zip(
    model_file, metric=False, opening_simplification='MergeAdjWindows',
    ventilation_method='Sum of Outdoor Air',
    program_name=None, program_version=None, output_file=None,
    imperial=True
):
    """Translate a Dragonfly Model to a gbXML file suitable for TRACE 700.

    Args:
        model_file: Path to either a DFJSON or DFpkl file. This can also be a
            HBJSON or a HBpkl from which a Dragonfly model should be derived.
        metric: Boolean to note whether the units of the values in the resulting
            matrix are in SI (True) instead of IP (False). (Default: False).
        opening_simplification: Optional text to note the method by which openings
            are simplified as part of the translation to gbXML. (Default: MergeAdjWindows).
            Choose from the following options.

            * None - No sub-face simplification will occur
            * MergeAdjWindows - Adjacent windows are merged; doors are left as is
            * SingleWindow - All doors removed; windows are merged into one per wall

        ventilation_method: Optional text for the ventilation method to be used in the
            resulting matrix. Choose from the following.

            * Sum of Outdoor Air
            * ASHRAE 62.1

        program_name: Optional text to set the name of the software that will
            appear under the programId and ProductName tags of the DocumentHistory
            section. This can be set things like "Ladybug Tools" or "Pollination"
            or some other software in which this gbXML export capability is being
            run. If None, the "OpenStudio" will be used. (Default: None).
        program_version: Optional text to set the version of the software that
            will appear under the DocumentHistory section. If None, and the
            program_name is also unspecified, only the version of OpenStudio will
            appear. Otherwise, this will default to "0.0.0" given that the version
            field is required. (Default: None).
        output_file: Optional gbXML file to output the string of the translation.
            By default it will be returned from this method.
    """
    # re-serialize the Dragonfly Model and translate it
    model = Model.from_file(model_file)
    zip_bytes = model_to_trace700_zip_bytes(
        model, metric, opening_simplification, ventilation_method,
        program_name, program_version
    )
    # write out the ZIP file
    if isinstance(output_file, str):
        with open(output_file, 'wb') as out_f:
            out_f.write(zip_bytes)
    else:
        if output_file is not None and output_file.name != '<stdout>' and \
                output_file.mode == 'wb':
            output_file.write(zip_bytes)
        else:  # convert the bytes to a base64 string
            b = base64.b64encode(zip_bytes)
            if output_file is None:
                f_contents = b.decode('utf-8')
                return f_contents
            elif output_file.mode == 'w':
                f_contents = b.decode('utf-8')
                output_file.write(f_contents)
            else:
                output_file.write(b)
