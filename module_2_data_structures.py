# Expense Tracker - Module 2: lists, dictionaries, sets, and slicing

CURRENCY = "₱"  # change this one line to switch currency symbols

expenses = [
    {"item": "Notebook", "category": "School", "amount": 45.0},
    {"item": "Bus fare", "category": "Transport", "amount": 12.0},
    {"item": "Pizza ", "category": "Food", "amount": 13.0},
    {"item": "Burger & Fries ", "category": "Food", "amount": 27.022},
    {"item": "Bus fare ", "category": "Transport", "amount": 15.0},
]

# Clean the data once, up front, so every step below works with clean values
for expense in expenses:
    expense["item"] = expense["item"].strip().title()
    expense["category"] = expense["category"].strip().title()
    expense["amount"] = round(expense["amount"], 2)

# Unique categories (a set removes duplicates; sorted() gives a stable order)
unique_categories = sorted({expense["category"] for expense in expenses})

# Running total of spending per category
totals = {}
for expense in expenses:
    category = expense["category"]
    totals[category] = totals.get(category, 0) + expense["amount"]

# Display
print("Categories:", ", ".join(unique_categories))

print("\nTotals per category:")
for category, total in totals.items():
    print(f"  {category}: {CURRENCY}{total:.2f}")
print(f"  Overall: {CURRENCY}{sum(totals.values()):.2f}")

print("\nLast 3 expenses:")
for expense in expenses[-3:]:
    print(f"  {expense['item']}: {CURRENCY}{expense['amount']:.2f}")