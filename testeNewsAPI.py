import requests
from datetime import datetime, timezone

API_KEY = '9442fe2ecbeb48f48fc7c7d196937dec'
url = f'https://newsapi.org/v2/everything?q=games&language=pt&sortBy=publishedAt&apiKey={API_KEY}'

response = requests.get(url)
news_data = response.json()

def time_since_published(published_at):
    published_time = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ')
    published_time = published_time.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    diff = now - published_time

    days = diff.days
    seconds = diff.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if days > 0:
        return f"{days} dias atrás"
    elif hours > 0:
        return f"{hours} horas atrás"
    elif minutes > 0:
        return f"{minutes} minutos atrás"
    else:
        return "agora mesmo"

for article in news_data['articles']:
    title = article['title']
    description = article['description']
    url = article['url']
    published_at = article['publishedAt']
    time_ago = time_since_published(published_at)

    print(f"Título: {title}")
    print(f"Descriçãp: {description}")
    print(f"URL: {url}")
    print(f"Publicado: {time_ago}")
    print()
