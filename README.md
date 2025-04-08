# 📊 E-Commerce Sales Dashboard (Streamlit App)

This is **Part 2** of a multi-stage e-commerce analytics project.  
It focuses on **exploratory data analysis (EDA)** and **interactive visualization** of cleaned sales data using **Streamlit** and **Plotly**.

🚀 **Live demo** coming soon via Streamlit Community Cloud

---

## 🧭 What's Inside?

This Streamlit app consists of multiple analytical sections that provide insights into sales transactions, customer behavior, and potential anomalies.

### 📂 Overview of Analytical Sections:

- 📍 **General Overview**  
  Key KPIs like total revenue, number of transactions, and dataset time coverage

- 🧍 **Customer Insights**  
  Customer segmentation (New, Returning, Loyal), order patterns, and revenue contribution

- 📈 **Sales Trends**  
  Time-series analysis of revenue and quantity sold, including moving averages

- 🔝 **Best-Selling Products**  
  Top products by quantity and revenue, plus low-selling products

- 🔁 **Returned Products & Refunds**  
  Return rates by month and product, impact of returns on revenue

- 🌍 **Geographic Analysis**  
  Country-level analysis of revenue, AOV, return rate, and product preferences

- 🕵️ **Anomalies & Issues Detection**  
  Outliers in order value, excessive returns, data gaps (e.g., unspecified countries)

---

## 🛠 Technologies Used

- [Streamlit](https://streamlit.io/) for building the dashboard UI  
- [Plotly](https://plotly.com/python/) for interactive visualizations  
- `pandas`, `numpy`, `xlsxwriter` for backend data handling  
- Python 3.11+

---

## 📁 Data Source

The dataset used was cleaned in [Part 1 – Data Cleaning & Preprocessing](https://github.com/mw3b3r/ecommerce-analysis-part1-cleaning), and is available publicly via Kaggle:

🔗 **[Kaggle Dataset – Raw + Cleaned Data](https://www.kaggle.com/datasets/martweber/e-commerce-sales-data-raw-cleaned)**

---

## 📦 How to Run Locally

1. Clone this repo  
2. Install required packages:
    ```bash
    pip install -r requirements.txt
    ```
3. Place `cleaned_sales_data.csv` in the root directory  
4. Run:
    ```bash
    streamlit run streamlit_app.py
    ```

---

## 💡 Why This Project?

This dashboard was built as a **portfolio piece** to showcase:

- 📊 Practical skills in exploratory analysis and business reporting  
- 🧠 UX-focused design of dashboards for non-technical users  
- 💬 Clear presentation of insights for decision-making

---

## 📍 Part of a Series

🔹 **[Part 1 – Data Cleaning & Preprocessing](https://github.com/mw3b3r/ecommerce-analysis-part1-cleaning)**  
🔹 **Part 2 – Interactive Dashboard (this repo)**
