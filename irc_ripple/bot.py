from api import ripple_api as ripple
import json
import asyncio
import bottom
import requests
import pymysql
import re
from dispatcher import Dispatcher, connector, cooldown
import importlib
import os
import sys
import psutil
import logging

with open("/home/discord/bots/DiscordBot/irc_ripple/config.json", "r") as f: 
    config = json.load(f)

connection = pymysql.connect(host=config['db_host'], user=config['db_user'], passwd=config['db_pass'], db=config['db_table'])
connection.autocommit(True)
cursor = connection.cursor(pymysql.cursors.DictCursor)

ripple_bot = bottom.Client(host=config["ripple_server"], port=6667, ssl=False)

print("Starting AdminBot. If it doesn't logon within 5 seconds check for errors!")
    
class RippleBot(Dispatcher):
    def shutdown(self, nick, message, channel):
        if nick in config['ripple_owners']:
            ripple_bot.send("privmsg", target=nick, message="Reading Config File")
            ripple_bot.send("privmsg", target=nick, message="Calculating")
            ripple_bot.send("privmsg", target=nick, message="You are in the admin list. Shutting down!")
            quit()
        else:
            ripple_bot.send("privmsg", target=nick, message="Reading Config File")
            ripple_bot.send("privmsg", target=nick, message="Calculating")
            ripple_bot.send("privmsg", target=nick, message="Something went wrong. Please try again later when you're in the admin list!")

    @cooldown(10)
    def ingame(self, nick, message, channel):
        ripple_bot.send("privmsg", target=nick, message="Nyo and Howl, HAHAHAHAHA. Please dont kill me ;D")

    @cooldown(10)
    def help(self, nick, message, channel):
        ripple_bot.send("privmsg", target=nick, message="I am simple. Try me out.")
        ripple_bot.send("privmsg", target=nick, message="These are my commands:")
        ripple_bot.send("privmsg", target=nick, message="!help/!commands, !meme, !project, !rank, !clear, !love all, !request sid/bid, !accept sid/bid")
    
    @cooldown(30)
    def rank(self, nick, message, channel):
        if nick in config['ripple_owners'] or nick == "Veii":
            ripple_bot.send("privmsg", target=nick, message="All Loved/Unranked Maps are now Ranked. If not check database!")
            cursor.execute("UPDATE beatmaps SET ranked = REPLACE(ranked, '0', '2')")
            cursor.execute("UPDATE beatmaps SET ranked = REPLACE(ranked, '5', '2')")
            cursor.execute("UPDATE beatmaps SET ranked = REPLACE(ranked, '3', '2')")
            cursor.execute("UPDATE beatmaps SET ranked_status_freezed = REPLACE(ranked_status_freezed, '0', '1')")
        else:
            ripple_bot.send("privmsg", target=nick, message="You don't have permission to use this command!")

    @cooldown(30)
    def restrict (self, nick, message, channel):
        if nick in config['ripple_owners']:
            ripple_bot.send("privmsg", target=nick, message="All users that was restricted are now unrestricted")
            cursor.execute("UPDATE users SET privileges = REPLACE(privileges, '6', '7')")
            cursor.execute("UPDATE users SET privileges = REPLACE(privileges, '2', '7')")
        else:
            ripple_bot.send("privmsg", target=nick, message="You dont have permission to use this command!")

    @cooldown(5)
    def request(self, nick, message, channel):
        bid = re.search("([0-9]+?)(?:\s|$|\?|&)", message).group(1)
        r = ripple.user(name=nick)
        id = r["id"]
        userid = id
        cursor.execute("SELECT song_name FROM beatmaps WHERE beatmap_id = %s", [bid])
        row = cursor.fetchone()
        if channel != None:
            ripple_bot.send("privmsg", target="#requests", message=("[http://osu.ppy.sh/b/" + bid + " " + row["song_name"] + "] has been requested to be ranked!"))
        else:
            ripple_bot.send("privmsg", target=nick, message=("[http://osu.ppy.sh/b/" + bid + " " + row["song_name"] + "] has been requested to be ranked!"))
        cursor.execute("INSERT INTO rank_requests (userid, bid, type, time, blacklisted) VALUES(%s, %s, %s, %s, %s)", [userid, bid, "b", 0, 0])
        connection.commit()

    @cooldown(5)
    def clear(self, nick, message, channel):
    	userid = re.search("([0-9]+?)(?:\s|$|\?|&)", message).group(1)
    	if nick == "Akuma":
    		ripple_bot.send("privmsg", target=nick, message="Scores for the specific user has been deleted.")
    		cursor.execute("DELETE FROM scores WHERE userid = (%s)", [userid])
    	else:
    		ripple_bot.send("privmsg", target=nick, message="You dont have permission to use this command!")
    	connection.commit()

    @cooldown(5)
    def accept(self, nick, message, channel):
        bid = re.search("([0-9]+?)(?:\s|$|\?|&)", message).group(1)
        cursor.execute("SELECT song_name FROM beatmaps WHERE beatmap_id = %s", [bid])
        row = cursor.fetchone()
        if nick in config['ripple_owners']:
            ripple_bot.send("privmsg", target="#requests", message=("[http://osu.ppy.sh/b/" + bid + " " + row["song_name"] + "] is now ranked"))
            cursor.execute("UPDATE beatmaps SET ranked = 2 WHERE beatmap_id = %s", [bid])
            cursor.execute("DELETE FROM rank_requests WHERE bid = (%s)", [bid])
            connection.commit()
        else:
            ripple_bot.send("privmsg", target="#requests", message="You dont have permission to use this command!")

    @cooldown(5)
    def setid(self, nick, message, channel):
        bid = re.search("([0-9]+?)(?:\s|$|&)", message).group(1)
        cursor.execute("SELECT song_name FROM beatmaps WHERE beatmapset_id = %s", [bid])
        row = cursor.fetchone()
        if nick in config['ripple_owners']:
            ripple_bot.send("privmsg", target="#requests", message=("[http://osu.ppy.sh/s/" + bid + " " + row["song_name"] + "] is now ranked"))
            cursor.execute("UPDATE beatmaps SET ranked = 2 WHERE beatmapset_id = %s", [bid])
            cursor.execute("DELETE FROM rank_requests WHERE bid = (%s)", [bid])
            connection.commit()
        else:
            ripple_bot.send("privmsg", target="#requests", message="You dont have permission to use this command!")

    @cooldown(5)
    def rsid(self, nick, message, channel):
        bid = re.search("([0-9]+?)(?:\s|$|&)", message).group(1)
        r = ripple.user(name=nick)
        id = r["id"]
        userid = id
        cursor.execute("SELECT song_name FROM beatmaps WHERE beatmapset_id = %s", [bid])
        row = cursor.fetchone()
        if channel != None:
            ripple_bot.send("privmsg", target="#requests", message=("[http://osu.ppy.sh/s/" + bid + " " + row["song_name"] + "] has been requested to be ranked!"))
        else:
            ripple_bot.send("privmsg", target=nick, message=("[http://osu.ppy.sh/s/" + bid + " " + row["song_name"] + "] has been requested to be ranked!"))
        cursor.execute("INSERT INTO rank_requests (userid, bid, type, time, blacklisted) VALUES(%s, %s, %s, %s, %s)", [userid, bid, "s", 0, 0])
        connection.commit()
        

    @cooldown(5)
    def project(self, nick, message, channel):
        ripple_bot.send("privmsg", target=channel, message="Source Code for this bot can be found [http://git.blosu.net/Diabloxx/AdminBot here!]")

    @cooldown(2)
    def apirequest(self, nick, message, channel): 
        userid = re.search("([0-9]+?)(?:\s|$|&)", message).group(1)
        try:
            request = requests.get("http://test.blosu.net/api/v1/get_user", params={"u" : userid})
            return json.loads(request.text)
            ripple_bot.send("privmsg", target=channel, message="Hi")
        except requests.exceptions.RequestException as e:
            return
        else:
            return
        connection.commit()

    def restart(self, nick, message, channel):
        if nick in config['ripple_owners'] or nick == "Veii":
            ripple_bot.send("privmsg", target=channel, message="The bot is restarting!")
            try:
                p = psutil.Process(os.getpid())
                for handler in p.get_open_files() + p.connections():
                    os.close(handler.fd)
            except Exception:
                logging.error("")
            python = sys.executable
            os.execl(python, python, *sys.argv)
        
        
    
    def command_patterns(self):
        return (
            ('!shutdown', self.shutdown),
            ('!commands', self.help),
            ('!meme', self.ingame),
            ('!rank', self.rank),
            ('!project', self.project),
            ('!help', self.help),
            ('!clear', self.clear),
            ('!love all', self.restrict),
            ('!request bid', self.request),
            ('!accept sid', self.accept),
            ('!request set', self.rsid),
            ('!accept set', self.setid),
            ('!santa', self.apirequest),
            ('!restart', self.restart)
        )
ripple_dispatcher = RippleBot(ripple_bot)
connector(ripple_bot, ripple_dispatcher, config["ripple_username"], ["#requests", "#haitai", "#osu", "#beatmaps"], config["ripple_password"])
ripple_bot.loop.create_task(ripple_bot.connect())
ripple_bot.loop.run_forever()
