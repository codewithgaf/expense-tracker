# Ask for the expense details and clean the text right away,
# so the variables hold clean data (not just the printed output)
item = input("Enter the item: ").strip().title()
category = input("Enter the category: ").strip().title()

# input() returns a string, so convert it to a number and round it for money
amount = round(float(input("Enter the amount: ")), 2)

print(f"Item: {item}\nCategory: {category}\nAmount: ${amount:.2f}")