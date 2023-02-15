import urllib.request, urllib.parse, urllib.error
import json
import time
import sqlite3

conn = sqlite3.connect('NBA_database.sqlite')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS Players
    (id INTEGER UNIQUE, player_name TEXT, body TEXT)''')

# Pick up where we left off
start = None
cur.execute('SELECT max(id) FROM Players' )
try:
    row = cur.fetchone()
    if row is None :
        start = 0
    else:
        start = row[0]
except:
    start = 0

if start is None : start = 0

serviceurl = 'https://www.balldontlie.io/api/v1/players/'

# player_name = input('Input a player name: ')
# name_split = player_name.split()

many = 0
count = 0
while True:
    if ( many < 1 ) :
        conn.commit()
        sval = input('How many players:')
        if ( len(sval) < 1 ) : break
        many = int(sval)

    start = start + 1
    cur.execute('SELECT id FROM Players WHERE id=?', (start,) )
    try:
        row = cur.fetchone()
        if row is not None : continue
    except:
        row = None

    many = many - 1
    url = serviceurl + str(start)
    print('Retriving', url)
    count = count + 1
    try:
        data = urllib.request.urlopen(url).read().decode()
    except KeyboardInterrupt:
        print('')
        print('Program interrupted by user...')
        break
    except:
        continue
    js = json.loads(data)
    player_name = js['first_name'] + ' ' + js['last_name']
    # if js['first_name'] == name_split[0] and js['last_name'] == name_split[1]:
    #     print('Player name:',js['first_name'],js['last_name'],'\nPlayer ID:',player_id)
    #     quit()
    cur.execute('''INSERT OR IGNORE INTO Players (id, player_name, body)
        VALUES ( ?, ?, ?, ?)''', ( start, player_name, data))
    if count % 50 == 0 : conn.commit()
    if count % 100 == 0 : time.sleep(1)

conn.commit()
cur.close()
