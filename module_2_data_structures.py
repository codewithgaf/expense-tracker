
expenses = [
    {"item": "Notebook", "category": "School", "amount": 45.00},
    {"item": "Bus fare", "category": "Transport", "amount": 12.00},
    {"item": "Pizza", "category": "Food", "amount": 13.00},
    {"item": "Burger & Fries", "category": "Food", "amount": 27.022},
    {"item": "Bus fare", "category": "Transport", "amount": 15.00},
]


def display_expenses(expenses):
    """Display expenses in a formatted table."""

    width = 66

    print("\n" + "=" * width)
    print("                 PERSONAL EXPENSE TRACKER")
    print("=" * width)

    print(f"{'No.':<5}{'Item':<25}{'Category':<18}{'Amount':>12}")
    print("-" * width)

    for number, expense in enumerate(expenses, start=1):
        item = expense["item"].strip()
        category = expense["category"].strip()
        amount = expense["amount"]

        print(
            f"{number:<5}"
            f"{item:<25}"
            f"{category:<18}"
            f"₱{amount:>10,.2f}"
        )

    print("-" * width)

    total = sum(expense["amount"] for expense in expenses)
    print(f"{'TOTAL EXPENSES:':<48}₱{total:>10,.2f}")

    print("=" * width)


def display_category_summary(expenses):
    """Display the total expenses per category."""

    category_totals = {}

    for expense in expenses:
        category = expense["category"].strip()
        amount = expense["amount"]

        category_totals[category] = (
            category_totals.get(category, 0) + amount
        )

    print("\n" + "=" * 50)
    print("                 CATEGORY SUMMARY")
    print("=" * 50)

    for category, total in sorted(category_totals.items()):
        print(f"{category:<30} ₱{total:>10,.2f}")

    print("-" * 50)
    print(f"{'UNIQUE CATEGORIES:':<30} {len(category_totals):>10}")
    print("=" * 50)


# Display reports
display_expenses(expenses)
display_category_summary(expenses)
