import streamlit as st

# Set Streamlit page configuration
st.set_page_config(
    page_title="TradeWisely",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Day Trading"])

# Home Page
if page == "Home":
    st.title("Welcome to TradeWisely")
    st.write("Analyze stock data and make informed decisions.")
    st.write("Use the sidebar to navigate to different tools, like Day Trading.")

# Day Trading Page
elif page == "Day Trading":
    st.experimental_set_query_params(page="daytrading")  # Optional for bookmarking
    # Import the logic from daytrading.py dynamically
    try:
        from pages import daytrading
        daytrading.run()  # Run the function in daytrading.py
    except ImportError:
        st.error("Error: 'daytrading.py' is missing or not in the 'pages/' directory.")
