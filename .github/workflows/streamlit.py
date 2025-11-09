import streamlit as st
import pandas as pd
import plotly.express as px
import calendar

st.title("Bookshop Executive Dashboard")

data = st.file_uploader("Upload Data", type = "csv")

if data:
    df = pd.read_csv(data)
    tab1, tab2, tab3 = st.tabs(["Sales & Revenue", "Customer Analysis", "Location Analysis"])
    
    with tab1:
        st.title("Sales & Revenue KPIs")
        
        IndexDate = pd.DatetimeIndex(df["InvoiceDate"])
        df["Month"] = IndexDate.month
        df["MonthName"] = df["Month"].apply(lambda x : calendar.month_name[x])
        df["Quarter"] = IndexDate.quarter
        quarterlist = sorted(df["Quarter"].unique(), reverse = False)
        quarterlist.insert(0, "Select All")
        
        st.subheader("Quarter Selection")
        quarterfilter = st.selectbox(label = "Select a Quarter", options = quarterlist)
        if quarterfilter != "Select All":
            quarter_filtered_df = df[df["Quarter"] == quarterfilter]
        else:
            quarter_filtered_df = df.copy()
        
        quarter_filtered_df["GrossProfit"] =  quarter_filtered_df["Quantity"] *  quarter_filtered_df["NetPrice"]
        quarter_filtered_df["GrossRevenue"] = quarter_filtered_df["Quantity"] * quarter_filtered_df["UnitPrice"]
        quarter_filtered_df["Cost"] = quarter_filtered_df["NetPrice"] - quarter_filtered_df["UnitPrice"]
        GrossProfit = quarter_filtered_df["GrossProfit"].sum()     
        GrossRevenue = quarter_filtered_df["GrossRevenue"].sum()
        Cost = quarter_filtered_df["Cost"].sum()
        
        col_revenue, col_cost, col_profit = st.columns(3)
        with col_revenue:
            st.metric(label = "Gross Revenue 💸", value = f"${GrossRevenue:,.0f}")
        with col_cost:
            st.metric(label = "Total Cost 🔻", value = f"-${-Cost:,.0f}")
        with col_profit:
            st.metric(label = "Gross Profit 🪙", value = f"${GrossProfit:,.0f}")
            
        month_filtered_df = quarter_filtered_df.groupby(["Month", "MonthName"]).agg(GrossProfit = ("GrossProfit", "sum"), TotalQuantity = ("Quantity", "sum")) .reset_index()
        month_filtered_df = month_filtered_df.sort_values(by = "Month")
        
        fig = px.bar(
            month_filtered_df,
            x = "MonthName",
            y = "GrossProfit",
            color = "GrossProfit",
            labels = {
                "MonthName" : "Month",
                "GrossProfit" : "Gross Profit ($)",
                "color" : "Profit Level"
            },
            title = "Monthly Gross Profit Performance"
        )
        fig.update_traces(
            texttemplate = "%{y:,.0f}",
            textposition = "outside",
            hovertemplate = "<b>Month:</b> %{x}<br>" +
                  "<b>Profit:</b> $%{y:,.0f}<br>" +
                  "<b>Orders:</b> %{customdata[0]:,.0f}<extra></extra>",
            customdata = month_filtered_df[["TotalQuantity"]]
        )
        fig.update_layout(
            xaxis_title = "Month",
            yaxis_title = "Gross Profit",
            coloraxis_colorbar_title="Profit Level")
        st.plotly_chart(fig, use_container_width = True)
