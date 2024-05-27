import requests

API_KEY = 'RGAPI-5bb518ad-56bf-471b-81d0-6b36658b63c1'  

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

def get_match_history(region, puuid, count=20):
    base_url = REGION_URLS.get(region.lower())
    if not base_url:
        print("Região inválida!")
        return None
    
    url = f"{base_url}/lol/match/v5/matches/by-puuid/{puuid}/ids"
    params = {
        'start': 0,
        'count': count  # Número de partidas a serem retornadas
    }
    headers = {
        'X-Riot-Token': API_KEY
    }
    response = requests.get(url, headers=headers, params=params)
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
        match_count = int(input("Quantas partidas você deseja buscar? (max 100): "))
        match_history = get_match_history(region, puuid, count=match_count)
        if match_history:
            print("Histórico de Partidas:")
            total_kills = total_deaths = total_assists = total_wins = total_games = 0
            
            for match_id in match_history:
                match_details = get_match_details(region, match_id)
                if match_details:
                    # Acumular estatísticas
                    total_games += 1
                    for player in match_details['info']['participants']:
                        if player['puuid'] == puuid:
                            total_kills += player['kills']
                            total_deaths += player['deaths']
                            total_assists += player['assists']
                            if player['win']:
                                total_wins += 1
                            break

            # Exibir estatísticas acumuladas
            print("\nEstatísticas Totais:")
            print(f"Total de Jogos: {total_games}")
            print(f"Vitórias: {total_wins}")
            print(f"Derrotas: {total_games - total_wins}")
            print(f"Kills: {total_kills}")
            print(f"Deaths: {total_deaths}")
            print(f"Assists: {total_assists}")
            print(f"KDA: {(total_kills + total_assists) / total_deaths if total_deaths > 0 else 'N/A'}")
        else:
            print("Não foi possível obter o histórico de partidas.")
    else:
        print("Conta não encontrada!")

if __name__ == "__main__":
    main()
