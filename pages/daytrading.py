import streamlit as st
import yfinance as yf
import pandas as pd

def run():
    # Set page-specific title
    st.title("TradeWisely: Intraday Stock Data")

    # Sidebar for stock input and date range
    st.sidebar.header("Intraday Stock Input")
    ticker = st.sidebar.text_input("Enter Stock Ticker:", value="AVGO").upper()
    interval = st.sidebar.selectbox(
        "Select Interval:",
        options=["1m", "5m", "15m", "30m", "1h"],
        index=2  # Default to 15m
    )
    start_date = st.sidebar.date_input("Start Date:", value=pd.Timestamp.today() - pd.Timedelta(days=1))
    end_date = st.sidebar.date_input("End Date:", value=pd.Timestamp.today())

    # Validate date range
    if start_date > end_date:
        st.sidebar.error("Error: Start Date must be before or equal to End Date.")

    # Use st.set_query_params instead of directly updating st.query_params
    st.set_query_params(
        ticker=ticker,
        interval=interval,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d")
    )

    # Fetch intraday data function
    @st.cache_data
    def fetch_intraday_data(ticker, interval, start_date, end_date):
        try:
            # Fetch data
            intraday_data = yf.download(
                ticker, start=start_date, end=end_date, interval=interval
            )
            if intraday_data.empty:
                st.error(f"No intraday data found for ticker '{ticker}' in the given date range.")
                return pd.DataFrame()
            intraday_data.reset_index(inplace=True)  # Ensure 'Datetime' is a column
            return intraday_data
        except Exception as e:
            st.error(f"An error occurred while fetching intraday data: {e}")
            return pd.DataFrame()

    # Fetch and display data when button is clicked
    if st.sidebar.button("Fetch Intraday Data"):
        if ticker.strip() == "":
            st.sidebar.error("Please enter a valid stock ticker symbol.")
        else:
            with st.spinner(f"Fetching intraday data for {ticker} with {interval} interval..."):
                intraday_data = fetch_intraday_data(ticker, interval, start_date, end_date)
            if not intraday_data.empty:
                st.subheader(f"Intraday Data for {ticker} ({interval} Interval)")
                st.dataframe(intraday_data)  # Show all data
            else:
                st.warning("No intraday data available to display.")
