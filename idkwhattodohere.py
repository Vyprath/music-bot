import hypixel
API_KEYS = ['6cd7ce31-00e7-4f4d-9ce2-60af5bcc4bb8']

hypixel.setKeys(API_KEYS)

Username = input('Enter Username: ')
player = hypixel.Player(Username)
UHCStats = player.JSON['stats']['UHC']
UHCKills = UHCStats['kills']
UHCWins =  UHCStats['wins']
UHCScore = UHCStats['score']
UHCCoins = UHCStats['coins']
UHCDeaths = UHCStats['deaths']
UHCKills = str(UHCKills)
UHCWins = str(UHCWins)
UHCScore = str(UHCScore)
UHCCoins = str(UHCCoins)
UHCDeaths = str(UHCDeaths)
UHC_Stats = Username + "'s UHC Stats: \n" + 'Kills: ' + UHCKills + '\n' + 'Wins: ' + UHCWins + '\n' + 'Score: ' + UHCScore + '\n' + 'Coins: ' + UHCCoins + '\n' + 'Deaths: ' + UHCDeaths + '\n\n'
print(UHC_Stats)
