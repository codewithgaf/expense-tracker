"""Spending analysis - Module 4 (Pandas, NumPy, Matplotlib)

The functions at the top take a DataFrame and RETURN results (no printing),
so they are easy to test. Only print_report() prints.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

COLUMNS = ["date", "item", "category", "amount", "size"]


def peso(amount):
    """Format a number as pesos, e.g. 1234.5 -> '₱1,234.50'."""
    return f"₱{amount:,.2f}"


# ---------- Building the DataFrame ----------

def expenses_to_dataframe(expenses):
    """Turn the list of expense dictionaries into a DataFrame with proper types."""
    df = pd.DataFrame(expenses, columns=COLUMNS)
    df["date"] = pd.to_datetime(df["date"])   # text -> real dates
    df["amount"] = df["amount"].astype(float)
    return df


# ---------- Analysis (pure functions) ----------

def category_summary(df):
    """Total, count, average and % share of spending for each category."""
    summary = (
        df.groupby("category")["amount"]
        .agg(total="sum", count="count", average="mean")
        .sort_values("total", ascending=False)
    )
    summary["average"] = summary["average"].round(2)
    summary["share_pct"] = np.round(summary["total"] / summary["total"].sum() * 100, 1)
    return summary


def daily_average(df):
    """Average spending per calendar day across the whole period.

    Returns (average, number_of_days). Days with no spending count too.
    """
    days = (df["date"].max() - df["date"].min()).days + 1
    return df["amount"].sum() / days, days


def weekly_totals(df):
    """Total spending per week (weeks end on Sunday). Quiet weeks show as 0."""
    return df.set_index("date")["amount"].resample("W").sum()


def amount_statistics(df):
    """Basic statistics on expense sizes, calculated with NumPy."""
    amounts = df["amount"].to_numpy()
    return {
        "mean": float(np.mean(amounts)),
        "median": float(np.median(amounts)),
        "std": float(np.std(amounts)),
        "p90": float(np.percentile(amounts, 90)),
        "max": float(np.max(amounts)),
    }


def unusually_large(df):
    """Expenses above the 90th percentile of all expense amounts."""
    threshold = np.percentile(df["amount"].to_numpy(), 90)
    return df[df["amount"] > threshold].sort_values("amount", ascending=False)


def budget_status(summary, budget_limits):
    """Compare what was spent in each category with its budget limit."""
    status = pd.DataFrame({"budget": pd.Series(budget_limits)})
    # reindex adds categories that have no spending yet, filled with 0
    status["spent"] = summary["total"].reindex(status.index, fill_value=0.0)
    status["used_pct"] = np.round(status["spent"] / status["budget"] * 100, 1)
    status["status"] = np.where(status["spent"] > status["budget"], "OVER", "OK")
    return status.sort_values("used_pct", ascending=False)


# ---------- Chart ----------

def plot_category_totals(status, filename):
    """Save a bar chart of spending per category, with budget limits marked."""
    fig, ax = plt.subplots(figsize=(8, 5))

    positions = np.arange(len(status))
    colors = np.where(status["status"] == "OVER", "#d9534f", "#4a90d9").tolist()

    ax.bar(positions, status["spent"], color=colors)
    ax.hlines(
        status["budget"].to_numpy(),
        positions - 0.4,
        positions + 0.4,
        colors="black",
        linestyles="dashed",
        label="Budget limit",
    )

    # Put each label above whichever is higher (the bar or its budget line)
    # so the text never collides with the dashed line.
    tops = np.maximum(status["spent"].to_numpy(), status["budget"].to_numpy())
    offset = tops.max() * 0.015
    for x, top, spent in zip(positions, tops, status["spent"]):
        ax.text(x, top + offset, f"₱{spent:,.0f}", ha="center", va="bottom")

    ax.set_ylim(0, tops.max() * 1.12)   # headroom so the top label isn't cramped
    ax.set_xticks(positions)
    ax.set_xticklabels(status.index)
    ax.set_ylabel("Amount (₱)")
    ax.set_title("Spending per Category (red = over budget)")
    ax.legend()
    fig.tight_layout()

    fig.savefig(filename, dpi=150)
    plt.close(fig)


# ---------- Report (the only function that prints) ----------

def print_report(df, budget_limits, chart_file):
    """Print the full analysis and save the chart."""
    width = 60
    print("\n" + "=" * width)
    print("SPENDING ANALYSIS".center(width))
    print("=" * width)

    if df.empty:
        print("No expenses to analyze yet. Add some first!")
        print("=" * width)
        return

    summary = category_summary(df)
    avg_per_day, days = daily_average(df)
    weekly = weekly_totals(df)
    stats = amount_statistics(df)
    status = budget_status(summary, budget_limits)

    first = df["date"].min().date()
    last = df["date"].max().date()
    top_name = summary["total"].idxmax()

    day_word = "day" if days == 1 else "days"
    print(f"Period        : {first} to {last} ({days} {day_word})")
    print(f"Expenses      : {len(df)}")
    print(f"Total spent   : {peso(df['amount'].sum())}")
    print(f"Daily average : {peso(avg_per_day)}")
    print(f"Top category  : {top_name} "
          f"({peso(summary.loc[top_name, 'total'])}, "
          f"{summary.loc[top_name, 'share_pct']}% of spending)")

    print("\n--- By category ---")
    print(f"{'Category':<12}{'Total':>14}{'Count':>7}{'Average':>13}{'Share':>9}")
    for category, row in summary.iterrows():
        print(f"{category:<12}{peso(row['total']):>14}{int(row['count']):>7}"
              f"{peso(row['average']):>13}{row['share_pct']:>8}%")

    print("\n--- Weekly totals (weeks end on Sunday) ---")
    biggest = weekly.max()
    for week_end, total in weekly.items():
        bar = "█" * int(round(total / biggest * 20))
        print(f"{week_end.date()}  {peso(total):>12}  {bar}")
    print(f"Most expensive week: ending {weekly.idxmax().date()} ({peso(biggest)})")

    print("\n--- Expense size statistics ---")
    print(f"Mean {peso(stats['mean'])} | Median {peso(stats['median'])} | "
          f"Std dev {peso(stats['std'])}")
    print(f"90th percentile {peso(stats['p90'])} | Largest {peso(stats['max'])}")

    large = unusually_large(df)
    if not large.empty:
        print("\nUnusually large expenses (above the 90th percentile):")
        for _, row in large.iterrows():
            print(f"  {row['date'].date()}  {row['item']:<20}{peso(row['amount']):>14}")

    print("\n--- Budget status ---")
    print(f"{'Category':<12}{'Spent':>14}{'Budget':>14}{'Used':>9}  Status")
    for category, row in status.iterrows():
        print(f"{category:<12}{peso(row['spent']):>14}{peso(row['budget']):>14}"
              f"{row['used_pct']:>8}%  {row['status']}")

    try:
        plot_category_totals(status, chart_file)
        print(f"\nChart saved as {chart_file}")
    except OSError as error:
        print(f"\nCould not save the chart ({error}).")
    print("=" * width)


def run_analysis(expenses, budget_limits, chart_file):
    """Entry point used by the menu: build the DataFrame, then print the report."""
    df = expenses_to_dataframe(expenses)
    print_report(df, budget_limits, chart_file)