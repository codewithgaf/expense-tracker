"""Expense Tracker - Module 3, Step 5: Objects and Classes

Two classes do the work:
    Expense         - ONE validated expense (its data and its own behavior)
    ExpenseTracker  - the COLLECTION: loading, saving, totals, budget checks

Everything else in this file is input/output: what the user sees and types.
"""

import json
import math
import os
from datetime import date, datetime

# ---------- Configuration (constants) ----------

DATA_FILE = "expenses.json"
CHART_FILE = "spending_chart.png"

# Single source of truth: the keys are the allowed categories.
BUDGET_LIMITS = {
    "Food": 3000,
    "Transport": 1500,
    "School": 2000,
    "Bills": 5000,
    "Other": 1000,
}

SMALL_LIMIT = 100      # below this -> Small
MEDIUM_LIMIT = 1000    # below this -> Medium, otherwise Large


# ---------- Parsers: turn raw values into valid ones, or raise ValueError ----------

def parse_amount(value):
    """Return a valid money amount (rounded to 2 decimals), or raise ValueError."""
    try:
        amount = float(value)
    except (ValueError, TypeError):
        raise ValueError("Please enter a valid number.") from None

    if not math.isfinite(amount):
        raise ValueError("Amount must be a finite number.")

    amount = round(amount, 2)  # round BEFORE checking, so 0.001 is rejected

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    return amount


def parse_date(value):
    """Return a clean YYYY-MM-DD string, or raise ValueError."""
    try:
        parsed = datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Use the format YYYY-MM-DD, e.g. 2026-10-25.") from None

    if parsed > date.today():
        raise ValueError("Date cannot be in the future.")

    return parsed.isoformat()


def parse_date_or_today(value):
    """Like parse_date, but an empty answer means today."""
    if not str(value).strip():
        return date.today().isoformat()
    return parse_date(value)


def parse_item(value):
    """Return a cleaned item name, or raise ValueError if it is empty."""
    item = str(value).strip().title()
    if not item:
        raise ValueError("Item cannot be empty.")
    return item


def parse_category(value):
    """Return a cleaned category, or raise ValueError if it isn't allowed."""
    category = str(value).strip().title()
    if category not in BUDGET_LIMITS:
        raise ValueError(f"Choose one of: {', '.join(sorted(BUDGET_LIMITS))}.")
    return category


# ---------- Class 1: one expense ----------

class Expense:
    """One validated expense. An invalid Expense can never be created."""

    def __init__(self, date_text, item, category, amount):
        # The constructor is the gatekeeper: every field is validated here.
        self.date = parse_date(date_text)
        self.item = parse_item(item)
        self.category = parse_category(category)
        self.amount = parse_amount(amount)

    @property
    def size(self):
        """'Small', 'Medium' or 'Large'. Calculated from the amount, never stored."""
        if self.amount < SMALL_LIMIT:
            return "Small"
        elif self.amount < MEDIUM_LIMIT:
            return "Medium"
        return "Large"

    def to_dict(self):
        """Plain dictionary, used for saving to JSON and for the Pandas analysis."""
        return {
            "date": self.date,
            "item": self.item,
            "category": self.category,
            "amount": self.amount,
            "size": self.size,
        }

    @classmethod
    def from_dict(cls, record):
        """Build an Expense from a loaded JSON record, or raise ValueError."""
        if not isinstance(record, dict):
            raise ValueError("Record must be a dictionary.")

        amount = record.get("amount")
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise ValueError("Amount must be a number.")

        item = record.get("item")
        category = record.get("category")
        if not isinstance(item, str) or not isinstance(category, str):
            raise ValueError("Item and category must be text.")

        raw_date = record.get("date")
        if raw_date is None:
            # Saved before dates existed (Module 3 step 4): use today's date.
            raw_date = date.today().isoformat()
        elif not isinstance(raw_date, str):
            raise ValueError("Date must be text.")

        return cls(raw_date, item, category, amount)

    def __str__(self):
        """Friendly text, used by print()."""
        return f"{self.date}  {self.item} ({self.category}): ₱{self.amount:,.2f}"

    def __repr__(self):
        """Developer text, shown in the Python shell and in error messages."""
        return (f"Expense(date={self.date!r}, item={self.item!r}, "
                f"category={self.category!r}, amount={self.amount!r})")


