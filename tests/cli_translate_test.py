"""Test cli translate module."""
import os
import json
from click.testing import CliRunner

from dragonfly_trace.cli.translate import model_to_trace700_csv_cli, \
    model_to_trace700_xlsx_cli, model_to_trace700_gbxml_cli, model_to_exp_cli, \
    model_to_trace700_zip_cli, \
    materials_from_exp_cli, constructions_from_exp_cli, construction_sets_from_exp_cli, \
    program_from_exp_cli


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
        model_to_exp_cli,
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


def test_materials_from_exp():
    runner = CliRunner()
    exp_path = './tests/assets/custom_lib.EXP'

    output_json = './tests/assets/custom_lib.json'
    result = runner.invoke(
        materials_from_exp_cli, [exp_path, '--output-file', output_json]
    )
    assert result.exit_code == 0

    assert os.path.isfile(output_json)
    with open(output_json, 'r') as of:
        result_dict = json.load(of)
    assert len(result_dict) == 63
    os.remove(output_json)


def test_constructions_from_exp():
    runner = CliRunner()
    exp_path = './tests/assets/custom_lib.EXP'

    output_json = './tests/assets/custom_lib.json'
    result = runner.invoke(
        constructions_from_exp_cli,
        [exp_path, '--output-file', output_json, '--abridged']
    )
    assert result.exit_code == 0

    assert os.path.isfile(output_json)
    with open(output_json, 'r') as of:
        result_dict = json.load(of)
    assert len(result_dict) == 32
    os.remove(output_json)


def test_construction_sets_from_exp():
    runner = CliRunner()
    exp_path = './tests/assets/custom_lib.EXP'

    output_json = './tests/assets/custom_lib.json'
    result = runner.invoke(
        construction_sets_from_exp_cli,
        [exp_path, '--output-file', output_json, '--abridged']
    )
    assert result.exit_code == 0

    assert os.path.isfile(output_json)
    with open(output_json, 'r') as of:
        result_dict = json.load(of)
    assert len(result_dict) == 1
    os.remove(output_json)


def test_program_from_trace700_exp():
    runner = CliRunner()
    exp_path = './tests/assets/custom_lib.EXP'

    output_json = './tests/assets/custom_lib.json'
    result = runner.invoke(
        program_from_exp_cli,
        [exp_path, '--output-file', output_json, '--abridged']
    )
    assert result.exit_code == 0

    assert os.path.isfile(output_json)
    with open(output_json, 'r') as of:
        result_dict = json.load(of)
    assert len(result_dict) == 11
    os.remove(output_json)
