import streamlit as st
from pdf_extraction import run

st.title("PDF Extraction")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file:
    data = run(uploaded_file.name)
    st.table(data['transactions'])
