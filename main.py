import discord
from discord.ext import commands
from discord.utils import get
import random
import os
import requests as rq
import re
import json
import datetime
import prettytable

client = commands.Bot(command_prefix = '?')
TestToken = 'NzE2MjExMzgzNzU0MDMxMTU1.XtId3Q.9Wypv3NT8ywhV3yAKZvFn-ouslY'
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

@client.command()
async def info(ctx, member: discord.Member):
 
    roles = [role for role in member.roles]
 
    embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)
 
    embed.set_author(name=f"User Info - {member}")
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
 
    embed.add_field(name="ID:", value=member.id,inline = True)
    embed.add_field(name="Name:", value=member.display_name, inline = True)
 
    embed.add_field(name="Created at:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"), inline = True)
    embed.add_field(name="Joined at:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"), inline = True)
 
    embed.add_field(name=f"Roles ({len(roles)})", value=" ".join([role.mention for role in roles]), inline = True)
    embed.add_field(name="Top role:", value=member.top_role.mention, inline = True)
 
    embed.add_field(name="Bot?", value=member.bot, inline = True)
 
    await ctx.send(embed=embed)


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




@client.command(aliases = ['bedwars', 'bw'])
async def bwstats(ctx, name: str):
    HYPIXEL_LINK = rq.get('https://api.hypixel.net/player?key={}&name={}'.format(HYPIXEL_API, name)).json()
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
    BBLR = round(int(bwstats['beds_broken_bedwars']) / int(bwstats['beds_lost_bedwars']), 2)
    WR = round(int(bwstats['wins_bedwars']) / int(bwstats["games_played_bedwars"]) * 100, 2)


    embed = discord.Embed(colour = discord.Colour.blue(), title = f"Bedwars stats for {name}")

    embed.set_author(name = "Requested by {}".format(ctx.author.name), icon_url= f"{ctx.author.avatar_url}")
    embed.set_image(url = 'https://cdn.discordapp.com/attachments/706135793185456221/715261418953375773/image.png')
    embed.add_field(name = "Level", value = f"{bw_level}", inline = False)
    embed.add_field(name = "Coins", value = f"{bw_coins}", inline = False)
    embed.add_field(name = "Games Played", value = f"{total_played}", inline = False)
    embed.add_field(name = "Games Won", value = f"{total_won}", inline = False)
    embed.add_field(name = "Win Rate", value = f"{WR}%", inline = False)
    embed.add_field(name = "Kills", value = f"{total_kills}", inline = False)
    embed.add_field(name = "Final Kills", value = f"{total_finals}", inline = False)
    embed.add_field(name = "Kills/Death Ratio", value = f"{KDR}", inline = False)
    embed.add_field(name = "Final Kills/Death Ratio", value = f"{FKDR}", inline = False)
    embed.add_field(name = "Winstreak", value = f"{Winstreak}", inline = False)
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
        BBLR2 = round(int(bwstats['beds_broken_bedwars']) / int(bwstats['beds_lost_bedwars']), 2)

        embed = discord.Embed(colour = discord.Colour.blue(), title = f"Comparing bedwars stats for {args[0]} and {args[1]} respectively.")
        await ctx.send(embed=embed)

        pretty.add_column('Criteria', ["Level", "Coins", "Games Played", 'Games Won', 'Win Rate', 'Total Kills', 'Final Kills','Final Kill/Death Ratio', 'Kill/Death Ratio', 'Winstreak', 'Beds Broken/Lost Ratio'])
        pretty.add_column(args[0], [bw_level, bw_coins, total_played, total_won, fWR, total_kills, total_finals, FKDR, KDR, Winstreak, BBLR])
        pretty.add_column(args[1], [bw_level2, bw_coins2, total_played2, total_won2, fWR2, total_kills2, total_finals2, FKDR2, KDR2, Winstreak2, BBLR2])

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
        BBLR3 = round(int(bwstats['beds_broken_bedwars']) / int(bwstats['beds_lost_bedwars']), 2)

        embed = discord.Embed(colour = discord.Colour.blue(), title = f"Comparing bedwars stats for {args[0]}, {args[1]} and {args[2]} respectively.")
        await ctx.send(embed=embed)

        pretty.add_column('Criteria', ["Level", "Coins", "Games Played", 'Games Won', 'Win Rate', 'Total Kills', 'Final Kills','Final Kill/Death Ratio', 'Kill/Death Ratio', 'Winstreak', 'Beds Broken/Lost Ratio'])
        pretty.add_column(args[0], [bw_level, bw_coins, total_played, total_won, fWR, total_kills, total_finals, FKDR, KDR, Winstreak, BBLR])
        pretty.add_column(args[1], [bw_level2, bw_coins2, total_played2, total_won2, fWR2, total_kills2, total_finals2, FKDR2, KDR2, Winstreak2, BBLR2])
        pretty.add_column(args[2], [bw_level3, bw_coins3, total_played3, total_won3, fWR3, total_kills3, total_finals3, FKDR3, KDR3, Winstreak3, BBLR3])

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
        pretty.add_column(args[0], [bw_level1, bw_coins1, total_played1, total_won1, fWR1, total_kills1, total_finals1, FKDR1, KDR1, Winstreak1, BBLR1])
        pretty.add_column(args[1], [bw_level2, bw_coins2, total_played2, total_won2, fWR2, total_kills2, total_finals2, FKDR2, KDR2, Winstreak2, BBLR2])
        pretty.add_column(args[2], [bw_level3, bw_coins3, total_played3, total_won3, fWR3, total_kills3, total_finals3, FKDR3, KDR3, Winstreak3, BBLR3])
        pretty.add_column(args[3], [bw_level4, bw_coins4, total_played4, total_won4, fWR4, total_kills4, total_finals4, FKDR4, KDR4, Winstreak4, BBLR4])

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
        pretty.add_column(args[0], [bw_level1, bw_coins1, total_played1, total_won1, fWR1, total_kills1, total_finals1, FKDR1, KDR1, Winstreak1, BBLR1])
        pretty.add_column(args[1], [bw_level2, bw_coins2, total_played2, total_won2, fWR2, total_kills2, total_finals2, FKDR2, KDR2, Winstreak2, BBLR2])
        pretty.add_column(args[2], [bw_level3, bw_coins3, total_played3, total_won3, fWR3, total_kills3, total_finals3, FKDR3, KDR3, Winstreak3, BBLR3])
        pretty.add_column(args[3], [bw_level4, bw_coins4, total_played4, total_won4, fWR4, total_kills4, total_finals4, FKDR4, KDR4, Winstreak4, BBLR4])
        pretty.add_column(args[4], [bw_level5, bw_coins5, total_played5, total_won5, fWR5, total_kills5, total_finals5, FKDR5, KDR5, Winstreak5, BBLR5])
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
        pretty.add_column(args[0], [bw_level1, bw_coins1, total_played1, total_won1, fWR1, total_kills1, total_finals1, FKDR1, KDR1, Winstreak1, BBLR1])
        pretty.add_column(args[1], [bw_level2, bw_coins2, total_played2, total_won2, fWR2, total_kills2, total_finals2, FKDR2, KDR2, Winstreak2, BBLR2])
        pretty.add_column(args[2], [bw_level3, bw_coins3, total_played3, total_won3, fWR3, total_kills3, total_finals3, FKDR3, KDR3, Winstreak3, BBLR3])
        pretty.add_column(args[3], [bw_level4, bw_coins4, total_played4, total_won4, fWR4, total_kills4, total_finals4, FKDR4, KDR4, Winstreak4, BBLR4])
        pretty.add_column(args[4], [bw_level5, bw_coins5, total_played5, total_won5, fWR5, total_kills5, total_finals5, FKDR5, KDR5, Winstreak5, BBLR5])
        pretty.add_column(args[5], [bw_level6, bw_coins6, total_played6, total_won6, fWR6, total_kills6, total_finals6, FKDR6, KDR6, Winstreak6, BBLR6])
        await ctx.send(f"```diff\n{pretty}```")
    else:
        await ctx.send("Cant compare statistics of more than 6 players simultaneously. Sorry.")










    

#@client.command(aliases = ['sw', 'sws'])
#async def swstats(ctx, name: str):
 #   HYPIXEL_LINK = rq.get('https://api.hypixel.net/player?key={}&name={}'.format(HYPIXEL_API, name)).json()
    #swstats = HYPIXEL_API['player']['stats']['SkyWars']
   # Souls = swstats['souls']









client.run(Token)