"""Pure value-score calculation rules.

The value score is transparent and configurable. Each component is normalized
to 0..100 and combined with the fixed weights documented in AGENTS.md 9.6.
"""

from __future__ import annotations

from dataclasses import dataclass

_BUDGET_FIT_WEIGHT = 0.30
_RELATIVE_PRICE_WEIGHT = 0.25
_USEFUL_TIME_WEIGHT = 0.20
_SCHEDULE_FIT_WEIGHT = 0.15
_COMFORT_WEIGHT = 0.10


@dataclass(frozen=True)
class ValueScoreBreakdown:
    """Normalized components that explain the final score."""

    budget_fit_score: float
    relative_price_score: float
    useful_time_score: float
    schedule_fit_score: float
    comfort_score: float

    @property
    def value_score(self) -> float:
        return round(
            self.budget_fit_score * _BUDGET_FIT_WEIGHT
            + self.relative_price_score * _RELATIVE_PRICE_WEIGHT
            + self.useful_time_score * _USEFUL_TIME_WEIGHT
            + self.schedule_fit_score * _SCHEDULE_FIT_WEIGHT
            + self.comfort_score * _COMFORT_WEIGHT,
            1,
        )


def clamp_score(value: float) -> float:
    """Clamp a component score to the 0..100 range."""
    return max(0.0, min(100.0, value))


def budget_fit_score(total_cost_eur: float, budget_eur: float | None) -> float | None:
    """Score how well the trip fits the budget.

    Returns None when the budget is unknown or the trip cost is missing. A trip
    at or below 70%% of the budget scores 100; at the budget it scores 60;
    over budget it drops proportionally.
    """
    if budget_eur is None or budget_eur <= 0:
        return None
    if total_cost_eur <= budget_eur * 0.7:
        return 100.0
    if total_cost_eur <= budget_eur:
        ratio = (budget_eur - total_cost_eur) / (budget_eur * 0.3)
        return 60.0 + ratio * 40.0
    return clamp_score(60.0 * (budget_eur / total_cost_eur))


def relative_price_score(
    total_cost_eur: float,
    reference_min_eur: float,
    reference_max_eur: float,
) -> float | None:
    """Score the trip price relative to observed alternatives.

    The cheapest option scores 100 and the most expensive 0.
    Returns None when the reference range is invalid.
    """
    if reference_max_eur <= reference_min_eur:
        return None
    if total_cost_eur <= reference_min_eur:
        return 100.0
    if total_cost_eur >= reference_max_eur:
        return 0.0
    span = reference_max_eur - reference_min_eur
    return clamp_score(100.0 * (reference_max_eur - total_cost_eur) / span)


def useful_time_score(
    useful_hours: float,
    target_hours: float = 24.0,
    max_hours: float = 48.0,
) -> float | None:
    """Score how much useful time the trip offers.

    Returns None when the trip has no useful hours. Reaching [targetHours]
    scores 100 and anything at or beyond [maxHours] also scores 100.
    """
    if useful_hours <= 0:
        return None
    if useful_hours >= target_hours:
        return 100.0
    return clamp_score(100.0 * useful_hours / max_hours)


def schedule_fit_score(
    matches_weekend: bool,
    within_vacation: bool,
) -> float:
    """Score how well the schedule matches the availability windows."""
    if matches_weekend and within_vacation:
        return 100.0
    if matches_weekend or within_vacation:
        return 60.0
    return 0.0


def comfort_score(
    direct_transport: bool,
    free_cancellation: bool,
    parking_available: bool,
) -> float:
    """Score comfort based on trip conveniences."""
    score = 0.0
    if direct_transport:
        score += 40.0
    if free_cancellation:
        score += 35.0
    if parking_available:
        score += 25.0
    return score
