import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import mplfinance as mpf
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
        # Ensure 'Date' is in datetime format
        stock_data["Date"] = pd.to_datetime(stock_data["Date"])

       

  
        # Proceed with additional calculations and visualizations
        # Add new columns for the table
        stock_data["Log Return (%)"] = stock_data["Log Return"] * 100  # Convert to percentage
        stock_data["Cumulative Return"] = (1 + stock_data["Log Return"]).cumprod()  # Calculate cumulative return
        stock_data["Cumulative Return (%)"] = (stock_data["Cumulative Return"] - 1) * 100  # Convert to percentage
        stock_data["Day of the Week"] = stock_data["Date"].dt.day_name()  # Extract day of the week
        stock_data["RV_9"] = stock_data["Volume"] / stock_data["Volume"].rolling(window=9).mean()

        # Initialize myPrice on the second day as the mean of the first two log returns
        if len(stock_data["Log Return"].dropna()) < 2:
            st.warning("Not enough data to calculate myPrice. Need at least two valid log return values.")
            st.stop()

        initial_myPrice = stock_data["Log Return"].iloc[:2].mean()  # Mean of Day 1 and Day 2
        myPrice = [np.nan, initial_myPrice]  # First day is NaN since no price is defined on Day 1

        # Update myPrice for subsequent days
        for i in range(2, len(stock_data)):  # Start from Day 3
            today_log_return = stock_data["Log Return"].iloc[i]

            # Calculate the mean of all log returns up to the current day
            current_mean = stock_data["Log Return"].iloc[: i + 1].mean()

            # Compare today's log return to the new mean
            previous_myPrice = myPrice[-1]

            if pd.isna(previous_myPrice):
                # If previous_myPrice is NaN, cannot perform calculation
                new_myPrice = np.nan
            elif today_log_return > current_mean:
                # Add the excess
                excess = today_log_return - current_mean
                new_myPrice = previous_myPrice + excess
            else:
                # Subtract the deficiency
                deficiency = current_mean - today_log_return
                new_myPrice = previous_myPrice - deficiency

            # Append the new myPrice
            myPrice.append(new_myPrice)

        # Ensure the myPrice list matches the length of stock_data
        if len(myPrice) != len(stock_data):
            st.error("Mismatch between myPrice list and stock_data length.")
            st.stop()

        # Add the myPrice column to the DataFrame
        stock_data["myPrice"] = myPrice

        # Optionally, add the scaled myPrice_x1000 column
        stock_data["myPrice_x1000"] = stock_data["myPrice"] * 1000

       
           
        table_data = stock_data[["Date", "Day of the Week", "RV_9","Log Return (%)", "Cumulative Return (%)", "myPrice", "myPrice_x1000"]]

    # Rename columns for better readability
    table_data.rename(
        columns={
            "Date": "Date",
            "Day of the Week": "Weekday",
            "RV_9": "Relative Volume (9 Days)",

            "Log Return (%)": "Log Return (%)",
            "Cumulative Return (%)": "Cumulative Return (%)",
            "myPrice": "My Price",
            "myPrice_x1000": "My Price x1000",
        },
        inplace=True,
    )

    # Display the table below the plot
    st.subheader(f"Daily Returns and Cumulative Performance for {ticker.upper()}")
    st.dataframe(table_data.dropna().reset_index(drop=True))





    # Plot the line chart for 'myPrice_x1000'
    st.subheader("My Price x1000 Over Time")
    if "myPrice_x1000" in stock_data.columns:
        # Get the latest myPrice_x1000 value
        latest_myPrice_x1000 = stock_data["myPrice_x1000"].iloc[-1]
        
        # Create the line chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=stock_data["Date"],
            y=stock_data["myPrice_x1000"],
            mode="lines",
            name="My Price x1000"
        ))
        
        # Update layout with dynamic title
        fig.update_layout(
            title=f"My Price x1000 Over Time (Latest: {latest_myPrice_x1000:.2f})",
            xaxis_title="Date",
            yaxis_title="My Price x1000",
            template="plotly_white"
        )
        
        # Render the chart
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available to plot 'My Price x1000'. Please fetch the data first.")

    






 