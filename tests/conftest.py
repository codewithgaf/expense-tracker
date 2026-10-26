"""Shared fixtures. pytest loads this file automatically; no import is needed."""

from datetime import date

import pytest

from app import Expense, ExpenseTracker


@pytest.fixture
def data_file(tmp_path):
    """Path to a data file inside a temporary folder.

    tmp_path is built into pytest: a fresh empty folder for each test, deleted
    afterwards. Tests therefore never touch your real expenses.json.
    """
    return tmp_path / "expenses.json"


@pytest.fixture
def tracker(data_file):
    """An empty ExpenseTracker that saves to the temporary data file."""
    return ExpenseTracker(str(data_file))


@pytest.fixture
def make_expense():
    """A factory that builds valid Expense objects with sensible defaults.

    Usage in a test:  make_expense(item="Pizza", amount=250)
    """

    def _make(date_text=None, item="Lunch", category="Food", amount=100):
        if date_text is None:
            date_text = date.today().isoformat()
        return Expense(date_text, item, category, amount)

    return _make