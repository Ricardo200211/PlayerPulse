import requests

API_KEY = 'RGAPI-ade6d8f0-1e43-4db9-b512-270349b74791'

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
        print(f"Erro ao procurar conta: {response.status_code}")
        return None


def get_match_history(region, puuid, count=20):
    base_url = REGION_URLS.get(region.lower())
    if not base_url:
        print("Região inválida!")
        return None

    url = f"{base_url}/tft/match/v1/matches/by-puuid/{puuid}/ids"
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
        print(f"Erro ao pesquisar histórico de partidas: {response.status_code}")
        return None


def get_match_details(region, match_id):
    base_url = REGION_URLS.get(region.lower())
    if not base_url:
        print("Região inválida!")
        return None

    url = f"{base_url}/tft/match/v1/matches/{match_id}"
    headers = {
        'X-Riot-Token': API_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao procurar detalhes da partida: {response.status_code}")
        return None


def main():
    region = input("Insira a região (americas, asia, europe): ").strip().lower()
    game_name = input("Insira o gameName: ").strip()
    tag_line = input("Insira o tagLine: ").strip()

    account_data = get_account_by_riot_id(region, game_name, tag_line)
    if account_data:
        puuid = account_data['puuid']
        print(f"Puuid: {puuid}")
        print(f"GameName: {account_data.get('gameName', 'N/A')}")
        print(f"TagLine: {account_data.get('tagLine', 'N/A')}")

        # Obter histórico de partidas
        match_count = int(input("Quantas partidas deseja pesquisar? (max 100): "))
        match_history = get_match_history(region, puuid, count=match_count)
        if match_history:
            print("Histórico de Partidas:")
            total_wins = total_top4 = total_games = 0

            for match_id in match_history:
                match_details = get_match_details(region, match_id)
                if match_details:
                    total_games += 1
                    for player in match_details['info']['participants']:
                        if player['puuid'] == puuid:
                            if player['placement'] == 1:
                                total_wins += 1
                            if player['placement'] <= 4:
                                total_top4 += 1
                            break

            # Exibir estatísticas acumuladas
            print("\nEstatísticas Totais:")
            print(f"Total de Jogos: {total_games}")
            print(f"Vitórias: {total_wins}")
            print(f"Top 4: {total_top4}")
            print(f"Percentagem de Vitórias: {total_wins / total_games * 100:.2f}%")
            print(f"Percentagem de Top 4: {total_top4 / total_games * 100:.2f}%")
        else:
            print("Não foi possível obter o histórico de partidas.")
    else:
        print("Conta não encontrada!")


if __name__ == "__main__":
    main()
