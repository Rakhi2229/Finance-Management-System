"""
=============================================================================
FINTRACK - PERSONAL FINANCE MANAGEMENT SYSTEM
Module: finance.py
Description: Core financial calculations, CRUD database operations for Income,
             Expense, and Budget records, Pandas data processing, and demo data.
=============================================================================
"""

from datetime import date, datetime, timedelta  # Import date/time utilities for transaction dating
import pandas as pd  # Import Pandas for structured financial data analysis and tabular transformations
from sqlalchemy import func, extract, and_  # Import SQLAlchemy query helpers
from database import SessionLocal, Income, Expense, Budget  # Import ORM models and session


# ---------------------------------------------------------------------------
# 1. CONSTANTS & CATEGORY DEFINITIONS
# ---------------------------------------------------------------------------

# Standard predefined income sources for consistency throughout the application
INCOME_SOURCES = [
    "Salary",
    "Freelance",
    "Business",
    "Investment",
    "Interest",
    "Other"
]

# Standard predefined expense categories for tracking and budget management
EXPENSE_CATEGORIES = [
    "Food",
    "Rent",
    "Transportation",
    "Shopping",
    "Bills",
    "Education",
    "Healthcare",
    "Entertainment",
    "Travel",
    "Other"
]

# Common payment methods for expense transactions
PAYMENT_METHODS = [
    "UPI",
    "Debit Card",
    "Credit Card",
    "Bank Transfer",
    "Cash"
]


# ---------------------------------------------------------------------------
# 2. INCOME CRUD OPERATIONS
# ---------------------------------------------------------------------------

def add_income(user_id: int, amount: float, source: str, description: str, income_date: date) -> tuple[bool, str]:
    """
    Insert a new Income transaction record for the specified user.

    Parameters:
        user_id (int): Primary key ID of the currently logged-in user.
        amount (float): Monetary value of the income (must be positive).
        source (str): Source category of income (e.g. Salary, Freelance).
        description (str): Optional note or memo regarding the income.
        income_date (date): Date on which the income was earned or received.

    Returns:
        tuple[bool, str]: (Success boolean, Status message)
    """
    # Validate that amount is strictly greater than zero
    if amount <= 0:
        return False, "Income amount must be greater than zero."

    # Validate that source category is selected
    if not source:
        return False, "Please select a valid income source."

    session = SessionLocal()
    try:
        # Create a new Income ORM object
        new_income = Income(
            user_id=user_id,
            amount=float(amount),
            source=source.strip(),
            description=description.strip() if description else "",
            income_date=income_date
        )

        # Stage and commit to database
        session.add(new_income)
        session.commit()
        return True, "Income added successfully!"
    except Exception as e:
        session.rollback()  # Rollback on database failure
        return False, f"Failed to add income: {str(e)}"
    finally:
        session.close()  # Clean up database session


def get_incomes_df(user_id: int, start_date: date = None, end_date: date = None, source: str = None) -> pd.DataFrame:
    """
    Retrieve all income records for a given user as a clean Pandas DataFrame.

    Parameters:
        user_id (int): Primary key ID of the logged-in user.
        start_date (date, optional): Earliest date filter boundary.
        end_date (date, optional): Latest date filter boundary.
        source (str, optional): Specific income source filter (or 'All').

    Returns:
        pd.DataFrame: Formatted DataFrame containing filtered income transactions.
    """
    session = SessionLocal()
    try:
        # Base query filtered strictly by user_id to ensure strict user privacy
        query = session.query(Income).filter(Income.user_id == user_id)

        # Apply start date filter if provided
        if start_date:
            query = query.filter(Income.income_date >= start_date)

        # Apply end date filter if provided
        if end_date:
            query = query.filter(Income.income_date <= end_date)

        # Apply income source filter if provided and not "All"
        if source and source != "All":
            query = query.filter(Income.source == source)

        # Order chronologically with the latest transactions first
        query = query.order_by(Income.income_date.desc(), Income.income_id.desc())

        # Execute query and load results into list of dicts
        records = query.all()
        data = [
            {
                "income_id": r.income_id,
                "amount": r.amount,
                "source": r.source,
                "description": r.description or "",
                "income_date": r.income_date,
                "created_at": r.created_at
            }
            for r in records
        ]

        # Convert dictionary list into a Pandas DataFrame
        df = pd.DataFrame(data)

        # Return empty DataFrame with predefined columns if no records match
        if df.empty:
            return pd.DataFrame(columns=["income_id", "amount", "source", "description", "income_date", "created_at"])

        return df

    except Exception as e:
        print(f"[Finance Error] get_incomes_df: {e}")
        return pd.DataFrame(columns=["income_id", "amount", "source", "description", "income_date", "created_at"])
    finally:
        session.close()


