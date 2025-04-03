import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO
import plotly.graph_objects as go

# Hlavní nadpis a popis sekce
st.markdown("""
    <h1 style="text-align: center;">Sales Transaction Analysis</h1>
    <h3 style="text-align: center; color: #555;">Customer Insights</h3>
    <div padding: 15px; border-radius: 10px; text-align: center;">
        <p style="font-size: 16px;">
            This page contains an analysis of sales trends over time. 
            It includes wholesale sales by month with/ without returns, 
            daily trends and monthly sales reports.
        </p>
    </div>
""", unsafe_allow_html=True)

# Načtení datasetu
df = pd.read_csv("cleaned_sales_data.csv", parse_dates=["Date"])
df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")  # Oprava typu
df["Revenue"] = df["Quantity"] * df["Price"]

st.divider()  # Oddělovač