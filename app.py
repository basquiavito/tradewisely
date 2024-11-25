import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Set Streamlit page configuration
st.set_page_config(
    page_title="TradeWisely: Stock Data Analysis",
    layout="wide",
    initial_sidebar_state="expanded",
)

# App Title
st.title("TradeWisely: Stock Data Analysis")

# Sidebar for stock input and date range
st.sidebar.header("Stock Input")
ticker = st.sidebar.text_input("Enter Stock Ticker:", value="AAPL").upper()
start_date = st.sidebar.date_input("Start Date:", value=pd.to_datetime("2024-01-01"))
end_date = st.sidebar.date_input("End Date:", value=pd.to_datetime("2024-11-01"))

# Validate date range
if start_date > end_date:
    st.sidebar.error("Error: Start Date must be before End Date.")

# Fetch stock data function with caching and enhanced error handling
@st.cache_data
def fetch_stock_data(ticker, start, end):
    try:
        data = yf.download(ticker, start=start, end=end)
        if data.empty:
            st.error(f"No data found for ticker '{ticker}' in the given date range.")
            return pd.DataFrame()
        
        # Calculate additional metrics
        data["Spread"] = data["High"] - data["Low"]
        data["Log Return"] = np.log(data["Close"] / data["Close"].shift(1))
        data["Cumulative Mean Log Return"] = data["Log Return"].expanding().mean()
        data.reset_index(inplace=True)  # Ensure 'Date' is a column
        return data
    except Exception as e:
        st.error(f"An error occurred while fetching data: {e}")
        return pd.DataFrame()

# Initialize stock_data as an empty DataFrame
stock_data = pd.DataFrame()

