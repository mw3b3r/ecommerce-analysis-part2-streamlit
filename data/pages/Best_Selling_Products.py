import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO

# Hlavní nadpis a popis sekce
st.markdown("""
    <h1 style="text-align: center;">Sales Transaction Analysis</h1>
    <h3 style="text-align: center; color: #555;">Best Selling Products</h3>
    <div padding: 15px; border-radius: 10px; text-align: center;">
        <p style="font-size: 16px;">
            This page contains an analysis of the best and worst selling products 
            in the e-shop. It includes TOP products by number of sales, products 
            with the lowest sales and products with the highest sales. <br>
        </p>
    </div>
""", unsafe_allow_html=True)

# Načtení datasetu
df = pd.read_csv("cleaned_sales_data.csv", parse_dates=["Date"])
df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")  # Oprava typu

st.divider()  # Oddělovač

# GRAF TOP SELLING PRODUCTS
# ------------------------------------------------------------------------------

# Vizuální oddělení výběru top N produktů
st.markdown("**Select number of top-selling products:**")
top_n = st.radio("", options=[5, 10, 15, 20], horizontal=True)

# Funkce pro generování grafu
def generate_top_products_graph(df, top_n):
    top_n_products = df.groupby('ProductNo')['Quantity'].sum().sort_values(ascending=False).head(top_n)

    top_n_products_df = pd.DataFrame({
        'Number of sales': top_n_products.values,
        'ProductNo': top_n_products.index
    })

    top_n_products_df = top_n_products_df.merge(df[['ProductNo', 'ProductName']].drop_duplicates(), on='ProductNo', how='left')

    fig = px.bar(
        top_n_products_df,
        x="Number of sales",
        y="ProductName",
        orientation="h",
        title=f"Top {top_n} Best-Selling Products",
        labels={"Number of sales": "Total Sales", "ProductName": "Product Name"},
    )

    # Vizuální úpravy grafu
    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(color="black"),
        title_font=dict(size=22),
        xaxis=dict(
            showgrid=True,
            gridcolor="lightgrey",
            gridwidth=1,
            tickfont=dict(size=14)
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(size=14),
            categoryorder="total ascending",
            tickmode="linear"
        )
    )

    # Přidání hodnot nad sloupce + tooltipy
    fig.update_traces(
       text=top_n_products_df["Number of sales"].apply(lambda x: f"{x:,.0f}"),
       textposition="inside",  # ⬅️ POSUNEME ČÍSLA DOVNITŘ SLOUPCŮ
       insidetextanchor="end",  # ⬅️ UKOTVÍME TEXT NA KONEC SLOUPCE
       hoverinfo="x+y",
       hoverlabel=dict(bgcolor="white", font_size=12, font_color="black"),
    )

    # Zvýraznění nejsilnějšího sloupce
    max_value = max(top_n_products_df["Number of sales"])
    fig.for_each_trace(lambda t: t.update(marker_color=[
        "#FF5733" if x == max_value else "#4682B4" for x in top_n_products_df["Number of sales"]
    ]))

    return fig

# Zobrazení grafu
fig = generate_top_products_graph(df, top_n)
st.plotly_chart(fig, use_container_width=True)
st.markdown("<br><br>", unsafe_allow_html=True)  # Mezera po grafu

st.divider()  # Oddělovač

# GRAF HIGHEST REVENUE PRODUCTS
# ------------------------------------------------------------------------------

# Unikátní klíč pro radio buttony (aby Streamlit věděl, že jde o jiný prvek)
st.markdown("**Select number of highest revenue products:**")
top_h = st.radio("", options=[5, 10, 15, 20], horizontal=True, key="top_h_revenue")

# Přidání sloupce Revenue (tržby) do datasetu
df["Revenue"] = df["Price"] * df["Quantity"]

