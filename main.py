import streamlit as st
import pandas as pd
import plotly.express as px

from pdf_extraction import run
from database.tables import create_tables
from database.queries import *
from transaction_analyzer import *
from kafka_producer import *


st.title("FinTrack")


# --------------------------------------------------
# Sidebar
# --------------------------------------------------


with st.sidebar:

    st.header("Database")

    if st.button("Clear Database", type="secondary"):

        clear_database()

        st.success("Database cleared.")

        st.rerun()


# --------------------------------------------------
# Database
# --------------------------------------------------

create_tables()


# --------------------------------------------------
# Tabs
# --------------------------------------------------

upload_tab, analytics_tab, accounts_tab, statements_tab, transactions_tab = st.tabs([
    "📤 Upload Statements",
    "📊 Analytics",
    "👤 Accounts",
    "📄 Statements",
    "💳 Transactions"
])


# ==================================================
# UPLOAD STATEMENTS
# ==================================================

with upload_tab:

    st.header("Upload Credit Card Statements")

    uploaded_files = st.file_uploader(
        "Select PDF statements",
        accept_multiple_files=True,
        type="pdf"
    )

    if uploaded_files:

        st.write(f"**{len(uploaded_files)} file(s) selected**")

        if st.button("Process Statements", type="primary"):

            for uploaded_file in uploaded_files:

                try:
                    data = run(uploaded_file)
                    produce_to_kafka(data)

                    st.success(
                        f"{uploaded_file.name} processed successfully."
                    )

                except Exception as e:

                    st.error(
                        f"Failed to process {uploaded_file.name}: {e}"
                    )

# ==================================================
# ANALYTICS
# ==================================================


def show_category_spending():
    category_spending = get_spending_by_category()

    # Convert query result into DataFrame
    df = pd.DataFrame(
        category_spending,
        columns=["Category", "Spending"]
    )

    # Convert Decimal values returned by PostgreSQL
    df["Spending"] = df["Spending"].astype(float)

    # Pie chart
    fig = px.pie(
        df,
        names="Category",
        values="Spending",
        title="Total Spending by Category",
        hole=0.3
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


with analytics_tab:

    st.header("Transaction Analytics")
    total_purchases = get_total_purchases()

    # -----------------------------
    # Summary Cards
    # -----------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Purchases",
            f"₹{total_purchases}"
        )

    with col2:
        st.metric(
            "Total Rewards",
            f"₹{get_total_rewards()}"
        )

    with col3:
        st.metric(
            "Total Fees",
            f"₹{get_total_fees()}"
        )

    with col4:
        emi = get_emi_summary()
        total_emi = sum(emi) if emi else 0

        st.metric(
            "Total EMI",
            f"₹{total_emi}"
        )

    st.divider()

    # -----------------------------
    # EMI & Fee Breakdown
    # -----------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("EMI Breakdown")

        emi_cat = [
            "Principal",
            "Interest",
            "Conversion"
        ]

        emi = get_emi_summary()

        emi_breakdown = []

        for category, value in zip(emi_cat, emi):
            emi_breakdown.append({
                "Component": category,
                "Amount": f"₹{value:,.2f}"
            })

        if emi_breakdown:
            st.dataframe(
                pd.DataFrame(emi_breakdown),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No EMI data available.")

    with col2:

        st.subheader("Fee Breakdown")

        fee_cat = [
            "Processing Fee",
            "Cashback Redemption Fee"
        ]

        fees = get_fee_breakdown()

        fee_breakdown = []

        for category, value in zip(fee_cat, fees):
            fee_breakdown.append({
                "Fee Type": category,
                "Amount": f"₹{value:,.2f}"
            })

        if fee_breakdown:
            st.dataframe(
                pd.DataFrame(fee_breakdown),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No fee data available.")

    if total_purchases > 0:
        st.divider()

        st.title("Spending Dashboard")

        st.subheader("Spending by category")
        show_category_spending()

        year = st.number_input(
            "Select Year",
            min_value=2020,
            max_value=2030,
            value=2026,
            step=1
        )
        st.subheader(f"Monthly Spending - {year}")

        df = get_yearly_monthly_spending(year)

        st.bar_chart(
            df,
            x="Month",
            y="Spending"
        )
# ==================================================
# ACCOUNTS
# ==================================================

with accounts_tab:

    st.header("Accounts")

    account_rows, account_cols = get_accounts()

    if account_rows:
        st.dataframe(
            pd.DataFrame(account_rows, columns=account_cols),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No accounts found.")


# ==================================================
# STATEMENTS
# ==================================================

with statements_tab:

    st.header("Statements")

    account_rows, account_cols = get_accounts()

    if account_rows:

        account_ids = [
            row[0]
            for row in account_rows
        ]

        account_options = ["All"] + account_ids

        selected_account = st.selectbox(
            "Account",
            account_options,
            key="statements_account"
        )

        if selected_account == "All":
            selected_account = None

        statement_rows, statement_cols = get_statements(
            selected_account
        )

        if statement_rows:

            st.dataframe(
                pd.DataFrame(
                    statement_rows,
                    columns=statement_cols
                ),
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No statements found for this account.")

    else:
        st.info("No accounts found.")


# ==================================================
# TRANSACTIONS
# ==================================================

with transactions_tab:

    st.header("Transactions")

    account_rows, account_cols = get_accounts()

    if account_rows:

        # ------------------------------------------
        # Filters
        # ------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            account_ids = [
                row[0]
                for row in account_rows
            ]

            account_options = ["All"] + account_ids

            selected_account = st.selectbox(
                "Account",
                account_options,
                key="transactions_account"
            )

            if selected_account == "All":
                selected_account = None

        with col2:

            statement_rows, statement_cols = get_statements(
                selected_account
            )
            statement_ids = [
                row[0]
                for row in statement_rows
            ]

            statement_options = ["All"] + statement_ids

            selected_statement = st.selectbox(
                "Statement",
                statement_options,
                key="transactions_statement"
            )

            if selected_statement == "All":
                selected_statement = None

        with col3:

            transaction_type = st.selectbox(
                "Transaction Type",
                ["All", "Debit", "Credit"],
                key="transaction_type"
            )

        with col4:

            categories = ["All"] + get_categories()

            selected_category = st.selectbox(
                "Category",
                categories,
                key="transaction_category"
            )

        # ------------------------------------------
        # Date Filters
        # ------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            start_date = st.date_input(
                "Start Date"
            )

        with col2:

            end_date = st.date_input(
                "End Date"
            )

        # ------------------------------------------
        # Search Button
        # ------------------------------------------

        search = st.button(
            "Search Transactions",
            type="primary"
        )

        # ------------------------------------------
        # Results
        # ------------------------------------------

        if search:

            if transaction_type == "All":
                transaction_type = None

            if selected_category == "All":
                selected_category = None

            transaction_rows, transaction_cols = get_transactions(
                account_id=selected_account,
                statement_id=selected_statement,
                transaction_type=transaction_type,
                selected_category=selected_category,
                date_range=[start_date, end_date]
            )

            if transaction_rows:

                st.subheader("Results")

                st.dataframe(
                    pd.DataFrame(
                        transaction_rows,
                        columns=transaction_cols
                    ),
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info(
                    "No transactions found for the selected filters."
                )

    else:

        st.info("No accounts found.")
