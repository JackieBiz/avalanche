# import packages
import streamlit as st
import pandas as pd
import re
import os
from pathlib import Path

st.set_page_config(page_title="Avalanche — Sentiment Insights", page_icon="📈")

# Responsive spacing + heading sizes
st.markdown(
    """
    <style>
      /* pull content up a bit */
      .block-container { padding-top: 0.75rem; }

      /* smaller top/bottom margins on headings */
      h1 { margin-top: 0.25rem; margin-bottom: 0.5rem; }
      h2 { margin-top: 0.25rem; margin-bottom: 0.5rem; }

      /* responsive heading sizes so they don't look cut off on laptops */
      h1 { font-size: clamp(1.75rem, 4vw + 0.25rem, 3rem); }
      h2 { font-size: clamp(1.25rem, 2.6vw + 0.25rem, 2rem); }

      /* keep some side padding on narrower screens */
      @media (max-width: 1200px) {
        .block-container { padding-left: 1rem; padding-right: 1rem; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- above-the-fold content ---
st.title("Avalanche, Inc.")
st.subheader("Customer Sentiment Insights")
st.caption("Instantly gauge how customers feel about your products.")

# --- polish: rounded corners for images (applies to all st.image) ---
st.markdown(
    """
    <style>
      .stImage img { border-radius: 8px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Centered header image (desktop centered, mobile full-width)
hero_img = Path(__file__).parent / "images" / "app_screenshot.png"
left, mid, right = st.columns([1, 8, 1])  # wide center column
with mid:
    if hero_img.exists():
        st.image(str(hero_img), width=900, caption="App overview")  # Streamlit scales down on mobile

# CSV lives next to this file (works locally & on Streamlit Cloud)
DATA_PATH = Path(__file__).parent / "customer_reviews.csv"

# Helper function to clean text
def clean_text(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)
    return text

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














