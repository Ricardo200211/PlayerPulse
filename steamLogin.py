import os
from flask import Flask, redirect, url_for, session, request, jsonify
from authlib.integrations.flask_client import OAuth
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Definições do OAuth
oauth = OAuth(app)
steam = oauth.register(
    name='steam',
    client_id='',
    client_secret='',
    authorize_url='https://steamcommunity.com/openid/login',
    authorize_params={
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.mode': 'checkid_setup',
        'openid.return_to': 'http://localhost:5000/authorize',
        'openid.realm': 'http://localhost:5000',
        'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
    },
    request_token_url=None,
    request_token_params=None,
    access_token_url=None,
    access_token_params=None,
    client_kwargs=None,
)

steam_api_key = 'DC8FFD05BAD290BE2C5C4B4442AA201A'

map_names = {
    'total_rounds_map_de_dust2': 'Dust II',
    'total_rounds_map_de_inferno': 'Inferno',
    'total_rounds_map_de_mirage': 'Mirage',
    'total_rounds_map_de_nuke': 'Nuke',
    'total_rounds_map_de_cache': 'Cache',
    'total_rounds_map_de_cbble': 'Cobblestone',
    'total_rounds_map_de_overpass': 'Overpass',
    'total_rounds_map_de_train': 'Train',
    'total_rounds_map_de_vertigo': 'Vertigo',
    'total_rounds_map_de_ancient': 'Ancient',
    'total_rounds_map_de_anubis': 'Anubis'
}

weapon_names = {
    'total_kills_ak47': 'AK-47',
    'total_kills_aug': 'AUG',
    'total_kills_awp': 'AWP',
    'total_kills_bizon': 'PP-Bizon',
    'total_kills_cz75auto': 'CZ75-Auto',
    'total_kills_deagle': 'Desert Eagle',
    'total_kills_elite': 'Dual Berettas',
    'total_kills_famas': 'FAMAS',
    'total_kills_fiveseven': 'Five-SeveN',
    'total_kills_g3sg1': 'G3SG1',
    'total_kills_galilar': 'Galil AR',
    'total_kills_glock': 'Glock-18',
    'total_kills_m249': 'M249',
    'total_kills_m4a1': 'M4A1',
    'total_kills_mac10': 'MAC-10',
    'total_kills_mag7': 'MAG-7',
    'total_kills_mp5sd': 'MP5-SD',
    'total_kills_mp7': 'MP7',
    'total_kills_mp9': 'MP9',
    'total_kills_negev': 'Negev',
    'total_kills_nova': 'Nova',
    'total_kills_hkp2000': 'P2000',
    'total_kills_p250': 'P250',
    'total_kills_p90': 'P90',
    'total_kills_sawedoff': 'Sawed-Off',
    'total_kills_scar20': 'SCAR-20',
    'total_kills_sg556': 'SG 553',
    'total_kills_ssg08': 'SSG 08',
    'total_kills_tec9': 'Tec-9',
    'total_kills_ump45': 'UMP-45',
    'total_kills_usp_silencer': 'USP-S',
    'total_kills_xm1014': 'XM1014'
}


@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return steam.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    args = request.args.to_dict()
    claimed_id = args.get('openid.claimed_id')
    if claimed_id:
        steam_id = claimed_id.split('/')[-1]
        session['steam_id'] = steam_id
        return redirect(url_for('profile'))
    return 'Erro na autenticação.'


@app.route('/profile')
def profile():
    if 'steam_id' not in session:
        return redirect(url_for('index'))

    steam_id = session['steam_id']
    api_url = f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={steam_api_key}&steamids={steam_id}'
    response = requests.get(api_url)

    try:
        data = response.json()
        player = data['response']['players'][0]
    except (ValueError, KeyError, IndexError):
        return jsonify(error='Erro ao obter dados do perfil da Steam. Verifique a chave da API e tente novamente.')

    # Obter informações dos jogos
    games_url = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={steam_api_key}&steamid={steam_id}&format=json&include_appinfo=true'
    games_response = requests.get(games_url)

    try:
        games_data = games_response.json()
        games = games_data['response']['games']


        total_games = len(games)
        total_hours = sum(game['playtime_forever'] / 60 for game in games)


        games_info = []
        for game in games:
            game_info = {
                'name': game.get('name', f'AppID {game["appid"]}'),
                'appid': game['appid'],
                'playtime_hours': game['playtime_forever'] / 60
            }
            games_info.append(game_info)

        # CS:GO
        cs_go = next((game for game in games if game['appid'] == 730), None)  # 730 é o appid do CS:GO
        cs_go_hours = cs_go['playtime_forever'] / 60 if cs_go else 0
    except (ValueError, KeyError, IndexError):
        total_games = total_hours = 0
        cs_go_hours = 0

    # Obter estatísticas de CS:GO
    cs_go_stats = {}
    try:
        stats_url = f'http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=730&key={steam_api_key}&steamid={steam_id}'
        stats_response = requests.get(stats_url)
        stats_data = stats_response.json()
        cs_go_stats = stats_data['playerstats']['stats']

        # Filtrar algumas estatísticas específicas
        kills = next((stat['value'] for stat in cs_go_stats if stat['name'] == 'total_kills'), 0)
        deaths = next((stat['value'] for stat in cs_go_stats if stat['name'] == 'total_deaths'), 0)
        wins = next((stat['value'] for stat in cs_go_stats if stat['name'] == 'total_wins'), 0)
        assists = next((stat['value'] for stat in cs_go_stats if stat['name'] == 'total_assists'), 0)

        # Mapas mais jogados (convertendo rodadas em jogos completos)
        maps_played = {stat['name']: stat['value'] for stat in cs_go_stats if
                       stat['name'].startswith('total_rounds_map_')}
        map_games = {map_names.get(stat, stat): rounds // 30 for stat, rounds in maps_played.items()}
        most_played_map = max(map_games, key=map_games.get, default='N/A')
        most_played_map_games = map_games.get(most_played_map, 0)

        # Kills por arma
        weapon_kills = {weapon_names.get(stat['name'], stat['name']): stat['value'] for stat in cs_go_stats if
                        stat['name'].startswith('total_kills_')}
    except (ValueError, KeyError, IndexError):
        kills = deaths = wins = assists = 0
        most_played_map = 'N/A'
        most_played_map_games = 0
        map_games = {}
        weapon_kills = {}

    profile_data = {
        'player': {
            'name': player['personaname'],
            'avatar': player['avatar']
        },
        'total_games': total_games,
        'total_hours': total_hours,
        'cs_go_hours': cs_go_hours,
        'cs_go_stats': {
            'kills': kills,
            'deaths': deaths,
            'wins': wins,
            'assists': assists,
            'most_played_map': most_played_map,
            'most_played_map_games': most_played_map_games,
            'map_games': map_games,
            'weapon_kills': weapon_kills
        },
        'games_info': games_info
    }

    return jsonify(profile_data)


@app.route('/logout')
def logout():
    session.pop('steam_id', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
