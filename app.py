"""
=============================================================================
FINTRACK - PERSONAL FINANCE MANAGEMENT SYSTEM
Module: app.py
Description: Main Streamlit application module containing the user interface,
             page routing, authentication screens, financial dashboards,
             CRUD management forms, analytical views, and CSV report exports.
=============================================================================
"""

from datetime import date, datetime  # Import datetime tools for current dates and greetings
import streamlit as st  # Import Streamlit for the complete web application user interface
import pandas as pd  # Import Pandas for DataFrame manipulation and CSV exports

# Import database initialization and session helpers
from database import init_db

# Import authentication functions and session state managers
from auth import (
    init_session_state,
    register_user,
    login_user,
    set_user_session,
    logout_user
)

# Import financial calculation, CRUD, and demo data utilities
from finance import (
    INCOME_SOURCES,
    EXPENSE_CATEGORIES,
    PAYMENT_METHODS,
    add_income,
    get_incomes_df,
    get_income_by_id,
    update_income,
    delete_income,
    add_expense,
    get_expenses_df,
    get_expense_by_id,
    update_expense,
    delete_expense,
    set_or_update_budget,
    get_budgets_df,
    get_budget_status_df,
    delete_budget,
    get_financial_summary,
    get_analytics_summary,
    get_all_transactions_df
)

# Import Plotly visualization builder functions
from charts import (
    plot_income_vs_expenses,
    plot_expense_by_category,
    plot_monthly_spending_trend,
    plot_savings_trend,
    plot_budget_vs_actual
)


# ---------------------------------------------------------------------------
# 1. STREAMLIT PAGE CONFIGURATION
# ---------------------------------------------------------------------------

