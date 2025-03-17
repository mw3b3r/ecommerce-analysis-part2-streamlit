import streamlit as st

# Nastavení nadpisu
st.markdown(
    '''<h1 style="text-align: center;">Sales Transaction Analysis</h1>''',
    unsafe_allow_html=True
)

# Nastavení postranního panelu
st.sidebar.title("Navigace")
page = st.sidebar.selectbox("Vyberte stránku", ["General Overview", 
                                                "Best-Selling Products", 
                                                "Sales Trends Over Time", 
                                                "Customer Insights",
                                                "Returned Products & Refunds",
                                                "Geographic Analysis",
                                                "Anomalies & Issues Detection"]
                            )

# Načtení obsahu stránky "General Overview"
if page == "General Overview":
    import data.pages.General_Overview
elif page == "Best-Selling Products":
    import data.pages.Best_Selling_Products
elif page == "Sales Trends Over Time":
    import data.pages.Sales_Trends
elif page == "Customer Insights":
    import data.pages.Customer_Insights
elif page == "Returned Products & Refunds":
    import data.pages.Returned_Products
elif page == "Geographic Analysis":
    import data.pages.Geographic_Analysis
elif page == "Anomalies & Issues Detection":
    import data.pages.Anomalies