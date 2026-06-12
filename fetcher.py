import requests
from config import NEWS_API_KEY

def fetch_news(topic):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": topic,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 6,
        "apiKey": NEWS_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data["status"] != "ok":
        print("Error fetching news:", data.get("message"))
        return []

    articles = []
    for item in data["articles"]:
        articles.append({
            "topic": topic,
            "headline": item["title"],
            "source": item["source"]["name"],
            "published_at": item["publishedAt"]
        })

    return articles