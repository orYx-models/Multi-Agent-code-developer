# streamlit_dashboard.py
import os
import math
import pandas as pd
import streamlit as st
import altair as alt
from PIL import Image
import base64
from io import BytesIO
from sklearn.feature_extraction.text import CountVectorizer

# ---------- Helpers ----------
def _first_present(d: pd.DataFrame, candidates):
    for c in candidates:
        if c in d.columns:
            return c
    return None

def logo_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def _prep(df: pd.DataFrame):
    bank_col     = _first_present(df, ["bank_name", "bank", "bankName"])
    text_col     = _first_present(df, ["review_text", "review", "content"])
    sent_col     = _first_present(df, ["sentiment", "sentiment_score"])
    cluster_col  = _first_present(df, ["cluster", "cluster_id"])
    keyword_col  = _first_present(df, ["top_keyword", "keywords", "review_keywords"])
    rating_col   = _first_present(df, ["rating", "score"])
    src_col      = _first_present(df, ["source", "store", "platform"])

    if bank_col is None:
        df["bank_name"] = "Unknown Bank"
        bank_col = "bank_name"
    if text_col is None:
        df["review_text"] = ""
        text_col = "review_text"
    if sent_col is None:
        df["sentiment"] = 0.0
        sent_col = "sentiment"
    if cluster_col is None:
        df["cluster"] = -1
        cluster_col = "cluster"
    if keyword_col is None:
        df["top_keyword"] = ""
        keyword_col = "top_keyword"
    if rating_col is None:
        df["rating"] = None
        rating_col = "rating"
    if src_col is None:
        df["source"] = ""
        src_col = "source"

    df[sent_col] = pd.to_numeric(df[sent_col], errors="coerce").fillna(0.0)
    df[rating_col] = pd.to_numeric(df[rating_col], errors="coerce")
    df["polarity"] = pd.cut(
        df[sent_col],
        bins=[-math.inf, -0.1, 0.1, math.inf],
        labels=["Negative", "Neutral", "Positive"]
    )

    return df, bank_col, text_col, sent_col, cluster_col, keyword_col, rating_col, src_col

