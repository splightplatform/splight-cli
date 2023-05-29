import pytest

# component is your component loaded as a pytest fixture
# using local clients for database, datalake and communication
from splight_lib.testing import mock_component

from main import {{component_name}}


def test_simple_example():
    assert 0 == 0, "The world is bad"
    assert "foo" == "foo", "Run away"


def test_using_component():
    min, max = 1, 10
    component = {{component_name}}(component_id="1234")
    random = component._give_a_random_number(min=min, max=max)
    assert random > min, "Random is below the defined range"
    assert random < max, "Random is above the defined range"
