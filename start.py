"""import bwstatscore

username=input("email:")
password=input("password:")
ign=input("ign:")
rate=input("Max request rate (20 for normal operation):")

bwstatsbot = bwstatscore.bot_thread(username,password,ign,rate)
bwstatsbot.start()"""

from __future__ import print_function
from minecraft import authentication
from minecraft.exceptions import YggdrasilError
from minecraft.networking.connection import Connection
from minecraft.networking.packets import Packet, clientbound, serverbound
from minecraft.compat import input

from threading import Thread
import datetime # for logging
import pickle   # for Object to file
import time
import sys
import json
import hypixelapi
import msgformat
import random
from importlib import reload

#: The base url for Ygdrassil requests
AUTH_SERVER = "https://authserver.mojang.com"
SESSION_SERVER = "https://sessionserver.mojang.com/session/minecraft"
# Need this content type, or authserver will complain
CONTENT_TYPE = "application/json"
HEADERS = {"content-type": CONTENT_TYPE}

class bot:
    def __init__(self, username, password, bot_ign, reply_rate=20):
        self.username = username
        self.password = password
        self.bot_ign  = bot_ign

        self.reply_rate = int(reply_rate)

        if self.bot_ign == "bwstats":
             self.reply_rate = 0

        if self.password!="" : #test for offline server (True for online mode)
            self.auth_token = authentication.AuthenticationToken()
            try: self.auth_token.authenticate(self.username, self.password)
            except YggdrasilError as e: print(e)
            print("Logged in as %s..." % self.auth_token.username)
            self.connection = Connection("mc.hypixel.net", 25565, auth_token=self.auth_token)
        else:
            self.connection = Connection("localhost", 25565, username=self.username)

        self.command_delay = 0
        self.msgQueue = []
        self.partyQueue = []
        self.commandQueue = []
        self.msgCurrentChannel = ""
        self.party = {"inP":False , "from":"" , "timestamp":0}
        self.partyConfig = {}
        self.playercooldown = {}
        self.cooldownTimer = time.time()
        self.heartbeat = time.time()+120
        self.heartbeatCooldown = time.time()+120
        self.msgformat = msgformat.formats(self.bot_ign,8) ## (ign, party_max)
        self.bots = {x:0 for x in msgformat.bots if x != self.bot_ign}
        self.quota = util.load_obj("quota")
        self.quotaChange = {}
        self.current_load = 0
        self.inQueue = False
        self.inQueueTime = 0
        self.debug = False
        self.minloadalts = "All_Bot_Are_Busy"
        self.muted = False
        self.msgErrorPending = []
        self.muteDuration = 3600
        self.unmutetime = 0
        self.muteheartbeat = 0
        self.mutereceivedelay = 0
        self.discordVerified = []

    def initialize(self):
        self.connection.register_packet_listener( self.handle_join_game, clientbound.play.JoinGamePacket)
        self.connection.register_packet_listener( self.handle_chat, clientbound.play.ChatMessagePacket)
        self.connection.connect()
        
    def disconnect(self):
        self.msgQueue = []
        self.partyQueue = []
        self.friendQueue = []
        self.connection.disconnect(True)
        
    def send_chat(self, text, delay=0.6, bypass=False):
        if not self.inQueue or bypass:
            text=text[:255] # limit to 255 characters
            packet = serverbound.play.ChatPacket()
            packet.message = text
            self.connection.write_packet(packet)
            if self.debug:
                debugtext="".join(x for x in text if x not in "-⛬⛫⛭⛮⛶_")
                print(debugtext)
        self.command_delay=time.time()
        time.sleep(delay*1.05)

    def handle_join_game(self, join_game_packet):
        self.heartbeat = time.time()-50
        self.heartbeatCooldown = time.time()-50
        time.sleep(0.5)
        self.send_chat("/p leave")
        print('Connected.')

    def handle_chat(self, chat_packet):
        try:
            chat_raw  = str(chat_packet.json_data)
            chat_json = json.loads(str(chat_packet.json_data))
            msg = util.raw_to_msg(chat_json)
            if not(self.muted):
                if ("red" in chat_raw and len(msg)<75 and "+]" not in msg) or self.debug:
                    debugtext="".join(x for x in msg if x not in "-⛬⛫⛭⛮⛶_")
                    print(debugtext)

                if ("red" in chat_raw and len(msg)<75 and "+]" not in msg):
                    mutedetect="".join(x for x in msg if x not in "-⛬⛫⛭⛮⛶_")
                    if "Your mute will expire in" in mutedetect:
                        self.muted = True
                        getduration = mutedetect[mutedetect.index("Your mute will expire in")+24:]
                        getduration = getduration.split()
                        getduration = [x.strip() for x in getduration if x.strip()[-1] in "dhms"]
                        self.muteDuration = 60
                        for i in getduration:
                            try:
                                 duration={"d":86400,"h":3600,"m":60,"s":1}
                                 self.muteDuration += duration[i[-1]] * int(i[:-1])
                            except Exception:
                                pass
                        self.unmutetime = time.time() + self.muteDuration
                        self.commandQueue.append({"command":"in_game"}) ## force limbo

                if "extra" in chat_json:
                    # On party request
                    if chat_raw.count("/party accept")>=2:
                        for data in chat_json["extra"]:
                            if "/party accept" in str(data):
                                user=data["clickEvent"]["value"].split()[-1]
                                if self.cooldowncheck(user,5): return  # cooldown
                                self.partyQueue.append({"mode":"queue","user":user})
                                return
                        return

                    # On heartbeat
                    elif "HeartBeat-KeepAlive" in chat_raw and "from" not in chat_raw.lower() and self.bot_ign in chat_raw:
                        try:
                            with open("verified.txt","r") as file:
                                self.discordVerified = [x for x in file.read().split("\n")]
                        except Exception as error_code:
                            self.discordVerified = []
                            print("load verified error -",error_code)
                        
                        if time.time()-self.heartbeat>70 and self.debug:
                            self.debug = False
                        self.heartbeat = time.time()
                        onlinehb = util.load_obj("onlinebot")
                        onlinehb.append([int(time.time()),self.bot_ign,min(int(max(self.current_load,1)/max(self.reply_rate,0.1)*100),100)])
                        onlinehb = [x for x in onlinehb if time.time()-x[0]<130]
                        util.save_obj(onlinehb,"onlinebot")
                        msgformat.bots = list(set([x[1] for x in onlinehb if time.time()-x[0]<130]))
                        self.bots = {}
                        for bot in onlinehb:
                            if bot[1] in self.bots:
                                self.bots[bot[1]] = max(bot[2],self.bots[bot[1]])
                            else:
                                self.bots[bot[1]] = bot[2]
                        self.minloadalts = ""
                        minloadbot = "All_Bot_Are_Busy"
                        minload = 100
                        for bot in self.bots:
                            if self.bots[bot]<minload:
                                minload = self.bots[bot]
                                minloadbot = bot
                        self.minloadalts = minloadbot
                        if self.debug or self.bot_ign == self.minloadalts:
                            for bot in self.bots:
                                print(bot,self.bots[bot],"%")
                            print(msgformat.bots)
                        return

                    # On party list return
                    elif "Party members" in chat_raw and "●" in chat_raw:
                        # Party members (2): [VIP] MinuteBrain ● [MVP+] Its_Me_Me ●
                        users = [user for user in msg[msg.index(":")+1:].split("●") if len(user)>1]
                        users = [user.split()[-1] for user in users]       # remove ranks
                        users.remove(self.bot_ign) # remove bot from the list
                        self.partyQueue = [{"mode":"list","user":users}] + self.partyQueue # put on top of the queue
                        return

                    # On msg request
                    elif ("From " in chat_raw) and ("light_purple" in chat_raw) and (self.bot_ign not in chat_raw):
                        self.chat_msg(msg)
                        return

                    # On open PM channel
                    elif {"text":" for the next 5 minutes. Use ","color":"green"} in chat_json["extra"]:
                        user=msg[msg.index("with")+4:msg.index("for")].split()[-1]
                        #print(user)
                        self.msgCurrentChannel=user
                        return

                    # On friend request
                    elif ("Click to" in chat_raw) and ("/f accept " in chat_raw):
                        for data in chat_json["extra"]:
                            if "/f accept " in str(data).lower():
                                user=data["clickEvent"]["value"].split()[-1]
                                if self.cooldowncheck(user,2): return  # cooldown
                                self.commandQueue.append({"command":"friend_request","user":user})
                                return
                        return

                    # On queue
                    elif ("The game starts in" in chat_raw) or ("has joined" in msg and "/" in msg) or ("has quit" in msg and "/" in msg) or ("The party leader, " in chat_raw and "yellow" in chat_raw):
                        if not(self.inQueue) and time.time()-self.inQueueTime>5:
                            self.inQueue=True
                            self.inQueueTime=time.time()
                            print("Blocked - "+self.party["from"])
                            self.cooldowncheck(self.party["from"],60)
                            self.party["inP"]=True
                            self.party["timestamp"] = time.time()+99999
                            time.sleep(1)
                            self.party["inP"]=True
                            self.send_chat("/p leave",1,True)
                            self.send_chat("/hub bw",0.7,True)
                            for _ in range(15): self.send_chat("/golimbo",0.07,True)
                            self.party["inP"]=True
                            self.party["timestamp"] = time.time()+5
                            self.inQueue=False
                            self.inQueueTime=time.time()
                        return

                    # On whereami respond
                    elif "You are currently connected to server" in msg and "aqua" in chat_raw.lower():
                        if "lobby" in msg:
                            self.commandQueue.append({"command":"in_lobby"})
                        else:
                            self.commandQueue.append({"command":"in_game"})
                        return
            else: # while muted
                self.heartbeat = time.time()
                if "extra" in chat_json:
                    if chat_raw.count("/party accept")>=2:
                        for data in chat_json["extra"]:
                            if "/party accept" in str(data):
                                user=data["clickEvent"]["value"].split()[-1]
                                print(user,self.minloadalts)
                                self.mutetransfer(user,self.minloadalts)
                                return
                        return
                    elif ("From " in chat_raw) and ("light_purple" in chat_raw) and (self.bot_ign not in chat_raw):
                        if "+send" not in msg.lower():
                            msg="".join([char for char in msg if char.lower() in "[]:abcdefghijklmnopqrstuvwxyz0123456789_ +/"])
                        msg=" ".join(msg.split()) # remove double space
                        msg=msg.replace("+ ","+").replace("++","+").replace("+]","]")
                        user=msg[:msg.index(":")].split()[-1]
                        if user not in self.bots:
                            print(user,self.minloadalts)
                            self.mutetransfer(user,self.minloadalts)
                        return

        except Exception as error_code:
            print("chat handle error!!",error_code)

