"""Expense Tracker - Module 4

Adds dates to expenses and an "Analyze Spending" option that uses
Pandas, NumPy and Matplotlib (see analysis.py).
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


# ---------- Pure logic (no input, no printing) ----------

def parse_amount(text):
    """Turn text into a valid money amount, or raise ValueError with a clear message."""
    try:
        amount = float(text)
    except ValueError:
        raise ValueError("Please enter a valid number.") from None

    if not math.isfinite(amount):
        raise ValueError("Amount must be a finite number.")

    amount = round(amount, 2)  # round BEFORE checking, so 0.001 is rejected

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    return amount


def parse_date(text):
    """Validate a YYYY-MM-DD date and return it as a clean ISO string."""
    try:
        parsed = datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Use the format YYYY-MM-DD, e.g. 2026-10-25.") from None

    if parsed > date.today():
        raise ValueError("Date cannot be in the future.")

    return parsed.isoformat()


def classify_expense(amount):
    """Return 'Small', 'Medium', or 'Large' based on the amount."""
    if amount < SMALL_LIMIT:
        return "Small"
    elif amount < MEDIUM_LIMIT:
        return "Medium"
    else:
        return "Large"


def calculate_category_totals(expenses):
    """Return {category: total_spent}, including categories with no spending."""
    totals = {category: 0.0 for category in BUDGET_LIMITS}
    for expense in expenses:
        totals[expense["category"]] += expense["amount"]
    return totals


def clean_record(record):
    """Return a cleaned expense dict from loaded data, or None if it's invalid."""
    if not isinstance(record, dict):
        return None

    item = record.get("item")
    category = record.get("category")
    amount = record.get("amount")
    raw_date = record.get("date")

    if not isinstance(item, str) or not item.strip():
        return None
    if not isinstance(category, str) or category not in BUDGET_LIMITS:
        return None
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        return None
    if not math.isfinite(amount):
        return None

    amount = round(float(amount), 2)
    if amount <= 0:
        return None

    if raw_date is None:
        # Record saved before dates existed (Module 3): use today's date.
        date_text = date.today().isoformat()
    elif isinstance(raw_date, str):
        try:
            date_text = parse_date(raw_date)
        except ValueError:
            return None
    else:
        return None

    return {
        "date": date_text,
        "item": item.strip().title(),
        "category": category,
        "amount": amount,
        "size": classify_expense(amount),
    }


# ---------- File handling ----------

def backup_corrupt_file(filename):
    """Move an unreadable data file aside so we never destroy the user's data."""
    backup = filename + ".corrupt"
    os.replace(filename, backup)
    print(f"Warning: {filename} could not be read.")
    print(f"A copy was kept as {backup}. Starting with an empty list.")


