import streamlit as st
import pandas as pd

from pdf_extraction import run
from database.tables import create_tables
from database.queries import *


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

upload_tab, accounts_tab, statements_tab, transactions_tab = st.tabs([
    "📤 Upload Statements",
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
                    insert(data)

                    st.success(
                        f"{uploaded_file.name} processed successfully."
                    )

                except Exception as e:

                    st.error(
                        f"Failed to process {uploaded_file.name}: {e}"
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