def _kpi(label: str, value, help_text: str = ""):
    st.markdown(
        f"""
        <div style="padding:12px;border:1px solid rgba(255,255,255,.1);border-radius:8px;background:rgba(255,255,255,.03)">
            <div style="font-size:12px;opacity:.7">{label}</div>
            <div style="font-size:28px;font-weight:700;line-height:1.1">{value}</div>
            {'<div style="font-size:11px;opacity:.6">'+help_text+'</div>' if help_text else ''}
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------- Main Dashboard ----------
def generate_dashboard(csv_path: str):
    st.set_page_config(page_title="Oryx Bank App Sentiment Dashboard", layout="wide")

    if os.path.exists("logo.png"):
        logo = Image.open("logo.png")
        logo_b64 = logo_to_base64(logo)
        st.markdown(f"""
        <div style='display:flex;align-items:center;margin-bottom:1rem;'>
            <img src='data:image/png;base64,{logo_b64}' style='height:60px;margin-right:12px;'/>
            <div>
                <h1 style='margin:0;font-size:36px;'>Oryx Mobile Banking App Customer Satisfaction</h1>
                <div style='font-size:15px;color:#ccc;margin-top:4px'>
                    What is the current status of customer satisfaction for Omani banking apps,<br>
                    and how can we improve utility in comparison to peers?
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.title("Oryx Mobile Banking App Customer Satisfaction")

    if not os.path.exists(csv_path):
        st.error(f"CSV not found: {csv_path}")
        return

    raw_df = pd.read_csv(csv_path)
    if raw_df.empty:
        st.warning("The dataset is empty. Try scraping more reviews.")
        return

    df, bank_col, text_col, sent_col, cluster_col, keyword_col, rating_col, src_col = _prep(raw_df)

    # --- Filters: No default selection ---
    st.markdown("### 🔧 Filter Options")
    col1, col2, col3 = st.columns([3, 3, 2])

    all_banks = sorted(df[bank_col].dropna().unique())
    all_sources = sorted(df[src_col].dropna().unique())
    rating_min, rating_max = 1, 5

    with col1:
        selected_banks = st.multiselect("Banks", options=all_banks, default=[])
    with col2:
        selected_sources = st.multiselect("Sources", options=all_sources, default=[])
    with col3:
        if df[rating_col].notna().any():
            rating_range = st.slider("Rating range", min_value=1, max_value=5, value=(rating_min, rating_max))
        else:
            rating_range = (1, 5)

    # --- Load Data Button Logic ---
    if "load_triggered" not in st.session_state:
        st.session_state["load_triggered"] = False

    if st.button("Load Data"):
        st.session_state["load_triggered"] = True

    if not selected_banks or not selected_sources:
        st.warning("Please select at least one Bank and one Source to load data.")
        return

    fdf = df[
        df[bank_col].isin(selected_banks) &
        df[src_col].isin(selected_sources) &
        df[rating_col].between(rating_range[0], rating_range[1])
    ]

    if not st.session_state["load_triggered"]:
        st.info("Please click the 'Load Data' button to generate the dashboard.")
        return

    if fdf.empty:
        st.info("No data matches your filters. Try adjusting the selections.")
        return

    # --- KPI Cards (1 Row, Same Size) ---
    def _kpi(label: str, value, help_text: str = ""):
        st.markdown(
            f"""
            <div style="height:110px;padding:12px;border:1px solid rgba(255,255,255,0.1);border-radius:8px;background:rgba(255,255,255,0.03);display:flex;flex-direction:column;justify-content:space-between;">
                <div style="font-size:12px;opacity:0.7">{label}</div>
                <div style="font-size:28px;font-weight:700;line-height:1.1">{value}</div>
                {'<div style="font-size:11px;opacity:0.6;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'+help_text+'</div>' if help_text else ''}
            </div>
            """,
            unsafe_allow_html=True
        )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        _kpi("Total Reviews", f"{len(fdf):,}", help_text="Based on selected filters")
    with col2:
        _kpi("Average Sentiment", f"{fdf[sent_col].mean():.3f}")
    with col3:
        _kpi("% Positive", f"{(fdf['polarity'] == 'Positive').mean() * 100:.1f}%")
    with col4:
        _kpi("% Negative", f"{(fdf['polarity'] == 'Negative').mean() * 100:.1f}%")


    # --- Charts ---
    left, right = st.columns(2)

    with left:
        st.subheader("Average Sentiment by Bank")
        avg_by_bank = fdf.groupby(bank_col)[sent_col].mean().reset_index(name="avg_sentiment")
        
        chart = alt.Chart(avg_by_bank).mark_bar().encode(
            x=alt.X("avg_sentiment:Q", title="Avg Sentiment"),
            y=alt.Y(f"{bank_col}:N", title="Bank", sort='-x'),
            tooltip=[bank_col, alt.Tooltip("avg_sentiment", title="Avg Sentiment", format=".3f")]
        ).properties(height=320)
        
        st.altair_chart(chart, use_container_width=True)


    with right:
        st.subheader("Review Count: Positive vs Negative")
        counts = fdf[fdf["polarity"].isin(["Positive", "Negative"])]
        data = counts.groupby([bank_col, "polarity"]).size().reset_index(name="count")
        chart = alt.Chart(data).mark_bar().encode(
            x=alt.X(f"{bank_col}:N", title="Bank", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("count:Q", title="Review Count"),
            color=alt.Color("polarity:N", scale=alt.Scale(domain=["Positive", "Negative"], range=["#90ee90", "#ff9999"])),
            tooltip=[bank_col, "polarity", "count"]
        ).properties(height=320)
        st.altair_chart(chart, use_container_width=True)

    # --- Top Bigrams + Cluster Distribution ---
    t1, t2 = st.columns(2)
    with t1:
        st.subheader("Top Bigrams")
        vectorizer = CountVectorizer(ngram_range=(2, 2), stop_words='english', max_features=20)
        bigrams = vectorizer.fit_transform(fdf[text_col].dropna().astype(str))
        sum_words = bigrams.sum(axis=0)
        words_freq = [(word, sum_words[0, idx]) for word, idx in vectorizer.vocabulary_.items()]
        kw_df = pd.DataFrame(words_freq, columns=['Bigram', 'Count']).sort_values(by="Count", ascending=False)
        st.dataframe(kw_df.reset_index(drop=True), use_container_width=True)

    with t2:
        st.subheader("Cluster Distribution by Bank")
        cluster_labels = {
            0: "Neutral / Arabic Feedback",
            1: "Negative / Technical Issues",
            2: "Positive Feedback",
            3: "Highly Positive / Praise"
        }
        fdf[cluster_col] = fdf[cluster_col].astype(int)
        fdf["cluster"] = fdf[cluster_col].map(cluster_labels)
        clus = fdf.groupby([bank_col, "cluster"]).size().reset_index(name="count")
        chart = alt.Chart(clus).mark_bar().encode(
            x=alt.X(f"{bank_col}:N", title="Bank", axis=alt.Axis(labelAngle=0)),
            y="count:Q",
            color="cluster:N",
            tooltip=[bank_col, "cluster", "count"]
        ).properties(height=320)
        st.altair_chart(chart, use_container_width=True)

    # --- Review Table ---
    st.markdown("---")
    st.subheader("Review Samples")
    cols = [bank_col, src_col, rating_col, sent_col, keyword_col, text_col, cluster_col]
    preview = fdf[cols].rename(columns={
        bank_col: "Bank",
        src_col: "Source",
        rating_col: "Rating",
        sent_col: "Sentiment",
        keyword_col: "Keywords",
        text_col: "Review Text",
        cluster_col: "Cluster"
    })
    st.dataframe(preview.head(200), use_container_width=True)

# Entry point
if __name__ == "__main__":
    generate_dashboard("ai_ml_output_20250818_143840.csv")
