import requests

API_KEY = 'RGAPI-fa1eaf44-7383-4d46-b53c-28dff87c4fa7'

REGION_URLS = {
    'americas': 'https://americas.api.riotgames.com',
    'asia': 'https://asia.api.riotgames.com',
    'europe': 'https://europe.api.riotgames.com',
    'esports': 'https://esports.api.riotgames.com',
    'br1': 'https://br1.api.riotgames.com',
    'eun1': 'https://eun1.api.riotgames.com',
    'euw1': 'https://euw1.api.riotgames.com',
    'jp1': 'https://jp1.api.riotgames.com',
    'kr': 'https://kr.api.riotgames.com',
    'la1': 'https://la1.api.riotgames.com',
    'la2': 'https://la2.api.riotgames.com',
    'na1': 'https://na1.api.riotgames.com',
    'oc1': 'https://oc1.api.riotgames.com',
    'tr1': 'https://tr1.api.riotgames.com',
    'ru': 'https://ru.api.riotgames.com'
}

def get_account_by_riot_id(region, game_name, tag_line):
    base_url = REGION_URLS.get(region.lower())
    if not base_url:
        print("Região inválida!")
        return None

    url = f"{base_url}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    headers = {
        'X-Riot-Token': API_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao buscar conta: {response.status_code} - {response.text}")
        return None

def get_match_history(region, puuid):
    base_url = REGION_URLS.get(region.lower())
    if not base_url:
        print("Região inválida!")
        return None

    url = f"{base_url}/lol/match/v5/matches/by-puuid/{puuid}/ids"
    params = {
        'api_key': API_KEY,
        'start': 0,
        'count': 10
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao buscar histórico de partidas: {response.status_code} - {response.text}")
        return None

def get_match_details(region, match_id):
    base_url = REGION_URLS.get(region.lower())
    if not base_url:
        print("Região inválida!")
        return None

    url = f"{base_url}/lol/match/v5/matches/{match_id}"
    headers = {
        'X-Riot-Token': API_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao encontrar detalhes da partida: {response.status_code} - {response.text}")
        return None


def main(region, game_name, tag_line):

    account_data = get_account_by_riot_id(region, game_name, tag_line)
    if account_data:
        puuid = account_data['puuid']
        match_history = get_match_history(region, puuid)
        if match_history:
            arr_matches = []
            for match_id in match_history:
                match_details = get_match_details(region, match_id)
                dict = {}
                if match_details:
                    arr_jog = []
                    for player in match_details['info']['participants']:
                        arr_jog.append({'player': player['summonerName'], 'champion': player['championName'], 'KDA': f'{player['kills']}/{player['deaths']}/{player['assists']}'})

                    dict = {
                        'match_id': match_id,
                        'duracao': match_details['info']['gameDuration'],
                        'modo': match_details['info']['gameMode'],
                        'data': match_details['info']['gameCreation'],
                        'match_data': arr_jog
                    }
                arr_matches.append(dict)
            return arr_matches
        else:
            print("Não foi possível obter o histórico de partidas.")
    else:
        print("Conta não encontrada!")

if __name__ == "__main__":
    main()
