"""Test cli translate module."""
from click.testing import CliRunner
from dragonfly_trace.cli.translate import model_to_trace700_csv_cli

import os


def test_model_to_trace700_csv():
    runner = CliRunner()
    input_df_model = './tests/assets/small_revit_sample.dfjson'

    output_csv = './tests/assets/in.csv'
    result = runner.invoke(
        model_to_trace700_csv_cli,
        [input_df_model, '--output-file', output_csv]
    )
    assert result.exit_code == 0

    assert os.path.isfile(output_csv)
    # os.remove(output_csv)
