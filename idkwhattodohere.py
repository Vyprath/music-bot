from tabulate import tabulate
import requests as rq
import json
import prettytable

HYPIXEL_API = '6cd7ce31-00e7-4f4d-9ce2-60af5bcc4bb8'

pretty = prettytable.PrettyTable()
pretty.add_column('Criteria', ["Level", "Coins", "Games Played", 'Games Won', 'Total Kills', 'Final Kills', 'Kill/Death Ratio', 'Winstreak', 'Beds Broken/Lost Ratio'])
print(pretty)
