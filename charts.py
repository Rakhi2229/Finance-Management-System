"""
=============================================================================
FINTRACK - PERSONAL FINANCE MANAGEMENT SYSTEM
Module: charts.py
Description: Interactive Plotly data visualization figures for financial
             dashboards, analytics, trends, and budget vs actual comparisons.
=============================================================================
"""

import pandas as pd  # Import Pandas for DataFrame manipulations before plotting
import plotly.graph_objects as go  # Import Plotly Graph Objects for fine-grained chart customizations
import plotly.express as px  # Import Plotly Express for color palettes and rapid figure builders


# ---------------------------------------------------------------------------
# 1. COLOR THEME PALETTE (PROFESSIONAL BANKING AESTHETIC)
# ---------------------------------------------------------------------------

COLOR_INCOME = "#10B981"      # Emerald Green for positive income
COLOR_EXPENSE = "#EF4444"     # Rose Red for expenditures
COLOR_SAVINGS = "#3B82F6"     # Royal Blue for savings
COLOR_BUDGET = "#6366F1"      # Indigo for budget allocations
COLOR_WARNING = "#F59E0B"     # Amber Orange for warnings

# Categorical color sequence for expense donut and bar charts
CATEGORY_COLORS = [
    "#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6",
    "#EC4899", "#14B8A6", "#6366F1", "#84CC16", "#F97316"
]


# ---------------------------------------------------------------------------
# 2. HELPER: EMPTY STATE CHART PLACEHOLDER
# ---------------------------------------------------------------------------

def _create_empty_chart(title: str, message: str = "No data recorded yet.") -> go.Figure:
    """
    Generate a clean placeholder Plotly figure when no data is available to plot.

    Parameters:
        title (str): The intended chart title.
        message (str): Explanatory message displayed to the user.

    Returns:
        go.Figure: A formatted empty state figure.
    """
    fig = go.Figure()
    # Add a centered annotation message
    fig.add_annotation(
        text=f"<b>{message}</b><br><span style='font-size:12px;color:#6B7280;'>Add transactions to view this chart</span>",
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=14, color="#4B5563")
    )
    # Apply standard minimalist styling
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color="#111827")),
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=320,
        margin=dict(l=20, r=20, t=45, b=20)
    )
    return fig


# ---------------------------------------------------------------------------
# 3. CHART: MONTHLY INCOME VS EXPENSES (BAR CHART)
# ---------------------------------------------------------------------------

