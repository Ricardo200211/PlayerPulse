import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse as urlparse
import requests
import json

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

class SteamProfileHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        path = parsed_path.path
        query = urlparse.parse_qs(parsed_path.query)
        cookies = self.parse_cookies(self.headers.get('Cookie'))

        if path == '/loginsteam':
            redirect_uri = 'http://localhost/authorize'
            self.send_response(302)
            self.send_header('Location',
                             f'https://steamcommunity.com/openid/login?openid.ns=http://specs.openid.net/auth/2.0&openid.mode=checkid_setup&openid.return_to={redirect_uri}&openid.realm=http://localhost:8080&openid.claimed_id=http://specs.openid.net/auth/2.0/identifier_select&openid.identity=http://specs.openid.net/auth/2.0/identifier_select')
            self.end_headers()

        elif path == '/authorize':
            claimed_id = query.get('openid.claimed_id')
            if claimed_id:
                steam_id = claimed_id[0].split('/')[-1]
                session_id = f'steam_id={steam_id}'
                self.send_response(302)
                self.send_header('Location', '/profile')
                self.send_header('Set-Cookie', session_id)
                self.end_headers()
            else:
                self.send_response(401)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'Erro na autentica\xc3\xa7\xc3\xa3o. <a href="/loginsteam">Tente novamente</a>.')

        elif path == '/profile':
            if not cookies or 'steam_id' not in cookies:
                self.send_response(302)
                self.send_header('Location', '/loginsteam')
                self.end_headers()
                return

            steam_id = cookies['steam_id']
            profile_data = self.get_steam_profile(steam_id)
            games_data = self.get_owned_games(steam_id)
            cs_go_stats = self.get_csgo_stats(steam_id)

            response_html = self.generate_profile_page(profile_data, games_data, cs_go_stats)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(response_html.encode('utf-8'))

        elif path == '/logout':
            self.send_response(302)
            self.send_header('Location', '/loginsteam')
            self.send_header('Set-Cookie', 'steam_id=; expires=Thu, 01 Jan 1970 00:00:00 GMT')
            self.end_headers()

    def get_steam_profile(self, steam_id):
        api_url = f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={steam_api_key}&steamids={steam_id}'
        response = requests.get(api_url)
        data = response.json()
        return data['response']['players'][0] if data['response']['players'] else None

    def get_owned_games(self, steam_id):
        games_url = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={steam_api_key}&steamid={steam_id}&format=json&include_appinfo=true'
        response = requests.get(games_url)
        return response.json().get('response', {}).get('games', [])

    def get_csgo_stats(self, steam_id):
        stats_url = f'http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=730&key={steam_api_key}&steamid={steam_id}'
        response = requests.get(stats_url)
        return response.json().get('playerstats', {}).get('stats', [])

    def generate_profile_page(self, profile, games, cs_go_stats):
        if not profile:
            return 'Erro ao obter dados do perfil da Steam.'

        total_games = len(games)
        total_hours = sum(game['playtime_forever'] / 60 for game in games)
        cs_go = next((game for game in games if game['appid'] == 730), None)
        cs_go_hours = cs_go['playtime_forever'] / 60 if cs_go else 0

        kills = next((stat['value'] for stat in cs_go_stats if stat['name'] == 'total_kills'), 0)
        deaths = next((stat['value'] for stat in cs_go_stats if stat['name'] == 'total_deaths'), 0)
        wins = next((stat['value'] for stat in cs_go_stats if stat['name'] == 'total_wins'), 0)
        assists = next((stat['value'] for stat in cs_go_stats if stat['name'] == 'total_assists'), 0)

        maps_played = {stat['name']: stat['value'] for stat in cs_go_stats if stat['name'].startswith('total_rounds_map_')}
        map_games = {map_names.get(stat, stat): rounds // 30 for stat, rounds in maps_played.items()}
        most_played_map = max(map_games, key=map_games.get, default='N/A')
        most_played_map_games = map_games.get(most_played_map, 0)

        weapon_kills = {weapon_names.get(stat['name'], stat['name']): stat['value'] for stat in cs_go_stats if stat['name'].startswith('total_kills_')}

        games_info = [{'name': game.get('name', f'AppID {game["appid"]}'), 'playtime_hours': game['playtime_forever'] / 60} for game in games]

        return f'''
        <h1>Perfil do Steam</h1>
        <p>Nome: {profile['personaname']}</p>
        <p><img src="{profile['avatar']}" alt="Avatar"></p>
        <p>Total de jogos: {total_games}</p>
        <p>Total de horas jogadas: {total_hours:.2f}</p>
        <p>Horas jogadas em CS:GO: {cs_go_hours:.2f}</p>
        <h2>Estatísticas de CS:GO</h2>
        <p>Kills: {kills}</p>
        <p>Deaths: {deaths}</p>
        <p>Wins: {wins}</p>
        <p>Assists: {assists}</p>
        <p>Mapa mais jogado: {most_played_map} ({most_played_map_games} jogos)</p>
        <h2>Kills por Arma</h2>
        <ul>
            {''.join([f"<li>{weapon}: {kills} kills</li>" for weapon, kills in weapon_kills.items()])}
        </ul>
        <h2>Horas jogadas em outros jogos</h2>
        <ul>
            {''.join([f"<li>{game['name']}: {game['playtime_hours']:.2f} horas</li>" for game in games_info])}
        </ul>
        <p><a href="/logout">Logout</a></p>
        '''

    def parse_cookies(self, cookie_string):
        cookies = {}
        if cookie_string:
            cookie_pairs = cookie_string.split('; ')
            for pair in cookie_pairs:
                name, value = pair.split('=', 1)
                cookies[name] = value
        return cookies

def run_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, SteamProfileHandler)
    print(f'Servidor http://localhost:8080')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
