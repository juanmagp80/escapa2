"""Tests for the price-alert evaluation rules."""

from __future__ import annotations

from app.domain.alerts import (
    AlertRuleCode,
    evaluate_price_alerts,
    parse_alert_rules,
)


def _evaluate(**kwargs) -> list:
    defaults = {
        "current_total_eur": 280.0,
        "previous_total_eur": 320.0,
        "min_recorded_eur": 300.0,
        "budget_eur": 350.0,
        "below_threshold_eur": None,
        "percent_drop_threshold": None,
        "absolute_drop_threshold_eur": None,
        "consecutive_rises": 0,
        "rises_to_alert": 0,
    }
    defaults.update(kwargs)
    return evaluate_price_alerts(**defaults)


def test_total_below_threshold_triggers() -> None:
    result = _evaluate(below_threshold_eur=300.0)
    codes = {item.rule for item in result if item.triggered}
    assert AlertRuleCode.TOTAL_BELOW_THRESHOLD in codes


def test_total_below_threshold_not_triggered_above() -> None:
    result = _evaluate(current_total_eur=350.0, below_threshold_eur=300.0)
    assert not any(item.triggered for item in result)


def test_percent_drop_triggers_at_threshold() -> None:
    result = _evaluate(
        current_total_eur=280.0, previous_total_eur=350.0, percent_drop_threshold=20.0
    )
    codes = {item.rule for item in result if item.triggered}
    assert AlertRuleCode.PERCENT_DROP in codes


def test_percent_drop_below_threshold_not_triggered() -> None:
    result = _evaluate(
        current_total_eur=340.0, previous_total_eur=350.0, percent_drop_threshold=20.0
    )
    assert not any(item.rule == AlertRuleCode.PERCENT_DROP and item.triggered for item in result)


def test_absolute_drop_triggers() -> None:
    result = _evaluate(
        current_total_eur=280.0,
        previous_total_eur=320.0,
        absolute_drop_threshold_eur=30.0,
    )
    codes = {item.rule for item in result if item.triggered}
    assert AlertRuleCode.ABSOLUTE_DROP in codes


def test_new_low_triggers() -> None:
    result = _evaluate(current_total_eur=280.0, min_recorded_eur=300.0)
    codes = {item.rule for item in result if item.triggered}
    assert AlertRuleCode.NEW_LOW in codes


def test_new_low_not_triggered_equal() -> None:
    result = _evaluate(current_total_eur=300.0, min_recorded_eur=300.0)
    assert not any(item.rule == AlertRuleCode.NEW_LOW and item.triggered for item in result)


def test_consecutive_rise_triggers() -> None:
    result = _evaluate(consecutive_rises=3, rises_to_alert=3)
    codes = {item.rule for item in result if item.triggered}
    assert AlertRuleCode.CONSECUTIVE_RISE in codes


def test_new_budget_match_triggers() -> None:
    result = _evaluate(current_total_eur=340.0, previous_total_eur=360.0, budget_eur=350.0)
    codes = {item.rule for item in result if item.triggered}
    assert AlertRuleCode.NEW_BUDGET_MATCH in codes


def test_new_budget_match_not_triggered_when_always_within_budget() -> None:
    result = _evaluate(current_total_eur=280.0, previous_total_eur=300.0, budget_eur=350.0)
    assert not any(
        item.rule == AlertRuleCode.NEW_BUDGET_MATCH and item.triggered for item in result
    )


def test_no_current_price_returns_no_alerts() -> None:
    result = _evaluate(current_total_eur=None)
    assert result == []


def test_alerts_include_explainable_messages() -> None:
    result = _evaluate(current_total_eur=280.0, min_recorded_eur=300.0)
    triggered = [item for item in result if item.triggered]
    assert len(triggered) >= 1
    assert all(item.message is not None for item in triggered)


def test_parse_alert_rules_extracts_thresholds() -> None:
    config = parse_alert_rules(
        [
            "Viaje por debajo de 350 EUR",
            "Bajada superior a 10%",
            "Bajada de 40 EUR",
            "Nuevo mínimo histórico",
            "Vuelve a estar dentro del presupuesto",
        ]
    )
    assert config.below_threshold_eur == 350.0
    assert config.percent_drop_threshold == 10.0
    assert config.absolute_drop_threshold_eur == 40.0
    assert config.new_low is True
    assert config.budget_match is True


def test_parse_alert_rules_ignores_unknown_rules() -> None:
    config = parse_alert_rules(["Regla desconocida", "otra cosa"])
    assert config.below_threshold_eur is None
    assert config.percent_drop_threshold is None
    assert config.new_low is False
    assert config.budget_match is False


def test_parse_alert_rules_handles_decimal_and_currency_variants() -> None:
    config = parse_alert_rules(["Bajada de 4,5%", "por debajo de 300€"])
    assert config.percent_drop_threshold == 4.5
    assert config.below_threshold_eur == 300.0
