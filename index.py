# Ask the user for item (no str() needed)
item = input("Enter the item: ")

# Ask the user for category
category = input("Enter the category: ")

# Ask the user for the amount
amount = float(input("Enter the amount: "))

# Using a proper f-string with \n for clean line breaks
print(f"Item: {item}\nCategory: {category}\nAmount: ${amount:.2f}")