"""Pydantic schemas for the AI layer."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator

from app.domain.enums import Confidence, TransportMode

__all__ = ["Confidence", "TransportMode"]


class OpportunitySummaryRequest(BaseModel):
    """Input for an AI-generated summary of a travel opportunity."""

    destination: str = Field(..., min_length=1, max_length=120)
    travelers: int = Field(..., ge=1, le=20)
    total_cost_eur: float = Field(..., ge=0)
    budget_eur: float = Field(..., ge=0)
    useful_hours: float = Field(..., ge=0)
    transport_mode: TransportMode
    verified_at: datetime
    facts: list[str] = Field(default_factory=list, max_length=30)

    @model_validator(mode="after")
    def _validate_facts(self) -> OpportunitySummaryRequest:
        cleaned: list[str] = []
        for fact in self.facts:
            fact = fact.strip()
            if fact:
                cleaned.append(fact)
        self.facts = cleaned
        return self


class OpportunitySummaryResponse(BaseModel):
    """Structured summary produced by the AI layer."""

    headline: str
    summary: str
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)
    confidence: Confidence
    generated_by_ai: bool


class InterpretSearchRequest(BaseModel):
    """Natural-language search request to be interpreted."""

    query: str = Field(..., min_length=1, max_length=500)

    @model_validator(mode="after")
    def _strip_query(self) -> InterpretSearchRequest:
        self.query = self.query.strip()
        return self


class InterpretSearchResponse(BaseModel):
    """Structured interpretation of a natural-language search."""

    origin_city: str | None = None
    budget_eur: float | None = None
    travelers: int | None = None
    preferred_transport: TransportMode | None = None
    interests: list[str] = Field(default_factory=list)
    max_drive_minutes: int | None = None
    start_window: date | None = None
    end_window: date | None = None
    duration_days: int | None = None
    confidence: Confidence
    generated_by_ai: bool


class ItineraryItem(BaseModel):
    """A single planned activity inside a day."""

    start_time: str
    end_time: str
    title: str
    estimated_cost_eur: float | None = None
    source_place_id: str | None = None


class ItineraryDay(BaseModel):
    """One day of the generated itinerary."""

    date: date
    title: str
    items: list[ItineraryItem] = Field(default_factory=list)


class ItineraryAiRequest(BaseModel):
    """Confirmed structured data used to generate an orientative itinerary."""

    destination: str = Field(..., min_length=1, max_length=120)
    start_date: date
    end_date: date
    transport_mode: TransportMode
    budget_eur: float = Field(..., ge=0)
    interests: list[str] = Field(default_factory=list, max_length=20)
    facts: list[str] = Field(default_factory=list, max_length=30)

    @model_validator(mode="after")
    def _validate_range(self) -> ItineraryAiRequest:
        if self.end_date < self.start_date:
            raise ValueError("end_date must not be earlier than start_date")
        return self

    @model_validator(mode="after")
    def _clean_lists(self) -> ItineraryAiRequest:
        self.interests = [item.strip() for item in self.interests if item.strip()]
        self.facts = [item.strip() for item in self.facts if item.strip()]
        return self


class ItineraryAiResponse(BaseModel):
    """Structured orientative itinerary validated before use."""

    summary: str
    warnings: list[str] = Field(default_factory=list)
    days: list[ItineraryDay]
    generated_by_ai: bool
