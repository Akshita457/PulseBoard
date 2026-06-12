from nltk.sentiment.vader import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(headline):
    scores = analyzer.polarity_scores(headline)
    compound = scores["compound"]

    if compound >= 0.05:
        label = "Positive"
    elif compound <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"

    return compound, label

if __name__ == "__main__":
    test_headlines = [
        "Tesla stock surges to all time high",
        "Company faces massive fraud allegations",
        "Markets remain stable today"
    ]

    for headline in test_headlines:
        score, label = analyze_sentiment(headline)
        print(f"{label} ({score:.2f}) — {headline}")