import json
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from services.severity import enrich_results_with_severity  # import the severity helper

# Load dataset
data_path = os.path.join(os.path.dirname(__file__), "../data/attackbench.json")
with open(data_path, "r") as f:
    dataset = json.load(f)

# Convert to DataFrame for easy search
df = pd.DataFrame(dataset)

# Optional: combine title + details for richer search
df['text'] = df['title'] + " " + df['details']

# Prepare TF-IDF retriever
vectorizer = TfidfVectorizer(stop_words="english")
X = vectorizer.fit_transform(df["text"])  # use the combined 'text' column

def search(query, top_k=5):
    """
    Returns top_k search results for the query from AttackBench dataset,
    enriched with severity based on impact.
    """
    query_vec = vectorizer.transform([query])
    sims = cosine_similarity(query_vec, X).flatten()
    top_indices = sims.argsort()[::-1][:top_k]
    results = df.iloc[top_indices].to_dict(orient="records")

    # Enrich results with severity
    results = enrich_results_with_severity(results)
    return results
