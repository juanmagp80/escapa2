"""Deterministic rule-based AI provider for development and fallback."""

from __future__ import annotations

import re
from datetime import date, timedelta

from app.ai.schemas import (
    Confidence,
    DailyReportOpportunityEntry,
    DailyReportRequest,
    DailyReportResponse,
    InterpretSearchRequest,
    InterpretSearchResponse,
    ItineraryAiRequest,
    ItineraryAiResponse,
    ItineraryDay,
    ItineraryItem,
    OpportunitySummaryRequest,
    OpportunitySummaryResponse,
)
from app.domain.enums import TransportMode

_INTEREST_KEYWORDS: dict[str, tuple[str, ...]] = {
    "playa": ("playa", "costa", "mar", "surf"),
    "naturaleza": ("naturaleza", "parque", "senderismo", "ruta", "camping"),
    "ciudad": ("ciudad", "urbano", "museos", "cultural"),
    "montaña": ("montaña", "sierra", "pico", "esquí", "esqui"),
    "gastronomía": ("gastronomía", "comer", "gastronomia", "restaurante", "tapas"),
    "tranquilidad": ("tranquilidad", "tranquilo", "relax", "descansar", "escapada rural"),
    "vida nocturna": ("fiesta", "nocturna", "discoteca", "bares", "conciertos"),
}

_ORIGIN_PATTERN = re.compile(
    r"\b(?:desde|salimos?\s+(?:de|desde))\s+([a-záéíóúñüü\-]{2,40})",
    re.IGNORECASE,
)
_BUDGET_PATTERN = re.compile(r"(\d{2,4})(?:\s*€|\s*eur(?:os)?)", re.IGNORECASE)
_TRAVELERS_PATTERN = re.compile(
    r"\b(?:para|somos)\s*(\d{1,2})\s*(?:personas?|viajeros?|adultos?)\b",
    re.IGNORECASE,
)
_DRIVE_PATTERN = re.compile(
    r"\b(?:máximo|max|hasta)\s*(\d{2,3})\s*(?:min|minutos)\b",
    re.IGNORECASE,
)
_DATE_PATTERN = re.compile(
    r"\b(\d{1,2})\s*(?:del|de|al|a|hasta|-)\s*(\d{1,2})\s*(?:de|del)?\s*([a-záéíóú]+)?\b",
    re.IGNORECASE,
)

_MONTHS = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "setiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}


class FakeAiProvider:
    """Produces explainable responses from rules, without external calls."""

    async def summarize_opportunity(
        self,
        request: OpportunitySummaryRequest,
    ) -> OpportunitySummaryResponse:
        return _rule_based_summary(request)

    async def interpret_search(
        self,
        request: InterpretSearchRequest,
    ) -> InterpretSearchResponse:
        return _rule_based_interpretation(request)

    async def generate_itinerary(
        self,
        request: ItineraryAiRequest,
    ) -> ItineraryAiResponse:
        return _rule_based_itinerary(request)

    async def generate_daily_report(
        self,
        request: DailyReportRequest,
    ) -> DailyReportResponse:
        return _rule_based_daily_report(request)


async def fallback_summary(
    request: OpportunitySummaryRequest,
) -> OpportunitySummaryResponse:
    """Rule-based fallback used when the AI provider is unavailable."""
    return _rule_based_summary(request)


async def fallback_interpretation(
    request: InterpretSearchRequest,
) -> InterpretSearchResponse:
    """Rule-based fallback for natural-language search interpretation."""
    return _rule_based_interpretation(request)


async def fallback_itinerary(
    request: ItineraryAiRequest,
) -> ItineraryAiResponse:
    """Rule-based fallback for orientative itinerary generation."""
    return _rule_based_itinerary(request)


async def fallback_daily_report(
    request: DailyReportRequest,
) -> DailyReportResponse:
    """Rule-based fallback for the personalized daily report."""
    return _rule_based_daily_report(request)


