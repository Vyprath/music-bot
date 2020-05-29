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
 
    embed.add_field(name="ID:", value=member.id,inline = False)
    embed.add_field(name="Guild name:", value=member.display_name, inline = False)
 
    embed.add_field(name="Created at:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"), inline = False)
    embed.add_field(name="Joined at:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"), inline = False)
 
    embed.add_field(name=f"Roles ({len(roles)})", value=" ".join([role.mention for role in roles]), inline = False)
    embed.add_field(name="Top role:", value=member.top_role.mention, inline = False)
 
    embed.add_field(name="Bot?", value=member.bot, inline = False)
 
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
async def bwcomparison(ctx, name: str, name2: str):


    pretty = prettytable.PrettyTable()

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

    HYPIXEL_LINK2 = rq.get('https://api.hypixel.net/player?key={}&name={}'.format(HYPIXEL_API, name2)).json()
    bw_level2 = HYPIXEL_LINK2['player']['achievements']['bedwars_level']
    bw_coins2 = HYPIXEL_LINK2['player']['stats']['Bedwars']['coins']
    total_played2 = HYPIXEL_LINK2['player']['stats']['Bedwars']["games_played_bedwars"]
    total_won2 = HYPIXEL_LINK2['player']['stats']['Bedwars']['wins_bedwars']
    total_kills2 = HYPIXEL_LINK2['player']['stats']['Bedwars']['kills_bedwars']
    total_finals2 = HYPIXEL_LINK2['player']['stats']['Bedwars']['final_kills_bedwars']
    KDR2 = round(int(HYPIXEL_LINK2['player']['stats']['Bedwars']['kills_bedwars']) / int(HYPIXEL_LINK2['player']['stats']['Bedwars']['deaths_bedwars']), 2)
    FKDR2 = round(int(HYPIXEL_LINK2['player']['stats']['Bedwars']['final_kills_bedwars']) / int(HYPIXEL_LINK2['player']['stats']['Bedwars']['final_deaths_bedwars']), 2)
    Winstreak2 = HYPIXEL_LINK2['player']['stats']['Bedwars']['winstreak']
    BBLR2 = round(int(HYPIXEL_LINK2['player']['stats']['Bedwars']['beds_broken_bedwars']) / int(HYPIXEL_LINK2['player']['stats']['Bedwars']['beds_lost_bedwars']), 2)

    embed = discord.Embed(colour = discord.Colour.blue(), title = f"Comparing bedwars stats for {name} and {name2} respectively.")

    pretty.add_column('Criteria', ["Level", "Coins", "Games Played", 'Games Won', 'Total Kills', 'Final Kills','Final Kill/Death Ratio', 'Kill/Death Ratio', 'Winstreak', 'Beds Broken/Lost Ratio'])
    pretty.add_column(name, [bw_level, bw_coins, total_played, total_won, total_kills, total_finals, FKDR, KDR, Winstreak, BBLR])
    pretty.add_column(name2, [bw_level2, bw_coins2, total_played2, total_won2, total_kills2, total_finals2, FKDR2, KDR2, Winstreak2, BBLR2])




    await ctx.send(f"```{pretty}```")





client.run(Token)
