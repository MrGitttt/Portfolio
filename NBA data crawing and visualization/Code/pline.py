import sqlite3
import time
import zlib

conn = sqlite3.connect('NBA_2021-2022.sqlite')
cur = conn.cursor()


cur.execute('SELECT player_id FROM Players')
pla_id = list()
for row in cur :
    pla_id.append(row[0])

pla_sco = dict()
for i in pla_id:
    cur.execute('''SELECT Players.player_name, Games.game_date, Stats.pts FROM Players
    JOIN Games JOIN Stats ON Players.player_id=Stats.player_id
    AND Games.game_id=Stats.game_id WHERE Players.player_id = ?''', (i, ))
    count = 0
    sum = 0
    for row in cur:
        pla_name = row[0]
        sum = sum + row[2]
        # adjust the average score
        if row[2] != 0:
            count = count + 1
            pla_sco[pla_name] = round(sum / count, 2)
    # select the players that played more than 50 games
    if count < 50:
        try:
            del pla_sco[pla_name]
        except:
            continue

plas = sorted(pla_sco, key=pla_sco.get, reverse=True)
plas = plas[:5]
print("Top 5 Players")
print(plas)

score = dict()
date_list = list()
for pla in plas:
    cur.execute('''SELECT Players.player_name, Games.game_date, Stats.pts FROM Players
    JOIN Games JOIN Stats ON Players.player_id=Stats.player_id
    AND Games.game_id=Stats.game_id WHERE Players.player_name = ?''', (pla, ))
    player_name = pla

    for row in cur:
        play_date = row[1]
        pts = row[2]
        key = (play_date, player_name)
        score[key] = pts
        if play_date not in date_list :
            date_list.append(play_date)
date_list.sort()

fhand = open('pline.js','w')
fhand.write("pline = [ ['Date'")
for pla in plas:
    fhand.write(",'"+pla+"'")
fhand.write("]")

for date in date_list:
    fhand.write(",\n['"+date+"'")
    for pla in plas:
        key = (date, pla)
        # default value = average score of the player
        val = score.get(key,pla_sco[pla])
        if val == 0: val = pla_sco[pla]
        fhand.write(","+str(val))
    fhand.write("]");

fhand.write("\n];\n")
fhand.close()

print("Output written to pline.js")
print("Open pline.htm to visualize the data")
