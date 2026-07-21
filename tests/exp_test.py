"""Test the translators to TRACE."""
from honeybee_energy.lib.programtypes import office_program

from dragonfly_trace.exp import program_to_exp


def test_program_to_exp():
    """Test the program_to_exp function."""

    data = program_to_exp(office_program)
    assert isinstance(data, str)
    assert 'EDITORSv6.3.1' in data
    assert 'T.LOAD_PEOPLE' in data
    assert 'T.LOAD_LIGHTS' in data
    assert 'T.LOAD_MISEQUIP' in data
    assert 'T.InternalLoadTemplate' in data
    assert 'T.AirflowTemplate' in data
    assert 'T.ThermostatTemplate' in data
    assert 'T.RoomTemplate' in data