def get_income_by_id(income_id: int, user_id: int):
    """
    Fetch a single income record by its primary key ID, ensuring it belongs to the user.

    Parameters:
        income_id (int): Income record ID.
        user_id (int): User ID to prevent unauthorized access.

    Returns:
        dict | None: Dictionary of income attributes or None if not found.
    """
    session = SessionLocal()
    try:
        record = session.query(Income).filter(
            Income.income_id == int(income_id),
            Income.user_id == int(user_id)
        ).first()

        if record:
            return {
                "income_id": record.income_id,
                "amount": record.amount,
                "source": record.source,
                "description": record.description,
                "income_date": record.income_date
            }
        return None
    finally:
        session.close()


def update_income(income_id: int, user_id: int, amount: float, source: str, description: str, income_date: date) -> tuple[bool, str]:
    """
    Update an existing income record owned by the authenticated user.

    Parameters:
        income_id (int): ID of the income record to modify.
        user_id (int): ID of the user (for ownership verification).
        amount (float): Updated income amount.
        source (str): Updated income source.
        description (str): Updated description.
        income_date (date): Updated date.

    Returns:
        tuple[bool, str]: (Success boolean, Status message)
    """
    if amount <= 0:
        return False, "Amount must be greater than zero."

    session = SessionLocal()
    try:
        # Retrieve record matching both income_id AND user_id
        record = session.query(Income).filter(
            Income.income_id == int(income_id),
            Income.user_id == int(user_id)
        ).first()

        if not record:
            return False, "Income record not found or access unauthorized."

        # Apply updated values
        record.amount = float(amount)
        record.source = source.strip()
        record.description = description.strip() if description else ""
        record.income_date = income_date

        session.commit()
        return True, "Income record updated successfully!"
    except Exception as e:
        session.rollback()
        return False, f"Update failed: {str(e)}"
    finally:
        session.close()


def delete_income(income_id: int, user_id: int) -> tuple[bool, str]:
    """
    Delete an income record owned by the authenticated user.

    Parameters:
        income_id (int): ID of the income record to delete.
        user_id (int): ID of the user.

    Returns:
        tuple[bool, str]: (Success boolean, Status message)
    """
    session = SessionLocal()
    try:
        # Locate target record
        record = session.query(Income).filter(
            Income.income_id == int(income_id),
            Income.user_id == int(user_id)
        ).first()

        if not record:
            return False, "Income record not found or access unauthorized."

        session.delete(record)
        session.commit()
        return True, "Income record deleted successfully!"
    except Exception as e:
        session.rollback()
        return False, f"Deletion failed: {str(e)}"
    finally:
        session.close()


# ---------------------------------------------------------------------------
# 3. EXPENSE CRUD OPERATIONS
# ---------------------------------------------------------------------------

def add_expense(user_id: int, amount: float, category: str, description: str, payment_method: str, expense_date: date) -> tuple[bool, str]:
    """
    Insert a new Expense transaction record for the specified user.

    Parameters:
        user_id (int): User's primary key ID.
        amount (float): Monetary value of the expenditure (must be positive).
        category (str): Category (e.g. Food, Rent, Transportation).
        description (str): Optional note or item description.
        payment_method (str): Payment method (e.g. UPI, Credit Card).
        expense_date (date): Date on which the expense was incurred.

    Returns:
        tuple[bool, str]: (Success boolean, Status message)
    """
    # Validation checks
    if amount <= 0:
        return False, "Expense amount must be greater than zero."

    if not category:
        return False, "Please select an expense category."

    if not payment_method:
        return False, "Please select a payment method."

    session = SessionLocal()
    try:
        # Create new Expense ORM object
        new_expense = Expense(
            user_id=user_id,
            amount=float(amount),
            category=category.strip(),
            description=description.strip() if description else "",
            payment_method=payment_method.strip(),
            expense_date=expense_date
        )

        session.add(new_expense)
        session.commit()
        return True, "Expense added successfully!"
    except Exception as e:
        session.rollback()
        return False, f"Failed to add expense: {str(e)}"
    finally:
        session.close()


def get_expenses_df(user_id: int, start_date: date = None, end_date: date = None, category: str = None, payment_method: str = None) -> pd.DataFrame:
    """
    Retrieve all expense records for a user as a formatted Pandas DataFrame.

    Parameters:
        user_id (int): User's primary key ID.
        start_date (date, optional): Minimum expense date.
        end_date (date, optional): Maximum expense date.
        category (str, optional): Expense category filter.
        payment_method (str, optional): Payment method filter.

    Returns:
        pd.DataFrame: Formatted DataFrame of filtered expenses.
    """
    session = SessionLocal()
    try:
        # Base query filtered by user_id
        query = session.query(Expense).filter(Expense.user_id == user_id)

        # Apply optional date filters
        if start_date:
            query = query.filter(Expense.expense_date >= start_date)
        if end_date:
            query = query.filter(Expense.expense_date <= end_date)

        # Apply category filter
        if category and category != "All":
            query = query.filter(Expense.category == category)

        # Apply payment method filter
        if payment_method and payment_method != "All":
            query = query.filter(Expense.payment_method == payment_method)

        # Sort with the newest expenses on top
        query = query.order_by(Expense.expense_date.desc(), Expense.expense_id.desc())

        records = query.all()
        data = [
            {
                "expense_id": r.expense_id,
                "amount": r.amount,
                "category": r.category,
                "description": r.description or "",
                "payment_method": r.payment_method,
                "expense_date": r.expense_date,
                "created_at": r.created_at
            }
            for r in records
        ]

        df = pd.DataFrame(data)
        if df.empty:
            return pd.DataFrame(columns=["expense_id", "amount", "category", "description", "payment_method", "expense_date", "created_at"])

        return df
    except Exception as e:
        print(f"[Finance Error] get_expenses_df: {e}")
        return pd.DataFrame(columns=["expense_id", "amount", "category", "description", "payment_method", "expense_date", "created_at"])
    finally:
        session.close()


