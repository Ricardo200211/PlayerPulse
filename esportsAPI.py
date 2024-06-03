import requests
from datetime import datetime
import locale

arr_maches = []
API_TOKEN = 'E9Arj0VU0akb2QRGbQAAAVmXh9B_x85OlvwEs9uaAx2gECtuUM0'
headers = {
    'Authorization': f'Bearer {API_TOKEN}'
}

# Configurar o locale para português
locale.setlocale(locale.LC_TIME, 'pt_PT.UTF-8')

def get_upcoming_matches(limit=10):
    url = f'https://api.pandascore.co/matches/upcoming?per_page={limit}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao obter partidas: {response.status_code}, {response.text}")
        return None

def format_datetime(datetime_str):
    dt = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%SZ")
    return dt.strftime("%d de %B de %Y, %H:%M UTC")

def get_maches():
    matches = get_upcoming_matches()
    if matches:
        for match in matches:
            try:
                game = match['videogame']['name']
                team1 = match['opponents'][0]['opponent']['name']
                img_team1 = match['opponents'][0]['opponent']['image_url']
                team2 = match['opponents'][1]['opponent']['name']
                img_team2 = match['opponents'][1]['opponent']['image_url']
                date = format_datetime(match['begin_at'])
                dict= {"game": game, "team1": team1, "img_team1": img_team1, "img_team2": img_team2, "team2": team2, "date": date}
                arr_maches.append(dict)
            except Exception as e:
                pass
    return arr_maches

print(get_maches())