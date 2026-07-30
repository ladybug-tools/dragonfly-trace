"""Test cli translate module."""
import os
from click.testing import CliRunner

from dragonfly_trace.cli.translate import model_to_trace700_csv_cli, \
    model_to_trace700_xlsx_cli, model_to_trace700_gbxml_cli, model_to_trace700_exp_cli, \
    model_to_trace700_zip_cli


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
    os.remove(output_csv)


def test_model_to_trace700_xlsx():
    runner = CliRunner()
    input_df_model = './tests/assets/small_revit_sample.dfjson'

    output_xlsx = './tests/assets/in.xlsx'
    result = runner.invoke(
        model_to_trace700_xlsx_cli,
        [input_df_model, '--output-file', output_xlsx]
    )
    assert result.exit_code == 0

    assert os.path.isfile(output_xlsx)
    os.remove(output_xlsx)


def test_model_to_trace700_gbxml():
    runner = CliRunner()
    input_df_model = './tests/assets/small_revit_sample.dfjson'

    output_xml = './tests/assets/in.xml'
    result = runner.invoke(
        model_to_trace700_gbxml_cli,
        [input_df_model, '--output-file', output_xml]
    )
    assert result.exit_code == 0

    assert os.path.isfile(output_xml)
    os.remove(output_xml)


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


def test_model_to_trace700_zip():
    runner = CliRunner()
    input_df_model = './tests/assets/small_revit_sample.dfjson'

    output_zip = './tests/assets/in.zip'
    result = runner.invoke(
        model_to_trace700_zip_cli,
        [input_df_model, '--output-file', output_zip]
    )
    assert result.exit_code == 0

    assert os.path.isfile(output_zip)
    os.remove(output_zip)
