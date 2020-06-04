import discord
from discord.ext import commands
from discord.utils import get
import random
import os
import youtube_dl
import shutil
import requests as rq
import re
import json
from youtube_search import YoutubeSearch

client = commands.Bot(command_prefix = '?')
Token = ''
YOUTUBE_API = ''
HYPIXEL_API = ''

#on the event that the bot is ready, print this.
@client.event
async def on_ready():
    print('Bot is ready.')
    await client.change_presence(status = discord.Status.idle, activity = discord.Game('Contact Moe#4035 if any errors persist.'))

@client.command(pass_context=True)
async def botstats(ctx):
    no_of_servers = len(client.guilds)
    total_members = 0
    total_members =  int(len(client.users))
    await ctx.send(f"Serving `{total_members}` members potpourri across `{no_of_servers}` servers")



@client.command()
async def ping(ctx):
  await ctx.send(f'Ba-dum-tss! {round(client.latency * 1000)}ms')


@client.command(aliases=['8ball'])
async def _8ball(ctx):
        responses = ["It is certain.",
                    "It is decidedly so.",
                    "Without a doubt.",
                    "Yes - definitely.",
                    "You may rely on it.",
                    "As I see it, yes.",
                    "Most likely.",
                    "Outlook good.",
                    "Yes.",
                    "Signs point to yes.",
                    "Reply hazy, try again.",
                    "Ask again later.",
                    "Better not tell you now.",
                    "Cannot predict now.",
                    "Concentrate and ask again.",
                    "Don't count on it.",
                    "My reply is no.",
                    "My sources say no.",
                    "Outlook not so good.",
                    "Very doubtful."]
        await ctx.send(f'Answer: {random.choice(responses)}')


@client.command()
async def clear(ctx, amount = None):
    await ctx.channel.purge(limit = amount)


@client.command(pass_context = True)
async def join(ctx):
    if not discord.opus.is_loaded():
        discord.opus.load_opus('libopus.so')
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild = ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        await ctx.send(f"Joined{channel}")


@client.command(pass_contex=True)
async def leave(ctx):
    await ctx.voice_client.disconnect()


