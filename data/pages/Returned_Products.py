import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO
import plotly.graph_objects as go


# Hlavní nadpis a popis sekce
st.markdown("""
    <h1 style="text-align: center;">Sales Transaction Analysis</h1>
    <h3 style="text-align: center; color: #555;">Returned Products & Refundss</h3>
    <div padding: 15px; border-radius: 10px; text-align: center;">
        <p style="font-size: 16px;">
            This page contains an analysis of Returned Products & Refunds.
            It includes the number of returned products vs. total sales, 
            the most frequently returned products and returned orders by country.
        </p>
    </div>
""", unsafe_allow_html=True)

# Načtení datasetu
df = pd.read_csv("cleaned_sales_data.csv", parse_dates=["Date"])
df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")  # Oprava typu
df["Revenue"] = df["Quantity"] * df["Price"]

st.divider()  # Oddělovač

# RETURNED ORDERS BY COUNTRY GRAPH
# ------------------------------------------------------------------------------
st.markdown("""
    <h2 style="text-align: center;">Returned Orders by Country</h2>
    <div style="text-align: center;">
        <p style="font-size: 16px;">
            This graph shows the number of returned products by country.
            The data is aggregated by the number of unique transactions.
            The graph uses a logarithmic scale for better visualization of the data.
        </p>
    </div>
""", unsafe_allow_html=True)

# st.subheader("Returned Orders by Country")

# Agregace dat: počet vrácených objednávek podle země
returns_by_country = (
    df[df['ReturnFlag'] == True]
    .groupby('Country')
    .size()
    .reset_index(name='Returned Orders')
    .sort_values(by='Returned Orders', ascending=False)
)

# Vytvoření grafu
fig = go.Figure(data=[go.Bar(
    x=returns_by_country['Country'],
    y=returns_by_country['Returned Orders'],
    marker_color='royalblue',
    text=returns_by_country['Returned Orders'],
    texttemplate='%{text:,}',
    textposition="outside"
)])

# Logaritmická osa Y
fig = go.Figure(data=[go.Bar(
    x=returns_by_country['Country'],
    y=returns_by_country['Returned Orders'],  
    marker_color='royalblue',
    text=returns_by_country['Returned Orders'],  
    texttemplate='%{text:,}',
    textposition="outside"
)])

st.plotly_chart(fig, use_container_width=True)

st.divider()  # Oddělovač

# RETURNED PRODUCTS VS TOTAL SALES GRAPH
# ------------------------------------------------------------------------------
st.markdown("""
    <h2 style="text-align: center;">Returned Products vs Total Sales</h2>
    <div style="text-align: center;">
        <p style="font-size: 16px;">
            This graph shows the number of returned products vs. total sales.
            The data is aggregated by the number of unique transactions.
            The graph uses a logarithmic scale for better visualization of the data.
        </p>
    </div>
""", unsafe_allow_html=True)


# Příprava dat
df['ReturnedQuantity'] = df.apply(lambda row: row['Quantity'] if row['ReturnFlag'] else 0, axis=1)
df['SoldQuantity'] = df.apply(lambda row: row['Quantity'] if not row['ReturnFlag'] else 0, axis=1)
df['YearMonth'] = df['Date'].dt.to_period("M").dt.to_timestamp()

# Agregace po měsících
monthly_data = df.groupby('YearMonth').agg({
    'SoldQuantity': 'sum',
    'ReturnedQuantity': 'sum'
}).reset_index()

# Formát měsíce do přehledné podoby
monthly_data['YearMonth'] = monthly_data['YearMonth'].dt.strftime("%b %Y")

# Bezpečný výpočet podílu vratek
monthly_data['ReturnRate (%)'] = (
    monthly_data['ReturnedQuantity'] /
    monthly_data['SoldQuantity'].replace(0, np.nan)
) * 100

# Zaokrouhlení + náhrada NaN nulou
monthly_data['ReturnRate (%)'] = monthly_data['ReturnRate (%)'].round(2).fillna(0)

# Graf: bar (prodeje) + line (vratky)
fig = go.Figure()
fig.add_trace(go.Bar(
    x=monthly_data['YearMonth'],
    y=monthly_data['SoldQuantity'],
    name='Total Sales',
    marker_color='royalblue'
))
fig.add_trace(go.Scatter(
    x=monthly_data['YearMonth'],
    y=monthly_data['ReturnedQuantity'],
    name='Returned Products',
    mode='lines+markers',
    line=dict(color='crimson', width=3),
    marker=dict(size=6)
))
fig.update_layout(
    title='Returned Products vs Total Sales (Monthly)',
    xaxis_title='Month',
    yaxis_title='Number of Products',
    legend_title='Legend',
    barmode='group',
    hovermode='x unified',
    template='plotly_white'
)

# Zobrazení grafu
# st.subheader("Returned Products vs Total Sales (Monthly Overview)")
st.plotly_chart(fig, use_container_width=True)

# Zobrazení tabulky
st.markdown("### Return Rate by Month (%)")
st.dataframe(
    monthly_data[['YearMonth', 'ReturnRate (%)']],
    use_container_width=True
)

st.divider()  # Oddělovač

# MOST FREQUENTLY RETURNED PRODUCTS GRAPH
# ------------------------------------------------------------------------------

st.markdown("""
    <h2 style="text-align: center;">Most Frequently Returned Products</h2>
    <div style="text-align: center;">
        <p style="font-size: 16px;">
            This graph shows the most frequently returned products.
            The data is aggregated by the number of returned units (absolute quantity).
        </p>
    </div>
""", unsafe_allow_html=True)

# Příprava dat
most_returned_products = (
    df[df['ReturnFlag'] == True]
    .copy()
)

# Oprava: absolutní hodnoty Quantity (kvůli záporným vratkám)
most_returned_products['AbsQuantity'] = most_returned_products['Quantity'].abs()

# Agregace a seřazení
most_returned_products = (
    most_returned_products
    .groupby('ProductName')['AbsQuantity']
    .sum()
    .reset_index()
    .sort_values(by='AbsQuantity', ascending=False)
)

# Vytvoření grafu s logaritmickou osou a změnou barevné palety
fig = px.bar(
    most_returned_products.head(10),
    x='ProductName',
    y='AbsQuantity',
    # title='Most Frequently Returned Products',
    labels={'ProductName': 'Product Name', 'AbsQuantity': 'Returned Quantity'},
    color='AbsQuantity',
    
)

fig.update_layout(
    xaxis_title='Product Name',
    yaxis_title='Returned Quantity',
    yaxis_type='log',  # logaritmická osa Y
    xaxis_tickangle=-45,  # otočení popisků
    legend_title='Legend',
    hovermode='x unified',
    template='plotly_white'
)

# Zobrazení grafu
# st.subheader("Most Frequently Returned Products")
st.plotly_chart(fig, use_container_width=True)