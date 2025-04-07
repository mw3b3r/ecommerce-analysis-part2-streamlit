import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO
import plotly.graph_objects as go

# Hlavní nadpis a popis sekce
st.markdown("""
    <h1 style="text-align: center;">Sales Transaction Analysis</h1>
    <h3 style="text-align: center; color: #555;">Anomalies & Issues Detection</h3>
    <div style="padding: 15px; border-radius: 10px; text-align: center;">
    <p style="font-size: 16px;">     
        This section is dedicated to identifying unusual patterns and potential data issues 
        in sales transactions. It highlights products and customers with high return rates, 
        unusually large orders, negative values, and other anomalies that may indicate 
        data quality problems, fraud, or operational inefficiencies.
    </p>
    </div>
""", unsafe_allow_html=True)

# Načtení datasetu
df = pd.read_csv("cleaned_sales_data.csv", parse_dates=["Date"])
df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")  # Oprava typu
df["Revenue"] = df["Quantity"] * df["Price"]

st.divider()  # Oddělovač
# ------------------------------------------------------------

st.markdown("""
### Negative Revenue Without Return Flag

In this check, we look for transactions where revenue is negative,  
but they are **not marked as returns**. These cases could indicate:
- Data entry errors (e.g. wrong quantity or price)
- System glitches
- Misclassified transactions

Only records with negative receipts and not marked as returns are shown below.
""")

# Vyfiltrování podezřelých záznamů
negative_revenue_issues = df[(df["Revenue"] < 0) & (df["ReturnFlag"] != True)]

# Zobrazení tabulky, pokud něco najdeme
if not negative_revenue_issues.empty:
    st.warning(f"{len(negative_revenue_issues)} suspicious records found with negative revenue and no return flag.")
    st.dataframe(negative_revenue_issues[["Date", "CustomerNo", "ProductName", "Quantity", "Price", "Revenue", "ReturnFlag", "Country"]], use_container_width=True)
else:
    st.success("✅ No issues found. All negative revenue transactions are properly marked as returns.")

st.divider()  # Oddělovač
# ------------------------------------------------------------

st.markdown("""
### Products with High Return Rate

This check identifies products with an unusually high return rate.  
A high return rate might indicate issues such as:
- poor product quality  
- misleading descriptions  
- mismatched expectations  
- or even technical problems

We calculate the return rate as the percentage of returned units out of total units sold.
Only products with **return rate above 30%** are shown.
""")

# Vynechání záporných quantity při prodeji (např. ručně odepsané položky)
df["ReturnedQuantity"] = df.apply(lambda row: abs(row["Quantity"]) if row["ReturnFlag"] else 0, axis=1)
df["SoldQuantity"] = df.apply(lambda row: row["Quantity"] if not row["ReturnFlag"] and row["Quantity"] > 0 else 0, axis=1)

# Výpočet agregací
product_returns = df.groupby("ProductName").agg(
    Total_Sold=("SoldQuantity", "sum"),
    Returned=("ReturnedQuantity", "sum")
).reset_index()

# Výpočet podílu vratek
product_returns["Return Rate (%)"] = (
    product_returns["Returned"] / product_returns["Total_Sold"].replace(0, np.nan) * 100
).round(2)

# Vyčištění
product_returns = product_returns.dropna()
product_returns = product_returns[product_returns["Total_Sold"] > 0]

# Filtrování produktů s vysokou vratkovostí
high_return_products = product_returns[product_returns["Return Rate (%)"] > 30].sort_values(by="Return Rate (%)", ascending=False)