def get_expense_by_id(expense_id: int, user_id: int):
    """
    Fetch a single expense record by its ID with ownership check.

    Parameters:
        expense_id (int): Expense primary key ID.
        user_id (int): User ID.

    Returns:
        dict | None: Dictionary of expense values or None.
    """
    session = SessionLocal()
    try:
        record = session.query(Expense).filter(
            Expense.expense_id == int(expense_id),
            Expense.user_id == int(user_id)
        ).first()

        if record:
            return {
                "expense_id": record.expense_id,
                "amount": record.amount,
                "category": record.category,
                "description": record.description,
                "payment_method": record.payment_method,
                "expense_date": record.expense_date
            }
        return None
    finally:
        session.close()


def update_expense(expense_id: int, user_id: int, amount: float, category: str, description: str, payment_method: str, expense_date: date) -> tuple[bool, str]:
    """
    Update an existing expense record.

    Parameters:
        expense_id (int): Expense ID.
        user_id (int): User ID.
        amount (float): Updated amount.
        category (str): Updated category.
        description (str): Updated description.
        payment_method (str): Updated payment method.
        expense_date (date): Updated date.

    Returns:
        tuple[bool, str]: (Success boolean, Status message)
    """
    if amount <= 0:
        return False, "Amount must be greater than zero."

    session = SessionLocal()
    try:
        record = session.query(Expense).filter(
            Expense.expense_id == int(expense_id),
            Expense.user_id == int(user_id)
        ).first()

        if not record:
            return False, "Expense record not found or access unauthorized."

        record.amount = float(amount)
        record.category = category.strip()
        record.description = description.strip() if description else ""
        record.payment_method = payment_method.strip()
        record.expense_date = expense_date

        session.commit()
        return True, "Expense record updated successfully!"
    except Exception as e:
        session.rollback()
        return False, f"Update failed: {str(e)}"
    finally:
        session.close()


def delete_expense(expense_id: int, user_id: int) -> tuple[bool, str]:
    """
    Delete an expense record owned by the user.

    Parameters:
        expense_id (int): Expense record ID.
        user_id (int): User ID.

    Returns:
        tuple[bool, str]: (Success boolean, Status message)
    """
    session = SessionLocal()
    try:
        record = session.query(Expense).filter(
            Expense.expense_id == int(expense_id),
            Expense.user_id == int(user_id)
        ).first()

        if not record:
            return False, "Expense record not found or access unauthorized."

        session.delete(record)
        session.commit()
        return True, "Expense record deleted successfully!"
    except Exception as e:
        session.rollback()
        return False, f"Deletion failed: {str(e)}"
    finally:
        session.close()


# ---------------------------------------------------------------------------
# 4. BUDGET CRUD & BUDGET TRACKING OPERATIONS
# ---------------------------------------------------------------------------

def set_or_update_budget(user_id: int, category: str, monthly_limit: float, month: int, year: int) -> tuple[bool, str]:
    """
    Set or update a monthly category budget limit.
    If a budget already exists for the given category, month, and year, update its limit;
    otherwise, create a new Budget record.

    Parameters:
        user_id (int): Logged-in user's ID.
        category (str): Target expense category.
        monthly_limit (float): Target spending cap (must be positive).
        month (int): Month number (1 to 12).
        year (int): Year (e.g. 2025).

    Returns:
        tuple[bool, str]: (Success boolean, Status message)
    """
    if monthly_limit <= 0:
        return False, "Budget limit must be greater than zero."

    if not category:
        return False, "Please select an expense category for the budget."

    session = SessionLocal()
    try:
        # Check if a budget record already exists for this user, category, month, and year
        existing_budget = session.query(Budget).filter(
            Budget.user_id == int(user_id),
            Budget.category == category,
            Budget.month == int(month),
            Budget.year == int(year)
        ).first()

        if existing_budget:
            # Update the existing budget limit
            existing_budget.monthly_limit = float(monthly_limit)
            session.commit()
            return True, f"Budget for {category} ({month}/{year}) updated to ₹{monthly_limit:,.2f}!"
        else:
            # Create a brand new budget allocation
            new_budget = Budget(
                user_id=int(user_id),
                category=category.strip(),
                monthly_limit=float(monthly_limit),
                month=int(month),
                year=int(year)
            )
            session.add(new_budget)
            session.commit()
            return True, f"Budget of ₹{monthly_limit:,.2f} set for {category} ({month}/{year})!"

    except Exception as e:
        session.rollback()
        return False, f"Failed to save budget: {str(e)}"
    finally:
        session.close()