def load_expenses(filename):
    """Load expenses from JSON. Returns (expenses, number_of_skipped_records)."""
    try:
        with open(filename, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return [], 0  # first run: no file yet, which is normal
    except (json.JSONDecodeError, UnicodeDecodeError):
        backup_corrupt_file(filename)
        return [], 0
    except OSError as error:
        print(f"Warning: could not open {filename} ({error}).")
        return [], 0

    if not isinstance(data, list):
        backup_corrupt_file(filename)
        return [], 0

    expenses = []
    skipped = 0
    for record in data:
        cleaned = clean_record(record)
        if cleaned is None:
            skipped += 1
        else:
            expenses.append(cleaned)

    return expenses, skipped


def save_expenses(expenses, filename):
    """Save expenses to JSON. Returns True on success, False on failure."""
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(expenses, file, indent=2)
    except OSError as error:
        print(f"Warning: could not save your data ({error}).")
        return False
    return True


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
    print(f"{'Date':<15}: {expense['date']}")
    print(f"{'Item':<15}: {expense['item']}")
    print(f"{'Category':<15}: {expense['category']}")
    print(f"{'Amount':<15}: {peso(expense['amount'])}")
    print(f"{'Size':<15}: {expense['size']}")
    print("=" * 45)


# ---------- Input ----------

def get_expense():
    """Ask the user for an expense, retrying each field until it's valid."""
    while True:
        text = input("Enter the date (YYYY-MM-DD, or press Enter for today): ").strip()
        if not text:
            date_text = date.today().isoformat()
            break
        try:
            date_text = parse_date(text)
        except ValueError as error:
            print(f"Error! {error}\n")
        else:
            break

    while True:
        item = input("Enter the item: ").strip().title()
        if item:
            break
        print("Error! Item cannot be empty.\n")

    while True:
        print("\nAllowed categories:", ", ".join(sorted(BUDGET_LIMITS)))
        category = input("Enter the category: ").strip().title()
        if category in BUDGET_LIMITS:
            break
        print("Error! Please choose a valid category.")

    while True:
        try:
            amount = parse_amount(input("Enter the amount (₱): ").strip())
        except ValueError as error:
            print(f"Error! {error}\n")
        else:
            break

    return {
        "date": date_text,
        "item": item,
        "category": category,
        "amount": amount,
        "size": classify_expense(amount),
    }


# ---------- Menu actions ----------

def add_expense(expenses):
    """Get an expense, add it, save to disk, and warn if over budget."""
    expense = get_expense()
    expenses.append(expense)
    save_expenses(expenses, DATA_FILE)

    print("\nExpense added successfully!")
    display_expense(expense)

    category = expense["category"]
    total = calculate_category_totals(expenses)[category]
    if total > BUDGET_LIMITS[category]:
        over = total - BUDGET_LIMITS[category]
        print(f"WARNING: {category} is over budget by {peso(over)}!")


def view_all_expenses(expenses):
    """Display every expense in a table."""
    width = 75
    print_header("ALL EXPENSES", width)

    if not expenses:
        print("No expenses recorded yet.")
        print("=" * width)
        return

    print(f"{'No.':<5}{'Date':<12}{'Item':<20}{'Category':<12}{'Size':<9}{'Amount':>17}")
    print("-" * width)

    grand_total = 0
    for number, expense in enumerate(expenses, start=1):
        print(
            f"{number:<5}"
            f"{expense['date']:<12}"
            f"{expense['item'][:18]:<20}"   # [:18] stops long names breaking the table
            f"{expense['category']:<12}"
            f"{expense['size']:<9}"
            f"{peso(expense['amount']):>17}"
        )
        grand_total += expense["amount"]

    print("-" * width)
    print(f"{'TOTAL EXPENSES':<58}{peso(grand_total):>17}")
    print("=" * width)


def show_category_totals(expenses):
    """Show spending per category next to its budget limit."""
    width = 50
    totals = calculate_category_totals(expenses)

    print_header("TOTALS PER CATEGORY", width)
    print(f"{'Category':<16}{'Total Spent':>17}{'Budget Limit':>17}")
    print("-" * width)

    for category, total in sorted(totals.items()):
        budget = BUDGET_LIMITS[category]
        print(f"{category:<16}{peso(total):>17}{peso(budget):>17}")
        if total > budget:
            print(f"  WARNING: {category} exceeded by {peso(total - budget)}!")

    print("-" * width)
    print(
        f"{'TOTAL':<16}"
        f"{peso(sum(totals.values())):>17}"
        f"{peso(sum(BUDGET_LIMITS.values())):>17}"
    )
    print("=" * width)


def analyze_spending(expenses):
    """Run the Pandas analysis. Imported here so the rest works without Pandas."""
    try:
        import analysis
    except ImportError:
        print("\nThis feature needs pandas, numpy and matplotlib.")
        print("Install them with:  pip install -r requirements.txt")
        return

    analysis.run_analysis(expenses, BUDGET_LIMITS, CHART_FILE)


# ---------- Main program ----------

def main():
    """Run the menu-driven expense tracker."""
    expenses, skipped = load_expenses(DATA_FILE)

    if expenses:
        print(f"Loaded {len(expenses)} saved expense(s).")
    if skipped:
        print(f"Skipped {skipped} invalid record(s) in {DATA_FILE}.")

    try:
        while True:
            show_menu()
            choice = input("Enter option [1-5]: ").strip()

            if choice == "1":
                add_expense(expenses)
            elif choice == "2":
                view_all_expenses(expenses)
            elif choice == "3":
                show_category_totals(expenses)
            elif choice == "4":
                analyze_spending(expenses)
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