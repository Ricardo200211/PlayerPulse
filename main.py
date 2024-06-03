import os
import pathlib
import logging
import requests
from flask import Flask, session, abort, redirect, request, render_template_string, url_for, jsonify
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from authlib.integrations.flask_client import OAuth

import APIriot
import riotAPI
import steamLogin
import NewsAPI
import connect_BD
import hash_parser
import esportsAPI

app = Flask("PlayerPulse")
state = ""
app.secret_key = "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"

app.config.update(
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "187220305616-2ukna03qgqujufhb4fjof9qlcqeifa14.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

if not os.path.exists(client_secrets_file):
    raise FileNotFoundError("client_secret.json file not found")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://localhost/callback"
)


@app.route("/login")
def login():
    authorization_url, state_ = flow.authorization_url()
    global state
    state = state_
    logging.debug(f"Login state set in session: {state}")
    logging.debug(f"Session after setting state: {session}")
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    global state
    state_in_session = state
    state_in_request = request.args.get("state")

    if state_in_session is None:
        logging.error("State is missing in session")
        return abort(400, description="State is missing in session")

    if state_in_session != state_in_request:
        logging.error(f"State mismatch: session state {state_in_session} vs request state {state_in_request}")
        return abort(400, description="State mismatch")

    try:
        flow.fetch_token(authorization_response=request.url)
    except Exception as e:
        logging.error(f"Error fetching token: {e}")
        return abort(500, description="Error fetching token")

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    try:
        id_info = id_token.verify_oauth2_token(
            id_token=credentials._id_token,
            request=token_request,
            audience=GOOGLE_CLIENT_ID
        )
    except ValueError as e:
        logging.error(f"Token verification failed: {e}")
        return abort(400, description="Token verification failed")

    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")
    try:
        conexao = connect_BD.conectar_mysql()
        cursor = conexao.cursor()
        query = "select id from player where email = %s"
        cursor.execute(query, (session['email'],))
        player = cursor.fetchall()
        session['id'] = player[0][0]
    except Exception as e:
        print(e)
        return "Erro ao conectar com a base de dados"
    finally:
        conexao.close()
    return redirect("/protected_area")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/")
def index():
    return render_template_string(open('templates/Login.html', encoding='utf-8').read())


@app.route("/protected_area")
def protected_area():
    criar_player_google()
    return redirect("/abrir_ecra_principal")


@app.route("/abrir_registo")
def abrir_registo():
    return render_template_string(open('templates/registo.html', encoding='utf-8').read())


@app.route("/abrir_perfil")
def abrir_perfil():
    try:
        conexao = connect_BD.conectar_mysql()
        cursor = conexao.cursor()
        query = "select * from steam where id_player = %s"
        cursor.execute(query, (session['id'], ))
        steam_player = cursor.fetchall()
        session['steam_name'] = steam_player[0][2]
        cursor2 = conexao.cursor()
        query2 = "select * from riot where id_player = %s"
        cursor2.execute(query2, (session['id'],))
        riot_player = cursor.fetchall()
        session['riot_regiao'] = riot_player[0][1]
        session['riot_name'] = riot_player[0][2]
        session['riot_tag'] = riot_player[0][3]
        session['riot_full_name'] = session['riot_name'] + '#' + session['riot_tag']
        return render_template_string(open('templates/perfil.html', encoding='utf-8').read(), name=session['name'], email=session['email'], steam_name=session['steam_name'], riot_name=session['riot_full_name'])
    except Exception as e:
        print(e)
        return "Erro ao conectar com a base de dados"
    finally:
        conexao.close()


@app.route("/criar_player", methods=['POST'])
def criar_player():
    id = 2
    nome = request.form['nome']
    email = request.form['Email']
    passwd = request.form['passwd']
    encripted_pass = hash_parser.parse_hash(passwd)
    try:
        conexao = connect_BD.conectar_mysql()
        cursor = conexao.cursor()
        query = "INSERT INTO player(id, nome, email, pass) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (id, nome, email, encripted_pass))
        conexao.commit()
        return redirect(url_for('index'))
    except Exception as e:
        print(e)
        return "Erro ao conectar com a base de dados"
    finally:
        conexao.close()


def criar_player_google():
    nome = session["name"]
    email = session["email"]
    try:
        conexao = connect_BD.conectar_mysql()
        cursor = conexao.cursor()
        query = "select * from player where email = %s"
        cursor.execute(query, (email,))
        player = cursor.fetchall()
        if not player:
            cursor2 = conexao.cursor()
            query2 = "INSERT INTO player(nome, email) VALUES (%s, %s)"
            cursor2.execute(query2, (nome, email))
            conexao.commit()
    except Exception as e:
        print(e)
        return "Erro ao conectar com a base de dados"
    finally:
        conexao.close()


