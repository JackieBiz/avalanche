# import packages
import streamlit as st
import pandas as pd
import re
from pathlib import Path

# ---------- page config ----------
st.set_page_config(page_title="Avalanche — Sentiment Insights", page_icon="📈")

# ---------- responsive spacing & style ----------
st.markdown(
    """
    <style>
      .block-container { padding-top: 0.75rem; }
      h1 { margin-top: 0.25rem; margin-bottom: 0.5rem; font-size: clamp(1.75rem, 4vw + 0.25rem, 3rem); }
      h2 { margin-top: 0.25rem; margin-bottom: 0.5rem; font-size: clamp(1.25rem, 2.6vw + 0.25rem, 2rem); }
      @media (max-width: 1200px) { .block-container { padding-left: 1rem; padding-right: 1rem; } }
      .stImage img { border-radius: 8px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- header ----------
st.title("Avalanche, Inc.")
st.subheader("Customer Sentiment Insights")
st.caption("Instantly gauge how customers feel about your products.")

# CSV lives next to this file (works locally & on Streamlit Cloud)
DATA_PATH = Path(__file__).parent / "customer_reviews.csv"

# ---------- helpers ----------
def clean_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    return text

# ---------- CTAs (keep above the fold) ----------
col1, col2 = st.columns(2)
with col1:
    load_clicked = st.button("📥 Load Sample Data")
with col2:
    clean_clicked = st.button("🧹 Clean & Prep Data", disabled=("df" not in st.session_state))

# ---------- hero image (hidden after data load) ----------
hero_ph = st.empty()
with hero_ph.container():
    hero_img = Path(__file__).parent / "images" / "app_screenshot.png"
    left, mid, right = st.columns([1, 8, 1])
    with mid:
        if hero_img.exists():
            st.image(str(hero_img), use_container_width=True, caption="App overview")

# ---------- button actions ----------
if load_clicked:
    try:
        st.session_state["df"] = pd.read_csv(DATA_PATH)
        hero_ph.empty()  # hide the hero after data is loaded
        st.success(f"Dataset loaded from: {DATA_PATH.name}")
    except FileNotFoundError:
        st.error(f"Dataset not found at: {DATA_PATH}")

if clean_clicked and "df" in st.session_state:
    st.session_state["df"]["CLEANED_SUMMARY"] = st.session_state["df"]["SUMMARY"].apply(clean_text)
    st.success("Data cleaned. You can filter and explore below.")

# ---------- main content ----------
if "df" in st.session_state:
    df = st.session_state["df"]

    st.subheader("🔍 Filter by Product")
    products = sorted(df["PRODUCT"].dropna().unique().tolist())
    product = st.selectbox("Choose a product", ["All Products"] + products)

    st.subheader(f"📁 Reviews for {product}")
    filtered = df if product == "All Products" else df[df["PRODUCT"] == product]
    st.dataframe(filtered, use_container_width=True)

    st.subheader("📊 Sentiment Score by Product")
    grouped = df.groupby("PRODUCT", dropna=True)["SENTIMENT_SCORE"].mean().sort_values(ascending=False)
    st.bar_chart(grouped)
else:
    st.info("Click **📥 Load Sample Data** to get started.")
