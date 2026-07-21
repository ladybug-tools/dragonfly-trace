"""Test cli translate module."""
from click.testing import CliRunner
from dragonfly_trace.cli.exp import program_to_trace700_exp_cli, model_to_trace700_exp_cli

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
    os.remove(output_exp)


def test_modeltrace700_exp():
    runner = CliRunner()
    input_df_model = './tests/assets/small_sample_exp_test.dfjson'

    output_exp = './tests/assets/small_sample_exp_test.exp'
    result = runner.invoke(
        model_to_trace700_exp_cli,
        [input_df_model, '--output-file', output_exp]
    )
    assert result.exit_code == 0

    assert os.path.isfile(output_exp)
    os.remove(output_exp)
