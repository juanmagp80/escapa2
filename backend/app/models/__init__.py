"""ORM models.

Importing this package registers every table on the declarative base.
"""

from __future__ import annotations

from app.models.airport_preference import AirportPreference
from app.models.availability_window import AvailabilityWindow
from app.models.itinerary import Itinerary
from app.models.notification_device import NotificationDevice
from app.models.notification_log import NotificationLogORM
from app.models.price_snapshot import PriceSnapshot
from app.models.search_watch import SearchWatch
from app.models.travel_opportunity import TravelOpportunity
from app.models.travel_profile import TravelProfile

__all__ = [
    "AirportPreference",
    "AvailabilityWindow",
    "Itinerary",
    "NotificationDevice",
    "NotificationLogORM",
    "PriceSnapshot",
    "SearchWatch",
    "TravelOpportunity",
    "TravelProfile",
]
