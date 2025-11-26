"""Tests para metricas."""
import pytest
from src.analytics.metrics import calc_ctr, calc_cpc, calc_roas


def test_calc_ctr():
    assert calc_ctr(100, 1000) == 0.1
    assert calc_ctr(0, 1000) == 0.0
    assert calc_ctr(100, 0) is None


def test_calc_cpc():
    assert calc_cpc(100, 50) == 2.0
    assert calc_cpc(100, 0) is None


def test_calc_roas():
    assert calc_roas(1000, 500) == 2.0
    assert calc_roas(1000, 0) is None
