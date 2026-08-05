"""Tests for the value score calculation rules."""

from __future__ import annotations

import math

from app.domain.scoring import (
    ValueScoreBreakdown,
    budget_fit_score,
    clamp_score,
    comfort_score,
    relative_price_score,
    schedule_fit_score,
    useful_time_score,
)


def test_budget_fit_score_below_70_percent_scores_full() -> None:
    assert budget_fit_score(200.0, 350.0) == 100.0


def test_budget_fit_score_at_budget_scores_60() -> None:
    assert math.isclose(budget_fit_score(350.0, 350.0), 60.0)


def test_budget_fit_score_over_budget_drops() -> None:
    score = budget_fit_score(400.0, 350.0)
    assert score is not None
    assert score < 60.0
    assert 50.0 < score < 60.0


def test_budget_fit_score_unknown_budget_is_none() -> None:
    assert budget_fit_score(200.0, None) is None


def test_relative_price_score_cheapest_is_100() -> None:
    assert relative_price_score(100.0, 100.0, 200.0) == 100.0


def test_relative_price_score_most_expensive_is_0() -> None:
    assert relative_price_score(200.0, 100.0, 200.0) == 0.0


def test_relative_price_score_midpoint_is_50() -> None:
    assert math.isclose(relative_price_score(150.0, 100.0, 200.0), 50.0)


def test_relative_price_score_invalid_range_is_none() -> None:
    assert relative_price_score(150.0, 200.0, 200.0) is None


def test_useful_time_score_reaching_target_is_100() -> None:
    assert useful_time_score(24.0) == 100.0


def test_useful_time_score_scales_below_target() -> None:
    assert math.isclose(useful_time_score(12.0), 25.0)


def test_useful_time_score_no_hours_is_none() -> None:
    assert useful_time_score(0.0) is None


def test_schedule_fit_score_both_matches_is_100() -> None:
    assert schedule_fit_score(True, True) == 100.0


def test_schedule_fit_score_single_match_is_60() -> None:
    assert schedule_fit_score(True, False) == 60.0
    assert schedule_fit_score(False, True) == 60.0


def test_schedule_fit_score_no_match_is_0() -> None:
    assert schedule_fit_score(False, False) == 0.0


def test_comfort_score_all_conveniences() -> None:
    assert comfort_score(True, True, True) == 100.0


def test_comfort_score_no_conveniences() -> None:
    assert comfort_score(False, False, False) == 0.0


def test_value_score_breakdown_combines_weights() -> None:
    breakdown = ValueScoreBreakdown(
        budget_fit_score=100.0,
        relative_price_score=100.0,
        useful_time_score=100.0,
        schedule_fit_score=100.0,
        comfort_score=100.0,
    )
    assert breakdown.value_score == 100.0


def test_value_score_breakdown_mixed() -> None:
    breakdown = ValueScoreBreakdown(
        budget_fit_score=100.0,
        relative_price_score=50.0,
        useful_time_score=50.0,
        schedule_fit_score=60.0,
        comfort_score=0.0,
    )
    expected = 100.0 * 0.30 + 50.0 * 0.25 + 50.0 * 0.20 + 60.0 * 0.15 + 0.0 * 0.10
    assert math.isclose(breakdown.value_score, round(expected, 1))


def test_clamp_score_limits_to_range() -> None:
    assert clamp_score(-10.0) == 0.0
    assert clamp_score(150.0) == 100.0
    assert clamp_score(55.0) == 55.0