def _rule_based_summary(
    request: OpportunitySummaryRequest,
) -> OpportunitySummaryResponse:
    difference = request.budget_eur - request.total_cost_eur

    if difference >= 0:
        headline = "Buena opción dentro del presupuesto"
        pros: list[str] = [
            f"Está {difference:.2f} EUR por debajo del presupuesto",
            f"{request.travelers} viajeros, {request.useful_hours:.1f} horas útiles",
        ]
    else:
        headline = "Por encima del presupuesto"
        pros = [f"{request.travelers} viajeros, {request.useful_hours:.1f} horas útiles"]

    cons: list[str] = []
    if difference < 0:
        cons.append(f"Excede el presupuesto en {-difference:.2f} EUR")

    summary_parts = [
        f"Oportunidad para {request.destination} con coste total de "
        f"{request.total_cost_eur:.2f} EUR para {request.travelers} viajeros."
    ]
    if request.facts:
        summary_parts.append("Hechos considerados: " + ", ".join(request.facts) + ".")
    summary_parts.append("Estos precios están verificados a la hora indicada y pueden cambiar.")

    for fact in request.facts:
        if fact not in pros:
            pros.append(fact)

    return OpportunitySummaryResponse(
        headline=headline,
        summary=" ".join(summary_parts),
        pros=pros[:6],
        cons=cons,
        confidence=Confidence.MEDIUM,
        generated_by_ai=False,
    )


def _detect_interests(query: str) -> list[str]:
    lower = query.lower()
    detected: list[str] = []
    for interest, keywords in _INTEREST_KEYWORDS.items():
        if any(keyword in lower for keyword in keywords):
            detected.append(interest)
    return detected


def _rule_based_interpretation(
    request: InterpretSearchRequest,
) -> InterpretSearchResponse:
    query = request.query

    origin_match = _ORIGIN_PATTERN.search(query)
    origin_city = origin_match.group(1).strip().capitalize() if origin_match else None

    budget_match = _BUDGET_PATTERN.search(query)
    budget_eur = float(budget_match.group(1)) if budget_match else None

    travelers_match = _TRAVELERS_PATTERN.search(query)
    travelers = int(travelers_match.group(1)) if travelers_match else 2

    drive_match = _DRIVE_PATTERN.search(query)
    max_drive_minutes = int(drive_match.group(1)) if drive_match else None

    lower = query.lower()
    transport: TransportMode | None = None
    if any(word in lower for word in ("coche", "conducir", "por carretera")):
        transport = TransportMode.CAR
    elif any(word in lower for word in ("avión", "avion", "vuelo", "volando", "aeropuerto")):
        transport = TransportMode.FLIGHT

    start_window: date | None = None
    end_window: date | None = None
    date_match = _DATE_PATTERN.search(query)
    if date_match:
        month = date_match.group(3)
        month_number = _MONTHS.get((month or "").lower()) if month else None
        try:
            year = 2026
            start_day = int(date_match.group(1))
            end_day = int(date_match.group(2))
            if month_number is not None and end_day >= start_day:
                start_window = date(year, month_number, start_day)
                end_window = date(year, month_number, end_day)
        except ValueError:
            start_window = None
            end_window = None

    duration_days: int | None = None
    if start_window is not None and end_window is not None:
        duration_days = (end_window - start_window).days

    recognized = sum(
        item is not None for item in (origin_city, budget_eur, transport, start_window)
    )
    if recognized >= 3:
        confidence = Confidence.HIGH
    elif recognized >= 1:
        confidence = Confidence.MEDIUM
    else:
        confidence = Confidence.LOW

    return InterpretSearchResponse(
        origin_city=origin_city,
        budget_eur=budget_eur,
        travelers=travelers,
        preferred_transport=transport,
        interests=_detect_interests(query),
        max_drive_minutes=max_drive_minutes,
        start_window=start_window,
        end_window=end_window,
        duration_days=duration_days,
        confidence=confidence,
        generated_by_ai=False,
    )


def _rule_based_itinerary(request: ItineraryAiRequest) -> ItineraryAiResponse:
    days: list[ItineraryDay] = []
    current = request.start_date
    index = 1
    while current <= request.end_date:
        items: list[ItineraryItem] = []
        if request.interests:
            interest = request.interests[0]
            items.append(
                ItineraryItem(
                    start_time="10:00",
                    end_time="12:00",
                    title=f"Explorar la zona de interés: {interest}",
                )
            )
        items.append(
            ItineraryItem(
                start_time="14:00",
                end_time="15:30",
                title="Comida local",
            )
        )
        items.append(
            ItineraryItem(
                start_time="16:30",
                end_time="18:30",
                title="Paseo y tiempo libre",
            )
        )
        days.append(
            ItineraryDay(
                date=current,
                title=f"Día {index}",
                items=items,
            )
        )
        current += timedelta(days=1)
        index += 1

    return ItineraryAiResponse(
        summary=(
            f"Itinerario orientativo de {len(days)} días en {request.destination}. "
            "Las actividades y horarios son una propuesta general, no una reserva."
        ),
        warnings=[
            "Itinerario orientativo generado por reglas: confirma horarios, aperturas "
            "y precios reales antes de planificar.",
            "Los costes estimados no están incluidos porque no son datos verificados.",
        ],
        days=days,
        generated_by_ai=False,
    )


