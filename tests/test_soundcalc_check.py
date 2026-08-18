"""Tests for UDR/JBR regime classification and significance checking."""

import math

from breaking_proofs.report.soundcalc_check import (
    Regime,
    classify_hit,
    classify_regime,
    jbr_bound,
    udr_bound,
)


class TestRegimeBounds:
    def test_udr_bound_quarter_rate(self):
        assert udr_bound(0.25) == (1 - 0.25) / 2  # 0.375

    def test_jbr_bound_quarter_rate(self):
        assert jbr_bound(0.25) == 1 - math.sqrt(0.25)  # 0.5

    def test_udr_bound_eighth_rate(self):
        assert abs(udr_bound(0.125) - 0.4375) < 1e-9

    def test_jbr_bound_eighth_rate(self):
        expected = 1 - math.sqrt(0.125)
        assert abs(jbr_bound(0.125) - expected) < 1e-9

    def test_udr_bound_sixteenth_rate(self):
        assert abs(udr_bound(0.0625) - 0.46875) < 1e-9

    def test_jbr_bound_sixteenth_rate(self):
        assert jbr_bound(0.0625) == 1 - 0.25  # 0.75


class TestClassifyRegime:
    def test_udr_regime(self):
        assert classify_regime(0.2, 0.25) == Regime.UDR

    def test_udr_at_boundary(self):
        assert classify_regime(0.375, 0.25) == Regime.UDR

    def test_jbr_regime(self):
        assert classify_regime(0.4, 0.25) == Regime.JBR

    def test_beyond_regime(self):
        assert classify_regime(0.6, 0.25) == Regime.BEYOND

    def test_beyond_at_jbr_boundary(self):
        assert classify_regime(0.5, 0.25) == Regime.BEYOND

    def test_jbr_regime_eighth_rate(self):
        assert classify_regime(0.5, 0.125) == Regime.JBR

    def test_udr_regime_deep_below(self):
        assert classify_regime(0.01, 0.125) == Regime.UDR


class TestClassifyHit:
    def test_udr_not_significant(self):
        result = classify_hit(0.2, 0.25)
        assert result.regime == Regime.UDR
        assert result.is_significant is False
        assert result.current_bound == udr_bound(0.25)

    def test_jbr_is_significant(self):
        result = classify_hit(0.4, 0.25)
        assert result.regime == Regime.JBR
        assert result.is_significant is True
        assert result.current_bound == udr_bound(0.25)

    def test_beyond_is_significant(self):
        result = classify_hit(0.6, 0.25)
        assert result.regime == Regime.BEYOND
        assert result.is_significant is True
        assert result.current_bound == jbr_bound(0.25)

    def test_measured_value_equals_theta(self):
        result = classify_hit(0.42, 0.25)
        assert result.measured_value == 0.42
        assert result.theta == 0.42

    def test_result_contains_both_bounds(self):
        result = classify_hit(0.4, 0.25)
        assert result.udr_bound == udr_bound(0.25)
        assert result.jbr_bound == jbr_bound(0.25)

    def test_result_is_frozen(self):
        result = classify_hit(0.4, 0.25)
        try:
            result.regime = Regime.UDR  # type: ignore[misc]
            raise AssertionError("Should raise")
        except AttributeError:
            pass

    def test_eighth_rate_gap_hit(self):
        result = classify_hit(0.5, 0.125)
        assert result.regime == Regime.JBR
        assert result.is_significant is True

    def test_sixteenth_rate_deep_gap(self):
        result = classify_hit(0.6, 0.0625)
        assert result.regime == Regime.JBR
        assert result.is_significant is True
        assert result.udr_bound < result.theta < result.jbr_bound
