from tabulate import tabulate
import requests as rq
import json

HYPIXEL_API = '6cd7ce31-00e7-4f4d-9ce2-60af5bcc4bb8'



name = "7T6"

HYPIXEL_LINK = rq.get('https://api.hypixel.net/player?key={}&name={}'.format(HYPIXEL_API, name)).json()
bWR = round(int(HYPIXEL_LINK['player']['stats']['Bedwars']['wins_bedwars']) / int(HYPIXEL_LINK['player']['stats']['Bedwars']["games_played_bedwars"]) * 100, 2)
WR = f"{bWR}%"
print(WR)
