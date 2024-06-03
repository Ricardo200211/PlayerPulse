import requests

API_KEY = 'RGAPI-9099361a-ee49-49a9-a8e7-e154e33c6061'

ACCOUNT_REGION_URLS = {
    'americas': 'https://americas.api.riotgames.com',
    'asia': 'https://asia.api.riotgames.com',
    'europe': 'https://europe.api.riotgames.com'
}

SUMMONER_REGION_URLS = {
    'americas': 'https://na1.api.riotgames.com',
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

def get_account_by_riot_id(account_region, game_name, tag_line):
    base_url = ACCOUNT_REGION_URLS.get(account_region.lower())
    if not base_url:
        print("Região de conta inválida!")
        return None

    url = f"{base_url}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    headers = {
        'X-Riot-Token': API_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao encontrar conta: {response.status_code} - {response.text}")
        return None

def get_summoner_by_puuid(summoner_region, puuid):
    base_url = SUMMONER_REGION_URLS.get(summoner_region.lower())
    if not base_url:
        print("Região de summoner inválida!")
        return None

    url = f"{base_url}/lol/summoner/v4/summoners/by-puuid/{puuid}"
    headers = {
        'X-Riot-Token': API_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao encontrar summoner: {response.status_code} - {response.text}")
        return None

def get_league_entries_by_summoner_id(summoner_region, encrypted_summoner_id):
    base_url = SUMMONER_REGION_URLS.get(summoner_region.lower())
    if not base_url:
        print("Região de summoner inválida!")
        return None

    url = f"{base_url}/lol/league/v4/entries/by-summoner/{encrypted_summoner_id}"
    headers = {
        'X-Riot-Token': API_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao encontrar entradas de LOL: {response.status_code} - {response.text}")
        return None

def main():
    account_region = input("Indique região da conta (americas, asia, europe): ").strip().lower()
    summoner_region = input("Indique região de summoner (e.g., euw1, na1, kr): ").strip().lower()

    if account_region not in ACCOUNT_REGION_URLS or summoner_region not in SUMMONER_REGION_URLS:
        print("Região inválida! Por favor insira uma região válida para a conta e summoner.")
        return

    game_name = input("Enter gameName: ").strip()
    tag_line = input("Enter tagLine: ").strip()

    account_data = get_account_by_riot_id(account_region, game_name, tag_line)
    if account_data:
        puuid = account_data['puuid']
        print(f"Puuid: {puuid}")
        print(f"GameName: {account_data.get('gameName', 'N/A')}")
        print(f"TagLine: {account_data.get('tagLine', 'N/A')}")

        summoner_data = get_summoner_by_puuid(summoner_region, puuid)
        if summoner_data:
            encrypted_summoner_id = summoner_data['id']
            summoner_level = summoner_data['summonerLevel']
            print(f"EncryptedSummonerId: {encrypted_summoner_id}")
            print(f"SummonerLevel: {summoner_level}")

            league_entries = get_league_entries_by_summoner_id(summoner_region, encrypted_summoner_id)
            if league_entries:
                print("League Entries:")
                solo_queue_found = False
                for entry in league_entries:
                    if entry.get('queueType') == 'RANKED_SOLO_5x5':
                        solo_queue_found = True
                        queue_type = entry.get('queueType', 'N/A')
                        tier = entry.get('tier', 'N/A')
                        rank = entry.get('rank', 'N/A')
                        league_points = entry.get('leaguePoints', 'N/A')
                        wins = entry.get('wins', 'N/A')
                        losses = entry.get('losses', 'N/A')
                        print(f"QueueType: {queue_type}, Tier: {tier}, Rank: {rank}, LeaguePoints: {league_points}, Vitorias: {wins}, Derrotas: {losses}")
                if not solo_queue_found:
                    print("Nenhum RANKED_SOLO_5x5 encontrado.")
            else:
                print("Nenhuma entrada de league encontrada.")
        else:
            print("Summoner não encontrada!")
    else:
        print("Conta não encontrada!")

if __name__ == "__main__":
    main()
