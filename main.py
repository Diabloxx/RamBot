#Normal python module import
import discord
import json
import random
import asyncio
import requests
import os
import sys
import psutil
import logging
import subprocess
import pymysql
import threading
#from folders import
from discord.ext import commands
from api import mirrorsearchapi as mirror
from api import ripple_api as ripple

with open("./configs/config.json", "r") as f: 
    config = json.load(f) 

with open("./configs/mysql.json", "r") as f:
	mysql = json.load(f)

connection = pymysql.connect(host=mysql['host'], user=mysql['user'], passwd=mysql['pass'], db=mysql['table'])
connection.autocommit(True)
cursor = connection.cursor(pymysql.cursors.DictCursor)


description = ''' Shitty Bot '''
bot = discord.Client()
bot = commands.Bot(command_prefix='!', description=description)

def admin_or_permissions():
    def predicate(ctx):
        return role_or_permissions(ctx, lambda r: r.name == config['moderator_role'])

def is_owner():
    return commands.check(lambda ctx: is_owner_check(ctx.message))

@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name=config['game']))
    print('Logged in as')
    print(bot.user.name)
    print("https://discordapp.com/oauth2/authorize?client_id=" + bot.user.id + "&scope=bot")
    print('------')

def is_owner_check(message):
    if message.author.id == config['admins']:
        return True
    else:
        return False

@bot.command()
@is_owner()
async def shutdown():
    await bot.say("REVENGE! REM I WILL GET MY REVENGE!")
    await bot.logout()
    await bot.close()

@bot.command()
@is_owner()
async def game(newgame : str):
    await bot.change_status(game=discord.Game(name=newgame))
    await bot.say("Changed game!", delete_after=5)

@bot.command(pass_context=True, no_pm=True)
@commands.cooldown(1, 30, commands.BucketType.user)
async def avatar(ctx, member : discord.Member = None):
    await bot.say(member.avatar_url)

@bot.command(name="8ball")
@commands.cooldown(1, 10, commands.BucketType.user)
async def eight_ball(*text):
    await bot.say(random.choice(config['answers']))

@bot.command(name="search", pass_context=True)
async def search(ctx, search):
    msg = ""
    m = mirror.search(name=search, limit=10)
    if search in config['memes']:
        await bot.say(random.choice(config['dankmemes']))
    else:
        if m[0]["code"] == 69:
            for i in range(0, len(m)):
                artist = m[i]["artist"]
                title = m[i]["title"]
                creator = m[i]["creator"]
                bmid = m[i]["id"]
                msg += (artist + " - " + title + " by " + creator + " | http://m.blosu.net/" + bmid + ".osz" + "\n")
            await bot.say(msg)
            if len(m) >= 10:
                await bot.say("For more maps go to http://m.blosu.net/search.php?&name={}".format(str(search.replace(" ", "%20"))))
            with open("./statistics/searches.txt", mode='a') as file:
                file.write('Item Searched > ' + search + '\n')
            print(str(search))
        else:
            await bot.say("Beatmap not found.")

@bot.command()
@commands.cooldown(1, 3, commands.BucketType.user)
async def project():
    await bot.say("You can find the source code for this bot at http://git.blosu.net/Diabloxx/DiscordBot")

@bot.command(pass_context=True)
@commands.cooldown(1, 3, commands.BucketType.user)
async def roll(ctx, number=100):
    n = str(random.randrange(0, number))
    await bot.say("You rolled " + n + ".")

@bot.command(pass_context=True)
@commands.cooldown(1, 3, commands.BucketType.user)
async def user(ctx, userid=999):
    try:
        request = requests.get("http://test.blosu.net/api/v1/users/full", params={"id" : userid})
        j = json.loads(request.text)
        await bot.say("The selected player's name is " + j["username"] + " " + "http://test.blosu.net/u/" + str(j["id"]))
    except requests.exceptions.RequestException as e:
        await bot.say("API is ded")

@bot.command(pass_context=True)
@commands.cooldown(1, 5, commands.BucketType.user)
async def mcafee(ctx):
    await bot.send_file(ctx.message.channel, './images/mcafee.png')

#Updates Bot from git
@bot.command(pass_context=True)
@is_owner()
async def update():
    await bot.say(os.popen('git pull origin master').read())

#Restart Command
@bot.command()
@is_owner()
async def restart():
    await bot.say("Bot is restarting, please stand by.")
    try:
        p = psutil.Process(os.getpid())
        for handler in p.get_open_files() + p.connections():
            os.close(handler.fd)
    except Exception:
        logging.error("")
    python = sys.executable
    os.execl(python, python, *sys.argv)

@bot.command(pass_context=True)
@commands.cooldown(1, 5, commands.BucketType.user)
async def image(ctx):
    await bot.send_file(ctx.message.channel, random.choice(config['images']))

@bot.command(pass_context=True)
@commands.cooldown(1, 5, commands.BucketType.user)
async def rem(ctx):
    await bot.send_file(ctx.message.channel, './images/rem.gif')

@bot.command()
@is_owner()
async def ripplebot():
    request = requests.get("http://c.blosu.net/api/v1/isOnline?id=1003")
    j = json.loads(request.text)
    if j['result'] == False:
        def runweb():   
            subprocess.check_output("python3 irc_ripple/bot.py", shell=True)
        thread = threading.Thread(target=runweb, args=())
        thread.daemon = True
        thread.start() 
        await bot.say("Starting AdminBot. If it doesn't logon within 5 seconds check for errors!")
    else:
        await bot.say("AdminBot should already be online!")

@bot.command()
@is_owner()
async def getpid():
    await bot.say(os.popen('ps aux | grep python').read())

@bot.command(pass_context=True)
@is_owner()
async def kill(ctx, processid=None):
    os.system("kill " + processid)




bot.run(config["token"])