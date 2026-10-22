# 💰 Expense Tracker & Budget Analyzer

A Python project that grows module by module to help answer one everyday question: **"Where does my money go?"**

Built as hands-on practice while completing **Python for Data Science, AI & Development** (part of the IBM DevOps and Software Engineering Professional Certificate on Coursera).

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Status](https://img.shields.io/badge/status-in%20progress-yellow)

---

## 📖 About the Project

Most people don't know exactly how much they spend on food, transport, or subscriptions until the month is over. This tool aims to make tracking expenses simple: log what you spend, categorize it, and eventually see clear summaries and charts of your spending habits.

The project is built in stages. Each stage applies the concepts from one module of the course to a real-world problem, so the code evolves from a simple script into a complete data-driven application.

## ✅ Current Features (Module 1)

- Prompts the user for an expense: item, category, and amount
- Cleans messy input (extra spaces, inconsistent capitalization)
- Converts the amount to a number and formats it to two decimal places
- Prints a clean, readable expense receipt

### Example

```
Enter the item:   coffee beans
Enter the category:   FOOD
Enter the amount: 250

Item: Coffee Beans
Category: Food
Amount: $250.00
```

## 🛠️ Getting Started

### Prerequisites

- Python 3.8 or higher ([download here](https://www.python.org/downloads/))

### Run the program

```bash
# Clone the repository
git clone https://github.com/codewithgaf/expense-tracker.git

# Move into the project folder
cd expense-tracker

# Run the script
python expense_tracker.py
```

> Replace `codewithgaf`, `expense-tracker`, and the script name with your own.

## 🗺️ Roadmap

This project follows the course modules. Checked items are completed.

| Module | Topic | What gets built | Status |
|--------|-------|-----------------|--------|
| 1 | Python Basics | Input handling, string cleaning, formatted receipt | ✅ Done |
| 2 | Data Structures | Store many expenses in lists and dictionaries, totals per category | ⬜ Planned |
| 3 | Programming Fundamentals | Menu-driven app, functions, `Expense` class, error handling, file saving | ⬜ Planned |
| 4 | Working with Data | Analysis with Pandas and NumPy, charts with Matplotlib | ⬜ Planned |
| 5 | APIs and Data Collection | Multi-currency support using a live exchange-rate API | ⬜ Planned |

## 📚 What I'm Learning

- Reading user input and converting data types
- String methods for cleaning data (`strip`, `title`, and chaining)
- f-string formatting for readable output
- Writing clean, commented code and committing progress step by step with Git

*This section will be updated as each module is completed.*

## 🧱 Project Structure

```
.
├── expense_tracker.py   # Main program
└── README.md            # Project documentation
```

## 🔮 Future Improvements

- Handle invalid input without crashing
- Save and load expenses between sessions
- Monthly budget limits with overspending warnings
- Spending charts and summaries
- Unit tests and a CI pipeline (later in the certificate)

## 👤 Author

**Your Name**
- GitHub: [@codewithgaf](https://github.com/codewithgaf)
- LinkedIn: [gafourpanolong](https://www.linkedin.com/in/gafourpanolong)

## 📄 License

This project is for learning purposes. Feel free to use it as a reference.