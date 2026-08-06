"""Pure price-alert evaluation rules.

Alerts are only emitted when a significant change exists; repeated identical
events must not be sent twice (AGENTS.md 9.5 and 17).
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class AlertRule:
    """Configuration for a single price alert rule."""

    code: str
    active: bool = True


class AlertRuleCode:
    """Stable alert rule codes."""

    TOTAL_BELOW_THRESHOLD = "total_below_threshold"
    PERCENT_DROP = "percent_drop"
    ABSOLUTE_DROP = "absolute_drop"
    NEW_LOW = "new_low"
    CONSECUTIVE_RISE = "consecutive_rise"
    NEW_BUDGET_MATCH = "new_budget_match"


@dataclass(frozen=True)
class AlertEvaluation:
    """Result of evaluating one alert rule."""

    rule: str
    triggered: bool
    message: str | None = None


@dataclass(frozen=True)
class AlertConfig:
    """Structured thresholds extracted from human-readable rule strings."""

    below_threshold_eur: float | None = None
    percent_drop_threshold: float | None = None
    absolute_drop_threshold_eur: float | None = None
    new_low: bool = False
    budget_match: bool = False


_BELOW_THRESHOLD_PATTERN = re.compile(
    r"por debajo de\s*(\d+(?:[.,]\d+)?)\s*(?:€|eur(?:os)?)",
    re.IGNORECASE,
)
_PERCENT_DROP_PATTERN = re.compile(
    r"bajada(?: superior a| de)?\s*(\d+(?:[.,]\d+)?)\s*%",
    re.IGNORECASE,
)
_ABSOLUTE_DROP_PATTERN = re.compile(
    r"bajada(?:\s*de)?\s*(\d+(?:[.,]\d+)?)\s*(?:€|eur(?:os)?)",
    re.IGNORECASE,
)
_NEW_LOW_PATTERN = re.compile(r"nuevo mínimo", re.IGNORECASE)
_BUDGET_MATCH_PATTERN = re.compile(r"presupuesto", re.IGNORECASE)


def parse_alert_rules(rules: list[str]) -> AlertConfig:
    """Extract structured thresholds from human-readable rule strings.

    Recognized rules (case-insensitive, Spanish):
    - "Viaje por debajo de 350 EUR" -> below_threshold_eur.
    - "Bajada superior a 10%" or "Bajada de 5%" -> percent_drop_threshold.
    - "Bajada de 40 EUR" -> absolute_drop_threshold_eur.
    - "Nuevo mínimo histórico/registrado" -> new_low.
    - "Vuelve a estar dentro del presupuesto" -> budget_match.
    """
    config = AlertConfig()
    for rule in rules:
        below = _BELOW_THRESHOLD_PATTERN.search(rule)
        if below:
            config = AlertConfig(
                below_threshold_eur=_to_float(below.group(1)),
                percent_drop_threshold=config.percent_drop_threshold,
                absolute_drop_threshold_eur=config.absolute_drop_threshold_eur,
                new_low=config.new_low,
                budget_match=config.budget_match,
            )
            continue
        percent = _PERCENT_DROP_PATTERN.search(rule)
        if percent:
            config = AlertConfig(
                below_threshold_eur=config.below_threshold_eur,
                percent_drop_threshold=_to_float(percent.group(1)),
                absolute_drop_threshold_eur=config.absolute_drop_threshold_eur,
                new_low=config.new_low,
                budget_match=config.budget_match,
            )
            continue
        absolute = _ABSOLUTE_DROP_PATTERN.search(rule)
        if absolute:
            config = AlertConfig(
                below_threshold_eur=config.below_threshold_eur,
                percent_drop_threshold=config.percent_drop_threshold,
                absolute_drop_threshold_eur=_to_float(absolute.group(1)),
                new_low=config.new_low,
                budget_match=config.budget_match,
            )
            continue
        if _NEW_LOW_PATTERN.search(rule):
            config = AlertConfig(
                below_threshold_eur=config.below_threshold_eur,
                percent_drop_threshold=config.percent_drop_threshold,
                absolute_drop_threshold_eur=config.absolute_drop_threshold_eur,
                new_low=True,
                budget_match=config.budget_match,
            )
            continue
        if _BUDGET_MATCH_PATTERN.search(rule):
            config = AlertConfig(
                below_threshold_eur=config.below_threshold_eur,
                percent_drop_threshold=config.percent_drop_threshold,
                absolute_drop_threshold_eur=config.absolute_drop_threshold_eur,
                new_low=config.new_low,
                budget_match=True,
            )
    return config


def _to_float(value: str) -> float:
    return float(value.replace(",", "."))


def evaluate_price_alerts(
    *,
    current_total_eur: float | None,
    previous_total_eur: float | None,
    min_recorded_eur: float | None,
    budget_eur: float | None,
    below_threshold_eur: float | None,
    percent_drop_threshold: float | None,
    absolute_drop_threshold_eur: float | None,
    consecutive_rises: int,
    rises_to_alert: int,
) -> list[AlertEvaluation]:
    """Evaluate all configured price alerts and return the triggered ones.

    Rules:
    - TOTAL_BELOW_THRESHOLD: trip below an absolute threshold.
    - PERCENT_DROP: drop of at least ``percent_drop_threshold``.
    - ABSOLUTE_DROP: drop of at least ``absolute_drop_threshold_eur``.
    - NEW_LOW: current price is below the recorded minimum.
    - CONSECUTIVE_RISE: at least ``rises_to_alert`` rises in a row.
    - NEW_BUDGET_MATCH: previous price was over budget and now fits.
    """
    evaluations: list[AlertEvaluation] = []

    if current_total_eur is None:
        return evaluations

    if below_threshold_eur is not None and current_total_eur <= below_threshold_eur:
        evaluations.append(
            AlertEvaluation(
                rule=AlertRuleCode.TOTAL_BELOW_THRESHOLD,
                triggered=True,
                message=f"Viaje completo por debajo de {below_threshold_eur:g} EUR",
            )
        )

    if (
        previous_total_eur is not None
        and previous_total_eur > 0
        and percent_drop_threshold is not None
    ):
        drop_pct = (previous_total_eur - current_total_eur) / previous_total_eur * 100
        if drop_pct >= percent_drop_threshold:
            evaluations.append(
                AlertEvaluation(
                    rule=AlertRuleCode.PERCENT_DROP,
                    triggered=True,
                    message=f"Bajada del {drop_pct:.1f}% respecto a la última verificación",
                )
            )

    if (
        previous_total_eur is not None
        and absolute_drop_threshold_eur is not None
        and previous_total_eur - current_total_eur >= absolute_drop_threshold_eur
    ):
        evaluations.append(
            AlertEvaluation(
                rule=AlertRuleCode.ABSOLUTE_DROP,
                triggered=True,
                message=f"Bajada de {previous_total_eur - current_total_eur:g} EUR",
            )
        )

    if min_recorded_eur is not None and current_total_eur < min_recorded_eur:
        evaluations.append(
            AlertEvaluation(
                rule=AlertRuleCode.NEW_LOW,
                triggered=True,
                message=f"Nuevo mínimo histórico: {current_total_eur:g} EUR",
            )
        )

    if rises_to_alert > 0 and consecutive_rises >= rises_to_alert:
        evaluations.append(
            AlertEvaluation(
                rule=AlertRuleCode.CONSECUTIVE_RISE,
                triggered=True,
                message=f"{consecutive_rises} registros consecutivos al alza",
            )
        )

    if (
        budget_eur is not None
        and previous_total_eur is not None
        and previous_total_eur > budget_eur
        and current_total_eur <= budget_eur
    ):
        evaluations.append(
            AlertEvaluation(
                rule=AlertRuleCode.NEW_BUDGET_MATCH,
                triggered=True,
                message="El viaje vuelve a estar dentro del presupuesto",
            )
        )

    return evaluations
