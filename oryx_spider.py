import os
import requests
import pandas as pd
from datetime import datetime
from google_play_scraper import reviews as gp_reviews
import xml.etree.ElementTree as ET

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_apple_reviews(app_id, country='us', max_reviews=100):
    reviews = []
    page = 1
    while len(reviews) < max_reviews:
        url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/xml"
        print(f"[SPIDER] Fetching Apple RSS page {page} → {url}")
        response = requests.get(url)
        if response.status_code != 200:
            print(f"[SPIDER] ❌ Error fetching Apple page {page}")
            break

        root = ET.fromstring(response.content)
        entries = root.findall(".//{http://www.w3.org/2005/Atom}entry")

        # First entry is usually app metadata, skip it
        if page == 1 and entries:
            entries = entries[1:]

        if not entries:
            print(f"[SPIDER] ❌ No more reviews or error at page {page}.")
            break

        for entry in entries:
            author = entry.find("{http://www.w3.org/2005/Atom}author")
            name = author.find("{http://www.w3.org/2005/Atom}name").text if author is not None else ""
            title = entry.find("{http://www.w3.org/2005/Atom}title").text
            content = entry.find("{http://www.w3.org/2005/Atom}content").text
            rating = entry.find("{http://itunes.apple.com/rss}rating")
            reviews.append({
                "source": "Apple",
                "author": name,
                "title": title,
                "review_text": content,
                "rating": int(rating.text) if rating is not None else None
            })

        if len(entries) < 50:
            break
        page += 1

    return reviews[:max_reviews]

def fetch_google_reviews(package_name, lang='en', country='us', max_reviews=100):
    result, _ = gp_reviews(
        package_name,
        lang=lang,
        country=country,
        count=max_reviews,
        filter_score_with=None
    )

    reviews = []
    for r in result:
        reviews.append({
            "source": "Google",
            "author": r['userName'],
            "title": "",
            "review_text": r['content'],
            "rating": r['score']
        })
    return reviews

def run_spider_on_bank(bank_name, apple_id, google_package, apple_country='us', google_country='us', google_lang='en', max_reviews=100):
    print(f"\n[SPIDER] 🚀 Starting review scraping for: {bank_name}")

    print(f"[SPIDER] 🛒 Scraping Apple App Store reviews for App ID: {apple_id} (Country: {apple_country})")
    apple_reviews = fetch_apple_reviews(apple_id, country=apple_country, max_reviews=max_reviews)
    print(f"[SPIDER] ✅ Collected {len(apple_reviews)} reviews from Apple")

    print(f"[SPIDER] 🤖 Scraping Google Play reviews for Package: {google_package} (Lang: {google_lang}, Country: {google_country})")
    google_reviews = fetch_google_reviews(google_package, lang=google_lang, country=google_country, max_reviews=max_reviews)
    print(f"[SPIDER] ✅ Collected {len(google_reviews)} reviews from Google Play")

    # Normalize and convert to DataFrame
    def safe_reviews_to_df(reviews):
        df = pd.DataFrame(reviews)
        if 'review_text' not in df.columns:
            df['review_text'] = ''
        df['review_text'] = df['review_text'].fillna("").astype(str)
        return df

    apple_df = safe_reviews_to_df(apple_reviews)
    google_df = safe_reviews_to_df(google_reviews)

    # Add bank name
    apple_df['bank'] = bank_name
    google_df['bank'] = bank_name

    combined_df = pd.concat([apple_df, google_df], ignore_index=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{bank_name.lower().replace(' ', '_')}_reviews_{timestamp}.csv"
    filepath = os.path.join(OUTPUT_DIR, filename)
    combined_df.to_csv(filepath, index=False)

    print(f"\n[SPIDER] 📦 Saved {len(combined_df)} reviews to {filepath}")
    return filepath, combined_df
