"""
Avalanche — Customer Sentiment Insights (Streamlit)

Clean first-frame render for Streamlit Cloud thumbnail + small UI polish.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Optional, Tuple


# ---------- page config ----------
st.set_page_config(
    page_title="Avalanche — Sentiment Insights",
    page_icon="❄️",
    layout="wide",
)


# ---------- banner for profile card (render on first load) ----------
base_dir = Path(__file__).parent
banner_path = base_dir / "images" / "app_screenshot.png"

if "show_banner" not in st.session_state:
    st.session_state.show_banner = True

banner_slot = st.empty()
if st.session_state.show_banner:
    if banner_path.exists():
        # Centered, slim preview for a clean first frame
        with banner_slot.container():
            _c1, _c2, _c3 = st.columns([1, 2, 1])
            _c2.image(str(banner_path), width=840)
    else:
        banner_slot.info("Avalanche — load data to begin.")


# ---------- styles ----------
st.markdown(
    """
    <style>
      .block-container { padding-top: 0.75rem; }
      .stImage img { border-radius: 8px; }
      .stButton>button { height: 40px; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- header ----------
st.title("Avalanche, Inc.")
st.subheader("Customer Sentiment Insights")
st.caption("Instantly gauge how customers feel about your products.")


# ---------- session state ----------
ss = st.session_state
ss.setdefault("df_loaded", False)
ss.setdefault("clean_done", False)
ss.setdefault("df_raw", None)
ss.setdefault("df_clean", None)
ss.setdefault("meta", None)


# ---------- helpers ----------
def try_load_local_csv() -> Optional[pd.DataFrame]:
    candidates = [base_dir / "customer_reviews.csv", base_dir / "data" / "customer_reviews.csv"]
    for p in candidates:
        if p.exists():
            return pd.read_csv(p)
    return None


def tiny_builtin_sample() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "PRODUCT": "Alpine Base Layer",
                "DATE": "2023-11-08",
                "SUMMARY": "The received base layer has inconsistent sizing, with a tighter fit in the shoulders and a looser fit around the waist.",
            },
            {
                "PRODUCT": "Summit Shell Jacket",
                "DATE": "2024-01-12",
                "SUMMARY": "Great wind resistance and overall construction; zipper feels a bit flimsy.",
            },
            {
                "PRODUCT": "Glacier Socks",
                "DATE": "2024-03-01",
                "SUMMARY": "Developed holes in two weeks of light use. Disappointed.",
            },
            {
                "PRODUCT": "Avalanche Beanie",
                "DATE": "2024-03-11",
                "SUMMARY": "Love the color and stretch. Keeps ears warm in windy weather.",
            },
        ]
    )


def normalize_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, str, str]:
    cols = {c.lower(): c for c in df.columns}
    product_candidates = ["product", "item", "sku", "product_name", "productid", "product_id"]
    text_candidates = ["summary", "review", "text", "comment", "feedback", "body", "content"]
    product_col = next((cols[c] for c in product_candidates if c in cols), df.columns[0])
    text_col = next((cols[c] for c in text_candidates if c in cols), df.columns[min(1, len(df.columns) - 1)])
    df[product_col] = df[product_col].astype(str)
    df[text_col] = df[text_col].astype(str)
    return df, product_col, text_col


def clean_dataframe(df: pd.DataFrame, text_col: str) -> pd.DataFrame:
    d = df.copy()
    d[text_col] = d[text_col].astype(str).str.strip()
    d = d[d[text_col].str.len() > 0]
    d[text_col] = d[text_col].str.slice(0, 2000)
    return d


def add_quick_sentiment(df: pd.DataFrame, text_col: str) -> pd.DataFrame:
    pos_words = r"(great|best|love|comfortable|happy|warm|perfect|well|excellent|amazing|fast)"
    neg_words = r"(tight|shrink|flimsy|holes|returned|disappointed|inconsistent|bad|slow|poor)"
    d = df.copy()
    d["SENTIMENT_SCORE"] = (
        d[text_col].str.lower().str.count(pos_words) * 0.2
        - d[text_col].str.lower().str.count(neg_words) * 0.2
        + 0.5
    ).clip(0, 1)
    return d


# ---------- actions ----------
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("📂 Load Sample Data"):
        ss.show_banner = False
        banner_slot.empty()

        df0 = try_load_local_csv()
        if df0 is None:
            st.info("`customer_reviews.csv` not found. Loading a small built-in sample.")
            df0 = tiny_builtin_sample()

        df0, product_col, text_col = normalize_columns(df0)
        ss.meta = {"product_col": product_col, "text_col": text_col}
        ss.df_raw = df0
        ss.df_loaded = True
        ss.clean_done = False  # reset cleaned view

with col2:
    if st.button("✨ Clean & Generate Sentiment", disabled=not ss.df_loaded):
        ss.show_banner = False
        banner_slot.empty()

        dfc = clean_dataframe(ss.df_raw.copy(), ss.meta["text_col"])
        dfc = add_quick_sentiment(dfc, ss.meta["text_col"])
        ss.df_clean = dfc
        ss.clean_done = True

st.caption(
    "Tip: ‘Load Sample Data’ shows the raw file. ‘Clean & Generate Sentiment’ prepares text and computes a quick score."
)

# ---------- sidebar about ----------
with st.sidebar:
    st.header("About")
    st.write(
        "Explore Avalanche customer review sentiment. Load a CSV, clean text, and see product‑level sentiment using a quick heuristic (no API key)."
    )
    st.markdown("[Open on Streamlit Cloud](https://avalanche-lab.streamlit.app/)")


# ---------- view logic (single section at a time) ----------
if ss.clean_done and ss.df_clean is not None:
    # CLEANED VIEW ONLY
    product_col = ss.meta["product_col"]
    text_col = ss.meta["text_col"]
    st.subheader("Sentiment Score by Product (cleaned data)")

    products = sorted(ss.df_clean[product_col].dropna().astype(str).unique().tolist())
    choice = st.selectbox("Choose a product", ["All Products"] + products)
    view = ss.df_clean if choice == "All Products" else ss.df_clean[ss.df_clean[product_col].astype(str) == choice]

    grouped = ss.df_clean.groupby(product_col, dropna=True)["SENTIMENT_SCORE"].mean().sort_values(ascending=False)
    st.bar_chart(grouped, width="stretch")

    st.dataframe(view, width="stretch", height=360)

elif ss.df_loaded and ss.df_raw is not None:
    # RAW VIEW ONLY
    product_col = ss.meta["product_col"]
    text_col = ss.meta["text_col"]
    st.subheader("Raw Data Preview")
    st.write(f"Detected Product: `{product_col}` — Text: `{text_col}`")

    products = sorted(ss.df_raw[product_col].dropna().astype(str).unique().tolist())
    choice = st.selectbox("Choose a product", ["All Products"] + products)
    view = ss.df_raw if choice == "All Products" else ss.df_raw[ss.df_raw[product_col].astype(str) == choice]

    st.write(f"Rows in selection: **{len(view):,}**")
    st.dataframe(view.head(25), width="stretch")

else:
    st.info("Click ‘Load Sample Data’ to get started.")