# Configure the browser tab title, page icon, layout mode, and initial sidebar state
st.set_page_config(
    page_title="FinTrack - Personal Finance Manager",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------------------------------------------------------------------
# 2. CUSTOM CSS STYLING (MODERN PROFESSIONAL BANKING DASHBOARD)
# ---------------------------------------------------------------------------

def apply_custom_styles():
    """
    Inject clean, minimal CSS for a professional personal banking UI aesthetic.
    Enhances card borders, metric containers, badges, and button styling.
    """
    st.markdown("""
    <style>
        /* Import clean modern font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Clean metric card containers */
        div[data-testid="stMetric"] {
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 10px;
            padding: 16px 20px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
            transition: all 0.2s ease-in-out;
        }

        div[data-testid="stMetric"]:hover {
            border-color: #CBD5E1;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
        }

        div[data-testid="stMetricLabel"] {
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            color: #6B7280 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.6rem !important;
            font-weight: 700 !important;
            color: #111827 !important;
        }

        /* Custom Card container for budget and analytics widgets */
        .fintrack-card {
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
        }

        /* Custom Pill Badges for Budget Status */
        .status-badge-good {
            background-color: #DCFCE7;
            color: #15803D;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        .status-badge-warning {
            background-color: #FEF3C7;
            color: #B45309;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        .status-badge-exceeded {
            background-color: #FEE2E2;
            color: #B91C1C;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        /* Clean Streamlit form submit button styling */
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.15s ease-in-out;
        }

        /* Table header formatting */
        div[data-testid="stDataFrame"] {
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            overflow: hidden;
        }

        /* Sidebar user branding box */
        .sidebar-brand-box {
            padding: 12px;
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# 3. HELPER: TIME-BASED GREETING
# ---------------------------------------------------------------------------

def get_time_greeting() -> str:
    """
    Generate a dynamic greeting string (morning, afternoon, evening) based on current hour.

    Returns:
        str: Context-aware greeting phrase.
    """
    current_hour = datetime.now().hour
    if current_hour < 12:
        return "Good morning"
    elif 12 <= current_hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"


# ---------------------------------------------------------------------------
# 4. AUTHENTICATION SCREENS (LOGIN & REGISTRATION)
# ---------------------------------------------------------------------------

def render_auth_page():
    """
    Render the clean, centered login and registration authentication screen.
    Displays tabbed forms for logging in and creating a new account.
    """
    # Center layout using 3 columns with empty side columns
    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        # Application branding header
        st.markdown(
            """
            <div style="text-align: center; margin-top: 20px; margin-bottom: 25px;">
                <h1 style="font-size: 2.4rem; font-weight: 800; color: #1E293B; margin-bottom: 4px;">
                    💳 FinTrack
                </h1>
                <p style="font-size: 1.05rem; color: #64748B; margin: 0;">
                    Personal Finance Management System
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Tabbed interface for Login and Registration
        tab_login, tab_register = st.tabs(["🔐 Login", "📝 Create Account"])

        # ----------------- LOGIN TAB -----------------
        with tab_login:
            st.markdown("<p style='color:#6B7280; font-size:0.9rem;'>Welcome back! Please enter your credentials.</p>", unsafe_allow_html=True)

            with st.form("login_form", clear_on_submit=False):
                login_email = st.text_input("Email Address", placeholder="name@example.com")
                login_password = st.text_input("Password", type="password", placeholder="••••••••")

                submit_login = st.form_submit_button("Log In", use_container_width=True, type="primary")

                if submit_login:
                    success, message, user_data = login_user(login_email, login_password)
                    if success:
                        # Store authenticated user details into Streamlit session state
                        set_user_session(
                            user_id=user_data["user_id"],
                            full_name=user_data["full_name"],
                            email=user_data["email"]
                        )
                        st.success(message)
                        st.rerun()  # Refresh immediately to show dashboard
                    else:
                        st.error(message)

        # ----------------- REGISTRATION TAB -----------------
        with tab_register:
            st.markdown("<p style='color:#6B7280; font-size:0.9rem;'>Create your personal finance account.</p>", unsafe_allow_html=True)

            with st.form("registration_form", clear_on_submit=True):
                reg_name = st.text_input("Full Name", placeholder="e.g. John Doe")
                reg_email = st.text_input("Email Address", placeholder="e.g. john@example.com")
                reg_pass = st.text_input("Password", type="password", placeholder="Minimum 6 characters")
                reg_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")

                submit_reg = st.form_submit_button("Create Account", use_container_width=True, type="primary")

                if submit_reg:
                    success, message = register_user(reg_name, reg_email, reg_pass, reg_confirm)
                    if success:
                        st.success(message)
                        st.info("Switch to the 'Login' tab to sign in with your new credentials.")
                    else:
                        st.error(message)


# ---------------------------------------------------------------------------
# 5. PAGE: DASHBOARD (HOME OVERVIEW)
# ---------------------------------------------------------------------------

def render_dashboard(user_id: int, user_name: str):
    """
    Render the main executive Financial Overview Dashboard.

    Displays:
        - Greeting and subtitle
        - 6 Primary KPI Metric Cards (Income, Expenses, Balance, Savings, Savings Rate, Transactions)
        - 4 Core Interactive Plotly Visualizations in a 2x2 grid
        - Recent Transactions Preview Ledger
    """
    # Header & Greeting
    greeting = get_time_greeting()
    st.markdown(f"## {greeting}, {user_name} 👋")
    st.markdown("<p style='color:#6B7280; margin-top:-10px; margin-bottom:20px;'>Here is your comprehensive financial overview and cash flow status.</p>", unsafe_allow_html=True)

    # 1. Fetch Financial KPI Metrics
    summary = get_financial_summary(user_id)

    # 2. Render Top Row of 3 KPI Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="Total Income",
            value=f"₹{summary['total_income']:,.2f}",
            help="Sum of all recorded income sources"
        )
    with col2:
        st.metric(
            label="Total Expenses",
            value=f"₹{summary['total_expenses']:,.2f}",
            help="Sum of all recorded expenditures"
        )
    with col3:
        # Highlight positive balance with green indicator or negative with red
        st.metric(
            label="Current Balance",
            value=f"₹{summary['balance']:,.2f}",
            delta=f"₹{summary['balance']:,.2f}",
            delta_color="normal" if summary['balance'] >= 0 else "inverse",
            help="Net remaining funds: Total Income minus Total Expenses"
        )

    # 3. Render Bottom Row of 3 KPI Cards
    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric(
            label="Total Savings",
            value=f"₹{summary['savings']:,.2f}",
            help="Net savings accumulated"
        )
    with col5:
        st.metric(
            label="Savings Rate",
            value=f"{summary['savings_rate']}%",
            delta=f"{summary['savings_rate']}% of income",
            help="Percentage of earned income retained as savings"
        )
    with col6:
        st.metric(
            label="Total Transactions",
            value=f"{summary['total_transactions']}",
            help="Total combined count of income and expense records"
        )

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

    # 4. Fetch Datasets for Interactive Plotly Charts
    income_df = get_incomes_df(user_id)
    expense_df = get_expenses_df(user_id)

    # Row 1 of Visualizations (Income vs Expenses Bar Chart | Expense by Category Donut)
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(
            plot_income_vs_expenses(income_df, expense_df),
            use_container_width=True
        )
    with chart_col2:
        st.plotly_chart(
            plot_expense_by_category(expense_df),
            use_container_width=True
        )

    # Row 2 of Visualizations (Monthly Spending Trend | Savings Progression)
    chart_col3, chart_col4 = st.columns(2)
    with chart_col3:
        st.plotly_chart(
            plot_monthly_spending_trend(expense_df),
            use_container_width=True
        )
    with chart_col4:
        st.plotly_chart(
            plot_savings_trend(income_df, expense_df),
            use_container_width=True
        )

    # 5. Recent Transactions Preview Table
    st.markdown("### 📋 Recent Transactions")
    recent_df = get_all_transactions_df(user_id)

    if not recent_df.empty:
        # Display latest 5 records
        display_preview = recent_df.head(5)[["Date", "Type", "Category / Source", "Amount (₹)", "Payment Method", "Description"]]
        st.dataframe(
            display_preview,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Amount (₹)": st.column_config.NumberColumn(format="₹ %,.2f")
            }
        )
    else:
        st.info("No recent transactions found. Use the sidebar to load demo data or add income/expenses!")


