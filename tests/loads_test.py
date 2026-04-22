"""Test the translators of loads to TRACE."""
from dragonfly.model import Model

from dragonfly_trace.loads import people_and_lights_trace700_matrix, \
    miscellaneous_loads_trace700_matrix


def test_people_and_lights_trace700_matrix():
    """Test the people_and_lights_trace700_matrix method."""
    sample_path = './tests/assets/small_revit_sample.dfjson'
    model = Model.from_file(sample_path)

    csv_mtx = people_and_lights_trace700_matrix(model.room_2ds)
    assert len(csv_mtx) == 15
    assert len(csv_mtx[0]) == len(model.room_2ds) + 1


def test_miscellaneous_loads_trace700_matrix():
    """Test the miscellaneous_loads_trace700_matrix method."""
    sample_path = './tests/assets/small_revit_sample.dfjson'
    model = Model.from_file(sample_path)

    csv_mtx = miscellaneous_loads_trace700_matrix(model.room_2ds)
    assert len(csv_mtx) == 8
    assert len(csv_mtx[0]) == len(model.room_2ds) + 1
