"""Test the translators to TRACE."""
from honeybee_energy.lib.programtypes import office_program
from dragonfly.model import Model

from dragonfly_trace.exp import program_to_exp
from dragonfly_trace.writer import model_to_exp


def test_program_to_exp():
    """Test the program_to_exp function."""

    exp = program_to_exp(office_program)
    assert isinstance(exp, str)
    assert 'EDITORSv6.3.1' in exp
    assert 'T.LOAD_PEOPLE' in exp
    assert 'T.LOAD_LIGHTS' in exp
    assert 'T.LOAD_MISEQUIP' in exp
    assert 'T.InternalLoadTemplate' in exp
    assert 'T.AirflowTemplate' in exp
    assert 'T.ThermostatTemplate' in exp
    assert 'T.RoomTemplate' in exp


def test_model_to_exp():
    """Test the model_to_exp function."""

    model = Model.from_dfjson('./tests/assets/small_sample_exp_test.dfjson')
    exp = model_to_exp(model)
    assert 'EDITORSv6.3.1' in exp
    assert 'T.LOAD_PEOPLE' in exp
    assert 'People;2019::SmallOffice::OpenOffice_People;1;190.475924;1;249.939255;7;249.939255;7;30.0;' in exp
    assert 'T.LOAD_LIGHTS' in exp
    assert 'Lighting;2019::SmallOffice::Elec/MechRoom_Lighting;1;SUSFLUOR;40.0;1;40.0;20.0;' in exp
    assert 'T.LOAD_MISEQUIP' in exp
    assert 'Miscellaneous;2019::SmllOffc::Elc/MchRmElctrc;1;0.270000;8;100.0;100.0;0.0;50.0;1;1;' in exp
    assert 'T.InternalLoadTemplate' in exp
    assert '2019::SmallOffice::Elec/MechRoom;None;Cooling Only (Design);0.000000;1;250.0000;7;250.0000;7;2019::SmallOffice::Elec/MechRoom_Lighting;Cooling Only (Design);0.430000;3;2019::SmllOffc::Elc/MchRmElctrc;Cooling Only (Design);0.270000;8;1;1;2;' in exp
    assert 'T.AirflowTemplate' in exp
    assert '2019::SmallOffice::Elec/MechRoom;None;Available (100%);13.903412;3;13.903412;3;None;Available (100%);0.112000;3;0.112000;3;9999.99;0;Available (100%);9999.99;8;9999.99;9;9999.99;10;9999.99;10;0;2;Available (100%);0;0;9999.99;0;9999.99;1;9999.99;9999.99;0;0;9999.99;0;' in exp
    assert 'T.ThermostatTemplate' in exp
    assert '2019::SmallOffice::Elec/MechRoom;75.0;1;70.0;1;50;85.0;None;60.0;None;1;0;2;1;' in exp
    assert 'T.RoomTemplate' in exp
    assert '2019::SmallOffice::Elec/MechRoom;2019::SmallOffice::Elec/MechRoom;2019::SmallOffice::Elec/MechRoom;2019::SmallOffice::Elec/MechRoom;Default;' in exp