# Fetch and display data when button is clicked
if st.sidebar.button("Fetch Data"):
    if ticker.strip() == "":
        st.sidebar.error("Please enter a valid stock ticker symbol.")
    else:
        with st.spinner(f"Fetching data for {ticker} from {start_date} to {end_date}..."):
            stock_data = fetch_stock_data(ticker, start_date, end_date)

    if not stock_data.empty:
        # Display Stock Data
        st.subheader(f"📈 Stock Data for {ticker.upper()}")
        st.dataframe(
            stock_data[["Date", "Open", "High", "Low", "Close", "Log Return", "Cumulative Mean Log Return"]]
            .dropna()
            .reset_index(drop=True),
            height=500,
        )

        # Interactive Plot with Plotly
        st.subheader(f"Interactive Log Return and Cumulative Mean for {ticker.upper()}")

        fig = go.Figure()

        # Log Return Line
        fig.add_trace(
            go.Scatter(
                x=stock_data["Date"],
                y=stock_data["Log Return"],
                mode="lines",
                name="Log Return",
                line=dict(width=1, color="blue"),
            )
        )

        # Cumulative Mean Log Return Line
        fig.add_trace(
            go.Scatter(
                x=stock_data["Date"],
                y=stock_data["Cumulative Mean Log Return"],
                mode="lines",
                name="Cumulative Mean Log Return",
                line=dict(width=2, color="red", dash="dash"),
            )
        )

        # Update Layout
        fig.update_layout(
            title=f"Log Return and Cumulative Mean: {ticker.upper()}",
            xaxis_title="Date",
            yaxis_title="Log Return",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified",  # Display hover info for all traces at once
        )

        # Display the Plot
        st.plotly_chart(fig, use_container_width=True)

        # Proceed with additional calculations and visualizations
        # Add new columns for the table
        stock_data["Log Return (%)"] = stock_data["Log Return"] * 100  # Convert to percentage
        stock_data["Cumulative Return"] = (1 + stock_data["Log Return"]).cumprod()  # Calculate cumulative return
        stock_data["Cumulative Return (%)"] = (stock_data["Cumulative Return"] - 1) * 100  # Convert to percentage
        stock_data["Day of the Week"] = pd.to_datetime(stock_data["Date"]).dt.day_name()  # Extract day of the week

        # Calculate custom myPrice
        # Step 1: Initialize myPrice with the first valid Log Return
        initial_myPrice = stock_data["Log Return"].dropna().iloc[0]
        myPrice = [initial_myPrice]  # First value is the initial mean

        # Step 2: Iteratively update myPrice by accumulating Log Returns
        for i in range(1, len(stock_data)):
            today_log_return = stock_data["Log Return"].iloc[i]
            previous_myPrice = myPrice[-1]

            # Update myPrice by adding today's log return
            new_myPrice = previous_myPrice + today_log_return

            # Append the new value to the myPrice list
            myPrice.append(new_myPrice)

        # Step 3: Add the myPrice column to the DataFrame
        stock_data["myPrice"] = myPrice
        # Step 4: Add the myPrice_x1000 column next to myPrice
        stock_data["myPrice_x1000"] = stock_data["myPrice"] * 1000

        # Prepare the table data
        table_data = stock_data[["Date", "Day of the Week", "Log Return (%)", "Cumulative Return (%)", "myPrice","myPrice_x1000"]]

        # Display the table below the plot
        st.subheader(f"Daily Returns and Cumulative Performance for {ticker.upper()}")
        st.dataframe(table_data.dropna().reset_index(drop=True))

        # Line chart for Cumulative Return
        st.subheader(f"Cumulative Return for {ticker.upper()}")

        # Create the figure
        fig_cumulative_return = go.Figure()

        # Add a line for Cumulative Return
        fig_cumulative_return.add_trace(
            go.Scatter(
                x=stock_data["Date"],
                y=stock_data["Cumulative Return (%)"],
                mode="lines",
                name="Cumulative Return (%)",
                line=dict(width=2, color="green"),
            )
        )

        # Add a line for myPrice
        fig_cumulative_return.add_trace(
            go.Scatter(
                x=stock_data["Date"],
                y=stock_data["myPrice_x1000"],
                mode="lines",
                name="myPrice",
                line=dict(width=2, color="orange", dash="dash"),
            )
        )

        # Update the layout
        fig_cumulative_return.update_layout(
            title=f"Cumulative Return and myPrice Over Time: {ticker.upper()}",
            xaxis_title="Date",
            yaxis_title="Value (%)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified",  # Show hover info for all traces at once
        )

        # Display the chart
        st.plotly_chart(fig_cumulative_return, use_container_width=True)

        # Calculate rolling statistics (window size of 7 days for example)
        stock_data["Mean"] = stock_data["Log Return"].rolling(window=7).mean()
        stock_data["By1000"] = stock_data["Mean"] * 1000  # New column: Mean multiplied by 1000
        stock_data["Mode"] = stock_data["Log Return"].rolling(window=7).apply(
            lambda x: pd.Series(x).mode().iloc[0] if not pd.Series(x).mode().empty else np.nan, raw=False
        )
        stock_data["Variance"] = stock_data["Log Return"].rolling(window=7).var()
        stock_data["Standard Deviation"] = stock_data["Log Return"].rolling(window=7).std()

        # Select relevant columns for rolling stats
        stats_table = stock_data[["Date", "Mean", "By1000", "Mode", "Variance", "Standard Deviation"]]

        # Display the table at the lower part of the UI
        st.subheader("📊 Rolling Statistics of Log Return Over Time")

        # Display as an interactive table
        st.dataframe(stats_table.dropna().reset_index(drop=True))

        # Additional Visualization: myPrice vs Log Return
        st.subheader(f"myPrice vs Log Return: {ticker.upper()}")

        fig_myprice_vs_logreturn = go.Figure()

        # Log Return Line
        fig_myprice_vs_logreturn.add_trace(
            go.Scatter(
                x=stock_data["Date"],
                y=stock_data["Log Return"],
                mode="lines",
                name="Log Return",
                line=dict(width=1, color="blue"),
            )
        )

        # myPrice Line
        fig_myprice_vs_logreturn.add_trace(
            go.Scatter(
                x=stock_data["Date"],
                y=stock_data["myPrice"],
                mode="lines",
                name="myPrice",
                line=dict(width=2, color="orange", dash="dash"),
            )
        )

        # Update Layout
        fig_myprice_vs_logreturn.update_layout(
            title=f"Log Return vs myPrice: {ticker.upper()}",
            xaxis_title="Date",
            yaxis_title="Value",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified",
        )

        # Display the Plot
        st.plotly_chart(fig_myprice_vs_logreturn, use_container_width=True)
    else:
        st.warning("No data available. Please check your inputs.")
else:
    st.write("➡️ **Click 'Fetch Data' in the sidebar to load stock data.**")
