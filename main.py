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
Token = 'NzExMjQ0NDc2MTk4Mjg5NDM4.XtAIFw.kAv75FBKQfw3nJnUiCYo4dFWxpg'
YOUTUBE_API = 'AIzaSyDmhOLQv6tNdYaElKnNGAhIq7kCl5gGsZA'
HYPIXEL_API = '6cd7ce31-00e7-4f4d-9ce2-60af5bcc4bb8'

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



client.run(Token)