# ---------- Class 2: the collection ----------

class ExpenseTracker:
    """Holds all expenses and knows how to load, save, total and check budgets."""

    def __init__(self, filename):
        self.filename = filename
        self.expenses = []     # a list of Expense objects (composition)
        self.skipped = 0       # invalid records found while loading

    def __len__(self):
        return len(self.expenses)

    # --- file handling ---

    def load(self):
        """Load expenses from the JSON file, skipping invalid records."""
        self.expenses = []
        self.skipped = 0

        try:
            with open(self.filename, encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            return  # first run: no file yet, which is normal
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._keep_corrupt_copy()
            return
        except OSError as error:
            print(f"Warning: could not open {self.filename} ({error}).")
            return

        if not isinstance(data, list):
            self._keep_corrupt_copy()
            return

        for record in data:
            try:
                self.expenses.append(Expense.from_dict(record))
            except ValueError:
                self.skipped += 1

    def save(self):
        """Save all expenses to the JSON file. Returns True on success."""
        try:
            with open(self.filename, "w", encoding="utf-8") as file:
                json.dump(self.to_dicts(), file, indent=2)
        except OSError as error:
            print(f"Warning: could not save your data ({error}).")
            return False
        return True

    def _keep_corrupt_copy(self):
        """Move an unreadable file aside so we never destroy the user's data.

        The leading underscore is a convention: "internal, not for outside use".
        """
        backup = self.filename + ".corrupt"
        os.replace(self.filename, backup)
        print(f"Warning: {self.filename} could not be read.")
        print(f"A copy was kept as {backup}. Starting with an empty list.")

    # --- adding and converting ---

    def add(self, expense):
        """Add an Expense and save to disk."""
        self.expenses.append(expense)
        return self.save()

    def to_dicts(self):
        """All expenses as a list of dictionaries."""
        return [expense.to_dict() for expense in self.expenses]

    # --- calculations ---

    def total_spent(self):
        """Total of every expense."""
        return sum(expense.amount for expense in self.expenses)

    def totals_by_category(self):
        """Return {category: total_spent}, including categories with no spending."""
        totals = {category: 0.0 for category in BUDGET_LIMITS}
        for expense in self.expenses:
            totals[expense.category] += expense.amount
        return totals

    def amount_over_budget(self, category):
        """How far a category is over its limit (0 if it isn't over)."""
        spent = self.totals_by_category()[category]
        return max(0.0, spent - BUDGET_LIMITS[category])

    def is_over_budget(self, category):
        """True if the category's total is above its budget limit."""
        return self.amount_over_budget(category) > 0


# ---------- Display helpers ----------

def peso(amount):
    """Format a number as pesos, e.g. 1234.5 -> '₱1,234.50'."""
    return f"₱{amount:,.2f}"


def print_header(title, width):
    """Print a title between two lines."""
    print("\n" + "=" * width)
    print(title.center(width))
    print("=" * width)


def show_menu():
    """Display the main menu."""
    print_header("EXPENSE TRACKER", 45)
    print("[1] Add Expense")
    print("[2] View All Expenses")
    print("[3] Totals per Category")
    print("[4] Analyze Spending (Pandas)")
    print("[5] Quit")
    print("=" * 45)


def display_expense(expense):
    """Display the details of a single expense."""
    print_header("EXPENSE DETAILS", 45)
    print(f"{'Date':<15}: {expense.date}")
    print(f"{'Item':<15}: {expense.item}")
    print(f"{'Category':<15}: {expense.category}")
    print(f"{'Amount':<15}: {peso(expense.amount)}")
    print(f"{'Size':<15}: {expense.size}")
    print("=" * 45)


# ---------- Input ----------

def ask(prompt, parser):
    """Keep asking until `parser` accepts the answer.

    `parser` is a function (parse_amount, parse_item, ...) passed in as an
    argument. It returns the clean value or raises ValueError.
    """
    while True:
        try:
            return parser(input(prompt))
        except ValueError as error:
            print(f"Error! {error}\n")


# ---------- Menu actions ----------

def add_expense(tracker):
    """Ask for an expense, build an Expense object, save it, warn if over budget."""
    date_text = ask("Enter the date (YYYY-MM-DD, or press Enter for today): ",
                    parse_date_or_today)
    item = ask("Enter the item: ", parse_item)
    print("\nAllowed categories:", ", ".join(sorted(BUDGET_LIMITS)))
    category = ask("Enter the category: ", parse_category)
    amount = ask("Enter the amount (₱): ", parse_amount)

    expense = Expense(date_text, item, category, amount)
    tracker.add(expense)

    print("\nExpense added successfully!")
    display_expense(expense)

    if tracker.is_over_budget(expense.category):
        over = tracker.amount_over_budget(expense.category)
        print(f"WARNING: {expense.category} is over budget by {peso(over)}!")


def view_all_expenses(tracker):
    """Display every expense in a table."""
    width = 75
    print_header("ALL EXPENSES", width)

    if len(tracker) == 0:
        print("No expenses recorded yet.")
        print("=" * width)
        return

    print(f"{'No.':<5}{'Date':<12}{'Item':<20}{'Category':<12}{'Size':<9}{'Amount':>17}")
    print("-" * width)

    for number, expense in enumerate(tracker.expenses, start=1):
        print(
            f"{number:<5}"
            f"{expense.date:<12}"
            f"{expense.item[:18]:<20}"   # [:18] stops long names breaking the table
            f"{expense.category:<12}"
            f"{expense.size:<9}"
            f"{peso(expense.amount):>17}"
        )

    print("-" * width)
    print(f"{'TOTAL EXPENSES':<58}{peso(tracker.total_spent()):>17}")
    print("=" * width)


def show_category_totals(tracker):
    """Show spending per category next to its budget limit."""
    width = 50
    totals = tracker.totals_by_category()

    print_header("TOTALS PER CATEGORY", width)
    print(f"{'Category':<16}{'Total Spent':>17}{'Budget Limit':>17}")
    print("-" * width)

    for category, total in sorted(totals.items()):
        print(f"{category:<16}{peso(total):>17}{peso(BUDGET_LIMITS[category]):>17}")
        if tracker.is_over_budget(category):
            print(f"  WARNING: {category} exceeded by "
                  f"{peso(tracker.amount_over_budget(category))}!")

    print("-" * width)
    print(
        f"{'TOTAL':<16}"
        f"{peso(tracker.total_spent()):>17}"
        f"{peso(sum(BUDGET_LIMITS.values())):>17}"
    )
    print("=" * width)


def analyze_spending(tracker):
    """Run the Pandas analysis. Imported here so the rest works without Pandas."""
    try:
        import analysis
    except ImportError:
        print("\nThis feature needs pandas, numpy and matplotlib.")
        print("Install them with:  pip install -r requirements.txt")
        return

    # analysis.py only sees plain dictionaries, never our classes.
    analysis.run_analysis(tracker.to_dicts(), BUDGET_LIMITS, CHART_FILE)


# ---------- Main program ----------

def main():
    """Run the menu-driven expense tracker."""
    tracker = ExpenseTracker(DATA_FILE)
    tracker.load()

    if len(tracker) > 0:
        print(f"Loaded {len(tracker)} saved expense(s).")
    if tracker.skipped:
        print(f"Skipped {tracker.skipped} invalid record(s) in {DATA_FILE}.")

    try:
        while True:
            show_menu()
            choice = input("Enter option [1-5]: ").strip()

            if choice == "1":
                add_expense(tracker)
            elif choice == "2":
                view_all_expenses(tracker)
            elif choice == "3":
                show_category_totals(tracker)
            elif choice == "4":
                analyze_spending(tracker)
            elif choice == "5":
                print("\nThank you for using Expense Tracker! Goodbye!")
                break
            else:
                print("\nError! Please enter a number from 1 to 5.")
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C or Ctrl+D: exit politely (data is saved after every add)
        print("\n\nExiting. Your expenses are already saved. Goodbye!")


if __name__ == "__main__":
    main()