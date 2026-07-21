"""Test cli translate module."""
from click.testing import CliRunner
from dragonfly_trace.cli.exp import program_to_trace700_exp_cli

import os


def test_program_to_trace700_exp():
    runner = CliRunner()
    input_json_program = './tests/assets/office_program.json'

    output_exp = './tests/assets/office_program.exp'
    result = runner.invoke(
        program_to_trace700_exp_cli,
        [input_json_program, '--output-file', output_exp]
    )
    assert result.exit_code == 0

    assert os.path.isfile(output_exp)
    # os.remove(output_csv)