def get_budgets_df(user_id: int, month: int = None, year: int = None) -> pd.DataFrame:
    """
    Fetch all budget records for a user as a Pandas DataFrame.

    Parameters:
        user_id (int): User ID.
        month (int, optional): Specific month filter.
        year (int, optional): Specific year filter.

    Returns:
        pd.DataFrame: DataFrame containing budget targets.
    """
    session = SessionLocal()
    try:
        query = session.query(Budget).filter(Budget.user_id == int(user_id))

        if month:
            query = query.filter(Budget.month == int(month))
        if year:
            query = query.filter(Budget.year == int(year))

        query = query.order_by(Budget.year.desc(), Budget.month.desc(), Budget.category.asc())

        records = query.all()
        data = [
            {
                "budget_id": r.budget_id,
                "category": r.category,
                "monthly_limit": r.monthly_limit,
                "month": r.month,
                "year": r.year,
                "created_at": r.created_at
            }
            for r in records
        ]

        df = pd.DataFrame(data)
        if df.empty:
            return pd.DataFrame(columns=["budget_id", "category", "monthly_limit", "month", "year", "created_at"])
        return df
    finally:
        session.close()


def delete_budget(budget_id: int, user_id: int) -> tuple[bool, str]:
    """
    Delete a specific budget target record.

    Parameters:
        budget_id (int): Budget record ID.
        user_id (int): User ID for authorization.

    Returns:
        tuple[bool, str]: (Success boolean, Status message)
    """
    session = SessionLocal()
    try:
        record = session.query(Budget).filter(
            Budget.budget_id == int(budget_id),
            Budget.user_id == int(user_id)
        ).first()

        if not record:
            return False, "Budget record not found or access unauthorized."

        session.delete(record)
        session.commit()
        return True, "Budget record deleted successfully!"
    except Exception as e:
        session.rollback()
        return False, f"Failed to delete budget: {str(e)}"
    finally:
        session.close()


