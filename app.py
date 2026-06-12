import streamlit as st
import plotly.express as px
import pandas as pd
import sqlite3
from config import DB_PATH
from db import setup_database
from fetcher import fetch_news
from sentiment import analyze_sentiment

setup_database()

def get_connection():
    return sqlite3.connect(DB_PATH)

def save_articles(articles):
    conn = get_connection()
    cursor = conn.cursor()
    saved = 0
    for article in articles:
        score, label = analyze_sentiment(article["headline"])
        cursor.execute("""
            INSERT OR IGNORE INTO articles 
            (topic, headline, source, published_at, sentiment_score, sentiment_label)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            article["topic"],
            article["headline"],
            article["source"],
            article["published_at"],
            score,
            label
        ))
        saved += 1
    conn.commit()

    cursor.execute("""
        INSERT INTO search_history (topic, articles_fetched)
        VALUES (?, ?)
    """, (articles[0]["topic"], saved))
    conn.commit()
    conn.close()
    return saved

def get_articles(topic):
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT headline, source, published_at, sentiment_score, sentiment_label
        FROM articles
        WHERE topic LIKE ?
        ORDER BY published_at DESC
    """, conn, params=[f"%{topic}%"])
    conn.close()
    return df

# --- UI ---
st.title("📰 PulseBoard")

topic = st.text_input("Enter a company or topic", placeholder="e.g. Tesla, Bitcoin, Infosys")

if st.button("Fetch Latest News"):
    if topic.strip() == "":
        st.warning("Please enter a topic.")
    else:
        with st.spinner("Fetching..."):
            articles = fetch_news(topic)
            if articles:
                saved = save_articles(articles)
                st.success(f"Done! Fetched {len(articles)} articles, {saved} new ones saved.")
            else:
                st.error("No articles found or API error.")

if topic.strip() != "":
    df = get_articles(topic)

    if df.empty:
        st.info("No data yet for this topic. Hit Fetch first!")
    else:
        count = len(df)
        if count >= 15:
            st.markdown("This is a **hot topic** 🔥 — the internet can't stop talking about it.")
        elif count >= 6:
            st.markdown("This is a **decent topic** 📰 — people are talking, but it's not breaking the internet.")
        else:
            st.markdown("This is a **quiet topic** 🦗 — barely anyone's covering this one.")

        st.subheader("Sentiment Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Positive", len(df[df["sentiment_label"] == "Positive"]))
        col2.metric("Negative", len(df[df["sentiment_label"] == "Negative"]))
        col3.metric("Neutral", len(df[df["sentiment_label"] == "Neutral"]))

        st.subheader("Headlines")
        st.dataframe(df, use_container_width=True)
