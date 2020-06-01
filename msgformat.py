## --------in hypixelapi.py--------------
## def convert(x,mode=0,formatMode=""):
##    return({"main":mainbody,"optional":optional,"mode":mode})
import random

def insertNoBreak(msg):
    #return(msg.replace(" ","‾"))
    return(msg.replace(" ","┈"))

def insertInvis(msg,n):
    for i in range(n):
        randomPos=random.randint(0,len(msg)-1)
        invischar="⛬⛫⛭⛮⛶"
        msg=msg[:randomPos]+invischar[random.randint(0,len(invischar)-1)]+msg[randomPos:]
    return(msg)

def chunks(l, n):
    for i in range(0, len(l), n):
        yield(l[i:i+n])

allknown=["bwstats"]
bots=["bwstats"]
announcement=insertNoBreak("")

def discordmsg():
    if "bwstats" not in bots:
        return(f'Discord; "/msg {bots[random.randint(0,len(bots)-1)]} +discord"')
    else:
        return(f'Discord; "/msg bwstats +discord"')

class formats:
    def __init__(self, bot_ign, party_max=8):
        self.bot_ign = bot_ign
        self.party_max = party_max
        
    def msg(self, raw,nextfkdr=False):
        modeLable=f"[{raw['mode']}]"
        pack=[]
        pack.append(discordmsg()) #pack.append( f'Discord; "/msg {self.bot_ign} +discord"' )
        pack.append( f"{modeLable:-^51}" )
        if nextfkdr: pack.append( insertNoBreak("       "+raw['optional']) )
        pack.append( insertNoBreak(raw['main']) )
        pack.append( f"{announcement:-^51}" )
        return(insertInvis(" ".join(pack),35))

    def party(self, raws, mode):
        modeDisplay=["OVERALL","SOLO","DOUBLES","3v3v3v3","4v4v4v4","4v4"]
        blocks = chunks(raws,4)
        for block in blocks:
            pack=[]
            pack.append(f'[{modeDisplay[mode]}]')
            for line in block: pack.append(insertNoBreak(line))
            if len(" ".join(pack))<200:
                yield(insertInvis(" ".join(pack),40))
            else:
                yield(" ".join(pack))
        if announcement!="":
            yield(announcement)

    def wrong_syntax(self):
        pack=[]
        pack.append(discordmsg()) #pack.append(f'Discord; "/msg {self.bot_ign} +discord"')
        pack.append(insertNoBreak(f'Use "/msg {self.bot_ign} username" for overall stats'))
        pack.append(insertNoBreak("Invite me to a party to check your teammates' stats"))
        pack.append(insertNoBreak('Find out more in Discord using the command above'))
        pack.append("_"*20)
        return(insertInvis(" ".join(pack),30))

    def party_too_large(self):
        pack=[]
        pack.append(f'max party size is {self.party_max}!!')
        return(insertInvis(" ".join(pack),30))

    def discord_request(self,verifyCode):
        pack=[]
        link = f'Discord; https://discord.gg/ZwJf3YS - '
        pack.append(insertNoBreak('           Your verification code is')+f' {verifyCode}')
        pack.append(insertNoBreak("send the code in the #verify chat channel within 2 minutes"))
        pack.append("_"*50)
        return(link+insertInvis(" ".join(pack),20))

    def party_mode(self,mode):
        modeDisplay=["OVERALL","SOLO","DOUBLES","3v3v3v3","4v4v4v4","4v4"]
        return(insertInvis(insertNoBreak(f"Got it! Next time you invite me I will show {modeDisplay[mode]} stats."),10))

    def overload(self,botassign="All_Bot_Are_Busy"):
        pack=[]
        pack.append(discordmsg())  #pack.append(f'Discord; "/msg {self.bot_ign} +discord"')
        pack.append(insertNoBreak("I'm currently under heavy load. (Party Only Mode)"))
        pack.append(insertNoBreak(f"Please use /msg {botassign} instead"))
        pack.append("_"*50)
        return(insertInvis(" ".join(pack),40))

    def discordpromote(self):
        pack=[]
        pack.append(discordmsg())  #pack.append(f'Discord; "/msg {self.bot_ign} +discord"')
        pack.append(insertNoBreak("Join the Discord for a lot more features"))
        pack.append(insertNoBreak("I could get muted anytime. So please join discord"))
        pack.append(insertNoBreak("There is a full list of online bots in there"))
        return(insertInvis(" ".join(pack),40))

    def promoteMinBot(self,botassign="bwstats"):
        pack=[]
        pack.append(f'Try "/msg {botassign} username"')
        pack.append(insertNoBreak(f'Please use "/p invite {botassign}" next time.'))
        return(" ".join(pack))

    def msgsendtomin(self):
        temp = bots[random.randint(0,len(bots)-1)]
        if temp!=self.bot_ign:
            return(insertInvis(f"-> Alternative Bot:. {temp} | Main Bot:. bwstats",10))
        return(None)

    