def generate_top_revenue_products_graph(df, top_n):  # Funkce nyní přijímá DF i top_n
    # Výběr top N produktů podle tržby
    top_n_revenue = df.groupby('ProductNo')['Revenue'].sum().sort_values(ascending=False).head(top_n)

    # Vytvoření DataFrame pro vizualizaci
    top_n_revenue_df = pd.DataFrame({
        'Amount of revenue': top_n_revenue.values,
        'ProductNo': top_n_revenue.index
    })

    # Přidání názvu produktu
    top_n_revenue_df = top_n_revenue_df.merge(df[['ProductNo', 'ProductName']].drop_duplicates(), on='ProductNo', how='left')

    # Vytvoření grafu pomocí Plotly
    fig = px.bar(
        top_n_revenue_df,
        x="Amount of revenue",
        y="ProductName",
        orientation="h",
        title=f"Top {top_n} Highest revenue products",
        labels={"Amount of revenue": "Amount of revenue", "ProductName": "Product Name"},
    )

    # Úprava vzhledu grafu
    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(color="black"),
        title_font=dict(size=22),
        xaxis=dict(
            showgrid=True,
            gridcolor="lightgrey",
            gridwidth=1,
            tickfont=dict(size=14)
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(size=14),
            categoryorder="total ascending",
            tickmode="linear"
        )
    )

    # Přidání hodnot nad sloupce + tooltipy
    fig.update_traces(
        text=top_n_revenue_df["Amount of revenue"].apply(lambda x: f"{x:,.0f}"),
        textposition="inside",  #  ČÍSLA DOVNITŘ SLOUPCŮ
        insidetextanchor="end",  # TEXT NA KONEC SLOUPCE
        hoverinfo="x+y",
        hoverlabel=dict(bgcolor="white", font_size=12, font_color="black"),
    )

    # Zvýraznění nejsilnějšího sloupce
    max_value = max(top_n_revenue_df["Amount of revenue"])
    fig.for_each_trace(lambda t: t.update(marker_color=[
        "#FF5733" if x == max_value else "#4682B4"
        for x in top_n_revenue_df["Amount of revenue"]
    ]))

    return fig

# Zobrazení grafu
fig = generate_top_revenue_products_graph(df, top_h)  # 
st.plotly_chart(fig, use_container_width=True)

# Oddělovač pro další obsah
st.divider()

# TABULKA LOWEST SELLING PRODUCTS
# ------------------------------------------------------------------------------

def show_lowest_sales_table(df, threshold=10):
    # Odstraníme vrácené produkty a spočítáme počet prodaných kusů podle ProductNo
    lowest_sales = df[df['ReturnFlag'] != True].groupby('ProductNo')['Quantity'].sum()

    # Vyfiltrujeme produkty s malým počtem prodejů
    lowest_sales = lowest_sales[lowest_sales <= threshold].sort_values()

    # Vytvoření DataFrame pro zobrazení
    table_df = pd.DataFrame({
        'ProductNo': lowest_sales.index,
        'Number of Sales': lowest_sales.values
    })

    # Přidáme názvy produktů
    table_df = table_df.merge(df[['ProductNo', 'ProductName']].drop_duplicates(), on='ProductNo', how='left')

    # Přeskládáme sloupce pro čitelnost
    table_df = table_df[['ProductName', 'ProductNo', 'Number of Sales']]

    # Nadpis
    st.subheader("Lowest Selling Products (≤ 10 sales)")
    st.markdown(
    "This table shows products with **very low sales**, specifically those with 10 or fewer units sold (excluding returns). "
    "It can help identify items that may need promotion or removal from the catalog."
    )

    # Zobrazíme tabulku ve Streamlit
    st.dataframe(table_df, use_container_width=True)

    # Stažení do Excelu
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        table_df.to_excel(writer, index=False, sheet_name='Low Sales')

    st.download_button(
        label="📥 Download as Excel",
        data=output.getvalue(),
        file_name="lowest_selling_products.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

show_lowest_sales_table(df)
