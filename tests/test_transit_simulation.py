#!/usr/bin/env python

"""Tests for `transit_simulation` package."""

import pytest

from transit_simulation import transit_simulation as ts


@pytest.fixture
def input_data():
    """Sample pytest fixture.
    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_simulation(input_data):
    """Sample pytest test function with the pytest fixture as an argument."""

    assert ts.simulate() == 2
    assert ts.simulate() != 1
