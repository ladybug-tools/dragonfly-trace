"""dragonfly trace exp translation commands."""
import click
import sys
import json
import logging

from ladybug.commandutil import process_content_to_output
from honeybee_energy.programtype import ProgramType

from dragonfly_trace.exp import program_to_exp, internal_loads_to_exp, \
    airflow_to_exp, thermostat_to_exp, programs_from_exp


_logger = logging.getLogger(__name__)


@click.group(help='Commands for translating Honeybee ProgramTypes to TRACE 700 EXP files.')
def exp():
    pass


@exp.command('program-to-trace700-exp')
@click.argument('program-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('--imperial/--metric', '-ip/-si', help='Flag to note whether imperial '
              'or metric units should be used for values in the output EXP file.',
              default=True, show_default=True)
@click.option('--output-file', '-f', help='Optional EXP file to output the string '
              'of the translation. By default it is printed out to stdout.',
              type=click.File('w'), default='-', show_default=True)
def program_to_trace700_exp_cli(program_file, imperial, output_file):
    """Translate a Honeybee ProgramType file to a TRACE 700 EXP file.

    \b
    Args:
        program_file: Full path to a Honeybee ProgramType JSON file.
    """
    try:
        metric = not imperial
        with open(program_file, 'r') as f:
            data = json.load(f)
        program = ProgramType.from_dict(data)
        process_content_to_output(program_to_exp(program, si_units=metric), output_file)
    except Exception as e:
        _logger.exception('Program EXP translation failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@exp.command('program-to-trace700-internal-loads')
@click.argument('program-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('--imperial/--metric', '-ip/-si', help='Flag to note whether imperial '
              'or metric units should be used for values in the output EXP file.',
              default=True, show_default=True)
@click.option('--output-file', '-f', help='Optional EXP file to output the string '
              'of the translation. By default it is printed out to stdout.',
              type=click.File('w'), default='-', show_default=True)
def program_to_trace700_internal_loads_cli(program_file, imperial, output_file):
    """Translate a Honeybee ProgramType JSON into an Internal Loads EXP template.

    \b
    Args:
        program_file: Full path to a Honeybee ProgramType JSON file.
    """
    try:
        metric = not imperial
        with open(program_file, 'r') as f:
            data = json.load(f)
        program = ProgramType.from_dict(data)
        process_content_to_output(internal_loads_to_exp(program, si_units=metric), output_file)
    except Exception as e:
        _logger.exception('Internal loads EXP translation failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@exp.command('program-to-trace700-airflow')
@click.argument('program-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('--imperial/--metric', '-ip/-si', help='Flag to note whether imperial '
              'or metric units should be used for values in the output EXP file.',
              default=True, show_default=True)
@click.option('--output-file', '-f', help='Optional EXP file to output the string '
              'of the translation. By default it is printed out to stdout.',
              type=click.File('w'), default='-', show_default=True)
def program_to_trace700_airflow_cli(program_file, imperial, output_file):
    """Translate a Honeybee ProgramType JSON into an Airflow EXP template.

    \b
    Args:
        program_file: Full path to a Honeybee ProgramType JSON file.
    """
    try:
        metric = not imperial
        with open(program_file, 'r') as f:
            data = json.load(f)
        program = ProgramType.from_dict(data)
        process_content_to_output(airflow_to_exp(program, si_units=metric), output_file)
    except Exception as e:
        _logger.exception('Airflow template EXP translation failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@exp.command('program-to-trace700-thermostat')
@click.argument('program-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('--imperial/--metric', '-ip/-si', help='Flag to note whether imperial '
              'or metric units should be used for values in the output EXP file.',
              default=True, show_default=True)
@click.option('--output-file', '-f', help='Optional EXP file to output the string '
              'of the translation. By default it is printed out to stdout.',
              type=click.File('w'), default='-', show_default=True)
def program_to_trace700_thermostat_cli(program_file, imperial, output_file):
    """Translate a Honeybee ProgramType JSON into a Thermostat EXP template.

    \b
    Args:
        program_file: Full path to a Honeybee ProgramType JSON file.
    """
    try:
        metric = not imperial
        with open(program_file, 'r') as f:
            data = json.load(f)
        program = ProgramType.from_dict(data)
        process_content_to_output(thermostat_to_exp(program, si_units=metric), output_file)
    except Exception as e:
        _logger.exception('Thermostat template EXP translation failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


@exp.command('programs-from-trace700-exp')
@click.argument('exp-file', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.option('--full/--abridged', ' /-a', help='Flag to note whether the objects '
              'should be translated as an abridged specification instead of a '
              'specification that fully describes the object. This option should be '
              'used when the schedules-from-osm command will be used to separately '
              'translate all of the schedules from the OSM.',
              default=True, show_default=True)
@click.option('--indent', '-i', help='Optional integer to specify the indentation in '
              'the output JSON file. Specifying an value here can produce more read-able'
              ' JSONs.', type=int, default=None, show_default=True)
@click.option('--output-file', '-f', help='Optional JSON file to output the string '
              'of the translation. By default it printed out to stdout',
              type=click.File('w'), default='-', show_default=True)
def program_from_trace700_exp_cli(exp_file, full, indent, output_file):
    """Translate all ProgramTypes in a TRACE 700 EXP file to a Honeybee JSON.

    The resulting JSON can be written into a user standards folder to add the
    programs to a users standards library.

    \b
    Args:
        exp_file: Path to a TRACE 700 EXP file.
    """
    try:
        abridged = not full
        programs_from_trace700_exp(exp_file, abridged, indent, output_file)
    except Exception as e:
        _logger.exception('Program translation failed.\n{}'.format(e))
        sys.exit(1)
    else:
        sys.exit(0)


def programs_from_trace700_exp(
    exp_file, abridged=False, indent=None, output_file=None, full=True
):
    """Translate all ProgramTypes in a TRACE 700 EXP file to a Honeybee JSON.

    The resulting JSON can be written into a user standards folder to add the
    programs to a users standards library.

    Args:
        exp_file: Path to a TRACE 700 EXP file.
        abridged: Boolean to note whether the objects should be translated as
            an abridged specification instead of a specification that fully
            describes the object. This option should be used when the
            schedules_from_osm function will be used to separately
            translate all of the constructions from the OSM. (Default: False).
        indent: Optional integer to specify the indentation in the output JSON file.
            Specifying an value here can produce more read-able JSONs. (Default: None).
        output_file: Optional JSON file to output the string of the translation.
            If None, it will be returned from this method. (Default: None).
    """
    with open(exp_file) as exp_f:
        file_contents = exp_f.read()
    programs = programs_from_exp(file_contents)
    out_dict = {p.identifier: p.to_dict(abridged=abridged) for p in programs}
    return process_content_to_output(json.dumps(out_dict, indent=indent), output_file)