@app.route("/login_normal", methods=['POST'])
def login_normal():
    email = request.form['email']
    passwd_original = request.form['passwd']
    passwd = hash_parser.parse_hash(passwd_original)
    conexao = connect_BD.conectar_mysql()
    if conexao:
        try:
            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM player WHERE email = %s and pass = %s", (email, passwd))
                resultado = cursor.fetchone()
                if resultado:
                    session["email"] = resultado[2]
                    session["name"] = resultado[1]
                    return redirect("/abrir_ecra_principal")
        except Exception as e:
            print(e)
        finally:
            conexao.close()
    else:
        print("Erro na conexão com a base de dados")


@app.route("/abrir_ecra_principal")
def abrir_ecra_principal():
    news = NewsAPI.get_news()
    esports_games = esportsAPI.get_maches()
    return render_template_string(open('templates/ecra_principal.html', encoding='utf-8').read(), nome=session["name"],
                                  news=news, esports_games=esports_games)


oauth = OAuth(app)
steam = oauth.register(
    name='steam',
    client_id='',  # Não é necessário para Steam OpenID
    client_secret='',  # Não é necessário para Steam OpenID
    authorize_url='https://steamcommunity.com/openid/login',
    authorize_params={
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.mode': 'checkid_setup',
        'openid.return_to': 'http://localhost/authorize_steam',
        'openid.realm': 'http://localhost',
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


@app.route('/login_steam')
def login_steam():
    redirect_uri = url_for('authorize_steam', _external=True)
    return steam.authorize_redirect(redirect_uri)


@app.route('/authorize_steam')
def authorize_steam():
    args = request.args.to_dict()
    claimed_id = args.get('openid.claimed_id')
    if claimed_id:
        steam_id = claimed_id.split('/')[-1]
        session['steam_id'] = steam_id
        api_url = f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={steam_api_key}&steamids={steam_id}'
        response = requests.get(api_url)
        data = response.json()
        player = data['response']['players'][0]
        name = player['personaname']
        try:
            conexao = connect_BD.conectar_mysql()
            cursor = conexao.cursor()
            query = "select * from steam where steam_id = %s"
            cursor.execute(query, (session['steam_id'],))
            player = cursor.fetchall()
            if not player:
                cursor2 = conexao.cursor()
                query2 = "INSERT INTO steam(steam_id, nome_steam, id_player) VALUES (%s, %s, %s)"
                cursor2.execute(query2, (session['steam_id'], name, session['id']))
                conexao.commit()
        except Exception as e:
            print(e)
            return "Erro ao conectar com a base de dados"
        finally:
            conexao.close()
        return render_template_string(open('templates/perfil.html', encoding='utf-8').read(), name=session['name'], email=session['email'], steam_name=name)
    return 'Erro na autenticação.'

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
@app.route('/profile_steam')
def profile_steam():
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


@app.route('/logout_steam')
def logout_steam():
    session.pop('steam_id', None)
    return render_template_string(open('templates/perfil.html', encoding='utf-8').read(), name=session['name'], email=session['email'])


@app.route('/login_riot', methods=['POST'])
def login_riot():
    session['regiao'] = request.form['region']
    session['riot_name'], session['tag'] = request.form['Riot'].split('#')
    try:
        conexao = connect_BD.conectar_mysql()
        cursor = conexao.cursor()
        query = "select * from riot where regiao = %s and nome = %s and tag = %s and id_player = %s"
        cursor.execute(query, (session['regiao'], session['riot_name'], session['tag'], session['id']))
        player = cursor.fetchall()
        if not player:
            cursor2 = conexao.cursor()
            query2 = "INSERT INTO riot(regiao, nome, tag, id_player) VALUES (%s, %s, %s, %s)"
            cursor2.execute(query2, (session['regiao'], session['riot_name'], session['tag'], session['id']))
            conexao.commit()
            return render_template_string(open('templates/perfil.html', encoding='utf-8').read(), name=session['name'],email=session['email'])
    except Exception as e:
        print(e)
        return "Erro ao conectar com a base de dados"
    finally:
        conexao.close()


@app.route('/abrir_noticias')
def abrir_noticias():
    news = NewsAPI.get_news()
    return render_template_string(open('templates/Noticias.html', encoding='utf-8').read(), name=session['name'], news=news)


@app.route('/abrir_esports')
def abrir_esports():
    games = esportsAPI.get_maches()
    return render_template_string(open('templates/Jogos Internacionais.html', encoding='utf-8').read(), name=session['name'], esports_games=games)


@app.route('/abrir_stats')
def abrir_stats():
    matches = APIriot.main(session['riot_regiao'], session['riot_name'], session['riot_tag'])
    stats = riotAPI.main(session['riot_regiao'], 'euw1', session['riot_name'], session['riot_tag'])
    return render_template_string(open('templates/vs.html', encoding='utf-8').read(), name=session['name'], matches=matches, stats=stats, riot_name=session['riot_name'])


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(host='0.0.0.0', port=80, debug=True)
