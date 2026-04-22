"""Test the translators to TRACE."""
from dragonfly.model import Model

from dragonfly_trace.writer import rooms_to_trace700_matrix


def test_rooms_to_trace700_matrix():
    """Test the rooms_to_trace700_matrix method."""
    sample_path = './tests/assets/small_revit_sample.dfjson'
    model = Model.from_file(sample_path)

    csv_mtx = rooms_to_trace700_matrix(model.room_2ds)
    assert len(csv_mtx) == 29
    assert len(csv_mtx[0]) == len(model.room_2ds) + 1
