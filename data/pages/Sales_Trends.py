import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO


# Hlavní nadpis a popis sekce
st.markdown("""
    <h1 style="text-align: center;">Sales Transaction Analysis</h1>
    <h3 style="text-align: center; color: #555;">Sales Trends Over Time</h3>
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

# MONTHLY REVENUE GRAPH
# ------------------------------------------------------------------------------

# Vizuální oddělení výběru měsíce
st.markdown("**Select number of months to display:**")
selected_months = st.selectbox(
    "",
    options=["all", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    format_func=lambda x: "All" if x == "all" else f"{x} month(s)",
    index=0
)

# Vizuální oddělení výběru vratek
st.markdown("**Include returns in the graph:**")
returns_filter = st.selectbox(
    "",
    options=["include", "exclude"],
    format_func=lambda x: "Include returns" if x == "include" else "Exclude returns",
    index=0
)

# Funkce pro generování grafu měsíčních tržeb
def generate_monthly_revenue_graph(selected_months="all", returns_filter="include"):
    # KOPIE DATASETU
    df_filtered = df.copy()

    # FILTRACE VRATEK
    if returns_filter == "exclude":
        df_filtered = df_filtered[df_filtered["Quantity"] > 0]  # Odstraní vratky (Quantity < 0)

    # SESKUPENÍ PODLE MĚSÍCŮ
    monthly_revenue = df_filtered.groupby(df_filtered['Date'].dt.to_period('M'))['Revenue'].sum()

    # PŘEVOD DATA NA FORMÁT "Mar 2019"
    formatted_months = monthly_revenue.index.to_timestamp().strftime("%b %Y")

    # FILTRACE POČTU MĚSÍCŮ
    if selected_months != "all":
        formatted_months = formatted_months[-int(selected_months):]
        monthly_revenue = monthly_revenue[-int(selected_months):]

    # VYTVOŘENÍ GRAFU
    fig = px.bar(
        x=formatted_months,
        y=monthly_revenue.values,
        labels={'x': 'Month', 'y': 'Total Revenue'},
        title='Total Revenue by Month',
        color=monthly_revenue.values,
        color_continuous_scale='Blues'
    )

    # NASTAVENÍ OSY X
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=list(formatted_months),
            tickangle=0
        )
    )

    # PŘIDÁNÍ POPISKŮ A TOOLTIPŮ
    fig.update_traces(
        text=monthly_revenue.values.astype(int),
        texttemplate='%{text:,}',
        textposition="outside",
        hoverinfo="x+y",
        hoverlabel=dict(bgcolor="white", font_size=12, font_color="black")
    )

    return fig

# VYTVOŘENÍ GRAFU
monthly_revenue_graph = generate_monthly_revenue_graph(selected_months, returns_filter)

# ZOBRAZENÍ GRAFU
st.plotly_chart(
    monthly_revenue_graph,
    use_container_width=True,
    config={"displayModeBar": False}
)

st.divider()  # Oddělovač

