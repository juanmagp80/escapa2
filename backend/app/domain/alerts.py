"""Pure price-alert evaluation rules.

Alerts are only emitted when a significant change exists; repeated identical
events must not be sent twice (AGENTS.md 9.5 and 17).
"""

from __future__ import annotations

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
