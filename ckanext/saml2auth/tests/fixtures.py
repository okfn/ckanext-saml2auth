import pytest


@pytest.fixture(autouse=True)
def load_standard_plugins(with_plugins):
    """ Use 'with_plugins' fixture in ALL tests """
    pass
