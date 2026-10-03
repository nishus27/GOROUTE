"""Pytest fixtures for the GoRoute backend."""

import sys
from pathlib import Path

import pytest

# Make the backend package importable when running `pytest` from backend/.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app  # noqa: E402
from app.config import Config  # noqa: E402
from app.extensions import db  # noqa: E402


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret-key"


@pytest.fixture()
def app():
    application = create_app(TestConfig)
    with application.app_context():
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
