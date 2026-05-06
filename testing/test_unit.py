import pytest
from app import app
from forms import loginForm, RegistrationForm

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client
