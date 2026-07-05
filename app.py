"""
Rounded Currency Converter - Streamlit MVP

Shows the exact converted value and a rounded value.
Default rounding follows the original idea: round UP to the nearest whole unit.
"""

from __future__ import annotations

import math
from datetime import date
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP
from typing import Any

import requests
import streamlit as st

API_BASE = "https://api.frankfurter.dev/v2"

POPULAR_DEFAULTS = {
    "USD": "US Dollar",
    "EUR": "Euro",
    "GBP": "British Pound",
    "SAR": "Saudi Riyal",
    "AED": "UAE Dirham",
    "TRY": "Turkish Lira",
    "SLL": "Sierra Leonean Leone",
    "NGN": "Nigerian Naira",
    "GHS": "Ghanaian Cedi",
    "EGP": "Egyptian Pound",
    "CAD": "Canadian Dollar",
    "AUD": "Australian Dollar",
    "JPY": "Japanese Yen",
    "CNY": "Chinese Yuan",
    "INR": "Indian Rupee",
}

SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "SAR": "﷼",
    "AED": "د.إ",
    "TRY": "₺",
    "SLL": "Le",
    "NGN": "₦",
    "GHS": "₵",
    "EGP": "E£",
    "CAD": "C$",
    "AUD": "A$",
    "JPY": "¥",
    "CNY": "¥",
    "INR": "₹",
}


def money(value: float | Decimal, currency: str, decimals: int = 2) -> str:
    """Format a currency amount without relying on locale settings."""
    symbol = SYMBOLS.get(currency, currency)
    number = f"{float(value):,.{decimals}f}"
    return f"{symbol} {number}"


def decimalize(value: float | int | str | Decimal) -> Decimal:
    return Decimal(str(value))


def round_up_to_step(value: Decimal, step: Decimal) -> Decimal:
    if step <= 0:
        return value
    return (value / step).to_integral_value(rounding=ROUND_CEILING) * step


def round_nearest_to_step(value: Decimal, step: Decimal) -> Decimal:
    if step <= 0:
        return value
    return (value / step).to_integral_value(rounding=ROUND_HALF_UP) * step


def next_99_price(value: Decimal) -> Decimal:
    """Return the nearest price ending in .99 that is not below the exact value."""
    whole = value.to_integral_value(rounding=ROUND_FLOOR)
    candidate = whole + Decimal("0.99")
    if candidate < value:
        candidate = whole + Decimal("1.99")
    return candidate


def apply_rounding(value: Decimal, mode: str, custom_step: Decimal) -> Decimal:
    if mode == "Round up to nearest whole unit":
        return round_up_to_step(value, Decimal("1"))
    if mode == "Round to nearest whole unit":
        return round_nearest_to_step(value, Decimal("1"))
    if mode == "Round up to nearest 0.05":
        return round_up_to_step(value, Decimal("0.05"))
    if mode == "Round up to nearest 0.10":
        return round_up_to_step(value, Decimal("0.10"))
    if mode == "Smart price ending .99":
        return next_99_price(value)
    if mode == "Custom round-up step":
        return round_up_to_step(value, custom_step)
    return value


def normalize_currency_response(data: Any) -> dict[str, str]:
    """Support both simple and metadata-style currency API responses."""
    if not isinstance(data, dict):
        return POPULAR_DEFAULTS

    currencies: dict[str, str] = {}
    for code, value in data.items():
        code = str(code).upper()
        if isinstance(value, str):
            currencies[code] = value
        elif isinstance(value, dict):
            currencies[code] = (
                value.get("name")
                or value.get("currency")
                or value.get("description")
                or code
            )
        else:
            currencies[code] = code

    return currencies or POPULAR_DEFAULTS


@st.cache_data(ttl=60 * 60)
def get_currencies() -> dict[str, str]:
    """Fetch available currencies, with a fallback list for offline/API failure."""
    try:
        response = requests.get(f"{API_BASE}/currencies", timeout=10)
        response.raise_for_status()
        fetched = normalize_currency_response(response.json())
        return {**POPULAR_DEFAULTS, **fetched}
    except requests.RequestException:
        return POPULAR_DEFAULTS


