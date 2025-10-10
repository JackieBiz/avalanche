# import packages
import streamlit as st
import pandas as pd
import re
import os
from pathlib import Path

st.set_page_config(page_title="Avalanche — Sentiment Insights", page_icon="📈", layout="wide")

# CSV lives next to this file (works locally & on Streamlit Cloud)
DATA_PATH = Path(__file__).parent / "customer_reviews.csv"

# Helper function to clean text
def clean_text(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)
    return text

st.title("Avalanche, Inc.")
st.subheader("Customer Sentiment Insights")
st.caption("Instantly gauge how customers feel about your products.")


# Layout two buttons side by side
col1, col2 = st.columns(2)

with col1:
    if st.button("📥 Load Sample Data"):
        try:
            st.session_state["df"] = pd.read_csv(DATA_PATH)
            st.success("Dataset loaded successfully!")
        except FileNotFoundError:
            st.error("Dataset not found. Please check the file path.")

with col2:
    if st.button("🧹 Clean & Prep Data"):
        if "df" in st.session_state:
            st.session_state["df"]["CLEANED_SUMMARY"] = st.session_state["df"]["SUMMARY"].apply(
                clean_text)
            st.success("Reviews parsed and cleaned!")
        else:
            st.warning("Please ingest the dataset first.")

# Display the dataset if it exists
if "df" in st.session_state:
    # Product filter dropdown
    st.subheader("🔍 Filter by Product")
    product = st.selectbox("Choose a product", [
                           "All Products"] + list(st.session_state["df"]["PRODUCT"].unique()))
    st.subheader(f"📁 Reviews for {product}")

    if product != "All Products":
        filtered_df = st.session_state["df"][st.session_state["df"]
                                             ["PRODUCT"] == product]
    else:
        filtered_df = st.session_state["df"]
    st.dataframe(filtered_df)

    st.subheader("Sentiment Score by Product")
    grouped = st.session_state["df"].groupby(
        ["PRODUCT"])["SENTIMENT_SCORE"].mean()
    st.bar_chart(grouped)