# ---------------------------------------------------------------------------
# 6. PAGE: INCOME MANAGEMENT
# ---------------------------------------------------------------------------

def render_income_page(user_id: int):
    """
    Render the Income Management section.

    Allows users to:
        - Add new income records via expander form
        - Filter by date range and source
        - View formatted income transactions table
        - Edit or Delete individual income records
    """
    st.markdown("## 💰 Income Management")
    st.markdown("<p style='color:#6B7280; margin-top:-10px; margin-bottom:20px;'>Record, monitor, and manage your earnings and revenue streams.</p>", unsafe_allow_html=True)

    # ---------------- 1. ADD INCOME FORM (EXPANDER) ----------------
    with st.expander("➕ Add New Income", expanded=False):
        with st.form("add_income_form", clear_on_submit=True):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                inc_amount = st.number_input("Amount (₹)", min_value=0.0, step=500.0, format="%.2f")
                inc_source = st.selectbox("Income Source", options=INCOME_SOURCES)
            with f_col2:
                inc_date = st.date_input("Income Date", value=date.today())
                inc_desc = st.text_input("Description / Memo", placeholder="e.g. Monthly Salary, Freelance project")

            submit_inc = st.form_submit_button("Save Income Record", type="primary", use_container_width=True)

            if submit_inc:
                if inc_amount <= 0:
                    st.error("Please enter a valid amount greater than ₹0.")
                else:
                    success, msg = add_income(
                        user_id=user_id,
                        amount=inc_amount,
                        source=inc_source,
                        description=inc_desc,
                        income_date=inc_date
                    )
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    # ---------------- 2. FILTER CONTROLS ----------------
    st.markdown("#### 🔍 Filter Incomes")
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        source_options = ["All"] + INCOME_SOURCES
        selected_source = st.selectbox("Filter by Source", options=source_options)

    with filter_col2:
        start_date = st.date_input("From Date", value=None)

    with filter_col3:
        end_date = st.date_input("To Date", value=None)

    # ---------------- 3. DATA TABLE DISPLAY ----------------
    incomes_df = get_incomes_df(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        source=selected_source
    )

    # Metric summary for filtered view
    total_filtered_inc = incomes_df["amount"].sum() if not incomes_df.empty else 0.0
    count_filtered = len(incomes_df)

    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.metric("Total Income (Filtered)", f"₹{total_filtered_inc:,.2f}")
    with m_col2:
        st.metric("Total Records", f"{count_filtered}")

    if not incomes_df.empty:
        # Clean display DataFrame
        display_df = incomes_df[["income_id", "income_date", "source", "amount", "description"]].copy()
        display_df.columns = ["ID", "Date", "Source", "Amount (₹)", "Description"]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Amount (₹)": st.column_config.NumberColumn(format="₹ %,.2f")
            }
        )

        # ---------------- 4. EDIT & DELETE ACTIONS ----------------
        st.markdown("---")
        st.markdown("#### ⚙️ Edit or Delete Income Record")
        action_col1, action_col2 = st.columns(2)

        # Select record by ID
        record_ids = incomes_df["income_id"].tolist()
        id_labels = [f"ID {r['income_id']} - ₹{r['amount']:,.2f} ({r['source']} on {r['income_date']})" for _, r in incomes_df.iterrows()]
        selected_label = st.selectbox("Select Record to Manage", options=id_labels)

        if selected_label:
            selected_id = int(selected_label.split(" - ")[0].replace("ID ", ""))
            rec = get_income_by_id(selected_id, user_id)

            if rec:
                with action_col1:
                    with st.form(f"edit_income_{selected_id}"):
                        st.markdown(f"**Edit Record #{selected_id}**")
                        edit_amt = st.number_input("Amount (₹)", value=float(rec["amount"]), min_value=0.01, step=100.0)
                        edit_src = st.selectbox("Source", options=INCOME_SOURCES, index=INCOME_SOURCES.index(rec["source"]) if rec["source"] in INCOME_SOURCES else 0)
                        edit_date = st.date_input("Date", value=rec["income_date"])
                        edit_desc = st.text_input("Description", value=rec["description"] or "")

                        if st.form_submit_button("Update Income", type="primary"):
                            ok, msg = update_income(selected_id, user_id, edit_amt, edit_src, edit_desc, edit_date)
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

                with action_col2:
                    st.markdown(f"**Delete Record #{selected_id}**")
                    st.warning("Are you sure you want to permanently delete this income record?")
                    if st.button("🗑️ Confirm Delete Income", key=f"del_inc_{selected_id}", type="secondary"):
                        ok, msg = delete_income(selected_id, user_id)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

    else:
        st.info("No income records found matching the specified filters.")