@st.cache_data(ttl=60 * 30)
def get_rate(base: str, quote: str) -> tuple[Decimal, str]:
    """Fetch one exchange rate. Returns rate and API date."""
    if base == quote:
        return Decimal("1"), date.today().isoformat()

    response = requests.get(f"{API_BASE}/rate/{base}/{quote}", timeout=10)
    response.raise_for_status()
    data = response.json()

    rate = data.get("rate")
    if rate is None and isinstance(data.get("rates"), dict):
        rate = data["rates"].get(quote)

    if rate is None:
        raise ValueError("Rate was not found in the API response.")

    rate_date = data.get("date") or date.today().isoformat()
    return decimalize(rate), str(rate_date)

#Streamlit Codes
st.set_page_config(
    page_title="Rounded Currency Converter",
    page_icon="💱",
    layout="centered",
)

st.markdown(
    """
    <style>
    .main-card {
        padding: 1.25rem;
        border-radius: 1rem;
        border: 1px solid rgba(128, 128, 128, 0.20);
        background: rgba(128, 128, 128, 0.06);
    }
    .small-muted {
        color: #777;
        font-size: 0.90rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Rounded Currency Converter")
st.caption("Convert money, see the exact value, then see the rounded value for cleaner pricing.")

currencies = get_currencies()
codes = sorted(currencies.keys())


def currency_label(code: str) -> str:
    return f"{code} — {currencies.get(code, code)}"


with st.sidebar:
    st.header("Settings")
    from_currency = st.selectbox(
        "From currency",
        options=codes,
        index=codes.index("USD") if "USD" in codes else 0,
        format_func=currency_label,
    )
    to_currency = st.selectbox(
        "To currency",
        options=codes,
        index=codes.index("SAR") if "SAR" in codes else 0,
        format_func=currency_label,
    )

    amount = st.number_input(
        "Amount",
        min_value=0.01,
        value=100.00,
        step=1.00,
        format="%.2f",
    )

    rounding_mode = st.selectbox(
        "Rounding mode",
        [
            "Round up to nearest whole unit",
            "Round to nearest whole unit",
            "Round up to nearest 0.05",
            "Round up to nearest 0.10",
            "Smart price ending .99",
            "Custom round-up step",
        ],
    )

    custom_step = Decimal("1")
    if rounding_mode == "Custom round-up step":
        custom_step_input = st.number_input(
            "Custom step",
            min_value=0.01,
            value=5.00,
            step=0.50,
            format="%.2f",
            help="Example: 5 means round up to 5, 10, 15, etc.",
        )
        custom_step = decimalize(custom_step_input)

try:
    rate, rate_date = get_rate(from_currency, to_currency)
    exact = decimalize(amount) * rate
    rounded = apply_rounding(exact, rounding_mode, custom_step)
    difference = rounded - exact

    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("Result")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Exact converted value", money(exact, to_currency, 2))
    with col2:
        st.metric("Rounded value", money(rounded, to_currency, 2))

    st.divider()

    st.write(
        f"**{money(amount, from_currency, 2)} {from_currency}** = "
        f"**{money(exact, to_currency, 2)} {to_currency}**"
    )

    st.write(f"**Rounded result:** {money(rounded, to_currency, 2)} {to_currency}")
    st.write(f"**Rounding difference:** {money(difference, to_currency, 2)} {to_currency}")

    st.caption(
        f"Rate used: 1 {from_currency} = {rate:.6f} {to_currency}. "
        f"Rate date: {rate_date}."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.info(
        "This is useful when you want a cleaner price after conversion, "
        "for example converting $100 to SAR and rounding it up for a customer-facing price."
    )

except Exception as exc:
    st.error("I could not fetch the exchange rate right now.")
    st.write("Check your internet connection or try another currency pair.")
    with st.expander("Technical details"):
        st.code(str(exc))

with st.expander("How the rounding works"):
    st.write(
        "The exact conversion is calculated first. Then the selected rounding rule is applied. "
        "The default option rounds upward to the nearest whole currency unit, matching the original simple idea."
    )
    st.code(
        "exact_value = amount * exchange_rate\n"
        "rounded_value = ceil(exact_value)  # default mode",
        language="python",
    )

st.markdown("---")
st.caption("Built with Streamlit + Frankfurter API. Not financial advice; exchange rates can change.")
