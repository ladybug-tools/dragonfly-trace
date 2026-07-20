"""dragonfly trace exp translation commands."""
import click
import sys
import json
import logging

from ladybug.commandutil import process_content_to_output
from honeybee_energy.programtype import ProgramType

from dragonfly_trace.exp import program_to_exp, internal_loads_to_exp, \
    airflow_to_exp, thermostat_to_exp


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
