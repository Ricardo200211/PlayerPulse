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
        return {'error': 'Região de conta inválida!'}

    url = f"{base_url}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    headers = {
        'X-Riot-Token': API_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': f"Erro ao encontrar conta: {response.status_code} - {response.text}"}

def get_summoner_by_puuid(summoner_region, puuid):
    base_url = SUMMONER_REGION_URLS.get(summoner_region.lower())
    if not base_url:
        return {'error': 'Região de summoner inválida!'}

    url = f"{base_url}/lol/summoner/v4/summoners/by-puuid/{puuid}"
    headers = {
        'X-Riot-Token': API_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': f"Erro ao encontrar summoner: {response.status_code} - {response.text}"}

def get_league_entries_by_summoner_id(summoner_region, encrypted_summoner_id):
    base_url = SUMMONER_REGION_URLS.get(summoner_region.lower())
    if not base_url:
        return {'error': 'Região de summoner inválida!'}

    url = f"{base_url}/lol/league/v4/entries/by-summoner/{encrypted_summoner_id}"
    headers = {
        'X-Riot-Token': API_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': f"Erro ao encontrar entradas de LOL: {response.status_code} - {response.text}"}


def main(account_region, summoner_region, game_name, tag_line):

    if account_region not in ACCOUNT_REGION_URLS not in SUMMONER_REGION_URLS:
        return {'error': 'Região inválida! Por favor insira uma região válida para a conta e summoner.'}

    account_data = get_account_by_riot_id(account_region, game_name, tag_line)
    if 'error' in account_data:
        return account_data

    puuid = account_data['puuid']
    summoner_data = get_summoner_by_puuid(summoner_region, puuid)
    if 'error' in summoner_data:
        return summoner_data

    encrypted_summoner_id = summoner_data['id']
    summoner_level = summoner_data['summonerLevel']

    league_entries = get_league_entries_by_summoner_id(summoner_region, encrypted_summoner_id)
    if 'error' in league_entries:
        return league_entries

    league_info = []
    for entry in league_entries:
        if entry.get('queueType') == 'RANKED_SOLO_5x5':
            queue_type = entry.get('queueType', 'N/A')
            tier = entry.get('tier', 'N/A')
            rank = entry.get('rank', 'N/A')
            league_points = entry.get('leaguePoints', 'N/A')
            wins = entry.get('wins', 'N/A')
            losses = entry.get('losses', 'N/A')
            league_info.append({
                'queueType': queue_type,
                'tier': tier,
                'rank': rank,
                'leaguePoints': league_points,
                'wins': wins,
                'losses': losses
            })

    if not league_info:
        league_info.append({'message': 'Nenhum RANKED_SOLO_5x5 encontrado.'})

    return {
        'account_data': account_data,
        'summoner_data': {
            'puuid': puuid,
            'encrypted_summoner_id': encrypted_summoner_id,
            'summoner_level': summoner_level
        },
        'league_entries': league_info
    }


if __name__ == "__main__":
    result = main()
    print(result)