# ---------------------------------------------------------------------------
# 7. PAGE: EXPENSE MANAGEMENT
# ---------------------------------------------------------------------------

def render_expenses_page(user_id: int):
    """
    Render the Expense Management section.

    Allows users to:
        - Add new expense records via expander form
        - Filter by category, payment method, and date range
        - View formatted expenses table
        - Edit or Delete individual expense records
    """
    st.markdown("## 💸 Expense Management")
    st.markdown("<p style='color:#6B7280; margin-top:-10px; margin-bottom:20px;'>Track expenditures, control spending habits, and categorize purchases.</p>", unsafe_allow_html=True)

    # ---------------- 1. ADD EXPENSE FORM (EXPANDER) ----------------
    with st.expander("➕ Add New Expense", expanded=False):
        with st.form("add_expense_form", clear_on_submit=True):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                exp_amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0, format="%.2f")
                exp_category = st.selectbox("Expense Category", options=EXPENSE_CATEGORIES)
                exp_method = st.selectbox("Payment Method", options=PAYMENT_METHODS)
            with f_col2:
                exp_date = st.date_input("Expense Date", value=date.today())
                exp_desc = st.text_input("Description / Memo", placeholder="e.g. Grocery store, Electricity bill")

            submit_exp = st.form_submit_button("Save Expense Record", type="primary", use_container_width=True)

            if submit_exp:
                if exp_amount <= 0:
                    st.error("Please enter a valid amount greater than ₹0.")
                else:
                    success, msg = add_expense(
                        user_id=user_id,
                        amount=exp_amount,
                        category=exp_category,
                        description=exp_desc,
                        payment_method=exp_method,
                        expense_date=exp_date
                    )
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    # ---------------- 2. FILTER CONTROLS ----------------
    st.markdown("#### 🔍 Filter Expenses")
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

    with filter_col1:
        cat_options = ["All"] + EXPENSE_CATEGORIES
        selected_cat = st.selectbox("Category", options=cat_options)

    with filter_col2:
        pm_options = ["All"] + PAYMENT_METHODS
        selected_pm = st.selectbox("Payment Method", options=pm_options)

    with filter_col3:
        start_date = st.date_input("From Date", value=None, key="exp_from_date")

    with filter_col4:
        end_date = st.date_input("To Date", value=None, key="exp_to_date")

    # ---------------- 3. DATA TABLE DISPLAY ----------------
    expenses_df = get_expenses_df(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        category=selected_cat,
        payment_method=selected_pm
    )

    total_filtered_exp = expenses_df["amount"].sum() if not expenses_df.empty else 0.0
    count_filtered = len(expenses_df)

    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.metric("Total Expenses (Filtered)", f"₹{total_filtered_exp:,.2f}")
    with m_col2:
        st.metric("Total Records", f"{count_filtered}")

    if not expenses_df.empty:
        display_df = expenses_df[["expense_id", "expense_date", "category", "amount", "payment_method", "description"]].copy()
        display_df.columns = ["ID", "Date", "Category", "Amount (₹)", "Payment Method", "Description"]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Amount (₹)": st.column_config.NumberColumn(format="₹ %,.2f")
            }
        )

        # ---------------- 4. EDIT & DELETE ACTIONS ----------------
        st.markdown("---")
        st.markdown("#### ⚙️ Edit or Delete Expense Record")
        action_col1, action_col2 = st.columns(2)

        id_labels = [f"ID {r['expense_id']} - ₹{r['amount']:,.2f} ({r['category']} on {r['expense_date']})" for _, r in expenses_df.iterrows()]
        selected_label = st.selectbox("Select Expense to Manage", options=id_labels)

        if selected_label:
            selected_id = int(selected_label.split(" - ")[0].replace("ID ", ""))
            rec = get_expense_by_id(selected_id, user_id)

            if rec:
                with action_col1:
                    with st.form(f"edit_expense_{selected_id}"):
                        st.markdown(f"**Edit Record #{selected_id}**")
                        edit_amt = st.number_input("Amount (₹)", value=float(rec["amount"]), min_value=0.01, step=50.0)
                        edit_cat = st.selectbox("Category", options=EXPENSE_CATEGORIES, index=EXPENSE_CATEGORIES.index(rec["category"]) if rec["category"] in EXPENSE_CATEGORIES else 0)
                        edit_pm = st.selectbox("Payment Method", options=PAYMENT_METHODS, index=PAYMENT_METHODS.index(rec["payment_method"]) if rec["payment_method"] in PAYMENT_METHODS else 0)
                        edit_date = st.date_input("Date", value=rec["expense_date"], key=f"edit_exp_date_{selected_id}")
                        edit_desc = st.text_input("Description", value=rec["description"] or "")

                        if st.form_submit_button("Update Expense", type="primary"):
                            ok, msg = update_expense(selected_id, user_id, edit_amt, edit_cat, edit_desc, edit_pm, edit_date)
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

                with action_col2:
                    st.markdown(f"**Delete Record #{selected_id}**")
                    st.warning("Are you sure you want to permanently delete this expense record?")
                    if st.button("🗑️ Confirm Delete Expense", key=f"del_exp_{selected_id}", type="secondary"):
                        ok, msg = delete_expense(selected_id, user_id)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

    else:
        st.info("No expense records found matching the specified filters.")


