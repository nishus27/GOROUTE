"""Shared Flask extension instances.

Kept in a separate module so models and the app factory can import them
without circular imports.
"""

from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
cors = CORS()
