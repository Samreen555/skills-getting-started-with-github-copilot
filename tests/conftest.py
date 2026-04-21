"""
Pytest configuration and fixtures for API tests
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities, get_default_activities


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Auto-use fixture that resets the activities database before each test.
    This ensures test isolation by providing a clean state.
    """
    # Reset to default state before each test
    activities.clear()
    activities.update(get_default_activities())
    yield
    # Cleanup after test (optional, but good practice)
    activities.clear()
    activities.update(get_default_activities())


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient for making requests to the API.
    Using the app as-is with the actual activities database.
    """
    return TestClient(app)


@pytest.fixture
def clean_activities():
    """
    Fixture that provides a fresh activities dictionary for tests
    that need to manipulate a clean dataset.
    """
    return get_default_activities()