_PRICE_DROP_PERCENT = 5.0
_NEW_LOW_EUR = 0.0


def _rule_based_daily_report(request: DailyReportRequest) -> DailyReportResponse:
    """Aggregates confirmed price data into a rule-based daily report."""
    entries: list[DailyReportOpportunityEntry] = []
    for watch in request.watches:
        previous = watch.previous_total_eur
        change_eur: float | None = None
        change_percent: float | None = None
        if previous is not None:
            change_eur = round(previous - watch.current_total_eur, 2)
            if previous > 0:
                change_percent = round((change_eur / previous) * 100, 1)

        is_new_low = watch.min_recorded_eur is not None and (
            watch.current_total_eur <= watch.min_recorded_eur + _NEW_LOW_EUR
        )

        within_budget: bool | None = (
            None if watch.budget_eur is None else watch.current_total_eur <= watch.budget_eur
        )

        recommendation = _daily_recommendation(
            change_eur=change_eur,
            change_percent=change_percent,
            is_new_low=is_new_low,
            within_budget=within_budget,
        )

        entries.append(
            DailyReportOpportunityEntry(
                watch_name=watch.watch_name,
                destination=watch.destination,
                change_eur=change_eur,
                change_percent=change_percent,
                is_new_low=is_new_low,
                within_budget=within_budget,
                recommendation=recommendation,
                confidence=Confidence.HIGH,
            )
        )

    drops = [entry for entry in entries if (entry.change_eur or 0) > 0]
    new_lows = [entry for entry in entries if entry.is_new_low]

    if drops:
        headline = (
            f"{len(drops)} de {len(entries)} viajes vigilados bajaron de precio"
            if len(drops) > 1
            else f"{drops[0].destination} bajó de precio hoy"
        )
        summary = (
            "Los precios verificados hoy bajan respecto al registro anterior en "
            + ", ".join(f"{entry.destination} (-{entry.change_eur:.2f} EUR)" for entry in drops)
            + ". Verifica la disponibilidad antes de reservar; los precios pueden cambiar."
        )
    elif new_lows:
        headline = f"{new_lows[0].destination} marca un nuevo mínimo registrado"
        summary = (
            "Algunos viajes vigilados están en su mínimo registrado según las fuentes "
            "consultadas. Confirma horarios y disponibilidad antes de tomar una decisión."
        )
    else:
        headline = "Sin cambios importantes en tus viajes vigilados"
        summary = (
            "Los precios verificados hoy no presentan bajadas significativas frente al "
            "registro anterior. Mantener el seguimiento activo permite detectar cambios."
        )

    warnings = [
        "Informe orientativo basado en datos verificados a la hora indicada.",
        "Los precios y la disponibilidad pueden cambiar sin previo aviso.",
    ]

    return DailyReportResponse(
        headline=headline,
        summary=summary,
        entries=entries,
        warnings=warnings,
        generated_by_ai=False,
    )


def _daily_recommendation(
    *,
    change_eur: float | None,
    change_percent: float | None,
    is_new_low: bool,
    within_budget: bool | None,
) -> str:
    if is_new_low:
        return "Nuevo mínimo registrado: es un buen momento para verificar y valorar la reserva."
    if change_eur is not None and change_eur > 0:
        return f"Ha bajado {change_eur:.2f} EUR respecto al registro anterior."
    if change_eur is not None and change_eur < 0:
        return "El precio ha subido respecto al registro anterior."
    if within_budget is True:
        return "Dentro del presupuesto; puedes seguir vigilándolo."
    if within_budget is False:
        return "Por encima del presupuesto; conviene esperar una bajada."
    return "Sin cambios significativos; se mantiene el seguimiento."
