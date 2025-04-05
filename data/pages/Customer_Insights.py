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
        This page provides insights into customer behavior and segmentation. 
        It includes an analysis of repeat purchase patterns, 
        customer value by segment (New, Returning, Loyal), 
        revenue contributions per group, and a geographic breakdown 
        of sales and customer activity across countries.
    </p>
    </div>
""", unsafe_allow_html=True)

# Načtení datasetu
df = pd.read_csv("cleaned_sales_data.csv", parse_dates=["Date"])
df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")  # Oprava typu
df["Revenue"] = df["Quantity"] * df["Price"]

st.divider()  # Oddělovač

# CUSTOMER INSIGHT - TOP CUSTOMERS TABLE
# ------------------------------------------------------------------------------

# Výběr počtu zákazníků
top_n = st.radio("Select number of top customers:", options=[5, 10, 15, 20], horizontal=True)

# Výpočet metrik
customer_stats = df.groupby("CustomerNo").agg(
    Total_Revenue=("Revenue", "sum"),
    Number_of_Purchases=("TransactionNo", "nunique")
).reset_index()

# Doplnění země
customer_stats = customer_stats.merge(df[["CustomerNo", "Country"]].drop_duplicates(), on="CustomerNo", how="left")

# Seřazení podle tržeb
top_customers_table = customer_stats.sort_values(by="Total_Revenue", ascending=False).head(top_n)

# Formátování čísel
top_customers_table["Total_Revenue"] = top_customers_table["Total_Revenue"].round(2)
top_customers_table["Number_of_Purchases"] = top_customers_table["Number_of_Purchases"].astype(int)

# Přehledná tabulka
st.markdown("### Top Customers (by Revenue)")
st.dataframe(
    top_customers_table[["CustomerNo", "Country", "Total_Revenue", "Number_of_Purchases"]],
    use_container_width=True
)

st.divider()  # Oddělovač

# Segmentace zákazníků podle počtu nákupů (New / Returning / Loyal)
# ------------------------------------------------------------------------------

# Počet nákupů na zákazníka
purchase_counts = df.groupby('CustomerNo')['TransactionNo'].nunique().reset_index()
purchase_counts.columns = ['CustomerNo', 'NumPurchases']

# Segmentace
def segment_customer(purchases):
    if purchases == 1:
        return 'New'
    elif 2 <= purchases <= 5:
        return 'Returning'
    else:
        return 'Loyal'

purchase_counts['Segment'] = purchase_counts['NumPurchases'].apply(segment_customer)

# Spojení segmentace zpět s df
df_segmented = df.merge(purchase_counts[['CustomerNo', 'Segment']], on='CustomerNo', how='left')

# Výběr segmentu
segment = st.radio("Select Customer Segment:", options=["New", "Returning", "Loyal"])

with st.expander("ℹ️ What do customer segments mean?"):
    st.markdown("""
    - **New** – Customers who have made **exactly 1 purchase**.
    - **Returning** – Customers who have made **2 to 5 purchases**.
    - **Loyal** – Customers who have made **more than 5 purchases**.
    """)

# Filtrování
filtered = df_segmented[df_segmented['Segment'] == segment]

# Funkce pro formátování čísel jako "28 463 185 £"
def format_currency(value):
    return f"{int(round(value)):,}".replace(",", " ") + " £"

# Výpočty
num_customers = filtered['CustomerNo'].nunique()
num_orders = filtered['TransactionNo'].nunique()
total_revenue = filtered['Revenue'].sum()
avg_revenue_per_order = total_revenue / num_orders if num_orders else 0

# Formátování hodnot
summary_df = pd.DataFrame({
    "Metric": ["Number of Customers", "Number of Orders", "Total Revenue", "Avg Revenue per Order"],
    "Value": [
        f"{num_customers:,}".replace(",", " "),
        f"{num_orders:,}".replace(",", " "),
        format_currency(total_revenue),
        format_currency(avg_revenue_per_order)
    ]
})
st.dataframe(summary_df, use_container_width=True)

# BAR CHART - Segmentace zákazníků
# ------------------------------------------------------------------------------

# Výpočet metrik pro každý segment
segment_summary = (
    df_segmented.groupby("Segment").agg(
        Customers=("CustomerNo", "nunique"),
        Orders=("TransactionNo", "nunique"),
        Total_Revenue=("Revenue", "sum")
    )
    .reset_index()
)

# Průměrná útrata na objednávku
segment_summary["Avg_Revenue_per_Order"] = (
    segment_summary["Total_Revenue"] / segment_summary["Orders"]
).round(2)

# Převod hodnot do tisícového formátu
segment_summary["Total_Revenue"] = segment_summary["Total_Revenue"].round()
segment_summary["Segment"] = pd.Categorical(
    segment_summary["Segment"],
    categories=["New", "Returning", "Loyal"],
    ordered=True
)

# Výběr metriky pro porovnání
metric_option = st.selectbox(
    "Select metric to compare across segments:",
    options=["Customers", "Orders", "Total_Revenue", "Avg_Revenue_per_Order"],
    format_func=lambda x: {
        "Customers": "Number of Customers",
        "Orders": "Number of Orders",
        "Total_Revenue": "Total Revenue (£)",
        "Avg_Revenue_per_Order": "Avg Revenue per Order (£)"
    }[x]
)

# Bar chart
fig = px.bar(
    segment_summary,
    x="Segment",
    y=metric_option,
    text=segment_summary[metric_option].apply(lambda x: f"{x:,.0f}".replace(",", " ") + (" £" if 'Revenue' in metric_option else "")),
    color="Segment",
    color_discrete_map={"New": "#9ecae1", "Returning": "#4292c6", "Loyal": "#08519c"},
    title=f"{metric_option.replace('_', ' ')} by Customer Segment",
    template="plotly_white"
)

fig.update_traces(textposition="outside")

fig.update_layout(
    yaxis_title=metric_option.replace("_", " "),
    xaxis_title="Customer Segment",
    showlegend=False,
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()  # Oddělovač

# CUSTOMER INSIGHT - REVENUE BY COUNTRY
# ------------------------------------------------------------------------------

# Agregace tržeb podle země
revenue_by_country = df.groupby("Country")["Revenue"].sum().reset_index()
revenue_by_country["Revenue"] = revenue_by_country["Revenue"].round()

# Mapa světa podle ISO 3 (pro Plotly)
import pycountry

# Funkce pro převod názvu země na kód ISO Alpha-3
def get_country_iso3(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_3
    except:
        return None

revenue_by_country["iso_alpha"] = revenue_by_country["Country"].apply(get_country_iso3)
revenue_by_country = revenue_by_country.dropna(subset=["iso_alpha"])

# MAP BY COUNTRY

# Vytvoření sloupce s logaritmem revenue
revenue_by_country["LogRevenue"] = np.log10(revenue_by_country["Revenue"] + 1)

# Choropleth mapa
fig = px.choropleth(
    revenue_by_country,
    locations="iso_alpha",
    color="LogRevenue",
    hover_name="Country",
    hover_data={"Revenue": ":,.0f", "LogRevenue": False},
    color_continuous_scale="Blues",
    title="Total Revenue by Country (log-scaled color)"
)

# Odstranit barevný popisek "log"
fig.update_coloraxes(colorbar_title="Relative Revenue")

st.plotly_chart(fig, use_container_width=True)