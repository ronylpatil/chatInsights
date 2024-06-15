import pytest
from chatInsights import _transformData

@pytest.mark.parametrize("path", ["tests/test_data/chat4.txt"])
def test_transformData(path):
    df = _transformData(path)
    assert df.isnull().sum().sum() == 0
    assert df.shape == (40, 15)
    