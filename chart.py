import streamlit as st
import plotly.graph_objects as go

def chart_tab():
    st.header("📊 Stock Candlestick Chart")

    # Check if stock_data is available in session_state
    if "stock_data" not in st.session_state:
        st.warning("No data available. Please go to the Analyze Data tab and fetch stock data.")
        return

    stock_data = st.session_state["stock_data"]

    # Ensure myPrice exists in stock_data
    if "myPrice" not in stock_data.columns or stock_data["myPrice"].isna().all():
        st.warning("myPrice is not available in the data. Please ensure it is calculated in the Analyze Data tab.")
        return

    # Prepare candlestick data
    stock_data["Open"] = stock_data["myPrice"].shift(1)
    stock_data["Close"] = stock_data["myPrice"]
    stock_data["High"] = stock_data[["Open", "Close"]].max(axis=1)
    stock_data["Low"] = stock_data[["Open", "Close"]].min(axis=1)

    # Drop rows with NaN values after shift
    candlestick_data = stock_data.dropna(subset=["Open", "High", "Low", "Close"])

    # Debugging display
    st.write("### Debug: Candlestick Data Preview", candlestick_data[["Date", "Open", "High", "Low", "Close"]].head())

    # Create candlestick plot using Plotly
    fig_candlestick = go.Figure()

    fig_candlestick.add_trace(
        go.Candlestick(
            x=candlestick_data["Date"],
            open=candlestick_data["Open"],
            high=candlestick_data["High"],
            low=candlestick_data["Low"],
            close=candlestick_data["Close"],
            increasing_line_color="green",
            decreasing_line_color="red",
            name="myPrice Candlestick"
        )
    )

    fig_candlestick.update_layout(
        title="Candlestick Chart for myPrice",
        xaxis_title="Date",
        yaxis_title="myPrice",
        xaxis_rangeslider_visible=False,
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    # Display the candlestick plot
    st.plotly_chart(fig_candlestick, use_container_width=True)
