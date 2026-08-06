"""In-memory route provider with simulated offers for development and tests."""

from __future__ import annotations

from datetime import UTC, datetime

from app.domain.offers import RouteOffer, RouteRequest


def _offer_id(request: RouteRequest) -> str:
    return f"route-{request.origin}-{request.destination}"


def _distance_km(request: RouteRequest) -> float:
    """Deterministic distance for the reference city pairs, else a default."""
    key = f"{request.origin}|{request.destination}".lower()
    known = {
        "madrid|santiago de compostela": 540.0,
        "madrid|sevilla": 530.0,
        "madrid|porto": 620.0,
    }
    return known.get(key, 550.0)


class MockRouteProvider:
    """Serves a deterministic route offer without calling Google Routes."""

    def calculate(self, request: RouteRequest) -> RouteOffer:
        distance = _distance_km(request)
        # Default estimate assumes a small fuel car at ~6 L/100km, 1.6 €/L.
        fuel = round(distance * 6.0 / 100 * 1.6, 2)
        toll = round(distance * 0.057, 2)
        parking = round(distance * 0.044, 2)
        wear = round(distance * 0.05, 2)
        verified = datetime.now(UTC).replace(microsecond=0)
        total = round(fuel + toll + parking + wear, 2)
        return RouteOffer(
            provider_offer_id=_offer_id(request),
            origin=request.origin,
            destination=request.destination,
            distance_km=distance,
            duration_minutes=round(distance / 80 * 60, 1),
            fuel_cost_eur=fuel,
            toll_cost_eur=toll,
            parking_cost_eur=parking,
            vehicle_wear_cost_eur=wear,
            total_cost_eur=total,
            route_polyline="mock-polyline",
            verified_at=verified,
        )
