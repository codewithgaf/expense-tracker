
def show_menu():
    print("\n" + "=" * 40)
    print("          EXPENSE TRACKER")
    print("=" * 40)

    print("\n1. Add Expense")
    print("\n2. View all expenses")
    print("\n3. Totals per category")
    print("\n4. Quit")

def get_expense(item, category, amount):
    """Collect and validate expense information."""

    while True:
        item = input("Enter the item: ").strip().title()

        if not item:
            print("Error! Item cannot be empty.\n")
            continue

        category = input("Enter the category: ").strip().title()

        if not category:
            print("Error! Category cannot be empty.\n")
            continue

        try:
            amount = float(input("Enter the amount: $"))

            if amount <= 0:
                print("Error! Amount must be greater than 0.\n")
                continue

        except ValueError:
            print("Error! Please enter a valid number.\n")
            continue

        return item, category, amount

def display_expense(item, category, amount):
    """Display expense details in a formatted box."""

    width = 42

    print("\n" + "=" * width)
    print("          EXPENSE DETAILS")
    print("=" * width)
    print(f"{'Item':<15}: {item}")
    print(f"{'Category':<15}: {category}")
    print(f"{'Amount':<15}: ${amount:,.2f}")
    print("=" * width)

def main():
    expenses = []
    
    while True:
        show_menu()
        user_input = int(input("Enter option (1-4):"))

        if user_input == 1:
        
            item, category, amount = get_expense()
            
            expense = {
                "item": item,
                "category": category,
                "amount": round(amount, 2)
            }
            expenses.append(expense)
            print("Expense Detail is saved.") 
            print("\033[H\033[2J", end="")
        elif user_input == 2:
            display_expense()
            


ALLOWED_CATEGORIES = {"Food", "Transport", "School", "Bills", "Other"}

BUDGET_LIMITS = {
    "Food": 3000,
    "Transport": 1500,
    "School": 2000,
    "Bills": 5000,
    "Other": 1000
}

if __name__ == "__main__":
    main()
