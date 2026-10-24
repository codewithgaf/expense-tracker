import math

ALLOWED_CATEGORIES = {"Food", "Transport", "School", "Bills", "Other"}

BUDGET_LIMITS = {
    "Food": 3000,
    "Transport": 1500,
    "School": 2000,
    "Bills": 5000,
    "Other": 1000
}


def show_menu():
    """Display the main menu."""
    print("\n" + "=" * 45)
    print("               EXPENSE TRACKER")
    print("=" * 45)
    print("[1] Add Expense")
    print("[2] View All Expenses")
    print("[3] Totals per Category")
    print("[4] Quit")
    print("=" * 45)


def get_expense():
    """Collect and validate expense information."""

    # Validate item name
    while True:
        item = input("Enter the item: ").strip().title()

        if not item:
            print("Error! Item cannot be empty.\n")
            continue

        break

    # Validate category
    while True:
        print("\nAllowed Categories:", ", ".join(sorted(ALLOWED_CATEGORIES)))
        category = input("Enter the category: ").strip().title()

        if category not in ALLOWED_CATEGORIES:
            print("Error! Please choose a valid category.\n")
            continue

        break

    # Validate amount independently
    while True:
        try:
            amount_input = input("Enter the amount (₱): ").strip()
            amount = float(amount_input)

            if not math.isfinite(amount):
                print("Error! Amount must be a finite number.\n")
                continue

            if amount <= 0:
                print("Error! Amount must be greater than zero.\n")
                continue

            break

        except ValueError:
            print("Error! Please enter a valid number.\n")

    return item, category, amount


def display_expense(item, category, amount):
    """Display the details of a single expense."""

    width = 45

    print("\n" + "=" * width)
    print("               EXPENSE DETAILS")
    print("=" * width)
    print(f"{'Item':<15}: {item}")
    print(f"{'Category':<15}: {category}")
    print(f"{'Amount':<15}: ₱{amount:,.2f}")
    print("=" * width)


def add_expense(expenses):
    """Add a validated expense to the expense list."""

    item, category, amount = get_expense()

    expense = {
        "item": item,
        "category": category,
        "amount": amount
    }

    expenses.append(expense)

    print("\nExpense added successfully!")
    display_expense(item, category, amount)


def view_all_expenses(expenses):
    """Display all recorded expenses in a summary table."""

    print("\n" + "=" * 75)
    print("                            ALL EXPENSES")
    print("=" * 75)

    if not expenses:
        print("No expenses recorded yet.")
        print("=" * 75)
        return

    print(f"{'No.':<5}{'Item':<25}{'Category':<15}{'Amount':>15}")
    print("-" * 75)

    grand_total = 0

    for index, expense in enumerate(expenses, start=1):
        print(
            f"{index:<5}"
            f"{expense['item']:<25}"
            f"{expense['category']:<15}"
            f"₱{expense['amount']:>14,.2f}"
        )

        grand_total += expense["amount"]

    print("-" * 75)
    print(f"{'TOTAL EXPENSES':<45} ₱{grand_total:>14,.2f}")
    print("=" * 75)


def totals_per_category(expenses):
    """Calculate category totals and compare them with budget limits."""

    # Initialize all categories, including those with no expenses.
    category_totals = {
        category: 0.0
        for category in ALLOWED_CATEGORIES
    }

    # Calculate cumulative spending for each category.
    for expense in expenses:
        category = expense["category"]
        category_totals[category] += expense["amount"]

    print("\n" + "=" * 65)
    print("                    TOTALS PER CATEGORY")
    print("=" * 65)

    print(f"{'Category':<15}{'Total Spent':>18}{'Budget Limit':>18}")
    print("-" * 65)

    for category, total in sorted(category_totals.items()):
        budget = BUDGET_LIMITS[category]

        print(
            f"{category:<15}"
            f"₱{total:>16,.2f}"
            f"₱{budget:>17,.2f}"
        )

        if total > budget:
            excess = total - budget
            print(
                f"  WARNING: {category} budget exceeded "
                f"by ₱{excess:,.2f}!"
            )

    grand_total = sum(category_totals.values())

    print("-" * 65)
    print(f"{'TOTAL SPENDING':<15}{'₱' + format(grand_total, ',.2f'):>18}")
    print("=" * 65)


def main():
    """Run the menu-driven expense tracker."""

    expenses = []

    while True:
        show_menu()

        choice = input("Enter option [1-4]: ").strip()

        if choice == "1":
            add_expense(expenses)

        elif choice == "2":
            view_all_expenses(expenses)

        elif choice == "3":
            totals_per_category(expenses)

        elif choice == "4":
            print("\nThank you for using Expense Tracker!")
            print("Goodbye!")
            break

        else:
            print("\nError! Invalid choice. Please enter a number from 1 to 4.")


if __name__ == "__main__":
    main()