def get_budget_status_df(user_id: int, month: int, year: int) -> pd.DataFrame:
    """
    Compare budgeted limits against actual spending for a specific month and year.

    Calculates:
        - Spent: Total expenses incurred in that category for that month/year.
        - Remaining: Budget limit minus actual spending.
        - Usage %: (Spent / Budget limit) * 100.
        - Status: 'Within Budget', 'Warning (>80%)', or 'Exceeded (>100%)'.

    Parameters:
        user_id (int): Active user's ID.
        month (int): Selected month (1-12).
        year (int): Selected year.

    Returns:
        pd.DataFrame: Merged budget status DataFrame with calculation columns.
    """
    # Step 1: Retrieve all budgets configured for this month/year
    budgets_df = get_budgets_df(user_id, month=month, year=year)

    if budgets_df.empty:
        return pd.DataFrame(columns=["category", "monthly_limit", "spent", "remaining", "usage_pct", "status", "budget_id"])

    # Step 2: Retrieve all expenses for this user in that specific month and year
    session = SessionLocal()
    try:
        expenses_query = session.query(
            Expense.category,
            func.sum(Expense.amount).label("total_spent")
        ).filter(
            Expense.user_id == user_id,
            extract("month", Expense.expense_date) == month,
            extract("year", Expense.expense_date) == year
        ).group_by(Expense.category).all()

        # Convert actual expenses into a lookup dictionary: {category: total_spent}
        expense_map = {cat: float(spent) for cat, spent in expenses_query}

    finally:
        session.close()

    # Step 3: Compute actual spending, remaining budget, and percentage usage
    rows = []
    for _, row in budgets_df.iterrows():
        cat = row["category"]
        limit = float(row["monthly_limit"])
        spent = expense_map.get(cat, 0.0)
        remaining = limit - spent

        # Calculate percentage used safely avoiding zero-division
        usage_pct = (spent / limit) * 100.0 if limit > 0 else 0.0

        # Determine health status indicator
        if usage_pct > 100.0:
            status = "Exceeded"
        elif usage_pct >= 80.0:
            status = "Warning"
        else:
            status = "Good"

        rows.append({
            "budget_id": row["budget_id"],
            "category": cat,
            "monthly_limit": limit,
            "spent": spent,
            "remaining": remaining,
            "usage_pct": round(usage_pct, 1),
            "status": status,
            "month": month,
            "year": year
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 5. FINANCIAL CALCULATIONS & DASHBOARD METRICS
# ---------------------------------------------------------------------------

def calculate_balance(total_income: float, total_expenses: float) -> float:
    """
    Calculate the user's current net balance.

    Parameters:
        total_income (float): Total income earned.
        total_expenses (float): Total expenses incurred.

    Returns:
        float: Remaining net balance.
    """
    return total_income - total_expenses


def calculate_savings(total_income: float, total_expenses: float) -> float:
    """
    Calculate net savings (Total Income - Total Expenses).

    Parameters:
        total_income (float): Total income.
        total_expenses (float): Total expenses.

    Returns:
        float: Savings amount.
    """
    return total_income - total_expenses


def calculate_savings_rate(total_income: float, total_expenses: float) -> float:
    """
    Calculate the savings rate percentage: (Savings / Total Income) * 100.
    Handles zero or negative income safely to avoid ZeroDivisionError.

    Parameters:
        total_income (float): Total income.
        total_expenses (float): Total expenses.

    Returns:
        float: Savings rate percentage rounded to 1 decimal place.
    """
    if total_income <= 0:
        return 0.0  # Safe zero fallback when no income has been recorded

    savings = calculate_savings(total_income, total_expenses)
    savings_rate = (savings / total_income) * 100.0
    return round(savings_rate, 1)


def get_financial_summary(user_id: int) -> dict:
    """
    Compute aggregate KPI metrics for the user's dashboard overview.

    Metrics:
        - Total Income
        - Total Expenses
        - Net Balance
        - Total Savings
        - Savings Rate (%)
        - Total Transactions Count

    Parameters:
        user_id (int): Active user's ID.

    Returns:
        dict: Key-value pairs of calculated financial indicators.
    """
    session = SessionLocal()
    try:
        # Sum all incomes for user
        total_income = session.query(func.coalesce(func.sum(Income.amount), 0.0)).filter(
            Income.user_id == user_id
        ).scalar()

        # Count total income records
        income_count = session.query(func.count(Income.income_id)).filter(
            Income.user_id == user_id
        ).scalar()

        # Sum all expenses for user
        total_expenses = session.query(func.coalesce(func.sum(Expense.amount), 0.0)).filter(
            Expense.user_id == user_id
        ).scalar()

        # Count total expense records
        expense_count = session.query(func.count(Expense.expense_id)).filter(
            Expense.user_id == user_id
        ).scalar()

        # Calculate derivative financial metrics
        total_income = float(total_income)
        total_expenses = float(total_expenses)
        balance = calculate_balance(total_income, total_expenses)
        savings = calculate_savings(total_income, total_expenses)
        savings_rate = calculate_savings_rate(total_income, total_expenses)
        total_transactions = (income_count or 0) + (expense_count or 0)

        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "balance": balance,
            "savings": savings,
            "savings_rate": savings_rate,
            "total_transactions": total_transactions,
            "income_count": income_count or 0,
            "expense_count": expense_count or 0
        }

    finally:
        session.close()


def get_analytics_summary(user_id: int) -> dict:
    """
    Perform deep data analysis on user spending and income patterns.

    Calculates:
        - Average monthly expenses
        - Highest single expense record (amount, category, description)
        - Highest spending category (name, sum)
        - Monthly income, expenses, and savings breakdown
        - Category-wise expense distribution
        - Dynamically generated actionable insights

    Parameters:
        user_id (int): Active user's ID.

    Returns:
        dict: Detailed analytics summary for reporting and charts.
    """
    session = SessionLocal()
    try:
        # Step 1: Query all expenses for user
        expenses = session.query(Expense).filter(Expense.user_id == user_id).all()
        incomes = session.query(Income).filter(Income.user_id == user_id).all()

        if not expenses and not incomes:
            return {
                "avg_monthly_expense": 0.0,
                "highest_expense_amount": 0.0,
                "highest_expense_category": "None",
                "highest_expense_desc": "None",
                "highest_category_name": "None",
                "highest_category_total": 0.0,
                "monthly_df": pd.DataFrame(),
                "category_df": pd.DataFrame(),
                "insights": ["No transaction data available yet. Add income or expenses to see analytical insights!"]
            }

        # Step 2: Build Expense DataFrame for Pandas aggregations
        exp_data = [
            {
                "amount": e.amount,
                "category": e.category,
                "description": e.description,
                "date": e.expense_date,
                "year_month": e.expense_date.strftime("%Y-%m")
            }
            for e in expenses
        ]
        exp_df = pd.DataFrame(exp_data)

        # Step 3: Build Income DataFrame for Pandas aggregations
        inc_data = [
            {
                "amount": i.amount,
                "source": i.source,
                "description": i.description,
                "date": i.income_date,
                "year_month": i.income_date.strftime("%Y-%m")
            }
            for i in incomes
        ]
        inc_df = pd.DataFrame(inc_data)

        # Calculate highest single expense
        highest_expense_amount = 0.0
        highest_expense_category = "N/A"
        highest_expense_desc = "N/A"
        if not exp_df.empty:
            max_idx = exp_df["amount"].idxmax()
            highest_expense_amount = float(exp_df.loc[max_idx, "amount"])
            highest_expense_category = str(exp_df.loc[max_idx, "category"])
            highest_expense_desc = str(exp_df.loc[max_idx, "description"])

        # Calculate category-wise breakdown and top spending category
        category_df = pd.DataFrame(columns=["category", "total_amount", "percentage"])
        highest_category_name = "N/A"
        highest_category_total = 0.0

        if not exp_df.empty:
            cat_grouped = exp_df.groupby("category")["amount"].sum().reset_index()
            cat_grouped.columns = ["category", "total_amount"]
            total_exp_sum = cat_grouped["total_amount"].sum()
            cat_grouped["percentage"] = (cat_grouped["total_amount"] / total_exp_sum * 100.0).round(1)
            cat_grouped = cat_grouped.sort_values(by="total_amount", ascending=False)
            category_df = cat_grouped

            top_cat_row = cat_grouped.iloc[0]
            highest_category_name = top_cat_row["category"]
            highest_category_total = float(top_cat_row["total_amount"])

        # Calculate monthly aggregations
        all_months = sorted(list(set(
            (exp_df["year_month"].tolist() if not exp_df.empty else []) +
            (inc_df["year_month"].tolist() if not inc_df.empty else [])
        )))

        monthly_rows = []
        for ym in all_months:
            m_inc = inc_df[inc_df["year_month"] == ym]["amount"].sum() if not inc_df.empty else 0.0
            m_exp = exp_df[exp_df["year_month"] == ym]["amount"].sum() if not exp_df.empty else 0.0
            m_sav = m_inc - m_exp
            m_rate = (m_sav / m_inc * 100.0) if m_inc > 0 else 0.0
            monthly_rows.append({
                "month_year": ym,
                "income": float(m_inc),
                "expenses": float(m_exp),
                "savings": float(m_sav),
                "savings_rate": round(m_rate, 1)
            })

        monthly_df = pd.DataFrame(monthly_rows)

        # Calculate average monthly expenses
        avg_monthly_expense = float(monthly_df["expenses"].mean()) if not monthly_df.empty else 0.0

        # Step 4: Generate automated, dynamic financial insights
        insights = []

        # Insight 1: Highest spending category
        if highest_category_name != "N/A":
            pct = category_df.iloc[0]["percentage"] if not category_df.empty else 0
            insights.append(f"📌 **{highest_category_name}** is your highest spending category, accounting for **₹{highest_category_total:,.2f}** ({pct}% of total expenses).")

        # Insight 2: Savings rate evaluation
        overall_summary = get_financial_summary(user_id)
        sav_rate = overall_summary["savings_rate"]
        if sav_rate >= 50:
            insights.append(f"🌟 Excellent financial discipline! Your overall savings rate is **{sav_rate}%**, which is well above the recommended 30% benchmark.")
        elif sav_rate >= 20:
            insights.append(f"👍 Healthy savings habit! You are saving **{sav_rate}%** of your total earnings. Aiming for 30%+ can accelerate your financial freedom.")
        elif sav_rate > 0:
            insights.append(f"⚠️ Your savings rate is currently **{sav_rate}%**. Consider reviewing non-essential spending like Shopping or Entertainment to boost savings.")
        else:
            insights.append(f"🚨 Caution: Your current expenditures exceed your income. Look into trimming your top expense categories to balance your cash flow.")

        # Insight 3: Month-over-Month Expense Trend
        if len(monthly_df) >= 2:
            latest_exp = monthly_df.iloc[-1]["expenses"]
            prev_exp = monthly_df.iloc[-2]["expenses"]
            if prev_exp > 0:
                diff_pct = ((latest_exp - prev_exp) / prev_exp) * 100.0
                if diff_pct > 0:
                    insights.append(f"📈 Your expenses increased by **{diff_pct:.1f}%** compared to the previous month.")
                elif diff_pct < 0:
                    insights.append(f"📉 Great job! Your expenses decreased by **{abs(diff_pct):.1f}%** compared to the previous month.")
                else:
                    insights.append(f"⚖️ Your monthly spending remained constant compared to the previous month.")

        # Insight 4: Highest single purchase reminder
        if highest_expense_amount > 0:
            insights.append(f"💳 Your largest single transaction was **₹{highest_expense_amount:,.2f}** under **{highest_expense_category}** ({highest_expense_desc or 'No description'}).")

        return {
            "avg_monthly_expense": avg_monthly_expense,
            "highest_expense_amount": highest_expense_amount,
            "highest_expense_category": highest_expense_category,
            "highest_expense_desc": highest_expense_desc,
            "highest_category_name": highest_category_name,
            "highest_category_total": highest_category_total,
            "monthly_df": monthly_df,
            "category_df": category_df,
            "insights": insights
        }

    finally:
        session.close()


# ---------------------------------------------------------------------------
# 6. UNIFIED TRANSACTIONS LEDGER
# ---------------------------------------------------------------------------

def get_all_transactions_df(
    user_id: int,
    start_date: date = None,
    end_date: date = None,
    transaction_type: str = "All",
    category: str = "All",
    search_term: str = None
) -> pd.DataFrame:
    """
    Combine both Income and Expense transactions into a single unified ledger DataFrame.

    Standard Columns:
        - Date: Transaction date (YYYY-MM-DD)
        - Type: 'Income' or 'Expense'
        - Category / Source: e.g. Salary or Food
        - Amount: Formatted floating point currency
        - Description: User notes
        - Payment Method: UPI, Credit Card, etc. ('N/A' for Income)
        - Record ID: Underlying database primary key

    Parameters:
        user_id (int): Active user ID.
        start_date (date, optional): Start date filter.
        end_date (date, optional): End date filter.
        transaction_type (str): 'All', 'Income', or 'Expense'.
        category (str): Category/Source filter.
        search_term (str, optional): Keyword search string.

    Returns:
        pd.DataFrame: Merged, sorted, and filtered transaction ledger.
    """
    rows = []

    # Fetch Incomes if transaction_type is 'All' or 'Income'
    if transaction_type in ["All", "Income"]:
        inc_df = get_incomes_df(user_id=user_id, start_date=start_date, end_date=end_date)
        for _, r in inc_df.iterrows():
            rows.append({
                "Date": r["income_date"],
                "Type": "Income",
                "Category / Source": r["source"],
                "Amount (₹)": float(r["amount"]),
                "Description": r["description"],
                "Payment Method": "Bank Deposit / Other",
                "ID": r["income_id"]
            })

    # Fetch Expenses if transaction_type is 'All' or 'Expense'
    if transaction_type in ["All", "Expense"]:
        exp_df = get_expenses_df(user_id=user_id, start_date=start_date, end_date=end_date)
        for _, r in exp_df.iterrows():
            rows.append({
                "Date": r["expense_date"],
                "Type": "Expense",
                "Category / Source": r["category"],
                "Amount (₹)": float(r["amount"]),
                "Description": r["description"],
                "Payment Method": r["payment_method"],
                "ID": r["expense_id"]
            })

    # Build Pandas DataFrame
    df = pd.DataFrame(rows)

    if df.empty:
        return pd.DataFrame(columns=["Date", "Type", "Category / Source", "Amount (₹)", "Description", "Payment Method", "ID"])

    # Apply Category filter if specified
    if category and category != "All":
        df = df[df["Category / Source"] == category]

    # Apply text search filter on Description or Category/Source
    if search_term and search_term.strip():
        term = search_term.strip().lower()
        df = df[
            df["Description"].str.lower().str.contains(term, na=False) |
            df["Category / Source"].str.lower().str.contains(term, na=False) |
            df["Payment Method"].str.lower().str.contains(term, na=False)
        ]

    # Sort descending by transaction Date
    df = df.sort_values(by="Date", ascending=False).reset_index(drop=True)

    return df


# ---------------------------------------------------------------------------
# 7. REALISTIC DEMO DATA POPULATOR
# ---------------------------------------------------------------------------

def load_demo_data(user_id: int) -> tuple[bool, str]:
    """
    Seed realistic sample financial records (Income, Expenses, Budgets)
    exclusively for the currently logged-in user.

    Provides multi-month transactions so charts, metrics, and budget progress bars
    immediately look lively and ready for presentation.

    Parameters:
        user_id (int): Active user's primary key ID.

    Returns:
        tuple[bool, str]: (Success boolean, Status message)
    """
    session = SessionLocal()
    try:
        # Determine baseline dates relative to current date
        today = date.today()
        current_year = today.year
        current_month = today.month

        # Month offsets: current month (0), last month (-1), 2 months ago (-2)
        sample_incomes = [
            # Current Month Incomes
            {"amount": 65000.0, "source": "Salary", "description": "Monthly Software Engineer Salary", "date": today.replace(day=1)},
            {"amount": 12000.0, "source": "Freelance", "description": "Client Web App UI Design", "date": today.replace(day=10) if today.day >= 10 else today},
            {"amount": 4500.0, "source": "Investment", "description": "Mutual Fund Quarterly Dividend", "date": today.replace(day=15) if today.day >= 15 else today},

            # Previous Month Incomes
            {"amount": 65000.0, "source": "Salary", "description": "Monthly Software Engineer Salary", "date": (today - timedelta(days=32)).replace(day=1)},
            {"amount": 15000.0, "source": "Freelance", "description": "Data Pipeline Consulting", "date": (today - timedelta(days=32)).replace(day=12)},
            {"amount": 3500.0, "source": "Interest", "description": "Fixed Deposit Accrued Interest", "date": (today - timedelta(days=32)).replace(day=20)},

            # 2 Months Ago Incomes
            {"amount": 62000.0, "source": "Salary", "description": "Monthly Software Engineer Salary", "date": (today - timedelta(days=64)).replace(day=1)},
            {"amount": 8000.0, "source": "Business", "description": "E-commerce Affiliate Income", "date": (today - timedelta(days=64)).replace(day=14)},
        ]

        sample_expenses = [
            # Current Month Expenses
            {"amount": 18000.0, "category": "Rent", "desc": "Apartment Monthly Rent", "method": "Bank Transfer", "date": today.replace(day=2)},
            {"amount": 6500.0, "category": "Food", "desc": "Grocery & Supermarket Stock", "method": "UPI", "date": today.replace(day=4)},
            {"amount": 2200.0, "category": "Food", "desc": "Weekend Dinner with Friends", "method": "Credit Card", "date": today.replace(day=7) if today.day >= 7 else today},
            {"amount": 3500.0, "category": "Transportation", "desc": "Fuel & Metro Card Recharge", "method": "UPI", "date": today.replace(day=8) if today.day >= 8 else today},
            {"amount": 4200.0, "category": "Shopping", "desc": "New Office Clothes & Shoes", "method": "Credit Card", "date": today.replace(day=11) if today.day >= 11 else today},
            {"amount": 2800.0, "category": "Bills", "desc": "Electricity & High-Speed WiFi Bill", "method": "UPI", "date": today.replace(day=12) if today.day >= 12 else today},
            {"amount": 1500.0, "category": "Entertainment", "desc": "Movie & Streaming Subscriptions", "method": "Debit Card", "date": today.replace(day=14) if today.day >= 14 else today},
            {"amount": 2000.0, "category": "Healthcare", "desc": "Doctor Consultation & Vitamins", "method": "Cash", "date": today.replace(day=16) if today.day >= 16 else today},

            # Previous Month Expenses
            {"amount": 18000.0, "category": "Rent", "desc": "Apartment Monthly Rent", "method": "Bank Transfer", "date": (today - timedelta(days=32)).replace(day=2)},
            {"amount": 7800.0, "category": "Food", "desc": "Weekly Groceries & Dining", "method": "UPI", "date": (today - timedelta(days=32)).replace(day=6)},
            {"amount": 3200.0, "category": "Transportation", "desc": "Cab Rides & Fuel", "method": "UPI", "date": (today - timedelta(days=32)).replace(day=10)},
            {"amount": 5500.0, "category": "Shopping", "desc": "Electronics & Accessories", "method": "Credit Card", "date": (today - timedelta(days=32)).replace(day=15)},
            {"amount": 2900.0, "category": "Bills", "desc": "Utility Bills", "method": "UPI", "date": (today - timedelta(days=32)).replace(day=18)},
            {"amount": 2500.0, "category": "Entertainment", "desc": "Concert Ticket", "method": "Debit Card", "date": (today - timedelta(days=32)).replace(day=22)},

            # 2 Months Ago Expenses
            {"amount": 18000.0, "category": "Rent", "desc": "Apartment Monthly Rent", "method": "Bank Transfer", "date": (today - timedelta(days=64)).replace(day=2)},
            {"amount": 7200.0, "category": "Food", "desc": "Groceries and Dining Out", "method": "UPI", "date": (today - timedelta(days=64)).replace(day=5)},
            {"amount": 3000.0, "category": "Transportation", "desc": "Public Transit & Petrol", "method": "UPI", "date": (today - timedelta(days=64)).replace(day=9)},
            {"amount": 3500.0, "category": "Shopping", "desc": "Home Essentials", "method": "Credit Card", "date": (today - timedelta(days=64)).replace(day=16)},
            {"amount": 2700.0, "category": "Bills", "desc": "Mobile & Internet Bills", "method": "UPI", "date": (today - timedelta(days=64)).replace(day=20)},
        ]

        sample_budgets = [
            # Current Month Budgets
            {"category": "Rent", "limit": 18000.0, "month": current_month, "year": current_year},
            {"category": "Food", "limit": 10000.0, "month": current_month, "year": current_year},
            {"category": "Transportation", "limit": 4500.0, "month": current_month, "year": current_year},
            {"category": "Shopping", "limit": 6000.0, "month": current_month, "year": current_year},
            {"category": "Bills", "limit": 3500.0, "month": current_month, "year": current_year},
            {"category": "Entertainment", "limit": 3000.0, "month": current_month, "year": current_year},
            {"category": "Healthcare", "limit": 3000.0, "month": current_month, "year": current_year},
        ]

        # Insert Incomes
        for inc in sample_incomes:
            session.add(Income(
                user_id=user_id,
                amount=inc["amount"],
                source=inc["source"],
                description=inc["description"],
                income_date=inc["date"]
            ))

        # Insert Expenses
        for exp in sample_expenses:
            session.add(Expense(
                user_id=user_id,
                amount=exp["amount"],
                category=exp["category"],
                description=exp["desc"],
                payment_method=exp["method"],
                expense_date=exp["date"]
            ))

        # Insert Budgets (delete existing ones for current month first to prevent duplicates)
        session.query(Budget).filter(
            Budget.user_id == user_id,
            Budget.month == current_month,
            Budget.year == current_year
        ).delete()

        for b in sample_budgets:
            session.add(Budget(
                user_id=user_id,
                category=b["category"],
                monthly_limit=b["limit"],
                month=b["month"],
                year=b["year"]
            ))

        session.commit()
        return True, "Demo financial data successfully loaded into your account!"

    except Exception as e:
        session.rollback()
        return False, f"Failed to load demo data: {str(e)}"
    finally:
        session.close()
