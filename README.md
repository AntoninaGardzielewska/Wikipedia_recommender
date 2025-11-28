# Wikipedia & Fandom Article Recommender
Wikipedia & Fandom Article Recommender System

A content-based recommendation system that suggests new Wikipedia and Fandom articles based on a user’s reading history. The system combines TF-IDF, sentence embeddings, and a hybrid similarity score to return accurate and diverse recommendations.

## Data Collection

* Collected 2000 articles (1000 Wikipedia + 1000 Fandom) using a custom Scrapy spider.
* The spider:
    * Validates article URLs
    * Extracts clean text
    * Removes short/non-content pages
    * Uses random fallback pages when needed
    * Saves data to CSV (wiki.csv, fandom.csv)

## Text Preprocessing

* Text preprocessing ensures consistency before vectorization.
* Steps include:
    * Lowercasing
    * Stopword removal
    * Removing non-alphabetic tokens
    * Lemmatization
    * Used for TF-IDF representation.
    * Embeddings are computed from raw text, as transformer models handle noise effectively.

## Handling User Input

* If the user provides too many URLs:
    * Articles are scraped and preprocessed
    * Embeddings are computed
    * K-Means clustering (k = 20) selects the most diverse article subset
    * Only unseen articles are considered for recommendations

## Feature Representation

We use two complementary vector representations.
* TF-IDF (lexical similarity)
    * Implements TfidfVectorizer
    * Highlights distinctive vocabulary

* Sentence Embeddings (semantic similarity)
    * Uses all-MiniLM-L6-v2 (SentenceTransformer)
    * Captures meaning beyond specific words

* Hybrid Score

` final_score = 0.4 * tfidf_similarity + 0.6 * embedding_similarity `

## Recommendation Algorithm

Given a user’s reading history:

* Filter out all articles the user has already seen
* Preprocess text in the same way as the dataset
* Compute TF-IDF and embedding similarities
* Apply hybrid similarity scoring
* Return:
    * All articles above a minimum score threshold (e.g., 0.9), or
    * If none exceed the threshold → top 10 most similar articles