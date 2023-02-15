import sqlite3
import time
import zlib
import string

conn = sqlite3.connect('NBA_2021-2022.sqlite')
cur1 = conn.cursor()
cur2 = conn.cursor()

cur1.execute('SELECT home_team_id, home_team_score, visitor_team_id, visitor_team_score FROM Games')
counts = dict()
for games in cur1 :
    home_team_id = games[0]
    home_team_score = games[1]
    visitor_team_id = games[2]
    visitor_team_score = games[3]

    if home_team_score > visitor_team_score:
        cur2.execute('SELECT team_name FROM Teams WHERE team_id = ?', (home_team_id,))
    else:
        cur2.execute('SELECT team_name FROM Teams WHERE team_id = ?', (visitor_team_id,))
    team_name = cur2.fetchone()[0]
    counts[team_name] = counts.get(team_name,0) + 1

x = sorted(counts, key=counts.get, reverse=True)
highest = None
lowest = None
for k in x:
    if highest is None or highest < counts[k] :
        highest = counts[k]
    if lowest is None or lowest > counts[k] :
        lowest = counts[k]
print('Range of counts:',highest,lowest)

# Spread the font sizes across 20-100 based on the count
bigsize = 80
smallsize = 20

fhand = open('tword.js','w')
fhand.write("tword = [")
first = True
for k in x:
    if not first : fhand.write( ",\n")
    first = False
    size = counts[k]
    size = (size - lowest) / float(highest - lowest)
    size = int((size * size * bigsize) + smallsize)
    fhand.write("{text: '"+k+"', size: "+str(size)+"}")
fhand.write( "\n];\n")
fhand.close()

print("Output written to tword.js")
print("Open tword.htm in a browser to see the vizualization")
