import streamlit as st

st.title("General Overview")
st.write("Obsah pro stránku General Overview")

st.metric(label="Total Unique Transactions", value=df["TransactionNo"].nunique())