import requests
from datetime import datetime
import locale

API_TOKEN = 'XNtIAkyP6EZt9OSC8KqO_3dfhxMWcOLqM3DPMPoCXiqrjzp4cxo'
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

def main():
    matches = get_upcoming_matches()
    if matches:
        for match in matches:
            game = match['videogame']['name']
            team1 = match['opponents'][0]['opponent']['name']
            team2 = match['opponents'][1]['opponent']['name']
            date = format_datetime(match['begin_at'])
            print(f"Jogo: {game}")
            print(f"Partida: {team1} vs {team2}")
            print(f"Data: {date}")
            print()

if __name__ == "__main__":
    main()
