"""Tests for finite field construction and primitive root finding."""

import pytest

from breaking_proofs.oracle.field import (
    build_evaluation_domain,
    find_primitive_root_of_unity,
    make_field,
)


class TestMakeField:
    def test_gf5(self):
        GF = make_field(5)
        assert GF.order == 5

    def test_gf7(self):
        GF = make_field(7)
        assert GF.order == 7

    def test_gf11(self):
        GF = make_field(11)
        assert GF.order == 11


class TestPrimitiveRootOfUnity:
    def test_f5_4th_root(self):
        """F_5 has 4th roots of unity since 5 - 1 = 4."""
        omega = find_primitive_root_of_unity(5, 4)
        assert pow(omega, 4, 5) == 1
        assert pow(omega, 2, 5) != 1
        assert pow(omega, 1, 5) != 1

    def test_f7_6th_root(self):
        omega = find_primitive_root_of_unity(7, 6)
        assert pow(omega, 6, 7) == 1
        assert pow(omega, 3, 7) != 1
        assert pow(omega, 2, 7) != 1

    def test_f7_3rd_root(self):
        omega = find_primitive_root_of_unity(7, 3)
        assert pow(omega, 3, 7) == 1
        assert pow(omega, 1, 7) != 1

    def test_f7_2nd_root(self):
        omega = find_primitive_root_of_unity(7, 2)
        assert pow(omega, 2, 7) == 1
        assert omega != 1

    def test_invalid_no_root(self):
        """5 - 1 = 4, not divisible by 3, so no 3rd root of unity."""
        with pytest.raises(ValueError):
            find_primitive_root_of_unity(5, 3)

    def test_f13_4th_root(self):
        """13 - 1 = 12, divisible by 4."""
        omega = find_primitive_root_of_unity(13, 4)
        assert pow(omega, 4, 13) == 1
        assert pow(omega, 2, 13) != 1

    def test_f17_8th_root(self):
        """17 - 1 = 16, divisible by 8."""
        omega = find_primitive_root_of_unity(17, 8)
        assert pow(omega, 8, 17) == 1
        assert pow(omega, 4, 17) != 1


class TestBuildEvaluationDomain:
    def test_f5_multiplicative_group(self):
        """The multiplicative group F_5^x = {1, 2, 3, 4} has order 4."""
        domain = build_evaluation_domain(5, 4)
        assert len(domain) == 4
        assert set(domain) == {1, 2, 3, 4}

    def test_f7_full_group(self):
        domain = build_evaluation_domain(7, 6)
        assert len(domain) == 6
        assert set(domain) == {1, 2, 3, 4, 5, 6}

    def test_domain_is_cyclic(self):
        """Each element is omega^i, so domain forms a cyclic group."""
        domain = build_evaluation_domain(5, 4)
        for i, d in enumerate(domain):
            assert d == pow(domain[1], i, 5) if i > 0 else d == 1
