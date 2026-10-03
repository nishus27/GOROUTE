"""SQLAlchemy models.

Importing this package registers every model with SQLAlchemy so that
``db.create_all()`` knows about all tables.
"""

from .booking import Booking
from .daily_commute import DailyCommute
from .journey import Journey
from .notification import Notification
from .route import Route
from .saved_place import SavedPlace
from .user import User

__all__ = [
    "User",
    "SavedPlace",
    "DailyCommute",
    "Journey",
    "Route",
    "Booking",
    "Notification",
]
