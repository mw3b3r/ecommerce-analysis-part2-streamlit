import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO
import plotly.graph_objects as go

# Hlavní nadpis a popis sekce
st.markdown("""
    <h1 style="text-align: center;">Sales Transaction Analysis</h1>
    <h3 style="text-align: center; color: #555;">Geographic analysis</h3>
    <div padding: 15px; border-radius: 10px; text-align: center;">
    <p style="font-size: 16px;">            
        This page provides a detailed overview of customer preferences by country.  
        It includes a breakdown of total and average revenue by country,  
        return rates across markets, and country-specific product preferences.  
        Users can explore top-performing countries and products,  
        analyze customer behavior, and download key datasets for further analysis. 
    </p>
    </div>
""", unsafe_allow_html=True)

# Načtení datasetu
df = pd.read_csv("cleaned_sales_data.csv", parse_dates=["Date"])
df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")  # Oprava typu
df["Revenue"] = df["Quantity"] * df["Price"]

st.divider()  # Oddělovač

# Top Countries by Sales (Revenue & Quantity)
# --------------------------------------------------

st.markdown("""
    <h2 style="text-align: center;">Top Countries by Sales</h2>
    <div style="text-align: center;">
        <p style="font-size: 16px;">
            This section shows the top-performing countries based on total revenue or quantity sold. 
            You can switch between metrics and control how many countries are displayed.
        </p>
    </div>
""", unsafe_allow_html=True)

# Výběr metriky
metric = st.selectbox(
    "Select metric:",
    options=["Revenue", "Quantity"],
    index=0
)

# Výběr počtu zemí k zobrazení
top_n = st.radio(
    "Select number of countries to display:",
    options=[5, 10, 15, "All"],
    horizontal=True,
    index=1
)

# Agregace podle země
country_summary = df.groupby("Country").agg({
    "Revenue": "sum",
    "Quantity": "sum"
}).reset_index()

# Seřazení podle zvolené metriky
country_summary = country_summary.sort_values(by=metric, ascending=False)

# Ořez dle výběru uživatele
if top_n != "All":
    country_summary = country_summary.head(int(top_n))

# Tabulka
st.markdown("### Country Summary Table")

# Formátování pro Revenue a Quantity
formatted_table = country_summary.copy()
if metric == "Revenue":
    formatted_table[metric] = formatted_table[metric].apply(lambda x: f"{x:,.0f}".replace(",", " ") + " £")
else:
    formatted_table[metric] = formatted_table[metric].apply(lambda x: f"{x:,.0f}".replace(",", " "))

# Zobrazení formátované tabulky
st.dataframe(
    formatted_table[["Country", metric]],
    use_container_width=True
)

# Poznámka pod tabulkou
st.markdown("""
<small style='color: gray;'>
⚠️ Some countries show negative revenue due to returns exceeding purchases within the selected timeframe. 
This may happen if the purchases fall outside the available dataset.
</small>
""", unsafe_allow_html=True)

st.divider()  # Oddělovač

# AOV (Average Order Value) by Country
# --------------------------------------------------

# Výpočet AOV
aov_by_country = (
    df[df["ReturnFlag"] != True]
    .groupby("Country")
    .agg(
        Revenue=("Revenue", "sum"),
        Orders=("TransactionNo", "nunique")
    )
    .reset_index()
)
aov_by_country["AOV"] = aov_by_country["Revenue"] / aov_by_country["Orders"]
aov_by_country = aov_by_country.sort_values(by="AOV", ascending=False).head(15)  # ⬅️ Top 15

# Graf
fig = px.bar(
    aov_by_country,
    x="Country",
    y="AOV",
    title="Top 15 Countries by Average Order Value (AOV)",
    labels={"AOV": "Avg Order Value (£)"},
    text=aov_by_country["AOV"].apply(lambda x: f"{x:,.2f} £".replace(",", " ")),
    color="AOV",
    color_continuous_scale="Blues"
)

fig.update_traces(textposition="outside")

fig.update_layout(
    yaxis_title="Average Order Value (£)",
    xaxis_title="Country",
    showlegend=False,
    hovermode="x unified",
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)

# Excel export celé tabulky (nejen top 15)
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='AOV by Country')
    return output.getvalue()

# Připravíme exportní data (včetně AOV zaokrouhleného na 2 desetinná místa)
export_df = aov_by_country.sort_values(by="AOV", ascending=False).copy()
export_df["AOV"] = export_df["AOV"].round(2)

st.markdown("""
**ℹ️ Full AOV Data Download**

The chart above shows the top 15 countries by average order value (AOV).  
If you'd like to see the complete dataset with all countries, you can download it below:
""")

# Tlačítko ke stažení
st.download_button(
    label="📥 Download Full AOV Table (Excel)",
    data=to_excel(export_df),
    file_name="aov_by_country.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.divider()  # Oddělovač

# Return Rate by Country
# --------------------------------------------------

st.markdown("### Return Rate by Country")

# Agregace
return_stats = (
    df.groupby("Country")
    .agg(
        Sold_Qty=("Quantity", lambda x: x[x > 0].sum()),
        Returned_Qty=("Quantity", lambda x: -x[x < 0].sum())  # vrácené zboží bývá záporné
    )
    .reset_index()
)

# Výpočet return rate
return_stats["Return Rate (%)"] = (
    return_stats["Returned_Qty"] / return_stats["Sold_Qty"].replace(0, np.nan) * 100
).round(2)

# Odstranit země bez nákupů
return_stats = return_stats.dropna(subset=["Return Rate (%)"])

# Zaokrouhlit a formátovat číselné hodnoty
return_stats["Sold_Qty"] = return_stats["Sold_Qty"].astype(int)
return_stats["Returned_Qty"] = return_stats["Returned_Qty"].astype(int)

# Seřazení sestupně podle return rate
return_stats = return_stats.sort_values(by="Return Rate (%)", ascending=False)

# Zobrazení tabulky
st.dataframe(return_stats, use_container_width=True)

# Poznámka
st.markdown("""
<small style='color: gray;'>
⚠️ Return rate is calculated as a percentage of returned items relative to all items sold per country.  
Countries with extremely high return rates may indicate data imbalance or limited sales volume.
</small>
""", unsafe_allow_html=True)

st.divider()  # Oddělovač

# Product Preferences by Country
# --------------------------------------------------

st.markdown("### Product Preferences by Country")

# Filtrování dostupných zemí
countries = sorted(df["Country"].dropna().unique())
selected_country = st.selectbox("Select a country to view top products:", countries)

# Filtrování pouze skutečných prodejů (bez vratek)
filtered_df = df[(df["Country"] == selected_country) & (df["ReturnFlag"] != True)]

# Agregace: nejprodávanější produkty podle počtu kusů
top_products = (
    filtered_df.groupby("ProductName")["Quantity"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

# Vykreslení grafu
fig = px.bar(
    top_products,
    x="Quantity",
    y="ProductName",
    orientation="h",
    title=f"Top 10 Products in {selected_country}",
    labels={"Quantity": "Quantity Sold", "ProductName": "Product"},
    template="plotly_white",
    color="Quantity",
    color_continuous_scale="Blues"
)
fig.update_layout(yaxis=dict(autorange="reversed"))

st.plotly_chart(fig, use_container_width=True)

# Poznámka pod grafem
st.markdown("""
<small>ℹ️ Only completed sales are included. Returned items have been excluded from this chart to provide a more accurate view of actual product demand.</small>
""", unsafe_allow_html=True)

st.divider()  # Oddělovač