def plot_income_vs_expenses(income_df: pd.DataFrame, expense_df: pd.DataFrame) -> go.Figure:
    """
    Create a grouped bar chart comparing Total Income vs Total Expenses per month.

    Parameters:
        income_df (pd.DataFrame): User's income records.
        expense_df (pd.DataFrame): User's expense records.

    Returns:
        go.Figure: Plotly grouped bar chart figure.
    """
    # Check if both datasets are empty
    if income_df.empty and expense_df.empty:
        return _create_empty_chart("Monthly Income vs Expenses")

    # Copy data to avoid mutating original DataFrames
    inc_copy = income_df.copy()
    exp_copy = expense_df.copy()

    # Extract 'YYYY-MM' strings for time grouping
    if not inc_copy.empty:
        inc_copy["month_year"] = pd.to_datetime(inc_copy["income_date"]).dt.strftime("%Y-%m")
        inc_monthly = inc_copy.groupby("month_year")["amount"].sum().reset_index()
    else:
        inc_monthly = pd.DataFrame(columns=["month_year", "amount"])

    if not exp_copy.empty:
        exp_copy["month_year"] = pd.to_datetime(exp_copy["expense_date"]).dt.strftime("%Y-%m")
        exp_monthly = exp_copy.groupby("month_year")["amount"].sum().reset_index()
    else:
        exp_monthly = pd.DataFrame(columns=["month_year", "amount"])

    # Merge monthly totals on month_year
    merged = pd.merge(inc_monthly, exp_monthly, on="month_year", how="outer", suffixes=("_inc", "_exp")).fillna(0.0)
    merged = merged.sort_values(by="month_year")

    # Build grouped bar figure
    fig = go.Figure()

    # Add Income bars (Green)
    fig.add_trace(go.Bar(
        x=merged["month_year"],
        y=merged["amount_inc"],
        name="Income",
        marker_color=COLOR_INCOME,
        hovertemplate="<b>Income</b><br>Month: %{x}<br>Amount: ₹%{y:,.2f}<extra></extra>",
        marker=dict(cornerradius=4)
    ))

    # Add Expense bars (Red)
    fig.add_trace(go.Bar(
        x=merged["month_year"],
        y=merged["amount_exp"],
        name="Expenses",
        marker_color=COLOR_EXPENSE,
        hovertemplate="<b>Expenses</b><br>Month: %{x}<br>Amount: ₹%{y:,.2f}<extra></extra>",
        marker=dict(cornerradius=4)
    ))

    # Update layout configuration for modern aesthetics
    fig.update_layout(
        title=dict(text="Monthly Income vs Expenses", font=dict(size=15, color="#111827", family="sans-serif")),
        barmode="group",
        bargap=0.25,
        bargroupgap=0.1,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(title=None, showgrid=False, linecolor="#E5E7EB"),
        yaxis=dict(title="Amount (₹)", gridcolor="#F3F4F6", tickprefix="₹", tickformat=","),
        height=340,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    return fig


# ---------------------------------------------------------------------------
# 4. CHART: EXPENSE BY CATEGORY (DONUT PIE CHART)
# ---------------------------------------------------------------------------

def plot_expense_by_category(expense_df: pd.DataFrame) -> go.Figure:
    """
    Create a clean donut chart displaying the percentage distribution of expenses by category.

    Parameters:
        expense_df (pd.DataFrame): User's expense records.

    Returns:
        go.Figure: Plotly Donut chart figure.
    """
    if expense_df.empty:
        return _create_empty_chart("Expenses by Category")

    # Aggregate total spending by category
    cat_summary = expense_df.groupby("category")["amount"].sum().reset_index()
    cat_summary = cat_summary.sort_values(by="amount", ascending=False)

    # Build Donut Chart
    fig = go.Figure(data=[
        go.Pie(
            labels=cat_summary["category"],
            values=cat_summary["amount"],
            hole=0.55,  # Creates the central hollow space for the modern donut appearance
            marker=dict(colors=CATEGORY_COLORS),
            textinfo="percent+label",
            textposition="outside",
            hovertemplate="<b>%{label}</b><br>Spent: ₹%{value:,.2f}<br>Share: %{percent}<extra></extra>"
        )
    ])

    fig.update_layout(
        title=dict(text="Expenses by Category", font=dict(size=15, color="#111827", family="sans-serif")),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=340,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    return fig


# ---------------------------------------------------------------------------
# 5. CHART: MONTHLY SPENDING TREND (LINE CHART)
# ---------------------------------------------------------------------------

def plot_monthly_spending_trend(expense_df: pd.DataFrame) -> go.Figure:
    """
    Create a line chart showing spending trajectory over time.

    Parameters:
        expense_df (pd.DataFrame): User's expense records.

    Returns:
        go.Figure: Plotly line chart figure.
    """
    if expense_df.empty:
        return _create_empty_chart("Monthly Spending Trend")

    exp_copy = expense_df.copy()
    exp_copy["month_year"] = pd.to_datetime(exp_copy["expense_date"]).dt.strftime("%Y-%m")
    trend_df = exp_copy.groupby("month_year")["amount"].sum().reset_index()
    trend_df = trend_df.sort_values(by="month_year")

    # Build Line Figure with gentle fill area
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=trend_df["month_year"],
        y=trend_df["amount"],
        mode="lines+markers",
        name="Spending",
        line=dict(color=COLOR_EXPENSE, width=3, shape="spline"),  # Spline smooths the curve
        marker=dict(size=7, color=COLOR_EXPENSE, symbol="circle"),
        fill="tozeroy",
        fillcolor="rgba(239, 68, 68, 0.08)",  # Subtle red glow fill under the curve
        hovertemplate="<b>Spending Trend</b><br>Month: %{x}<br>Total Spent: ₹%{y:,.2f}<extra></extra>"
    ))

    fig.update_layout(
        title=dict(text="Monthly Spending Trend", font=dict(size=15, color="#111827")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title=None, showgrid=False, linecolor="#E5E7EB"),
        yaxis=dict(title="Spent (₹)", gridcolor="#F3F4F6", tickprefix="₹", tickformat=","),
        height=320,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    return fig


# ---------------------------------------------------------------------------
# 6. CHART: SAVINGS PROGRESSION & TREND (LINE & AREA CHART)
# ---------------------------------------------------------------------------

def plot_savings_trend(income_df: pd.DataFrame, expense_df: pd.DataFrame) -> go.Figure:
    """
    Create a chart displaying monthly net savings (Income - Expenses) over time.

    Parameters:
        income_df (pd.DataFrame): User's income records.
        expense_df (pd.DataFrame): User's expense records.

    Returns:
        go.Figure: Plotly savings trend figure.
    """
    if income_df.empty and expense_df.empty:
        return _create_empty_chart("Monthly Savings Trend")

    inc_copy = income_df.copy()
    exp_copy = expense_df.copy()

    if not inc_copy.empty:
        inc_copy["month_year"] = pd.to_datetime(inc_copy["income_date"]).dt.strftime("%Y-%m")
        inc_m = inc_copy.groupby("month_year")["amount"].sum().reset_index()
    else:
        inc_m = pd.DataFrame(columns=["month_year", "amount"])

    if not exp_copy.empty:
        exp_copy["month_year"] = pd.to_datetime(exp_copy["expense_date"]).dt.strftime("%Y-%m")
        exp_m = exp_copy.groupby("month_year")["amount"].sum().reset_index()
    else:
        exp_m = pd.DataFrame(columns=["month_year", "amount"])

    merged = pd.merge(inc_m, exp_m, on="month_year", how="outer", suffixes=("_inc", "_exp")).fillna(0.0)
    merged["savings"] = merged["amount_inc"] - merged["amount_exp"]
    merged = merged.sort_values(by="month_year")

    fig = go.Figure()

    # Add Net Savings trace
    fig.add_trace(go.Scatter(
        x=merged["month_year"],
        y=merged["savings"],
        mode="lines+markers",
        name="Net Savings",
        line=dict(color=COLOR_SAVINGS, width=3, shape="spline"),
        marker=dict(size=7, color=COLOR_SAVINGS),
        fill="tozeroy",
        fillcolor="rgba(59, 130, 246, 0.1)",
        hovertemplate="<b>Savings</b><br>Month: %{x}<br>Net Savings: ₹%{y:,.2f}<extra></extra>"
    ))

    # Add zero-line reference for break-even
    fig.add_hline(y=0, line_dash="dash", line_color="#9CA3AF", line_width=1)

    fig.update_layout(
        title=dict(text="Monthly Savings Trend", font=dict(size=15, color="#111827")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title=None, showgrid=False, linecolor="#E5E7EB"),
        yaxis=dict(title="Savings (₹)", gridcolor="#F3F4F6", tickprefix="₹", tickformat=","),
        height=320,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    return fig


# ---------------------------------------------------------------------------
# 7. CHART: BUDGET VS ACTUAL SPENDING (COMPARISON BAR CHART)
# ---------------------------------------------------------------------------

def plot_budget_vs_actual(budget_status_df: pd.DataFrame) -> go.Figure:
    """
    Create a grouped bar chart comparing budgeted limits against actual spending per category.

    Parameters:
        budget_status_df (pd.DataFrame): Budget status calculation DataFrame.

    Returns:
        go.Figure: Plotly comparison bar chart figure.
    """
    if budget_status_df.empty:
        return _create_empty_chart("Budget vs Actual Spending", "No budgets configured for this month.")

    fig = go.Figure()

    # Trace 1: Budget Target Limit (Indigo)
    fig.add_trace(go.Bar(
        x=budget_status_df["category"],
        y=budget_status_df["monthly_limit"],
        name="Budget Limit",
        marker_color=COLOR_BUDGET,
        hovertemplate="<b>Budget Target</b><br>Category: %{x}<br>Limit: ₹%{y:,.2f}<extra></extra>",
        marker=dict(cornerradius=4)
    ))

    # Trace 2: Actual Amount Spent (Orange / Red)
    # Color bars dynamically: red if exceeded, amber otherwise
    colors = [
        COLOR_EXPENSE if row["usage_pct"] > 100 else COLOR_WARNING
        for _, row in budget_status_df.iterrows()
    ]

    fig.add_trace(go.Bar(
        x=budget_status_df["category"],
        y=budget_status_df["spent"],
        name="Actual Spent",
        marker_color=colors,
        hovertemplate="<b>Actual Spent</b><br>Category: %{x}<br>Spent: ₹%{y:,.2f}<extra></extra>",
        marker=dict(cornerradius=4)
    ))

    fig.update_layout(
        title=dict(text="Budget vs Actual Spending by Category", font=dict(size=15, color="#111827")),
        barmode="group",
        bargap=0.25,
        bargroupgap=0.1,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(title=None, showgrid=False, linecolor="#E5E7EB"),
        yaxis=dict(title="Amount (₹)", gridcolor="#F3F4F6", tickprefix="₹", tickformat=","),
        height=350,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    return fig
