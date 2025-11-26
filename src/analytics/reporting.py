"""Funciones de formateo y reporting."""
import pandas as pd


def format_currency(value: float, currency: str = "$") -> str:
    if value is None:
        return "N/A"
    return f"{currency}{value:,.2f}"


def format_percentage(value: float) -> str:
    if value is None:
        return "N/A"
    return f"{value * 100:.2f}%"


def format_number(value: float) -> str:
    if value is None:
        return "N/A"
    return f"{value:,.0f}"


def format_roas(value: float) -> str:
    if value is None:
        return "N/A"
    return f"{value:.2f}x"