# Výstup: varování nebo tabulka
if not high_return_products.empty:
    st.warning(f"{len(high_return_products)} product(s) with return rate above 30%.")
    st.dataframe(high_return_products, use_container_width=True)

    # Poznámka pod tabulkou
    st.markdown("""
    ⚠️ **Note:** Due to the dataset representing only a partial time period,  
    some products may appear with a return rate above 100% — this can happen  
    when returns are recorded but the corresponding sale is outside of the dataset.
    """)

    # Funkce pro export do Excelu
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='High Return Rate Products')
        return output.getvalue()

    excel_file = to_excel(high_return_products)

    # Tlačítko pro stažení
    st.download_button(
        label="📥 Download Excel",
        data=excel_file,
        file_name="high_return_rate_products.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.success("✅ No products found with return rate above 30%.")


st.divider()  # Oddělovač
# ------------------------------------------------------------

st.markdown("""
### Customers with Excessive Returns

In this check, we analyze customers who have returned a high number of orders  
compared to their total number of purchases. This might indicate:
- frequent dissatisfaction
- potential abuse of return policy
- or inconsistencies in transaction labeling

The table below shows customers with a **return rate over 30%**.
""")

# Unikátní objednávky s informací, zda byly vráceny
unique_orders = df[["TransactionNo", "CustomerNo", "ReturnFlag"]].drop_duplicates()

# Počet objednávek a počet vrácených objednávek na zákazníka
customer_returns = unique_orders.groupby("CustomerNo").agg(
    Total_Orders=("TransactionNo", "count"),
    Returned_Orders=("ReturnFlag", "sum")
).reset_index()

# Výpočet return rate
customer_returns["Return Rate (%)"] = (
    customer_returns["Returned_Orders"] / customer_returns["Total_Orders"].replace(0, np.nan) * 100
).round(2)

# Výběr podezřelých
high_return_customers = customer_returns[customer_returns["Return Rate (%)"] > 30].sort_values(by="Return Rate (%)", ascending=False)

# Výstup
if not high_return_customers.empty:
    st.warning(f"{len(high_return_customers)} customers found with return rate above 30%.")
    st.dataframe(high_return_customers, use_container_width=True)
else:
    st.success("✅ No customers found with excessive return rates.")

# Volitelná poznámka
st.markdown("""
⚠️ **Note:** These customers have a return rate above 30%.  
Further analysis may be needed to understand the cause (e.g., product issues, abuse, or data gaps).
""")

# Funkce pro export do Excelu
def to_excel_customers(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='High Return Rate Customers')
    return output.getvalue()

excel_data_customers = to_excel_customers(high_return_customers)

# Tlačítko pro stažení
st.download_button(
    label="📥 Download Customer Return Data",
    data=excel_data_customers,
    file_name="high_return_rate_customers.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.divider()  # Oddělovač
# ------------------------------------------------------------

# OUTLIERS IN ORDER VALUE
# ------------------------------------------------------------------------------

st.markdown("### Outliers in Order Value")
st.markdown("""
This section helps identify unusually high or low order values.  
Such outliers might indicate errors, fraud, or exceptional customers.
""")

# Výpočet celkové hodnoty objednávky (na základě TransactionNo)
order_values = df.groupby("TransactionNo")["Revenue"].sum().reset_index()
order_values.columns = ["TransactionNo", "TotalOrderValue"]

# BOX PLOT – pro detekci outlierů
box_fig = px.box(
    order_values,
    y="TotalOrderValue",
    points="outliers",  # zobrazí outliery jako body
    title="Box Plot of Total Order Value",
    template="plotly_white"
)
st.plotly_chart(box_fig, use_container_width=True)

with st.expander("ℹ️ What does this chart show?"):
    st.markdown("""
    - **Box Plot:** This chart shows the overall spread of total order values.  
      The dots outside the box are considered **outliers** – unusually high or low values compared to most orders.
      
    These charts help detect suspiciously large orders or potential errors in the data.
    """)

# HISTOGRAM – pro přehled rozložení (s logaritmickou osou Y)
hist_fig = px.histogram(
    order_values,
    x="TotalOrderValue",
    nbins=50,
    title="Distribution of Total Order Value (Log-Scaled Y)",
    template="plotly_white",
    log_y=True
)
st.plotly_chart(hist_fig, use_container_width=True)

with st.expander("ℹ️ What does this chart show?"):
    st.markdown("""
        
    - **Histogram:** This chart shows how often different order values occur.  
      The **logarithmic Y-axis** helps highlight even rare or extreme values that would otherwise be hard to see.
      
    These charts help detect suspiciously large orders or potential errors in the data.
    """)

st.divider()  # Oddělovač
# ------------------------------------------------------------

# Výpočet hranice pro horní 1 % objednávek
threshold = order_values["TotalOrderValue"].quantile(0.99)
formatted_threshold = f"{int(round(threshold)):,}".replace(",", " ") + " £"

# Výběr objednávek nad touto hranicí
top_orders = order_values[order_values["TotalOrderValue"] >= threshold].sort_values(
    by="TotalOrderValue", ascending=False
)

# Formátování čísel do čitelné podoby
top_orders["TotalOrderValue"] = top_orders["TotalOrderValue"].apply(
    lambda x: f"{int(round(x)):,}".replace(",", " ") + " £"
)

# Popis
st.markdown("### Top 1% Orders by Value")
st.markdown(
    f"""
    These are the top 1% of orders with the highest total value.  
    They may indicate **bulk purchases**, **corporate buyers**, or **potential anomalies**.

    - Threshold for top 1%: **{formatted_threshold}**
    """
)

# Zobrazení tabulky
st.dataframe(top_orders, use_container_width=True)

# Funkce pro export do Excelu
def to_excel_top_orders(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Top 1 Percent Orders')
    return output.getvalue()

excel_data_top_orders = to_excel_top_orders(top_orders)

# Tlačítko pro stažení
st.download_button(
    label="📥 Download Top 1% Orders as Excel",
    data=excel_data_top_orders,
    file_name="top_1_percent_orders.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
