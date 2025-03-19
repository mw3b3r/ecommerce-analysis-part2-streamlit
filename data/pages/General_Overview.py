import streamlit as st
import pandas as pd
import numpy as np
import datetime
import time

# Hlavní nadpis
st.markdown("""
    <h1 style="text-align: center;">Sales Transaction Analysis</h1>
    <h3 style="text-align: center; color: #555;">General Overview</h3>
    <p style="text-align: center; font-size: 16px; color: #666;">
        This analysis is based on anonymized transaction data from an e-commerce store.
        The dataset contains information about orders, customers, and product sales.
        The goal is to identify key sales trends, best-selling products, and customer behavior.
    </p>
""", unsafe_allow_html=True)

# Import datasetu
df = pd.read_csv("cleaned_sales_data.csv", parse_dates=["Date"])
df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")  # Oprava typu

# CSS pro stylování karet
card_style = """
    <style>
        .metric-card {
            background-color: #E3F2FD;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin: 10px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        }
        .metric-title {
            font-size: 18px;
            font-weight: bold;
            color: #333;
        }
        .metric-value {
            font-size: 32px;
            font-weight: bold;
            color: #007BFF;
        }
    </style>
"""
st.markdown(card_style, unsafe_allow_html=True)

# **První řada: Tři metriky vedle sebe**
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">📊 Total Unique Transactions</div>
            <div class="metric-value">{'{:,.0f}'.format(df["TransactionNo"].nunique()).replace(',', ' ')}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">📦 Total Unique Products</div>
            <div class="metric-value">{'{:,.0f}'.format(df["ProductNo"].nunique()).replace(',', ' ')}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">👥 Total Unique Customers</div>
            <div class="metric-value">{'{:,.0f}'.format(df["CustomerNo"].nunique()).replace(',', ' ')}</div>
        </div>
    """, unsafe_allow_html=True)

# **Přidání mezery mezi řadami**
st.markdown("<br>", unsafe_allow_html=True)  # Přidání mezery

# **Druhá řada: Dvě metriky vedle sebe**
col4, col5 = st.columns(2)

with col4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">📜 Total Number of Transactions</div>
            <div class="metric-value">{'{:,.0f}'.format(df["TransactionNo"].count()).replace(',', ' ')}</div>
        </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">💲 Total Sales</div>
            <div class="metric-value">${'{:,.2f}'.format((df["Price"] * df["Quantity"]).sum()).replace(',', ' ')}</div>
        </div>
    """, unsafe_allow_html=True)

# **Přidání mezery mezi řadami**
st.markdown("<br>", unsafe_allow_html=True)  # Přidání mezery

# **Třetí řada: Časový rozsah**
st.markdown(f"""
    <div class="metric-card" style="background-color: #E3F2FD; max-width: 400px; margin: auto;">
        <div class="metric-title">🕒 Time Range of Data</div>
        <div class="metric-value">{df['Date'].min().strftime('%d.%m.%Y')} - {df['Date'].max().strftime('%d.%m.%Y')}</div>
    </div>
""", unsafe_allow_html=True)
