"""Test the translators for airflow."""
from dragonfly.model import Model

from dragonfly_trace.airflows import airflows_trace700_matrix


def test_airflows_trace700_matrix():
    """Test the rooms_to_trace700_matrix method."""
    sample_path = './tests/assets/small_revit_sample.dfjson'
    model = Model.from_file(sample_path)

    csv_mtx = airflows_trace700_matrix(model.room_2ds)
    assert len(csv_mtx) == 45
    assert len(csv_mtx[0]) == len(model.room_2ds) + 1
