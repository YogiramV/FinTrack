import streamlit as st
import pandas as pd
from pdf_extraction import run
from database.tables import create_tables
from database.queries import *

st.title("FinTrack")

ans = st.button("Clear database?")
if ans:
    clear_database()

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file:
    data = run(uploaded_file.name)

    # Create tables
    create_tables()
    insert(data)

    st.header('Accounts table')
    account_rows, account_cols = get_accounts()
    st.table(pd.DataFrame(account_rows, columns=account_cols))

    st.header('Statements table')
    with st.form("Conditions for statements table"):
        acc_id = st.text_input('Enter account id')
        submitted = st.form_submit_button("Submit")
        if submitted:
            statement_rows, statement_cols = get_statements(acc_id)
            st.table(pd.DataFrame(statement_rows, columns=statement_cols))

    st.header('Transactions table')
    with st.form("Conditions for transactions table"):
        account_id = st.text_input('Enter account_id')
        start_date = st.date_input("Start Date:")
        end_date = st.date_input("End Date:")
        transaction_type = st.selectbox(
            'Enter transaction_type', ['All', 'Debit', 'Credit'])
        submitted = st.form_submit_button("Submit")
        if submitted:
            if transaction_type == 'All':
                transaction_type = None
            transaction_rows, transaction_cols = get_transactions(
                account_id=acc_id, transaction_type=transaction_type, date_range=[start_date, end_date])
            st.table(pd.DataFrame(transaction_rows, columns=transaction_cols))
