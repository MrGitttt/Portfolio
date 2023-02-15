import urllib.request, urllib.parse, urllib.error
import json
import time
import sqlite3

conn = sqlite3.connect('NBA_2021-2022.sqlite')
cur = conn.cursor()

cur.executescript('''
CREATE TABLE IF NOT EXISTS Players
    (player_id INTEGER PRIMARY KEY, player_name TEXT, position TEXT, height_feet INTEGER, height_inches INTEGER, weight_pounds INTEGER);
CREATE TABLE IF NOT EXISTS Teams
    (team_id INTEGER PRIMARY KEY, city_name TEXT, team_name TEXT, conference TEXT);
CREATE TABLE IF NOT EXISTS Games
    (game_id INTEGER PRIMARY KEY, game_date TEXT, home_team_id INTEGER, home_team_score INTEGER, visitor_team_id INTEGER, visitor_team_score INTEGER, postseason BOOLEAN);
CREATE TABLE IF NOT EXISTS Stats
    (id INTEGER, player_id INTEGER, team_id INTEGER, game_id INTEGER, pts INTEGER, reb INTEGER, ast INTEGER, stl INTEGER)''')

# Pick up where we left off
game_id = None
cur.execute('SELECT max(game_id) FROM Games' )
try:
    row = cur.fetchone()
    if row is None :
        game_id = 473408
    else:
        game_id = row[0]
except:
    game_id = 473408

if game_id is None : game_id = 473408

stat_count = None
cur.execute('SELECT max(id) FROM Stats' )
try:
    row = cur.fetchone()
    if row is None :
        stat_count = 0
    else:
        stat_count = row[0]
except:
    stat_count = 0

if stat_count is None : stat_count = 0

many = 0
while True:
    if ( many < 1 ) :
        conn.commit()
        sval = input('How many games:')
        if ( len(sval) < 1 ) : break
        many = int(sval)

    many -= 1

    game_id += 1
    url = 'https://www.balldontlie.io/api/v1/stats?'+ '&game_ids[]=' + str(game_id)
    print('Retriving',url)

    try:
        data = urllib.request.urlopen(url).read().decode()
    except KeyboardInterrupt:
        print('')
        print('Program interrupted by user...')
        break
    except:
        continue
    js = json.loads(data)

    if len(js['data']) < 1:
        print('No data retrived.')
        break

    for i in js['data']:
        stat_count += 1
        cur.execute('SELECT id FROM Stats WHERE id=?', (stat_count,) )
        try:
            row = cur.fetchone()
            if row is not None : continue
        except:
            row = None

        try:
            player_name = i['player']['first_name'] + ' ' + i['player']['last_name']
        except:
            stat_count -= 1
            continue

        position = i['player']['position']
        height_feet = i['player']['height_feet']
        height_inches = i['player']['height_inches']
        weight_pounds = i['player']['weight_pounds']
        city_name = i['team']['city']
        team_name = i['team']['name']
        game_date = i['game']['date'][:10]
        home_team_id = i['game']['home_team_id']
        home_team_score = i['game']['home_team_score']
        visitor_team_id = i['game']['visitor_team_id']
        visitor_team_score = i['game']['visitor_team_score']
        postseason = i['game']['postseason']
        game_id = i['game']['id']
        player_id = i['player']['id']
        team_id = i['team']['id']
        conference = i['team']['conference']
        pts = i['pts']
        reb = i['reb']
        ast = i['ast']
        stl = i['stl']
        cur.execute('''INSERT OR IGNORE INTO Players (player_id, player_name, position, height_feet, height_inches, weight_pounds)
            VALUES ( ?, ?, ?, ?, ?, ?)''', ( player_id, player_name, position, height_feet, height_inches, weight_pounds))
        cur.execute('''INSERT OR IGNORE INTO Teams (team_id, city_name, team_name, conference)
            VALUES ( ?, ?, ?, ?)''', ( team_id, city_name, team_name, conference))
        cur.execute('''INSERT OR IGNORE INTO Games (game_id, game_date, home_team_id, home_team_score, visitor_team_id, visitor_team_score, postseason)
            VALUES ( ?, ?, ?, ?, ?, ?, ?)''', ( game_id, game_date, home_team_id, home_team_score, visitor_team_id, visitor_team_score, postseason))
        cur.execute('''INSERT OR IGNORE INTO Stats (id, player_id, team_id, game_id, pts, reb, ast, stl)
            VALUES ( ?, ?, ?, ?, ?, ?, ?, ?)''', ( stat_count, player_id, team_id, game_id, pts, reb, ast, stl))

        if stat_count % 50 == 0 : conn.commit()
        if stat_count % 5000 == 0 :
            print(' ')
            time.sleep(1)
conn.commit()
cur.close()