@client.command(aliases=['p', 'pla'])
async def play(ctx, *, arg):
    results = YoutubeSearch(arg, max_results=1).to_json()
    fixed = json.loads(results)
    song = "https://www.youtube.com/watch?v={}".format(fixed['videos'][0]['id'])

    def check_queue():
        Queue_infile = os.path.isdir("./Queue")
        if Queue_infile is True:
            DIR = os.path.abspath(os.path.realpath("Queue"))
            length = len(os.listdir(DIR))
            still_q = length - 1
            try:
                first_file = os.listdir(DIR)[0]
            except:
                print("No more queued song(s)\n")
                queues.clear()
                return
            main_location = os.path.dirname(os.path.realpath(__file__))
            song_path = os.path.abspath(os.path.realpath("Queue") + "\\" + first_file)
            if length != 0:
                print("Song done, playing next queued\n")
                print(f"Songs still in queue: {still_q}")
                song_there = os.path.isfile("song.mp3")
                if song_there:
                    os.remove("song.mp3")
                shutil.move(song_path, main_location)
                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        os.rename(file, 'song.mp3')

                voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.4

            else:
                queues.clear()
                return

        else:
            queues.clear()
            print("No songs were queued before the ending of the last song\n")



    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            queues.clear()
            print("Removed old song file")
    except PermissionError:
        print("Trying to delete song file, but it's being played")
        await ctx.send("ERROR: Music playing")
        return


    Queue_infile = os.path.isdir("./Queue")
    try:
        Queue_folder = "./Queue"
        if Queue_infile is True:
            print("Removed old Queue Folder")
            shutil.rmtree(Queue_folder)
    except:
        print("No old Queue folder")

    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            print("Removed old song file")
    except PermissionError:
        print("Trying to delete song file, but it's being played")
        await ctx.send("ERROR: Music playing")
        return

    await ctx.send('Searching for `{}`'.format(arg))

    voice = get(client.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([song])

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            print(f"Renamed File: {file}\n")
            os.rename(file, "song.mp3")

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.4

    nname = fixed['videos'][0]['title']
    await ctx.send(f"Playing :musical_note:  : `{nname}`")
    print("playing\n")



@client.command(pass_context=True, aliases=['n', 'nex'])
async def next(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Playing Next Song")
        voice.stop()
        await ctx.send("Playing Next Song.")
    else:
        print("No music playing")
        await ctx.send("No music playing failed")

queues = {}

@client.command(pass_context=True, aliases=['q', 'que'])

async def queue(ctx, *, arg):
    results = YoutubeSearch(arg, max_results=1).to_json()
    fixed = json.loads(results)
    song = "https://www.youtube.com/watch?v={}".format(fixed['videos'][0]['id'])
    nname = fixed['videos'][0]['title']


    Queue_infile = os.path.isdir("./Queue")
    if Queue_infile is False:
        os.mkdir("Queue")
    DIR = os.path.abspath(os.path.realpath("Queue"))
    q_num = len(os.listdir(DIR))
    q_num += 1
    add_queue = True
    while add_queue:
        if q_num in queues:
            q_num += 1
        else:
            add_queue = False
            queues[q_num] = q_num

    queue_path = os.path.abspath(os.path.realpath("Queue") + f"\song{q_num}.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'outtmpl': queue_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([song])
    await ctx.send("Adding:`{}` to the queue".format(nname))

    print("Song added to queue\n")

@client.command(aliases = ['bedwars', 'bw'])
async def bwstats(ctx, name: str):
    HYPIXEL_LINK = rq.get('https://api.hypixel.net/player?key={}&name={}'.format(HYPIXEL_API, name)).json()
    bw_level = HYPIXEL_LINK['player']['achievements']['bedwars_level']
    bw_coins = HYPIXEL_LINK['player']['stats']['Bedwars']['coins']
    total_played = HYPIXEL_LINK['player']['stats']['Bedwars']["games_played_bedwars"]
    total_won = HYPIXEL_LINK['player']['stats']['Bedwars']['wins_bedwars']
    total_kills = HYPIXEL_LINK['player']['stats']['Bedwars']['kills_bedwars']
    total_finals = HYPIXEL_LINK['player']['stats']['Bedwars']['final_kills_bedwars']
    KDR = round(int(HYPIXEL_LINK['player']['stats']['Bedwars']['kills_bedwars']) / int(HYPIXEL_LINK['player']['stats']['Bedwars']['deaths_bedwars']), 2)
    FKDR = round(int(HYPIXEL_LINK['player']['stats']['Bedwars']['final_kills_bedwars']) / int(HYPIXEL_LINK['player']['stats']['Bedwars']['final_deaths_bedwars']), 2)
    Winstreak = HYPIXEL_LINK['player']['stats']['Bedwars']['winstreak']
    BBLR = round(int(HYPIXEL_LINK['player']['stats']['Bedwars']['beds_broken_bedwars']) / int(HYPIXEL_LINK['player']['stats']['Bedwars']['beds_lost_bedwars']), 2)

    embed = discord.Embed(colour = discord.Colour.blue(), title = f"Bedwars stats for {name}")

    embed.set_author(name = "Requested by {}".format(ctx.author.name), icon_url= f"{ctx.author.avatar_url}")
    embed.set_image(url = 'https://cdn.discordapp.com/attachments/706135793185456221/715261418953375773/image.png')
    embed.add_field(name = "Level", value = f"{bw_level}", inline = False)
    embed.add_field(name = "Coins", value = f"{bw_coins}", inline = False)
    embed.add_field(name = "Games Played", value = f"{total_played}", inline = False)
    embed.add_field(name = "Games Won", value = f"{total_won}", inline = False)
    embed.add_field(name = "Kills", value = f"{total_kills}", inline = False)
    embed.add_field(name = "Final Kills", value = f"{total_finals}", inline = False)
    embed.add_field(name = "Kills/Death Ratio", value = f"{KDR}")
    embed.add_field(name = "Final Kills/Death Ratio", value = f"{FKDR}", inline = False)
    embed.add_field(name = "Winstreak", value = f"{Winstreak}")
    embed.add_field(name = "Beds Broken/Lost Ratio", value = f"{BBLR}", inline = False)

    await ctx.send(embed=embed)
    
    @client.command(aliases = ['bwcompare', 'bwc'])
async def bwcomparison(ctx, *args: str):

    if len(args) == 1:
        await ctx.send(f'Cant compare info of only 1 player. Do ``?bw {args[0]}`` instead')

    elif len(args) == 2:
        pretty = prettytable.PrettyTable()

        HYPIXEL_LINK = rq.get('https://api.hypixel.net/player?key={}&name={}'.format(HYPIXEL_API, args[0])).json()
        bwstats = HYPIXEL_LINK['player']['stats']['Bedwars']
        bw_level = HYPIXEL_LINK['player']['achievements']['bedwars_level']
        bw_coins = bwstats['coins']
        total_played = bwstats["games_played_bedwars"]
        total_won = bwstats['wins_bedwars']
        total_kills = bwstats['kills_bedwars']
        total_finals = bwstats['final_kills_bedwars']
        KDR = round(int(bwstats['kills_bedwars']) / int(bwstats['deaths_bedwars']), 2)
        FKDR = round(int(bwstats['final_kills_bedwars']) / int(bwstats['final_deaths_bedwars']), 2)
        Beds_Broken1 = bwstats['beds_broken_bedwars']
        Winstreak = bwstats['winstreak']
        BBLR = round(int(bwstats['beds_broken_bedwars']) / int(bwstats['beds_lost_bedwars']), 2)
        WR = round(int(bwstats['wins_bedwars']) / int(bwstats["games_played_bedwars"]) * 100, 2)
        fWR = f"{WR}%"

        HYPIXEL_LINK2 = rq.get('https://api.hypixel.net/player?key={}&name={}'.format(HYPIXEL_API, args[1])).json()
        bwstats = HYPIXEL_LINK2['player']['stats']['Bedwars']
        bw_level2 = HYPIXEL_LINK2['player']['achievements']['bedwars_level']
        bw_coins2 = bwstats['coins']
        total_played2 = bwstats["games_played_bedwars"]
        total_won2 = bwstats['wins_bedwars']
        WR2 = round(int(bwstats['wins_bedwars']) / int(bwstats["games_played_bedwars"]) * 100, 2)
        fWR2 = f'{WR2}%'
        total_kills2 = bwstats['kills_bedwars']
        total_finals2 = bwstats['final_kills_bedwars']
        KDR2 = round(int(bwstats['kills_bedwars']) / int(bwstats['deaths_bedwars']), 2)
        FKDR2 = round(int(bwstats['final_kills_bedwars']) / int(bwstats['final_deaths_bedwars']), 2)
        Winstreak2 = bwstats['winstreak']
        Beds_Broken2 = bwstats['beds_broken_bedwars']
        BBLR2 = round(int(bwstats['beds_broken_bedwars']) / int(bwstats['beds_lost_bedwars']), 2)

        embed = discord.Embed(colour = discord.Colour.blue(), title = f"Comparing bedwars stats for {args[0]} and {args[1]} respectively.")
        await ctx.send(embed=embed)

        pretty.add_column('Criteria', ["Level", "Coins", "Games Played", 'Games Won', 'Win Rate', 'Total Kills', 'Final Kills','Final Kill/Death Ratio', 'Kill/Death Ratio', 'Winstreak', 'Beds Broken/Lost Ratio'])
        pretty.add_column(args[0], [bw_level1, bw_coins1, total_played1, total_won1, fWR1, total_kills1, total_finals1, FKDR1, KDR1, Beds_Broken1, Winstreak1, BBLR1])
        pretty.add_column(args[1], [bw_level2, bw_coins2, total_played2, total_won2, fWR2, total_kills2, total_finals2, FKDR2, KDR2, Beds_Broken2, Winstreak2, BBLR2])

        await ctx.send(f"```diff\n{pretty}```")


    elif len(args) == 3:
        pretty = prettytable.PrettyTable()
        HYPIXEL_LINK = rq.get('https://api.hypixel.net/player?key={}&name={}'.format(HYPIXEL_API, args[0])).json()
        bwstats = HYPIXEL_LINK['player']['stats']['Bedwars']
        bw_level = HYPIXEL_LINK['player']['achievements']['bedwars_level']
        bw_coins = bwstats['coins']
        total_played = bwstats["games_played_bedwars"]
        total_won = bwstats['wins_bedwars']
        total_kills = bwstats['kills_bedwars']
        total_finals = bwstats['final_kills_bedwars']
        KDR = round(int(bwstats['kills_bedwars']) / int(bwstats['deaths_bedwars']), 2)
        FKDR = round(int(bwstats['final_kills_bedwars']) / int(bwstats['final_deaths_bedwars']), 2)
        Winstreak = bwstats['winstreak']
        Beds_Broken1 = bwstats['beds_broken_bedwars']
        BBLR = round(int(bwstats['beds_broken_bedwars']) / int(bwstats['beds_lost_bedwars']), 2)
        WR = round(int(bwstats['wins_bedwars']) / int(bwstats["games_played_bedwars"]) * 100, 2)
        fWR = f"{WR}%"

        HYPIXEL_LINK2 = rq.get('https://api.hypixel.net/player?key={}&name={}'.format(HYPIXEL_API, args[1])).json()
        bwstats = HYPIXEL_LINK2['player']['stats']['Bedwars']
        bw_level2 = HYPIXEL_LINK2['player']['achievements']['bedwars_level']
        bw_coins2 = bwstats['coins']
        total_played2 = bwstats["games_played_bedwars"]
        total_won2 = bwstats['wins_bedwars']
        WR2 = round(int(bwstats['wins_bedwars']) / int(bwstats["games_played_bedwars"]) * 100, 2)
        fWR2 = f'{WR2}%'
        total_kills2 = bwstats['kills_bedwars']
        total_finals2 = bwstats['final_kills_bedwars']
        KDR2 = round(int(bwstats['kills_bedwars']) / int(bwstats['deaths_bedwars']), 2)
        FKDR2 = round(int(bwstats['final_kills_bedwars']) / int(bwstats['final_deaths_bedwars']), 2)
        Winstreak2 = bwstats['winstreak']
        Beds_Broken2 = bwstats['beds_broken_bedwars']
        BBLR2 = round(int(bwstats['beds_broken_bedwars']) / int(bwstats['beds_lost_bedwars']), 2)

        HYPIXEL_LINK3 = rq.get('https://api.hypixel.net/player?key={}&name={}'.format(HYPIXEL_API, args[2])).json()
        bwstats = HYPIXEL_LINK3['player']['stats']['Bedwars']
        bw_level3 = HYPIXEL_LINK3['player']['achievements']['bedwars_level']
        bw_coins3 = bwstats['coins']
        total_played3 = bwstats["games_played_bedwars"]
        total_won3 = bwstats['wins_bedwars']
        WR3 = round(int(bwstats['wins_bedwars']) / int(bwstats["games_played_bedwars"]) * 100, 2)
        fWR3 = f'{WR2}%'
        total_kills3 = bwstats['kills_bedwars']
        total_finals3 = bwstats['final_kills_bedwars']
        KDR3 = round(int(bwstats['kills_bedwars']) / int(bwstats['deaths_bedwars']), 2)
        FKDR3 = round(int(bwstats['final_kills_bedwars']) / int(bwstats['final_deaths_bedwars']), 2)
        Winstreak3 = bwstats['winstreak']
        Beds_Broken3 = bwstats['beds_broken_bedwars']
        BBLR3 = round(int(bwstats['beds_broken_bedwars']) / int(bwstats['beds_lost_bedwars']), 2)

        embed = discord.Embed(colour = discord.Colour.blue(), title = f"Comparing bedwars stats for {args[0]}, {args[1]} and {args[2]} respectively.")
        await ctx.send(embed=embed)

        pretty.add_column('Criteria', ["Level", "Coins", "Games Played", 'Games Won', 'Win Rate', 'Total Kills', 'Final Kills','Final Kill/Death Ratio', 'Kill/Death Ratio', 'Winstreak', 'Beds Broken/Lost Ratio'])
        pretty.add_column(args[0], [bw_level1, bw_coins1, total_played1, total_won1, fWR1, total_kills1, total_finals1, FKDR1, KDR1, Beds_Broken1, Winstreak1, BBLR1])
        pretty.add_column(args[1], [bw_level2, bw_coins2, total_played2, total_won2, fWR2, total_kills2, total_finals2, FKDR2, KDR2, Beds_Broken2, Winstreak2, BBLR2])
        pretty.add_column(args[2], [bw_level3, bw_coins3, total_played3, total_won3, fWR3, total_kills3, total_finals3, FKDR3, KDR3, Beds_Broken3, Winstreak3, BBLR3])
        await ctx.send(f"```diff\n{pretty}```")

    elif len(args) == 4:
        pretty = prettytable.PrettyTable()
        HYPIXEL_LINK1 = rq.get('https://api.hypixel.net/player?key={}&name={}'.format(HYPIXEL_API, args[0])).json()
        bwstats = HYPIXEL_LINK1['player']['stats']['Bedwars']
        bw_level1 = HYPIXEL_LINK1['player']['achievements']['bedwars_level']
        bw_coins1 = bwstats['coins']
        total_played1 = bwstats["games_played_bedwars"]
        total_won1 = bwstats['wins_bedwars']
        total_kills1 = bwstats['kills_bedwars']
        total_finals1 = bwstats['final_kills_bedwars']
        KDR1 = round(int(bwstats['kills_bedwars']) / int(bwstats['deaths_bedwars']), 2)
        FKDR1 = round(int(bwstats['final_kills_bedwars']) / int(bwstats['final_deaths_bedwars']), 2)
        Winstreak1 = bwstats['winstreak']
        BBLR1 = round(int(bwstats['beds_broken_bedwars']) / int(bwstats['beds_lost_bedwars']), 2)
        WR1 = round(int(bwstats['wins_bedwars']) / int(bwstats["games_played_bedwars"]) * 100, 2)
        fWR1 = f"{WR1}%"

        HYPIXEL_LINK2 = rq.get('https://api.hypixel.net/player?key={}&name={}'.format(HYPIXEL_API, args[1])).json()
        bwstats = HYPIXEL_LINK2['player']['stats']['Bedwars']
        bw_level2 = HYPIXEL_LINK2['player']['achievements']['bedwars_level']
        bw_coins2 = bwstats['coins']
        total_played2 = bwstats["games_played_bedwars"]
        total_won2 = bwstats['wins_bedwars']
        WR2 = round(int(bwstats['wins_bedwars']) / int(bwstats["games_played_bedwars"]) * 100, 2)
        fWR2 = f'{WR2}%'
        total_kills2 = bwstats['kills_bedwars']
        total_finals2 = bwstats['final_kills_bedwars']
        KDR2 = round(int(bwstats['kills_bedwars']) / int(bwstats['deaths_bedwars']), 2)
        FKDR2 = round(int(bwstats['final_kills_bedwars']) / int(bwstats['final_deaths_bedwars']), 2)
        Winstreak2 = bwstats['winstreak']
        BBLR2 = round(int(bwstats['beds_broken_bedwars']) / int(bwstats['beds_lost_bedwars']), 2)

        HYPIXEL_LINK3 = rq.get('https://api.hypixel.net/player?key={}&name={}'.format(HYPIXEL_API, args[2])).json()
        bwstats = HYPIXEL_LINK3['player']['stats']['Bedwars']
        bw_level3 = HYPIXEL_LINK3['player']['achievements']['bedwars_level']
        bw_coins3 = bwstats['coins']
        total_played3 = bwstats["games_played_bedwars"]
        total_won3 = bwstats['wins_bedwars']
        WR3 = round(int(bwstats['wins_bedwars']) / int(bwstats["games_played_bedwars"]) * 100, 2)
        fWR3 = f'{WR3}%'
        total_kills3 = bwstats['kills_bedwars']
        total_finals3 = bwstats['final_kills_bedwars']
        KDR3 = round(int(bwstats['kills_bedwars']) / int(bwstats['deaths_bedwars']), 2)
        FKDR3 = round(int(bwstats['final_kills_bedwars']) / int(bwstats['final_deaths_bedwars']), 2)
        Winstreak3 = bwstats['winstreak']
        BBLR3 = round(int(bwstats['beds_broken_bedwars']) / int(bwstats['beds_lost_bedwars']), 2)

        HYPIXEL_LINK4 = rq.get('https://api.hypixel.net/player?key={}&name={}'.format(HYPIXEL_API, args[3])).json()
        bwstats = HYPIXEL_LINK4['player']['stats']['Bedwars']
        bw_level4 = HYPIXEL_LINK4['player']['achievements']['bedwars_level']
        bw_coins4 = bwstats['coins']
        total_played4 = bwstats["games_played_bedwars"]
        total_won4 = bwstats['wins_bedwars']
        WR4 = round(int(bwstats['wins_bedwars']) / int(bwstats["games_played_bedwars"]) * 100, 2)
        fWR4 = f'{WR2}%'
        total_kills4 = bwstats['kills_bedwars']
        total_finals4 = bwstats['final_kills_bedwars']
        KDR4 = round(int(bwstats['kills_bedwars']) / int(bwstats['deaths_bedwars']), 2)
        FKDR4 = round(int(bwstats['final_kills_bedwars']) / int(bwstats['final_deaths_bedwars']), 2)
        Winstreak4 = bwstats['winstreak']
        BBLR4 = round(int(bwstats['beds_broken_bedwars']) / int(bwstats['beds_lost_bedwars']), 2)

        embed = discord.Embed(colour = discord.Colour.blue(), title = f"Comparing bedwars stats for {args[0]}, {args[1]}, {args[2]} and {args[3]} respectively.")
        await ctx.send(embed=embed)

        pretty.add_column('Criteria', ["Level", "Coins", "Games Played", 'Games Won', 'Win Rate', 'Total Kills', 'Final Kills','Final Kill/Death Ratio', 'Kill/Death Ratio', 'Winstreak', 'Beds Broken/Lost Ratio'])
        pretty.add_column(args[0], [bw_level1, bw_coins1, total_played1, total_won1, fWR1, total_kills1, total_finals1, FKDR1, KDR1, Beds_Broken1, Winstreak1, BBLR1])
        pretty.add_column(args[1], [bw_level2, bw_coins2, total_played2, total_won2, fWR2, total_kills2, total_finals2, FKDR2, KDR2, Beds_Broken2, Winstreak2, BBLR2])
        pretty.add_column(args[2], [bw_level3, bw_coins3, total_played3, total_won3, fWR3, total_kills3, total_finals3, FKDR3, KDR3, Beds_Broken3, Winstreak3, BBLR3])
        pretty.add_column(args[3], [bw_level4, bw_coins4, total_played4, total_won4, fWR4, total_kills4, total_finals4, FKDR4, KDR4, Beds_Broken4, Winstreak4, BBLR4])

        await ctx.send(f"```diff\n{pretty}```")

    elif len(args) == 5:
        pretty = prettytable.PrettyTable()
        HYPIXEL_LINK1 = rq.get('https://api.hypixel.net/player?key={}&name={}'.format(HYPIXEL_API, args[0])).json()
        bwstats = HYPIXEL_LINK1['player']['stats']['Bedwars']
        bw_level1 = HYPIXEL_LINK1['player']['achievements']['bedwars_level']
        bw_coins1 = bwstats['coins']
        total_played1 = bwstats["games_played_bedwars"]
        total_won1 = bwstats['wins_bedwars']
        total_kills1 = bwstats['kills_bedwars']
        total_finals1 = bwstats['final_kills_bedwars']
        KDR1 = round(int(bwstats['kills_bedwars']) / int(bwstats['deaths_bedwars']), 2)
        FKDR1 = round(int(bwstats['final_kills_bedwars']) / int(bwstats['final_deaths_bedwars']), 2)
        Winstreak1 = bwstats['winstreak']
        BBLR1 = round(int(bwstats['beds_broken_bedwars']) / int(bwstats['beds_lost_bedwars']), 2)
        WR1 = round(int(bwstats['wins_bedwars']) / int(bwstats["games_played_bedwars"]) * 100, 2)
        Beds_Broken1 = bwstats['beds_broken_bedwars']
        fWR1 = f"{WR1}%"

        HYPIXEL_LINK2 = rq.get('https://api.hypixel.net/player?key={}&name={}'.format(HYPIXEL_API, args[1])).json()
        bwstats = HYPIXEL_LINK2['player']['stats']['Bedwars']
        bw_level2 = HYPIXEL_LINK2['player']['achievements']['bedwars_level']
        bw_coins2 = bwstats['coins']
        total_played2 = bwstats["games_played_bedwars"]
        total_won2 = bwstats['wins_bedwars']
        WR2 = round(int(bwstats['wins_bedwars']) / int(bwstats["games_played_bedwars"]) * 100, 2)
        fWR2 = f'{WR2}%'
        total_kills2 = bwstats['kills_bedwars']
        total_finals2 = bwstats['final_kills_bedwars']
        KDR2 = round(int(bwstats['kills_bedwars']) / int(bwstats['deaths_bedwars']), 2)
        FKDR2 = round(int(bwstats['final_kills_bedwars']) / int(bwstats['final_deaths_bedwars']), 2)
        Winstreak2 = bwstats['winstreak']
        BBLR2 = round(int(bwstats['beds_broken_bedwars']) / int(bwstats['beds_lost_bedwars']), 2)
        Beds_Broken2 = bwstats['beds_broken_bedwars']

        HYPIXEL_LINK3 = rq.get('https://api.hypixel.net/player?key={}&name={}'.format(HYPIXEL_API, args[2])).json()
        bwstats = HYPIXEL_LINK3['player']['stats']['Bedwars']
        bw_level3 = HYPIXEL_LINK3['player']['achievements']['bedwars_level']
        bw_coins3 = bwstats['coins']
        total_played3 = bwstats["games_played_bedwars"]
        total_won3 = bwstats['wins_bedwars']
        WR3 = round(int(bwstats['wins_bedwars']) / int(bwstats["games_played_bedwars"]) * 100, 2)
        fWR3 = f'{WR3}%'
        total_kills3 = bwstats['kills_bedwars']
        total_finals3 = bwstats['final_kills_bedwars']
        KDR3 = round(int(bwstats['kills_bedwars']) / int(bwstats['deaths_bedwars']), 2)
        FKDR3 = round(int(bwstats['final_kills_bedwars']) / int(bwstats['final_deaths_bedwars']), 2)
        Beds_Broken3 = bwstats['beds_broken_bedwars']
        Winstreak3 = bwstats['winstreak']
        BBLR3 = round(int(bwstats['beds_broken_bedwars']) / int(bwstats['beds_lost_bedwars']), 2)

        HYPIXEL_LINK4 = rq.get('https://api.hypixel.net/player?key={}&name={}'.format(HYPIXEL_API, args[3])).json()
        bwstats = HYPIXEL_LINK4['player']['stats']['Bedwars']
        bw_level4 = HYPIXEL_LINK4['player']['achievements']['bedwars_level']
        bw_coins4 = bwstats['coins']
        total_played4 = bwstats["games_played_bedwars"]
        total_won4 = bwstats['wins_bedwars']
        Beds_Broken4 = bwstats['beds_broken_bedwars']
        WR4 = round(int(bwstats['wins_bedwars']) / int(bwstats["games_played_bedwars"]) * 100, 2)
        fWR4 = f'{WR4}%'
        total_kills4 = bwstats['kills_bedwars']
        total_finals4 = bwstats['final_kills_bedwars']
        KDR4 = round(int(bwstats['kills_bedwars']) / int(bwstats['deaths_bedwars']), 2)
        FKDR4 = round(int(bwstats['final_kills_bedwars']) / int(bwstats['final_deaths_bedwars']), 2)
        Winstreak4 = bwstats['winstreak']
        BBLR4 = round(int(bwstats['beds_broken_bedwars']) / int(bwstats['beds_lost_bedwars']), 2)

        HYPIXEL_LINK5 = rq.get('https://api.hypixel.net/player?key={}&name={}'.format(HYPIXEL_API, args[4])).json()
        bwstats = HYPIXEL_LINK5['player']['stats']['Bedwars']
        bw_level5 = HYPIXEL_LINK5['player']['achievements']['bedwars_level']
        bw_coins5 = bwstats['coins']
        total_played5 = bwstats["games_played_bedwars"]
        Beds_Broken5 = bwstats['beds_broken_bedwars']
        total_won5 = bwstats['wins_bedwars']
        WR5 = round(int(bwstats['wins_bedwars']) / int(bwstats["games_played_bedwars"]) * 100, 2)
        fWR5 = f'{WR5}%'
        total_kills5 = bwstats['kills_bedwars']
        total_finals5 = bwstats['final_kills_bedwars']
        KDR5 = round(int(bwstats['kills_bedwars']) / int(bwstats['deaths_bedwars']), 2)
        FKDR5 = round(int(bwstats['final_kills_bedwars']) / int(bwstats['final_deaths_bedwars']), 2)
        Winstreak5 = bwstats['winstreak']
        BBLR5 = round(int(bwstats['beds_broken_bedwars']) / int(bwstats['beds_lost_bedwars']), 2)

        embed = discord.Embed(colour = discord.Colour.blue(), title = f"Comparing bedwars stats for {args[0]}, {args[1]}, {args[2]}, {args[3]} and {args[4]} respectively.")
        await ctx.send(embed=embed)

        pretty.add_column('Criteria', ["Level", "Coins", "Games Played", 'Games Won', 'Win Rate', 'Total Kills', 'Final Kills','Final Kill/Death Ratio', 'Kill/Death Ratio', 'Winstreak', 'Beds Broken/Lost Ratio'])
        pretty.add_column(args[0], [bw_level1, bw_coins1, total_played1, total_won1, fWR1, total_kills1, total_finals1, FKDR1, KDR1, Beds_Broken1, Winstreak1, BBLR1])
        pretty.add_column(args[1], [bw_level2, bw_coins2, total_played2, total_won2, fWR2, total_kills2, total_finals2, FKDR2, KDR2, Beds_Broken2, Winstreak2, BBLR2])
        pretty.add_column(args[2], [bw_level3, bw_coins3, total_played3, total_won3, fWR3, total_kills3, total_finals3, FKDR3, KDR3, Beds_Broken3, Winstreak3, BBLR3])
        pretty.add_column(args[3], [bw_level4, bw_coins4, total_played4, total_won4, fWR4, total_kills4, total_finals4, FKDR4, KDR4, Beds_Broken4, Winstreak4, BBLR4])
        pretty.add_column(args[4], [bw_level5, bw_coins5, total_played5, total_won5, fWR5, total_kills5, total_finals5, FKDR5, KDR5, Beds_Broken5, Winstreak5, BBLR5])
        await ctx.send(f"```diff\n{pretty}```")

    elif len(args) == 6:
        pretty = prettytable.PrettyTable()
        HYPIXEL_LINK1 = rq.get('https://api.hypixel.net/player?key={}&name={}'.format(HYPIXEL_API, args[0])).json()
        bwstats = HYPIXEL_LINK1['player']['stats']['Bedwars']
        bw_level1 = HYPIXEL_LINK1['player']['achievements']['bedwars_level']
        bw_coins1 = bwstats['coins']
        total_played1 = bwstats["games_played_bedwars"]
        total_won1 = bwstats['wins_bedwars']
        total_kills1 = bwstats['kills_bedwars']
        total_finals1 = bwstats['final_kills_bedwars']
        KDR1 = round(int(bwstats['kills_bedwars']) / int(bwstats['deaths_bedwars']), 2)
        FKDR1 = round(int(bwstats['final_kills_bedwars']) / int(bwstats['final_deaths_bedwars']), 2)
        Winstreak1 = bwstats['winstreak']
        BBLR1 = round(int(bwstats['beds_broken_bedwars']) / int(bwstats['beds_lost_bedwars']), 2)
        Beds_Broken1 = bwstats['beds_broken_bedwars']
        WR1 = round(int(bwstats['wins_bedwars']) / int(bwstats["games_played_bedwars"]) * 100, 2)
        fWR1 = f"{WR1}%"

        HYPIXEL_LINK2 = rq.get('https://api.hypixel.net/player?key={}&name={}'.format(HYPIXEL_API, args[1])).json()
        bwstats = HYPIXEL_LINK2['player']['stats']['Bedwars']
        bw_level2 = HYPIXEL_LINK2['player']['achievements']['bedwars_level']
        bw_coins2 = bwstats['coins']
        Beds_Broken2 = bwstats['beds_broken_bedwars']
        total_played2 = bwstats["games_played_bedwars"]
        total_won2 = bwstats['wins_bedwars']
        WR2 = round(int(bwstats['wins_bedwars']) / int(bwstats["games_played_bedwars"]) * 100, 2)
        fWR2 = f'{WR2}%'
        total_kills2 = bwstats['kills_bedwars']
        total_finals2 = bwstats['final_kills_bedwars']
        KDR2 = round(int(bwstats['kills_bedwars']) / int(bwstats['deaths_bedwars']), 2)
        FKDR2 = round(int(bwstats['final_kills_bedwars']) / int(bwstats['final_deaths_bedwars']), 2)
        Winstreak2 = bwstats['winstreak']
        BBLR2 = round(int(bwstats['beds_broken_bedwars']) / int(bwstats['beds_lost_bedwars']), 2)

        HYPIXEL_LINK3 = rq.get('https://api.hypixel.net/player?key={}&name={}'.format(HYPIXEL_API, args[2])).json()
        bwstats = HYPIXEL_LINK3['player']['stats']['Bedwars']
        bw_level3 = HYPIXEL_LINK3['player']['achievements']['bedwars_level']
        bw_coins3 = bwstats['coins']
        total_played3 = bwstats["games_played_bedwars"]
        total_won3 = bwstats['wins_bedwars']
        WR3 = round(int(bwstats['wins_bedwars']) / int(bwstats["games_played_bedwars"]) * 100, 2)
        Beds_Broken3 = bwstats['beds_broken_bedwars']
        fWR3 = f'{WR3}%'
        total_kills3 = bwstats['kills_bedwars']
        total_finals3 = bwstats['final_kills_bedwars']
        KDR3 = round(int(bwstats['kills_bedwars']) / int(bwstats['deaths_bedwars']), 2)
        FKDR3 = round(int(bwstats['final_kills_bedwars']) / int(bwstats['final_deaths_bedwars']), 2)
        Winstreak3 = bwstats['winstreak']
        BBLR3 = round(int(bwstats['beds_broken_bedwars']) / int(bwstats['beds_lost_bedwars']), 2)

        HYPIXEL_LINK4 = rq.get('https://api.hypixel.net/player?key={}&name={}'.format(HYPIXEL_API, args[3])).json()
        bwstats = HYPIXEL_LINK4['player']['stats']['Bedwars']
        bw_level4 = HYPIXEL_LINK4['player']['achievements']['bedwars_level']
        bw_coins4 = bwstats['coins']
        Beds_Broken4 = bwstats['beds_broken_bedwars']
        total_played4 = bwstats["games_played_bedwars"]
        total_won4 = bwstats['wins_bedwars']
        WR4 = round(int(bwstats['wins_bedwars']) / int(bwstats["games_played_bedwars"]) * 100, 2)
        fWR4 = f'{WR4}%'
        total_kills4 = bwstats['kills_bedwars']
        total_finals4 = bwstats['final_kills_bedwars']
        KDR4 = round(int(bwstats['kills_bedwars']) / int(bwstats['deaths_bedwars']), 2)
        FKDR4 = round(int(bwstats['final_kills_bedwars']) / int(bwstats['final_deaths_bedwars']), 2)
        Winstreak4 = bwstats['winstreak']
        BBLR4 = round(int(bwstats['beds_broken_bedwars']) / int(bwstats['beds_lost_bedwars']), 2)

        HYPIXEL_LINK5 = rq.get('https://api.hypixel.net/player?key={}&name={}'.format(HYPIXEL_API, args[4])).json()
        bwstats = HYPIXEL_LINK5['player']['stats']['Bedwars']
        bw_level5 = HYPIXEL_LINK5['player']['achievements']['bedwars_level']
        bw_coins5 = bwstats['coins']
        total_played5 = bwstats["games_played_bedwars"]
        total_won5 = bwstats['wins_bedwars']
        Beds_Broken5 = bwstats['beds_broken_bedwars']
        WR5 = round(int(bwstats['wins_bedwars']) / int(bwstats["games_played_bedwars"]) * 100, 2)
        fWR5 = f'{WR5}%'
        total_kills5 = bwstats['kills_bedwars']
        total_finals5 = bwstats['final_kills_bedwars']
        KDR5 = round(int(bwstats['kills_bedwars']) / int(bwstats['deaths_bedwars']), 2)
        FKDR5 = round(int(bwstats['final_kills_bedwars']) / int(bwstats['final_deaths_bedwars']), 2)
        Winstreak5 = bwstats['winstreak']
        BBLR5 = round(int(bwstats['beds_broken_bedwars']) / int(bwstats['beds_lost_bedwars']), 2)

        HYPIXEL_LINK6 = rq.get('https://api.hypixel.net/player?key={}&name={}'.format(HYPIXEL_API, args[5])).json()
        bwstats = HYPIXEL_LINK6['player']['stats']['Bedwars']
        bw_level6 = HYPIXEL_LINK6['player']['achievements']['bedwars_level']
        bw_coins6 = bwstats['coins']
        total_played6 = bwstats["games_played_bedwars"]
        total_won6 = bwstats['wins_bedwars']
        WR6 = round(int(bwstats['wins_bedwars']) / int(bwstats["games_played_bedwars"]) * 100, 2)
        Beds_Broken6 = bwstats['beds_broken_bedwars']
        fWR6 = f'{WR6}%'
        total_kills6 = bwstats['kills_bedwars']
        total_finals6 = bwstats['final_kills_bedwars']
        KDR6 = round(int(bwstats['kills_bedwars']) / int(bwstats['deaths_bedwars']), 2)
        FKDR6 = round(int(bwstats['final_kills_bedwars']) / int(bwstats['final_deaths_bedwars']), 2)
        Winstreak6 = bwstats['winstreak']
        BBLR6 = round(int(bwstats['beds_broken_bedwars']) / int(bwstats['beds_lost_bedwars']))

        embed = discord.Embed(colour = discord.Colour.blue(), title = f"Comparing bedwars stats for {args[0]}, {args[1]}, {args[2]}, {args[3]}, {args[4]} and {args[5]} respectively.")
        await ctx.send(embed=embed)

        pretty.add_column('Criteria', ["Level", "Coins", "Games Played", 'Games Won', 'Win Rate', 'Total Kills', 'Final Kills','Final Kill/Death Ratio', 'Kill/Death Ratio', 'Winstreak', 'Beds Broken/Lost Ratio'])
        pretty.add_column(args[0], [bw_level1, bw_coins1, total_played1, total_won1, fWR1, total_kills1, total_finals1, FKDR1, KDR1, Beds_Broken1, Winstreak1, BBLR1])
        pretty.add_column(args[1], [bw_level2, bw_coins2, total_played2, total_won2, fWR2, total_kills2, total_finals2, FKDR2, KDR2, Beds_Broken2, Winstreak2, BBLR2])
        pretty.add_column(args[2], [bw_level3, bw_coins3, total_played3, total_won3, fWR3, total_kills3, total_finals3, FKDR3, KDR3, Beds_Broken3, Winstreak3, BBLR3])
        pretty.add_column(args[3], [bw_level4, bw_coins4, total_played4, total_won4, fWR4, total_kills4, total_finals4, FKDR4, KDR4, Beds_Broken4, Winstreak4, BBLR4])
        pretty.add_column(args[4], [bw_level5, bw_coins5, total_played5, total_won5, fWR5, total_kills5, total_finals5, FKDR5, KDR5, Beds_Broken5, Winstreak5, BBLR5])
        pretty.add_column(args[5], [bw_level6, bw_coins6, total_played6, total_won6, fWR6, total_kills6, total_finals6, FKDR6, KDR6, Beds_Broken6, Winstreak6, BBLR6])
        await ctx.send(f"```diff\n{pretty}```")
    else:
        await ctx.send("Cant compare statistics of more than 6 players simultaneously. Sorry.")


    

@client.command(aliases = ['sw', 'sws'])
async def swstats(ctx, name: str):
    HYPIXEL_LINK = rq.get('https://api.hypixel.net/player?key={}&name={}'.format(HYPIXEL_API, name)).json()
    swstats = HYPIXEL_LINK['player']['stats']['SkyWars']
    Winstreak = swstats['win_streak']
    Souls = swstats['souls']
    Played = swstats['games']
    Kills = swstats['kills']
    Won = swstats['wins']
    Lost = swstats['losses']
    Coins = swstats['coins']
    KDR = round(int(swstats['kills'])/int(swstats['deaths']), 2)
    WR = round(int(swstats['wins']) / int(swstats["games"]) * 100, 2)

    embed = discord.Embed(colour = discord.Colour.blue(), title = f"Skywars stats for {name}")


    embed.set_author(name = "Requested by {}".format(ctx.author.name), icon_url= f"{ctx.author.avatar_url}")
    embed.set_image(url = 'https://image.ibb.co/htOT5q/liUywIa.png')
    embed.add_field(name = "Souls", value = f"{Souls}", inline = False)
    embed.add_field(name = "Played", value = f"{Played}", inline = False)
    embed.add_field(name = "Kills", value = f"{Kills}", inline = False)
    embed.add_field(name = "Won", value = f"{Won}", inline = False)
    embed.add_field(name = "Lost", value = f"{Lost}", inline = False)
    embed.add_field(name = "Coins", value = f"{Coins}", inline = False)
    embed.add_field(name = "KDR", value = f"{KDR}", inline = False)
    embed.add_field(name = "WR", value = f"{WR}%", inline = False)

    await ctx.send(embed=embed)



client.run(Token)
