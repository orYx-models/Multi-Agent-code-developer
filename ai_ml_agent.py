import pandas as pd
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from textblob import TextBlob

def run_aiml_models_on_file(csv_path):
    df = pd.read_csv(csv_path)

    # Normalize text
    df['review_text'] = df['review_text'].fillna("").astype(str)

    # Sentiment
    df["sentiment"] = df["review_text"].apply(lambda x: TextBlob(x).sentiment.polarity)

    # Keywords via TF-IDF
    tfidf = TfidfVectorizer(max_features=100)
    tfidf_matrix = tfidf.fit_transform(df["review_text"])
    keywords = tfidf.get_feature_names_out()
    df["top_keyword"] = [keywords[i.argmax()] if i.nnz else "" for i in tfidf_matrix]

    # Clustering
    km = KMeans(n_clusters=4, random_state=42)
    df["cluster"] = km.fit_predict(tfidf_matrix)
    score = silhouette_score(tfidf_matrix, df["cluster"])
    print(f"[AL agent] Clustering done. Silhouette Score: {score}")

    # Save output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"ai_ml_output_{timestamp}.csv"
    df.to_csv(output_path, index=False)
    print(f"[AL agent] Output written to: {output_path}")
    return output_path
