import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

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
ticker = st.sidebar.text_input("Enter Stock Ticker:", value="AAPL").upper().strip()
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
        data["Spread"] = data["High"] - data["Low"]  # Spread: High - Low
        data["Log Return"] = np.log(data["Close"] / data["Close"].shift(1))
        data["Log Return"].fillna(0, inplace=True)
          # Log Return
        data.reset_index(inplace=True)  # Ensure 'Date' is a column
        data["Date"] = data["Date"].dt.strftime("%Y-%m-%d")  # Format 'Date' column
        return data
    except Exception as e:
        st.error(f"An error occurred while fetching data: {e}")
        return pd.DataFrame()

# # Fetch and display data when button is clicked
if st.sidebar.button("Fetch Data"):
    if ticker.strip() == "":
        st.sidebar.error("Please enter a valid stock ticker symbol.")
    else:
        with st.spinner(f"Fetching data for {ticker} from {start_date} to {end_date}..."):
            stock_data = fetch_stock_data(ticker, start_date, end_date)
        
        if not stock_data.empty:
            st.subheader(f"📈 Stock Data for {ticker.upper()}")
            
            # Display the table with formatted columns and single header row
            st.dataframe(
                stock_data[["Date", "Open", "High", "Low", "Close", "Spread", "Log Return"]]
                .dropna()
                .reset_index(drop=True),
                height=500
            )
        else:
            st.warning("No data available. Please check your inputs.")
else:
    st.write("➡️ **Click 'Fetch Data' in the sidebar to load stock data.**")
