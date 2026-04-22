"""dragonfly trace translation commands."""
import click
import sys
import logging

from ladybug.commandutil import process_content_to_output
from dragonfly.model import Model
from dragonfly_trace.writer import model_to_trace700_csv as model_to_csv


_logger = logging.getLogger(__name__)


@click.group(help='Commands for translating URBANopt systems to OSM/IDF.')
def translate():
    pass


@translate.command('model-to-trace700-csv')
@click.argument('model-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
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
@click.option('--imperial/--metric', '-ip/-si', help='Flag to note whether imperial '
              'or metric units should be used for values in the output CSV.',
              default=True, show_default=True)
@click.option('--geometry-ids/--geometry-names', ' /-gn', help='Flag to note whether a '
              'cleaned version of all geometry display names should be used instead '
              'of identifiers when translating the Model.',
              default=True, show_default=True)
@click.option('--resource-ids/--resource-names', ' /-rn', help='Flag to note whether a '
              'cleaned version of all resource display names should be used instead '
              'of identifiers when translating the Model.',
              default=True, show_default=True)
@click.option('--output-file', '-f', help='Optional CSV file to output the string '
              'of the translation. By default it printed out to stdout.',
              type=click.File('w'), default='-', show_default=True)
def model_to_trace700_csv_cli(
    model_file, multiplier, plenum, merge_method, imperial,
    geometry_ids, resource_ids, output_file
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
        res_names = not resource_ids
        model_to_trace700_csv(
            model_file, full_geometry, separate_plenum, merge_method,
            metric, geo_names, res_names, output_file
        )
    except Exception as e:
        _logger.exception('System translation failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


def model_to_trace700_csv(
    model_file, full_geometry=False, separate_plenum=False, merge_method='None',
    metric=False, geometry_names=False, resource_names=False, output_file=None,
    multiplier=True, plenum=True, imperial=True, geometry_ids=True, resource_ids=True
):
    """Translate a Dragonfly Model to a CSV with tables for TRACE 700 attributes.

    The resulting CSV tables can be copied into the tables that appear in the
    Component Tree view of TRACE 700. The order and organization of rooms in
    the resulting matrix should match that of the gbXML produced from the same model.

    Args:
        model: A dragonfly Model for which a TRACE 700 CSV matrix will be returned.
        multiplier: If True, the multipliers on this Model's Stories will be
            passed along to the CSV. If False, full geometry objects will be written
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

        metric: Boolean to note whether the units of the values in the resulting
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
        output_file: Optional CSV file to output the CSV string of the translation.
            By default this string will be returned from this method.
    """
    # load the model and translate it to a CSV
    model = Model.from_file(model_file)
    exclude_plenums = not separate_plenum
    csv_str = model_to_csv(
        model, multiplier, exclude_plenums, merge_method,
        metric, geometry_names, resource_names
    )

    return process_content_to_output(csv_str, output_file)
