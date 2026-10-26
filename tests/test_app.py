"""Unit tests for the Expense class and the parse_* helper functions."""

from datetime import date, timedelta

import pytest

from app import (
    Expense,
    parse_amount,
    parse_category,
    parse_date,
    parse_date_or_today,
    parse_item,
)

TODAY = date.today().isoformat()
TOMORROW = (date.today() + timedelta(days=1)).isoformat()


# ---------- Creating a valid Expense ----------


def test_valid_expense_stores_clean_values():
    expense = Expense("2026-10-01", "  pizza ", "  fOOD ", "150")

    assert expense.date == "2026-10-01"
    assert expense.item == "Pizza"
    assert expense.category == "Food"
    assert expense.amount == 150.0


def test_amount_is_rounded_to_two_decimals():
    assert Expense(TODAY, "Lunch", "Food", 10.126).amount == 10.13
    assert Expense(TODAY, "Lunch", "Food", "10.126").amount == 10.13


def test_date_is_normalized_to_iso_format():
    assert Expense("2026-1-5", "Lunch", "Food", 10).date == "2026-01-05"


def test_today_is_a_valid_date():
    assert Expense(TODAY, "Lunch", "Food", 10).date == TODAY


# ---------- Rejecting invalid input ----------


@pytest.mark.parametrize("item", ["", "   ", "\t\n"])
def test_empty_item_is_rejected(item):
    with pytest.raises(ValueError, match="Item cannot be empty"):
        Expense(TODAY, item, "Food", 10)


@pytest.mark.parametrize("category", ["gaming", "", "   ", "foods"])
def test_unknown_category_is_rejected(category):
    with pytest.raises(ValueError, match="Choose one of"):
        Expense(TODAY, "Lunch", category, 10)


@pytest.mark.parametrize(
    "amount, message",
    [
        ("abc", "valid number"),
        ("", "valid number"),
        ("12,5", "valid number"),
        (None, "valid number"),
        ("nan", "finite"),
        ("inf", "finite"),
        ("-inf", "finite"),
        (0, "greater than zero"),
        (-5, "greater than zero"),
        (0.001, "greater than zero"),  # rounds to 0.0, so it must be rejected
    ],
)
def test_invalid_amount_is_rejected(amount, message):
    with pytest.raises(ValueError, match=message):
        Expense(TODAY, "Lunch", "Food", amount)


@pytest.mark.parametrize("bad_date", ["2026-13-45", "25-10-2026", "yesterday", ""])
def test_badly_formatted_date_is_rejected(bad_date):
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        Expense(bad_date, "Lunch", "Food", 10)


def test_future_date_is_rejected():
    with pytest.raises(ValueError, match="future"):
        Expense(TOMORROW, "Lunch", "Food", 10)


# ---------- The size property ----------


@pytest.mark.parametrize(
    "amount, expected_size",
    [
        (0.01, "Small"),
        (99.99, "Small"),
        (100, "Medium"),  # boundary: exactly 100 is Medium
        (999.99, "Medium"),
        (1000, "Large"),  # boundary: exactly 1000 is Large
        (25000, "Large"),
    ],
)
def test_size_classification(amount, expected_size):
    assert Expense(TODAY, "Lunch", "Food", amount).size == expected_size


def test_size_is_read_only(make_expense):
    expense = make_expense()
    with pytest.raises(AttributeError):
        expense.size = "Large"


def test_size_is_calculated_from_the_current_amount(make_expense):
    expense = make_expense(amount=50)
    assert expense.size == "Small"

    expense.amount = 5000
    assert expense.size == "Large"  # no stale stored value


# ---------- to_dict ----------


def test_to_dict_contains_all_fields(make_expense):
    expense = make_expense(date_text="2026-10-01", item="Pizza", category="Food", amount=250)

    assert expense.to_dict() == {
        "date": "2026-10-01",
        "item": "Pizza",
        "category": "Food",
        "amount": 250.0,
        "size": "Medium",
    }


def test_changing_the_dict_does_not_change_the_expense(make_expense):
    expense = make_expense(item="Pizza")
    data = expense.to_dict()
    data["item"] = "Hacked"

    assert expense.item == "Pizza"


# ---------- from_dict ----------


def test_from_dict_round_trip(make_expense):
    original = make_expense(date_text="2026-10-01", item="Pizza", amount=250)
    rebuilt = Expense.from_dict(original.to_dict())

    assert rebuilt.to_dict() == original.to_dict()


def test_from_dict_recalculates_size_instead_of_trusting_the_file():
    record = {"date": "2026-10-01", "item": "Tea", "category": "Food", "amount": 10, "size": "Large"}

    assert Expense.from_dict(record).size == "Small"


def test_from_dict_without_a_date_uses_today():
    record = {"item": "Old record", "category": "Food", "amount": 10}

    assert Expense.from_dict(record).date == TODAY


@pytest.mark.parametrize(
    "record",
    [
        "not a dictionary",
        None,
        [],
        {"item": "X", "category": "Food"},  # no amount
        {"item": "X", "category": "Food", "amount": True},  # a bool is not a real number
        {"item": "X", "category": "Food", "amount": "12"},  # numbers must not be text
        {"item": "X", "category": "Food", "amount": float("nan")},
        {"item": "X", "category": "Food", "amount": -1},
        {"item": 5, "category": "Food", "amount": 1},
        {"item": "", "category": "Food", "amount": 1},
        {"item": "X", "category": 5, "amount": 1},
        {"item": "X", "category": "Gaming", "amount": 1},
        {"item": "X", "category": "Food", "amount": 1, "date": 20261025},
        {"item": "X", "category": "Food", "amount": 1, "date": "not-a-date"},
    ],
)
def test_from_dict_rejects_invalid_records(record):
    with pytest.raises(ValueError):
        Expense.from_dict(record)


# ---------- Text representations ----------


def test_str_is_friendly(make_expense):
    expense = make_expense(date_text="2026-10-01", item="Pizza", amount=1500)

    assert str(expense) == "2026-10-01  Pizza (Food): ₱1,500.00"


def test_repr_shows_how_to_rebuild_the_object(make_expense):
    expense = make_expense(date_text="2026-10-01", item="Pizza", amount=150)

    assert repr(expense) == (
        "Expense(date='2026-10-01', item='Pizza', category='Food', amount=150.0)"
    )


# ---------- The parse_* helpers ----------


def test_parse_amount_accepts_numbers_and_text():
    assert parse_amount(12) == 12.0
    assert parse_amount("12.5") == 12.5
    assert parse_amount("  7 ") == 7.0


def test_parse_item_cleans_the_text():
    assert parse_item("  coffee beans ") == "Coffee Beans"


def test_parse_category_cleans_the_text():
    assert parse_category(" tRANSPORT ") == "Transport"


def test_parse_date_returns_iso_text():
    assert parse_date(" 2026-10-01 ") == "2026-10-01"


@pytest.mark.parametrize("blank", ["", "   "])
def test_parse_date_or_today_treats_blank_as_today(blank):
    assert parse_date_or_today(blank) == TODAY


def test_parse_date_or_today_passes_real_dates_through():
    assert parse_date_or_today("2026-10-01") == "2026-10-01"