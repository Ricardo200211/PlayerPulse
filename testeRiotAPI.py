import requests

API_KEY = 'RGAPI-5bb518ad-56bf-471b-81d0-6b36658b63c1'  # Substitua pela sua chave de API da Riot Games

# Mapeamento das regiões para os URLs base
REGION_URLS = {
    'americas': 'https://americas.api.riotgames.com',
    'asia': 'https://asia.api.riotgames.com',
    'europe': 'https://europe.api.riotgames.com'
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
        print(f"Erro ao buscar conta: {response.status_code}")
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
        'count': 10  # Número de partidas a serem retornadas
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao buscar histórico de partidas: {response.status_code}")
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
        print(f"Erro ao buscar detalhes da partida: {response.status_code}")
        return None

def main():
    region = input("Digite a região (americas, asia, europe): ").strip().lower()
    game_name = input("Digite o gameName: ").strip()
    tag_line = input("Digite o tagLine: ").strip()
    
    account_data = get_account_by_riot_id(region, game_name, tag_line)
    if account_data:
        puuid = account_data['puuid']
        print(f"Puuid: {puuid}")
        print(f"GameName: {account_data.get('gameName', 'N/A')}")
        print(f"TagLine: {account_data.get('tagLine', 'N/A')}")
        
        # Obter histórico de partidas
        match_history = get_match_history(region, puuid)
        if match_history:
            print("Histórico de Partidas:")
            for match_id in match_history:
                print(f"Match ID: {match_id}")
                match_details = get_match_details(region, match_id)
                if match_details:
                    # Exibir alguns detalhes da partida
                    print(f"Detalhes da Partida {match_id}:")
                    print(f"  Duração: {match_details['info']['gameDuration']} segundos")
                    print(f"  Modo de Jogo: {match_details['info']['gameMode']}")
                    print(f"  Data: {match_details['info']['gameCreation']}")
                    print("  Jogadores:")
                    for player in match_details['info']['participants']:
                        print(f"    - {player['summonerName']} ({player['championName']}) - KDA: {player['kills']}/{player['deaths']}/{player['assists']}")
        else:
            print("Não foi possível obter o histórico de partidas.")
    else:
        print("Conta não encontrada!")

if __name__ == "__main__":
    main()
