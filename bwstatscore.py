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

class util:
    def raw_to_msg(msg_json):
        try:
            msg=""
            #print(msg_json)
            if "text" in msg_json:
                msg+=msg_json["text"]
            if "extra" in msg_json:
                for i in msg_json["extra"]:
                    if "text" in i:
                        msg+=i["text"]
            return(msg)
        except Exception as error_code:
            print(error_code)
            return("")

    def save_obj(obj, name):
        with open('obj/'+ name + '.pkl', 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

    def load_obj(name):
        with open('obj/' + name + '.pkl', 'rb') as f:
            return pickle.load(f)

    class multithreading:
        def __init__(self, users, mode=0):
            self.userlist = users
            self.output = {}
            self.mode = mode
        def getplayerdata(self,user,mode=0):
            global output
            data=hypixelapi.getPlayer(user,hypixelapi.nextKey())
            text=hypixelapi.convert(data,mode,"party")["main"]
            self.output[user]=text
        def start(self):
            self.threads = list()
            for user in self.userlist: self.threads.append(Thread(target=self.getplayerdata, args=(user,self.mode,)))
            for thread in self.threads: thread.start()
            for thread in self.threads: thread.join()

    def dict_increment(dic,key,n):
        if key in dic:  dic[key] += n
        else:           dic[key] = n

    def dict_combine(large_dict,small_dict):
        for key in list(small_dict):
            util.dict_increment(large_dict,key,small_dict[key])

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
        try:
            with open("verified.txt","r") as file:
                self.discordVerified = [x for x in file.read().split("\n")]
        except Exception:
            self.discordVerified = []
        print("verified loaded", len(self.discordVerified))

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

    def mutetransfer(self,user,assignedbot):
        if assignedbot in list(self.bots) and assignedbot != self.bot_ign:
            transfer = util.load_obj("mutedtransfer")
            transfer.append([int(time.time()),user,assignedbot])
            while True:
                try:
                    util.save_obj(transfer,"mutedtransfer")
                    break
                except Exception:
                    print("failed to save")
                    time.sleep(0.1)

    def mutereceive(self):
        if time.time() - self.mutereceivedelay > 3:
            self.mutereceivedelay = time.time()
            transfer = util.load_obj("mutedtransfer")
            transfer = [x for x in transfer if time.time()-x[0]<4]
            myjob = [x for x in transfer if x[2] == self.bot_ign]
            if len(myjob)>0:
                transfer = [x for x in transfer if x[2] != self.bot_ign]
                while True:
                    try:
                        util.save_obj(transfer,"mutedtransfer")
                        break
                    except Exception:
                        print("failed to save")
                        time.sleep(0.1)

                for job in myjob:
                    user = job[1]
                    if hypixelapi.getPlayer(user,hypixelapi.nextKey())["msgsetting"]:
                        while time.time()-self.command_delay<0.7: time.sleep(0.05)
                        self.send_chat(f"/msg {user} "+msgformat.insertInvis("Please msg/party me instead!",10),0.4)
                    else:
                        if not self.party["inP"]:
                            self.commandQueue.append({"command":"send_command","send":f"/f remove {user}"})
                            self.commandQueue.append({"command":"send_command","send":f"/f {user}"})

    def chat_msg(self,msg):
        if "+send" not in msg.lower():
            msg="".join([char for char in msg if char.lower() in "[]:abcdefghijklmnopqrstuvwxyz0123456789_ +/"])
        msg=" ".join(msg.split()) # remove double space
        msg=msg.replace("+ ","+").replace("++","+").replace("+]","]")
        # >>> x="From [VIP] MinuteBrain: test agu1 agu2"
        # >>> x[:x.index(":")].split()[-1]
        # 'MinuteBrain'
        # >>> x[x.index(":")+1:].split()
        # ['test', 'agu1', 'agu2']
        user=msg[:msg.index(":")].split()[-1] 
        agus=msg[msg.index(":")+1:].split()
        
        mode=0  ##stats mode
        if len(agus)>1 and "+send" not in "".join(agus).lower():
            mode=agus[-1]
            mode=mode.replace("4v4","5").replace("44","5")
            if mode in [str(x) for x in range(6)]:
                mode=int(mode)
                agus.pop(-1)
            else:
                mode=0

        #print(user,agus,mode)

        if self.cooldowncheck(user,1) and user.lower() not in ["minutebrain","7types","0utplay3d"]: return # player cooldown

        # commands
        if "+" in msg:
            command = agus[0]
            if command.lower() in ["+discord","+verify"]:
                self.msgQueue = [{"msgMode":"discord_request","user":user}] + self.msgQueue
                
            elif command.lower() == "+send" and user.lower() in ["minutebrain","0utplay3d"] and len(agus)>=2:
                self.commandQueue.append({"command":"send_command","send":" ".join(agus[1:])})
                
            elif command.lower() in ["+pmode","+setpartymode"]:
                self.partyConfig[user]=mode
                self.msgQueue = [{"msgMode":"party_mode","user":user,"mode":mode}] + self.msgQueue

            elif command.lower() == "+resetcooldown" and user.lower() in ["minutebrain","0utplay3d"]:
                self.playercooldown = {}

            elif command.lower() in ["+reload","+reloadall"] and user.lower() in ["minutebrain","0utplay3d"] + [x.lower() for x in list(self.bots)]:
                if command.lower()=="+reloadall":
                    botstoreload = [x.lower() for x in list(self.bots) if self.bot_ign.lower() != x.lower()]
                    for bot in botstoreload:
                        random_msg="".join([chr(random.randint(64,125)) for _ in range(10)])
                        self.commandQueue.append({"command":"send_command","send":f"/t {bot} +reload {random_msg}"})
                    print("Reloading",str(botstoreload))
                print("Reloading...")
                try:
                    reload(msgformat)
                    self.msgformat = msgformat.formats(self.bot_ign,8) ## (ign, party_max)
                    self.bots = {x:0 for x in msgformat.bots if x != self.bot_ign}
                except Exception:
                    print("Fail to reload msgformat")
                try:
                    reload(hypixelapi)
                except Exception:
                    print("Fail to reload hypixelapi")
            elif command.lower() == "+debug" and user.lower() in ["minutebrain","0utplay3d"]:
                self.debug = not(self.debug)
                print(f"Debug : {self.debug}")
            else:
                self.msgQueue = [{"msgMode":"wrong_syntax","user":user}] + self.msgQueue

            return

        # stats request
        if self.current_load <= self.reply_rate:
            if len(agus)>0:
                if len(agus[0])<=16:
                    if len(agus)==1:
                        self.msgQueue = [{"msgMode":"stats","replyto":user ,"username":agus[0] ,"mode":mode }] + self.msgQueue
                    elif len(agus)>1 and len(agus)<=4:
                        self.msgQueue = [{"msgMode":"stats_multiple","replyto":user ,"username":agus ,"mode":mode }] + self.msgQueue
                    else:
                        self.msgQueue = [{"msgMode":"wrong_syntax","user":user}] + self.msgQueue
                else:
                    self.msgQueue = [{"msgMode":"wrong_syntax","user":user}] + self.msgQueue
            else:
                self.msgQueue = [{"msgMode":"wrong_syntax","user":user}] + self.msgQueue
        else:
            self.msgQueue = [{"msgMode":"overload","user":user}] + self.msgQueue
        
    def cooldowncheck(self,user,n=1):
        if user not in self.playercooldown:
            self.playercooldown[user] = n
        else:
            if self.playercooldown[user]>6:
                self.playercooldown[user] += 3
            else:
                self.playercooldown[user] += n

        if self.playercooldown[user]>100:
            self.commandQueue.append({"command":"ignore","user":user})
            print("Ignored",user,self.playercooldown[user])
            return True
        elif self.playercooldown[user]>6:
            print("Reject spam from",user,self.playercooldown[user])
            return True
        else:
            self.current_load += 1
            return False
    def cooldown_tick(self):
        if time.time()-self.cooldownTimer>=6:
            self.cooldownTimer=time.time()
            for user in list(self.playercooldown):
                self.playercooldown[user]-=1
            self.playercooldown={x:self.playercooldown[x] for x in list(self.playercooldown) if self.playercooldown[x]>0}
    
    def msg_tick(self):
        if len(self.msgQueue)>0:
            currentQueue = self.msgQueue.pop(0)
            if currentQueue["msgMode"] == "stats":
                replyTo = currentQueue["replyto"]
                username = currentQueue["username"]
                if currentQueue["username"].lower() == "me":
                    username = currentQueue["replyto"]
                mode = currentQueue["mode"]
                util.dict_increment(self.quotaChange,replyTo,1)
                if self.msgCurrentChannel != replyTo:
                    while time.time()-self.command_delay<0.5: time.sleep(0.05)
                    self.send_chat("/r",0)
                data = hypixelapi.getPlayer(username,hypixelapi.nextKey())
                raw  = hypixelapi.convert(data,mode,"msg")
                msg  = self.msgformat.msg(raw,replyTo.lower()==username.lower())
                while time.time()-self.command_delay<0.7: time.sleep(0.05)
                if replyTo.lower() == self.msgCurrentChannel.lower():
                    print(f"(R) {replyTo} --> {username}")
                    if random.randint(0,2) == 0:
                        if replyTo not in self.discordVerified:
                            self.send_chat(self.msgformat.discordpromote(),0.7)
                        else:
                            temptext=self.msgformat.msgsendtomin()
                            if temptext != None:
                                self.send_chat(temptext,0.7)
                    self.send_chat(msg,0.4)
                    if replyTo in self.msgErrorPending:
                        print(f"(R) {replyTo} --> MSG policy warning")
                        self.msgErrorPending.remove(replyTo)
                        while time.time()-self.command_delay<0.7: time.sleep(0.05)
                        self.send_chat("I couldn't reply you last times. Please make sure to set the MSG policy to None to prevent this",0.4)
                else:
                    if hypixelapi.getPlayer(replyTo,hypixelapi.nextKey())["msgsetting"]:
                        print(f"(MSG) {replyTo} --> {username}")
                        self.send_chat(f"/msg {replyTo} "+msg,0.4)
                    else:
                        print(f"(MSG) Couldn't reply to {replyTo}")
                        self.msgErrorPending.append(replyTo)

            if currentQueue["msgMode"] == "stats_multiple":
                replyTo = currentQueue["replyto"]
                usernames = currentQueue["username"]
                mode = currentQueue["mode"]
                util.dict_increment(self.quotaChange,replyTo,len(usernames))
                if self.msgCurrentChannel != replyTo:
                    while time.time()-self.command_delay<0.6: time.sleep(0.05)
                    self.send_chat("/r",0)
                handle = util.multithreading(usernames,mode)
                handle.start()
                raws = [handle.output[x] for x in list(handle.output)]
                msg = list(self.msgformat.party(raws,mode))[0]
                msg = msgformat.insertInvis(msg,20)
                while time.time()-self.command_delay<0.7: time.sleep(0.05)
                if replyTo.lower() == self.msgCurrentChannel.lower():
                    print(f"(R) {replyTo} --> {usernames}")
                    self.send_chat(msg,0.4)
                else:
                    if hypixelapi.getPlayer(replyTo,hypixelapi.nextKey())["msgsetting"]:
                        print(f"(MSG) {replyTo} --> {username}")
                        self.send_chat(f"/msg {replyTo} "+msg,0.4)
                    else:
                        print(f"(MSG) Can't send msg {replyTo}")
    
            elif currentQueue["msgMode"] == "discord_request":
                user = currentQueue["user"]
                temp = util.load_obj("discordverify")
                verifyCode=f"{random.randint(0000,9999):04d}"
                while verifyCode in temp: verifyCode=f"{random.randint(0000,9999):04d}" #prevent duplicate code
                temp[verifyCode]={"user":user,"timestamp":time.time()}
                util.save_obj(temp,"discordverify")
                print(f"Discord: {user} --> {verifyCode}")
                while time.time()-self.command_delay<0.5: time.sleep(0.05)
                self.send_chat("/r "+self.msgformat.discord_request(verifyCode))

            elif currentQueue["msgMode"] == "wrong_syntax":
                print(f"Wrong_syntax: {currentQueue['user']}")
                while time.time()-self.command_delay<0.5: time.sleep(0.05)
                self.send_chat("/r "+self.msgformat.wrong_syntax(),0.5)

            elif currentQueue["msgMode"] == "party_mode":
                print(f"Party Mode: {currentQueue['user']} --> {currentQueue['mode']}")
                while time.time()-self.command_delay<0.5: time.sleep(0.05)
                self.send_chat("/r "+self.msgformat.party_mode(currentQueue["mode"]),0.5)

            elif currentQueue["msgMode"] == "overload":
                print(f"Overload: {currentQueue['user']}")
                while time.time()-self.command_delay<0.5: time.sleep(0.05)
                minloadbot = "All_Bot_Are_Busy"
                minload = 100
                for bot in self.bots:
                    if self.bots[bot]<minload:
                        minload = self.bots[bot]
                        minloadbot = bot
                self.send_chat("/r "+self.msgformat.overload(minloadbot),0.5)

    def party_chat_transit(self,msg,delay=0.5):
        while len(self.msgQueue)>0:
            self.msg_tick()
            time.sleep(0.05)
        while time.time()-self.command_delay<delay: time.sleep(0.05)
        self.send_chat(msg,delay)
        self.party["timestamp"]=time.time()

    def party_tick(self):
        if len(self.partyQueue)>0 and len(self.msgQueue)==0:
            currentQueue=self.partyQueue.pop(0)
            if currentQueue["mode"]=="queue" and self.party["inP"]: # requeue if in party
                #print("Party Requeued !!")
                self.partyQueue.append(currentQueue)
            else:
                if currentQueue["mode"]=="queue":
                    self.party = {"inP": True , "from": currentQueue["user"]}
                    #print("Party accepted -",self.party["from"],self.quota["MinuteBrain"])
                    util.dict_increment(self.quotaChange,self.party["from"],1)
                    while time.time()-self.command_delay<0.5: time.sleep(0.05) # prevent sending command too fast
                    self.party_chat_transit(f"/p accept {self.party['from']}",0.4)
                    self.party_chat_transit(f"/pl",0.3)
                elif currentQueue["mode"]=="list":
                    users=currentQueue['user']
                    print("Party list -"," ".join(users))
                    for user in users:
                        if user.lower() != self.bot_ign and user in list(self.bots):
                            print("multiple bots in party!!!!!")
                            self.cooldowncheck(self.party["from"],20)
                            while time.time()-self.command_delay<2:
                                self.msg_tick()
                                time.sleep(0.05)
                            self.send_chat("/p leave")
                            self.party["inP"]=False
                            return
                    if len(users) <= self.msgformat.party_max:
                        if self.party["from"] in self.partyConfig:
                            mode = self.partyConfig[self.party["from"]]
                        else:
                            mode = 0
                        handle = util.multithreading(users,mode)
                        handle.start()
                        raws = [handle.output[x] for x in list(handle.output)]
                        msgs = self.msgformat.party(raws,mode)
                        while time.time()-self.command_delay<0.3: time.sleep(0.05)
                        for msg in msgs : self.party_chat_transit(f"/pchat {msg}",0.3)
                    else:
                        while time.time()-self.command_delay<0.3: time.sleep(0.05)
                        self.party_chat_transit("/pchat "+self.msgformat.party_too_large(),0.3)
                    if random.randint(0,1) == 0:
                        self.party_chat_transit(f"/pchat "+self.msgformat.discordpromote(),0.3)
                    self.party_chat_transit(f"/pchat "+self.msgformat.promoteMinBot(self.minloadalts),0.3)
                    while time.time()-self.command_delay<1:
                        self.msg_tick()
                        time.sleep(0.05)
                    self.send_chat("/p leave")
                    self.party["inP"]=False
        if self.party["inP"] and time.time()-self.party["timestamp"]>2:
            print("Party timeout",self.party["from"])
            while time.time()-self.command_delay<0.8: time.sleep(0.05)
            self.send_chat("/p leave",0.3)
            self.party["inP"]=False

    def command_tick(self):
        if len(self.commandQueue)>0:
            currentQueue=self.commandQueue.pop(0)

            if currentQueue["command"]=="friend_request":
                print(f"Friend accepted - {currentQueue['user']}")
                while time.time()-self.command_delay<0.7: time.sleep(0.05)
                self.send_chat(f"/f accept {currentQueue['user']}",0.3)

            elif currentQueue["command"]=="send_command":
                print(f"Command sent - {currentQueue['send']}")
                while time.time()-self.command_delay<0.7: time.sleep(0.05)
                self.send_chat(currentQueue["send"],0.3,True)

            elif currentQueue["command"]=="in_game":
                print("Warp to Lobby")
                while time.time()-self.command_delay<0.5: time.sleep(0.05)
                self.send_chat("/hub bw",0.3,True)

            elif currentQueue["command"]=="in_lobby":
                print("Warp to Limbo")
                for _ in range(15): self.send_chat("/golimbo",0.07,True)
                self.send_chat("/whereami")

            elif currentQueue["command"]=="ignore":
                print(f"Ignored - {currentQueue['user']}")
                while time.time()-self.command_delay<0.7: time.sleep(0.05)
                self.send_chat(f"/ignore add {currentQueue['user']}")
            
    def heartbeat_tick(self):
        if time.time()-self.heartbeat>610:
            self.connection.disconnect(True)
            raise Exception("No heartbeat detect! Reconnecting")
            return

        if time.time()-self.heartbeat>120 and not(self.debug):
            #self.debug = True
            self.connection.connect()
            #print("Debug : True")
            print("Reconnecting")

        if time.time()-self.heartbeat>60 and time.time()-self.heartbeatCooldown>30:
            heartbeat_length = time.time()-self.heartbeat
            random_msg="".join([chr(random.randint(64,125)) for _ in range(30)])
            while time.time()-self.command_delay<0.5: time.sleep(0.7)
            self.send_chat(f"/msg {self.bot_ign} HeartBeat-KeepAlive {random_msg}",0.3)  #comment this to test heartbeat restart system.
            self.heartbeatCooldown = time.time()
            self.send_chat("/whereami",0.2)
            
            self.quota = util.load_obj("quota")
            util.dict_combine(self.quota,self.quotaChange)
            util.save_obj(self.quota,"quota")
            self.quotaChange = {}

            if self.current_load>self.reply_rate:
                print("Overloaded!! <-----")
            self.current_load = 0

            if time.time()-self.heartbeat>300:
                self.connection.connect()
                print("Reconnecting")

            print(f"Heartbeat ({int(heartbeat_length)}sec)")
            return

    def mute_heartbeat_tick(self):
        if time.time() - self.muteheartbeat>60:
            self.muteheartbeat = time.time()
            try:
                onlinehb = util.load_obj("onlinebot")
                onlinehb = [x for x in onlinehb if time.time()-x[0]<130]
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
            except Exception: pass
            while time.time()-self.command_delay<0.5: time.sleep(0.7)
            self.send_chat("/whereami",0.2)
        if time.time() - self.heartbeat>300:
            self.connection.disconnect(True)
            raise Exception("No heartbeat detect! Reconnecting")

            
    def tick(self):
        if self.muted:  self.mute_heartbeat_tick()
        else:           self.heartbeat_tick()
        try:
            self.mutereceive()
            self.party_tick()
            self.msg_tick()
            self.command_tick()
            self.cooldown_tick()
        except Exception as error_code:
            print("Tick error! (skiped) -",error_code)

class bot_thread:
    def __init__(self, username, password, bot_ign, reply_rate=20):
        self.username = username
        self.password = password
        self.bot_ign = bot_ign
        self.reply_rate = int(reply_rate)

        self.mutedelay = 0

    def start(self):
        while True:
            try:
                self.bot_handle = bot(self.username,self.password,self.bot_ign,self.reply_rate)
                self.bot_handle.initialize()
                while True:
                    try:
                        time.sleep(0.05)
                        self.bot_handle.tick()
                        if self.bot_handle.muted:
                            if int(self.bot_handle.unmutetime-time.time())>0:
                                if time.time() - self.mutedelay >= 360:
                                    self.mutedelay = time.time()
                                    try:
                                        mutehb = util.load_obj("mutedbot")
                                        mutehb.append([int(time.time()),self.bot_ign,int(self.bot_handle.unmutetime-time.time())])
                                        mutehb = [x for x in mutehb if time.time()-x[0]<900]
                                        util.save_obj(mutehb,"mutedbot")
                                    except Exception as error_code:
                                        print("error to write the file - ",error_code)
                                        time.sleep(0.5)
                                    print("Muted", round(int(self.bot_handle.unmutetime-time.time())/3600,1), "hr left")
                            else:
                                self.muted = self.bot_handle.muted = False

                    except Exception as error_code:
                        self.bot_handle.connection.disconnect(True)
                        print("Bye! ", error_code)
                        time.sleep(30)
                        self.bot_handle = bot(self.username,self.password,self.bot_ign,self.reply_rate)
                        self.bot_handle.initialize()
            except Exception as error_code:
                self.bot_handle = 0
                print("Bye! ", error_code)
                time.sleep(120)

