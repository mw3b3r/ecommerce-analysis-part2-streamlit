import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO
import plotly.graph_objects as go


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

# DAILY REVENUE GRAF (0,9 percentil)
# ------------------------------------------------------------------------------

# Přidáme nový sloupec pro rok a měsíc
df["YearMonth"] = df["Date"].dt.to_period("M")

# Vytvoření seznamu unikátních měsíců (např. '2024-03', '2024-04')
month_options = sorted(df["YearMonth"].astype(str).unique())

# Selectbox pro výběr měsíce
selected_month = st.selectbox("Select month to display:", options=month_options)

# Filtrování dat podle výběru
df_filtered = df[df["YearMonth"].astype(str) == selected_month]

# Funkce pro generování grafu denních tržeb
def generate_daily_revenue_graph(data = None): # Přidání argumentu 'data'
    
    # Pokud není zadán DataFrame, použij globální 'df'
    if data is None:
        data = df_filtered

    daily_revenue = data[data['ReturnFlag'] != True].groupby('Date')['Revenue'].sum()

    # Výpočet 90. percentilu
    threshold = daily_revenue.quantile(0.90)

    # Odstranění extrémních hodnot nad tímto thresholdem
    daily_revenue = daily_revenue[daily_revenue <= threshold]

    # Najdeme nejlepší a nejhorší dny podle tržeb
    top_days = daily_revenue.nlargest(1).index
    bottom_days = daily_revenue.nsmallest(1).index

    # Počet objednávek na den bez započtení vratek
    daily_orders = df[df['ReturnFlag'] != True].groupby('Date')['TransactionNo'].nunique()

    # Určení barev
    colors = ['#4682B4' if date not in top_days and date not in bottom_days
            else 'darkorange' if date in top_days
            else '#4682B4' #added else to fix the syntax
            for date in daily_revenue.index]

    # Vytvoření grafu - Aktualizace barvy sloupců
    fig = go.Figure(data=[go.Bar(
        x=daily_revenue.index,
        y=daily_revenue.values,
        marker_color=colors
    )])

    # Přidání čísel nad sloupce
    fig.update_traces(
    text=daily_revenue.values.astype(int),  # Převod na celé číslo
    texttemplate='%{text:,}',  # Formátování s oddělovačem tisíců
    textposition="outside",  # Popisky nad sloupci
    )

    # Přidání hover informací
    hover_text = [
    f"Orders: {daily_orders.get(date, 0)}<br>"
    f"Total Revenue: {revenue:,.0f}<br>"
    f"Avg Order Value: {revenue / daily_orders.get(date, 1):,.0f}"  # Prevence dělení nulou
    for date, revenue in daily_revenue.items()
    ]

    fig.update_traces(
        hoverinfo="x+y+text",
        hovertext=hover_text
    )

    fig.update_layout(
        title="Daily Revenue (filtered by 90th percentile)",
        xaxis_title="Date",
        yaxis_title="Revenue",
        xaxis=dict(tickangle=-45),
        yaxis=dict(tickformat=",.0f")
    )

    # Převod indexu na číslo dne (pro měsíční výběr)
    day_labels = daily_revenue.index.strftime('%d')

    # Podmínka pro odlišení měsíčního a celoročního zobrazení
    if len(daily_revenue.index.unique()) <= 31:  # Pokud je méně než 31 dní, zobrazujeme jen čísla
        fig.update_layout(
            xaxis=dict(
                tickmode="array",
                tickvals=list(daily_revenue.index),  # Dny jako hodnoty
                ticktext=list(day_labels),  # Pouze čísla dnů jako popisky
                tickangle=0
            )
        )
    else:
        fig.update_layout(
            xaxis=dict(
                tickangle=-45  # Pro celý rok necháme klasický formát
            )
)

    return fig
# VYTVOŘENÍ GRAFU
daily_revenue_graph = generate_daily_revenue_graph(df_filtered)

# ZOBRAZENÍ GRAFU
st.plotly_chart(
    daily_revenue_graph,
    use_container_width=True,
    config={"displayModeBar": False}
)

st.divider()  # Oddělovač

# MONTHLY REVENUE TABLE - Přehled měsíčních tržeb
# ------------------------------------------------------------------------------

def generate_monthly_revenue_table():
    monthly_data = df[df['ReturnFlag'] != True].groupby(df['Date'].dt.to_period('M')).agg(
        Total_Revenue=('Revenue', 'sum'),
        Orders_Count=('TransactionNo', 'nunique')
    )

    # Přidání sloupce pro průměrnou hodnotu objednávky
    monthly_data['Average_Order_Value'] = (monthly_data['Total_Revenue'] / monthly_data['Orders_Count']).round(2)

    # Přidání sloupce pro celkový počet objednávek
    monthly_returns = df[df['ReturnFlag'] == True].groupby(df['Date'].dt.to_period('M'))['ReturnFlag'].count()
    monthly_data = monthly_data.merge(monthly_returns, left_index=True, right_index=True, how='left') \
                               .rename(columns={'ReturnFlag': 'Return_Count'})
    monthly_data['Return_Count'] = monthly_data['Return_Count'].fillna(0).astype(int)

    # Přidání sloupce pro celkovou hodnotu vratek
    returned_revenue_by_month = df[df['ReturnFlag'] == True].groupby(df['Date'].dt.to_period('M'))['Revenue'].sum()
    monthly_data = monthly_data.merge(returned_revenue_by_month, left_index=True, right_index=True, how='left') \
                               .rename(columns={'Revenue': 'Returned_Revenue'})
    monthly_data['Returned_Revenue'] = monthly_data['Returned_Revenue'].fillna(0)
    monthly_data['Net_Revenue'] = monthly_data['Total_Revenue'] - monthly_data['Returned_Revenue']

    # Přidání sloupce pro procento vratek
    monthly_data = monthly_data.reset_index()
    monthly_data['Date'] = monthly_data['Date'].astype(str)

    return monthly_data

# VYTVOŘENÍ TABULKY
monthly_revenue_table = generate_monthly_revenue_table()

st.subheader("📊 Monthly Revenue Overview")
st.dataframe(monthly_revenue_table, use_container_width=True)

# Vytvoření tlačítka pro stažení tabulky jako XLSX
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Monthly Revenue Overview')
    return output.getvalue()

excel_data = to_excel(monthly_revenue_table)

st.download_button(
    label="📥 Download Monthly Revenue Overview as XLSX",
    data=excel_data,
    file_name="monthly_revenue_overview.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
# END OF PAGE