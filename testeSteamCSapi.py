import requests

API_KEY = 'DC8FFD05BAD290BE2C5C4B4442AA201A'


def get_steam_id_from_vanity_url(vanity_url):
    url = f"http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={API_KEY}&vanityurl={vanity_url}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['response']['success'] == 1:
            return data['response']['steamid']
        else:
            print("Não foi possível encontrar a URL personalizada.")
            return None
    else:
        print(f"Erro ao procurar Steam ID: {response.status_code}")
        return None


def get_steam_id_from_profile_url(profile_url):
    if profile_url.startswith("https://steamcommunity.com/id/"):
        vanity_url = profile_url.split("/")[-2]
        return get_steam_id_from_vanity_url(vanity_url)
    elif profile_url.startswith("https://steamcommunity.com/profiles/"):
        return profile_url.split("/")[-2]
    else:
        print("Formato de URL inválido.")
        return None


def get_player_summary(steam_id):
    url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={API_KEY}&steamids={steam_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao procurar resumo do jogador: {response.status_code}")
        return None


def get_player_stats(steam_id):
    url = f"http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=730&key={API_KEY}&steamid={steam_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao procurar estatísticas do jogador: {response.status_code}")
        return None


def main():
    profile_input = input("Insira o nome personalizado ou URL completa do perfil da Steam: ").strip()

    if profile_input.startswith("https://steamcommunity.com/"):
        steam_id = get_steam_id_from_profile_url(profile_input)
    else:
        steam_id = get_steam_id_from_vanity_url(profile_input)

    if steam_id:
        print(f"Steam ID: {steam_id}")

        player_summary = get_player_summary(steam_id)
        if player_summary:
            print("Resumo do Jogador:")
            for player in player_summary['response']['players']:
                print(f"Nome: {player.get('personaname', 'N/A')}")
                print(f"Steam ID: {player.get('steamid', 'N/A')}")
                print(f"Perfil: {player.get('profileurl', 'N/A')}")
                print(f"Avatar: {player.get('avatarfull', 'N/A')}")

        player_stats = get_player_stats(steam_id)
        if player_stats:
            print("\nEstatísticas do Jogador no CS:GO:")
            for stat in player_stats['playerstats']['stats']:
                print(f"{stat['name']}: {stat['value']}")
    else:
        print("Não foi possível obter o Steam ID.")


if __name__ == "__main__":
    main()
