import discord
from discord.ext import commands
from discord.utils import get
import random
import os
import youtube_dl
import shutil

client = commands.Bot(command_prefix = 'h!')
Token = 'NzExMjQ0NDc2MTk4Mjg5NDM4.XstsPw.XL8xXNcYWs7w5Ph23fo1lh1Ec2M'
YOUTUBE_API = 'AIzaSyDmhOLQv6tNdYaElKnNGAhIq7kCl5gGsZA'

@client.event
async def on_ready():
    print('Bot is ready.')
    await client.change_presence(status = discord.Status.idle, activity = discord.Game('Contact Moe#4035 if any errors persist.'))


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
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild = ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        await ctx.send(f"Joined{channel}")


@client.command(pass_context = True)
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild = ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        await ctx.send(f"Left{channel}")


@client.command(pass_context = True, aliases = ['p'])
async def play(ctx, song_name: str):
    song_pack = rq.get("https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={}&key={}".format(song_name, YOUTUBE_API)).json()
    song_url = "https://www.youtube.com/watch?v={}".format(song_pack['items'][0]['id']['videoId'])

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
                    if file.endswith("mp3"):
                        os.rename(file, 'song.mp3')

                voice.play(discord.FFmpegPCMAudio("song.mp3"), after = lambda e: check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.7

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
            print('Removed old song file')
    except PermissionError:
        print("Trying to delete song file, but, it is being played.")
        await ctx.send("ERROR: Music Playing")
        return


    Queue_infile = os.path.isdir("./Queue")
    try:
        Queue_folder = "./Queue"
        if Queue_infile is True:
            print("Removed old Queue folder")
            shutil.rmtree(Queue_folder)
    except:
        print("No old queue folder")

    await ctx.send("Getting everything ready now")

    voice = get(client.voice_clients, guild = ctx.guild)

    ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'postprocessors':[{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([song_url])

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            print(f"Renamed File: {file}\n")
            os.rename(file, "song.mp3")

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after = lambda e: check_queue())
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.7

    nname = name.rsplit("-", 2)
    await ctx.send(f"Playing: {nname[0]}")
    print("Playing\n")


@client.command(pass_context = True, aliases = ['pa', 'pau'])
async def pause(ctx):

    voice = get(client.voice_clients, guild = ctx.guild)

    if voice and voice.is_playing():
        print("Music paused")
        voice.pause()
        await ctx.send("Music paused")
    else:
        print("Music not playing. Pause failed.")
        await ctx.send('Music not playing. Pause failed.')


@client.command(pass_context = True, aliases=['r', 'res'])
async def resume(ctx):

    voice = get(client.voice_clients, guild = ctx.guild)

    if voice and voice.is_paused():
        print("Resumed music")
    else:
        print("Music is not paused")
        await ctx.send("Music is not paused")


@client.command(pass_context = True, aliases=['s', 'ski'])
async def skip(ctx):
    voice = get(client.voice_clients, guild = ctx.guild)
    queues.clear()

    if voice and voice.is_playing():
        print("Music skipped")
        voice.stop()
        await ctx.send("Music skipped")
    else:
        print("No music playing. Could not skip.")
        await ctx.send("No music playing. Could not skip.")

# ty for reading this far. Here you go. 7779, 7777, 7742, 7745, 7720 and 7717
# to get more, co-operate further.

queues = {}

@client.command(pass_context = True, aliases=['q', 'que'])
async def queue(ctx, url: str):
    Queue_infile = os.path.isdir("./Queue")
    if Queue_infile is False:
        os.mkdir("Queue")
    DIR = os.path.abspath(os.path.realpath("Queue"))
    q_num = len(os.listdir(DIR))
    q_num += 1
    add_queue = True

    while add_queue:
        if q_num in queues:
            q_num+=1
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
        print('Downloading audio now\n')
        ydl.download([song_url])
    await ctx.send("Adding song" + str(q_num) + "to the queue")

    print("Song added to queue/n")

client.run(Token)