# ---------------------------------------------------------------------------
# 8. PAGE: BUDGET MANAGEMENT & TRACKING
# ---------------------------------------------------------------------------

def render_budgets_page(user_id: int):
    """
    Render the Budget Management and Visual Spending Cap Tracker section.

    Displays:
        - Monthly selector
        - Expander to configure or update monthly category budget limits
        - Dynamic budget progress cards with color-coded status badges
        - Budget vs Actual Spending comparison chart
        - Manage and delete budget targets
    """
    st.markdown("## 🎯 Budget Management")
    st.markdown("<p style='color:#6B7280; margin-top:-10px; margin-bottom:20px;'>Set category spending limits and monitor real-time consumption against your budget targets.</p>", unsafe_allow_html=True)

    # 1. Month & Year Selector
    today = date.today()
    sel_col1, sel_col2 = st.columns(2)
    with sel_col1:
        months_list = list(range(1, 13))
        month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        selected_month_name = st.selectbox("Select Month", options=month_names, index=today.month - 1)
        selected_month = month_names.index(selected_month_name) + 1

    with sel_col2:
        selected_year = st.number_input("Select Year", min_value=2020, max_value=2035, value=today.year, step=1)

    # 2. Add / Update Budget Form (Expander)
    with st.expander(f"➕ Set / Update Budget for {selected_month_name} {selected_year}", expanded=False):
        with st.form("set_budget_form", clear_on_submit=True):
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                b_category = st.selectbox("Category", options=EXPENSE_CATEGORIES)
            with b_col2:
                b_limit = st.number_input("Monthly Spending Limit (₹)", min_value=0.0, step=500.0, format="%.2f")

            submit_budget = st.form_submit_button("Save Budget Target", type="primary", use_container_width=True)

            if submit_budget:
                if b_limit <= 0:
                    st.error("Budget limit must be greater than ₹0.")
                else:
                    success, msg = set_or_update_budget(
                        user_id=user_id,
                        category=b_category,
                        monthly_limit=b_limit,
                        month=selected_month,
                        year=int(selected_year)
                    )
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    # 3. Retrieve and Display Budget Status
    status_df = get_budget_status_df(user_id, selected_month, int(selected_year))

    if not status_df.empty:
        st.markdown(f"### 📊 Budget Status ({selected_month_name} {selected_year})")

        # Display Visual Progress Cards in a 2-column grid
        card_cols = st.columns(2)
        for i, (_, row) in enumerate(status_df.iterrows()):
            col_target = card_cols[i % 2]
            with col_target:
                # Determine badge styling based on spending status
                if row["status"] == "Exceeded":
                    badge_html = f"<span class='status-badge-exceeded'>🚨 EXCEEDED ({row['usage_pct']}%)</span>"
                    progress_val = 1.0
                elif row["status"] == "Warning":
                    badge_html = f"<span class='status-badge-warning'>⚠️ WARNING ({row['usage_pct']}%)</span>"
                    progress_val = min(row["usage_pct"] / 100.0, 1.0)
                else:
                    badge_html = f"<span class='status-badge-good'>✅ ON TRACK ({row['usage_pct']}%)</span>"
                    progress_val = min(row["usage_pct"] / 100.0, 1.0)

                st.markdown(
                    f"""
                    <div class="fintrack-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-size: 1.1rem; font-weight: 700; color: #1E293B;">{row['category']}</span>
                            {badge_html}
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.9rem; color: #4B5563; margin-bottom: 4px;">
                            <span><b>Budget:</b> ₹{row['monthly_limit']:,.2f}</span>
                            <span><b>Spent:</b> ₹{row['spent']:,.2f}</span>
                            <span><b>Remaining:</b> ₹{row['remaining']:,.2f}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                # Streamlit visual progress bar
                st.progress(progress_val)
                st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

        # Plotly comparison chart
        st.plotly_chart(
            plot_budget_vs_actual(status_df),
            use_container_width=True
        )

        # Delete Budget option
        with st.expander("⚙️ Manage / Delete Budget Targets"):
            b_list = [f"ID {r['budget_id']} - {r['category']} (Limit: ₹{r['monthly_limit']:,.2f})" for _, r in status_df.iterrows()]
            selected_b = st.selectbox("Select Budget to Delete", options=b_list)
            if selected_b:
                del_b_id = int(selected_b.split(" - ")[0].replace("ID ", ""))
                if st.button("🗑️ Delete Selected Budget Target", type="secondary"):
                    ok, msg = delete_budget(del_b_id, user_id)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
    else:
        st.info(f"No budgets configured for {selected_month_name} {selected_year}. Use the expander above to set your first category budget limit!")


# ---------------------------------------------------------------------------
# 9. PAGE: ANALYTICS & DEEP FINANCIAL INSIGHTS
# ---------------------------------------------------------------------------

def render_analytics_page(user_id: int):
    """
    Render the Financial Data Analytics section.

    Calculates and presents:
        - Key analytical summary indicators (Avg monthly expense, Top expense, Top category)
        - Actionable dynamic financial insights
        - Monthly cash flow breakdown table
        - Category-wise spending distribution
    """
    st.markdown("## 📊 Financial Analytics & Insights")
    st.markdown("<p style='color:#6B7280; margin-top:-10px; margin-bottom:20px;'>Advanced analytical insights and data-driven evaluations of your spending habits.</p>", unsafe_allow_html=True)

    analytics = get_analytics_summary(user_id)

    # 1. Key Analytics KPI Metrics
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric("Avg. Monthly Expense", f"₹{analytics['avg_monthly_expense']:,.2f}")
    with kpi2:
        st.metric("Highest Single Expense", f"₹{analytics['highest_expense_amount']:,.2f}", f"{analytics['highest_expense_category']}")
    with kpi3:
        st.metric("Top Spending Category", f"{analytics['highest_category_name']}", f"₹{analytics['highest_category_total']:,.2f}")

    # 2. Automated Financial Insights Box
    st.markdown("### 💡 Financial Insights & Recommendations")
    for insight in analytics["insights"]:
        st.info(insight)

    st.markdown("---")

    # 3. Monthly Financial Breakdown & Category Distribution Tabs
    tab_monthly, tab_category = st.tabs(["📅 Monthly Performance", "🏷️ Category Distribution"])

    with tab_monthly:
        st.markdown("#### Monthly Income, Expenses & Savings Summary")
        monthly_df = analytics["monthly_df"]
        if not monthly_df.empty:
            display_m_df = monthly_df.copy()
            display_m_df.columns = ["Month-Year", "Income (₹)", "Expenses (₹)", "Savings (₹)", "Savings Rate (%)"]
            st.dataframe(
                display_m_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Income (₹)": st.column_config.NumberColumn(format="₹ %,.2f"),
                    "Expenses (₹)": st.column_config.NumberColumn(format="₹ %,.2f"),
                    "Savings (₹)": st.column_config.NumberColumn(format="₹ %,.2f"),
                    "Savings Rate (%)": st.column_config.NumberColumn(format="%.1f%%")
                }
            )
        else:
            st.info("No monthly data available yet.")

    with tab_category:
        st.markdown("#### Category-wise Spending Share")
        cat_df = analytics["category_df"]
        if not cat_df.empty:
            display_cat = cat_df.copy()
            display_cat.columns = ["Category", "Total Spent (₹)", "Share (%)"]
            st.dataframe(
                display_cat,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Total Spent (₹)": st.column_config.NumberColumn(format="₹ %,.2f"),
                    "Share (%)": st.column_config.NumberColumn(format="%.1f%%")
                }
            )
        else:
            st.info("No category data available yet.")


# ---------------------------------------------------------------------------
# 10. PAGE: UNIFIED TRANSACTIONS LEDGER
# ---------------------------------------------------------------------------

def render_transactions_page(user_id: int):
    """
    Render the Unified Transactions Ledger.

    Combines all Income and Expense records into a single sortable, searchable,
    and filterable DataFrame.
    """
    st.markdown("## 📋 Unified Transactions Ledger")
    st.markdown("<p style='color:#6B7280; margin-top:-10px; margin-bottom:20px;'>Complete transaction history combining both income earnings and expense outlays.</p>", unsafe_allow_html=True)

    # Filter Controls
    c1, c2, c3 = st.columns(3)
    with c1:
        tx_type = st.selectbox("Transaction Type", options=["All", "Income", "Expense"])
    with c2:
        search_kw = st.text_input("🔍 Search Keyword", placeholder="Search description, category, method...")
    with c3:
        all_cats = ["All"] + sorted(list(set(INCOME_SOURCES + EXPENSE_CATEGORIES)))
        selected_cat = st.selectbox("Filter Category / Source", options=all_cats)

    d1, d2 = st.columns(2)
    with d1:
        start_date = st.date_input("From Date", value=None, key="tx_start_date")
    with d2:
        end_date = st.date_input("To Date", value=None, key="tx_end_date")

    # Retrieve unified transaction records
    transactions_df = get_all_transactions_df(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        transaction_type=tx_type,
        category=selected_cat,
        search_term=search_kw
    )

    st.metric("Total Filtered Transactions", f"{len(transactions_df)}")

    if not transactions_df.empty:
        st.dataframe(
            transactions_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Amount (₹)": st.column_config.NumberColumn(format="₹ %,.2f")
            }
        )
    else:
        st.info("No transactions found matching the selected search criteria.")


# ---------------------------------------------------------------------------
# 11. PAGE: FINANCIAL REPORTS & CSV EXPORT
# ---------------------------------------------------------------------------

def render_reports_page(user_id: int):
    """
    Render the Financial Reports generation and CSV export section.

    Allows users to:
        - Select report types (Complete Ledger, Income, Expense, Monthly Summary, Category-wise, Budget)
        - Apply customized date/category filters
        - Preview the report table
        - Download as a clean CSV file via st.download_button
    """
    st.markdown("## 📄 Financial Reports & Data Export")
    st.markdown("<p style='color:#6B7280; margin-top:-10px; margin-bottom:20px;'>Generate structured financial statements and export data for spreadsheet analysis.</p>", unsafe_allow_html=True)

    report_types = [
        "1. Complete Transaction Ledger Report",
        "2. Income Statement Report",
        "3. Expense Report",
        "4. Monthly Financial Summary Report",
        "5. Category-wise Expense Report",
        "6. Budget Performance Report"
    ]

    selected_report = st.selectbox("Select Report Type", options=report_types)

    r_col1, r_col2 = st.columns(2)
    with r_col1:
        rep_start = st.date_input("Start Date", value=None, key="rep_start")
    with r_col2:
        rep_end = st.date_input("End Date", value=None, key="rep_end")

    report_df = pd.DataFrame()
    filename = "fintrack_report.csv"

    # Generate selected report DataFrame
    if "1. Complete" in selected_report:
        report_df = get_all_transactions_df(user_id, start_date=rep_start, end_date=rep_end)
        filename = f"FinTrack_All_Transactions_{date.today()}.csv"

    elif "2. Income" in selected_report:
        report_df = get_incomes_df(user_id, start_date=rep_start, end_date=rep_end)
        filename = f"FinTrack_Income_Report_{date.today()}.csv"

    elif "3. Expense" in selected_report:
        report_df = get_expenses_df(user_id, start_date=rep_start, end_date=rep_end)
        filename = f"FinTrack_Expense_Report_{date.today()}.csv"

    elif "4. Monthly" in selected_report:
        analytics = get_analytics_summary(user_id)
        report_df = analytics["monthly_df"]
        filename = f"FinTrack_Monthly_Summary_{date.today()}.csv"

    elif "5. Category" in selected_report:
        analytics = get_analytics_summary(user_id)
        report_df = analytics["category_df"]
        filename = f"FinTrack_Category_Expenses_{date.today()}.csv"

    elif "6. Budget" in selected_report:
        report_df = get_budgets_df(user_id)
        filename = f"FinTrack_Budgets_{date.today()}.csv"

    # Display Preview & Download Button
    st.markdown("### 📑 Report Preview")
    if not report_df.empty:
        st.dataframe(report_df, use_container_width=True, hide_index=True)

        # Convert DataFrame to CSV encoded string
        csv_data = report_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label=f"📥 Download {selected_report.split('. ')[1]} (CSV)",
            data=csv_data,
            file_name=filename,
            mime="text/csv",
            type="primary"
        )
    else:
        st.info("No data available to generate this report.")


# ---------------------------------------------------------------------------
# 12. MAIN APPLICATION ENTRY POINT & NAVIGATION ROUTER
# ---------------------------------------------------------------------------

def main():
    """
    Main application router.

    1. Applies custom CSS styling.
    2. Initializes SQLite database tables.
    3. Initializes session state variables.
    4. Routes between Unauthenticated (Login/Register) and Authenticated views.
    5. Manages sidebar navigation across all 7 functional pages.
    """
    # Step 1: Inject styling
    apply_custom_styles()

    # Step 2: Initialize database schema
    init_db()

    # Step 3: Initialize authentication session state keys
    init_session_state()

    # Step 4: Authentication check
    if not st.session_state.get("logged_in", False):
        # Render login & registration screen if unauthenticated
        render_auth_page()
        return

    # User is securely authenticated
    current_user_id = st.session_state["user_id"]
    current_user_name = st.session_state["user_name"]

    # ---------------- 5. SIDEBAR NAVIGATION ----------------
    with st.sidebar:
        st.markdown(
            """
            <div style="margin-bottom: 15px;">
                <h2 style="font-size: 1.5rem; font-weight: 800; color: #1E293B; margin: 0;">
                    💳 FinTrack
                </h2>
                <p style="font-size: 0.85rem; color: #64748B; margin: 0;">
                    Personal Finance Manager
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Radio navigation menu
        nav_choice = st.radio(
            label="Navigation Menu",
            options=[
                "🏠 Dashboard",
                "💰 Income",
                "💸 Expenses",
                "🎯 Budgets",
                "📊 Analytics",
                "📋 Transactions",
                "📄 Reports"
            ],
            label_visibility="collapsed"
        )

        st.markdown("---")

        # Active user profile card
        st.markdown(
            f"""
            <div class="sidebar-brand-box">
                <span style="font-size: 0.75rem; color: #64748B; text-transform: uppercase; font-weight: 600;">Logged in as:</span><br>
                <b style="color: #1E293B; font-size: 0.95rem;">{current_user_name}</b>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Logout button
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            logout_user()

    # ---------------- 6. ROUTE SELECTED PAGE ----------------
    if nav_choice == "🏠 Dashboard":
        render_dashboard(current_user_id, current_user_name)
    elif nav_choice == "💰 Income":
        render_income_page(current_user_id)
    elif nav_choice == "💸 Expenses":
        render_expenses_page(current_user_id)
    elif nav_choice == "🎯 Budgets":
        render_budgets_page(current_user_id)
    elif nav_choice == "📊 Analytics":
        render_analytics_page(current_user_id)
    elif nav_choice == "📋 Transactions":
        render_transactions_page(current_user_id)
    elif nav_choice == "📄 Reports":
        render_reports_page(current_user_id)


# Execute main application when executed directly
if __name__ == "__main__":
    main()
