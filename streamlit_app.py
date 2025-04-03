# Import potřebných knihoven
# ------------------------------------------------------------------------------
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime
import time
from io import BytesIO
import plotly.graph_objects as go

# Nastavení postranního panelu
st.sidebar.title("Navigace")
page = st.sidebar.selectbox("Vyberte stránku", ["General Overview", 
                                                "Best-Selling Products", 
                                                "Sales Trends Over Time", 
                                                "Returned Products & Refunds",
                                                "Customer Insights",
                                                "Geographic Analysis",
                                                "Anomalies & Issues Detection"]
                            )

# Dynamické načítání obsahu stránek
if page == "General Overview":
    exec(open("data/pages/General_Overview.py").read())
elif page == "Best-Selling Products":
    exec(open("data/pages/Best_Selling_Products.py").read())
elif page == "Sales Trends Over Time":
    exec(open("data/pages/Sales_Trends.py").read())
elif page == "Returned Products & Refunds":
    exec(open("data/pages/Returned_Products.py").read())
elif page == "Customer Insights":
    exec(open("data/pages/Customer_Insights.py").read())
elif page == "Geographic Analysis":
    exec(open("data/pages/Geographic_Analysis.py").read())
elif page == "Anomalies & Issues Detection":
    exec(open("data/pages/Anomalies.py").read())


