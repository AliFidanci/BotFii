import discord
from discord.ext import commands
from discord.utils import get as dcGet
import youtube_dl
import time
from requests import get
import asyncio

class song: 
  def __init__(self, name, duration,totalSec,webpage_url, url2): 
    self.name = name 
    self.duration = duration
    self.totalSec = totalSec
    self.url2 = url2
    self.webpage_url = webpage_url

class music(commands.Cog):
  def __init__(self, client):
    self.client = client
    self.playIcon = "⏯️"
    self.newQ = {}
    self.reactions = ["👍", "👎"]
    self.selcuk = ["🇸", "🇪", "🇱", "🇨", "🇺", "🇰"]
    self.alifii = ["🇦", "🇱", "🇮"]

  async def is_playing_checker(self, ctx):
    is_playing = ctx.voice_client.is_playing()
    print("is playing status = ",is_playing)
    print("biten dahil liste uzunluğu= ",len(self.newQ["_"+str(ctx.guild.id)]))
    if not is_playing:
      if not len(self.newQ["_"+str(ctx.guild.id)]) == 0:
        self.newQ["_"+str(ctx.guild.id)].pop(0)
      if len(self.newQ["_"+str(ctx.guild.id)]) > 0:
        await self.playing(ctx, self.newQ["_"+str(ctx.guild.id)][0])
        print("listede şarkı var")
      else:
        await ctx.send("```Hocam işim bitti benim. Çalacak bir şey kalmadı```")
        print("şarkılar bitti")
  
  @commands.command(name='join', aliases=['gel', 'j','gelburaya'])
  async def join(self, ctx):
    self.newQ["_"+str(ctx.guild.id)] = []
    await ctx.send(f'{ctx.author.name}, you are currently in {ctx.guild.name} ({ctx.guild.id}).')
    if ctx.author.voice is None:
      await ctx.send("```Bir ses kanalina gir de yanina geleyim```")
      return 0

    voice_channel = ctx.author.voice.channel

    if ctx.voice_client is None:
      await voice_channel.connect()
      await ctx.send("```<"+voice_channel.name+"> kanalı bekle beni ben geliyorum```")
    else:
      bot_channel = ctx.voice_client.channel
      if bot_channel.name == voice_channel.name :
        await ctx.send("```Bilader zaten yan yanayiz```") 
      else:
        await ctx.send("```Ben <"+voice_channel.name+"> kanalına geçiyorum. Öptm.```")
        await ctx.voice_client.move_to(voice_channel)

  @commands.command(name='disconnect', aliases=['dc', 'git','defol'])
  async def disconnect(self, ctx):
    self.newQ["_"+str(ctx.guild.id)] = []
    await ctx.send("```Öptüm baaaayy!```")
    await ctx.voice_client.disconnect()


  @commands.command(name='play', aliases=['cal', 'p','çal'])
  async def play(self, ctx, *args):
  
    arg = self.listToString(args)

    #join check again :/
    if ctx.author.voice is None:
      await ctx.send("```Bir ses kanalina gir de yanina geleyim```")
      return 0

    voice_channel = ctx.author.voice.channel
    if not "_"+str(ctx.guild.id) in self.newQ:
      self.newQ["_"+str(ctx.guild.id)] = []

    if ctx.voice_client is None:
      await voice_channel.connect()
    else:
      bot_channel = ctx.voice_client.channel
      if bot_channel.name != voice_channel.name :
        await ctx.voice_client.move_to(voice_channel)
    #Join check end

    #is playing check
    is_playing = ctx.voice_client.is_playing()
    #print('is playing? ',is_playing)
    #is_playing end

    #ctx.voice_client.stop()
    info = self.search(arg)
    self.addList(info, ctx)
    if not is_playing:
      await self.playing(ctx, self.newQ["_"+str(ctx.guild.id)][0])
    else: 
      await ctx.send('```'+info["title"]+' listeye eklendi```')
    return True

  @commands.command(name='stop', aliases=['s','sus','dur'])
  async def stop(self, ctx):
    ctx.voice_client.stop()
    await ctx.send('```Durdum abi.```')

  @commands.command(name='clear', aliases=['c','temizle','lt'])
  async def clear(self, ctx):
    if "_"+str(ctx.guild.id) in self.newQ:
      if len(self.newQ["_"+str(ctx.guild.id)]) > 0:
        self.newQ["_"+str(ctx.guild.id)] = []
      await ctx.send("```Listede şarkı kalmadı, gitti hepsi. \nSevdiklerim gibi 💔```")
    else:
      await ctx.send("``` Liste artık kalbim gibi tertemiz ❤️❤️❤️```")

  @commands.command(name='playinlist', aliases=['lç','listedençal','listedencal'])
  async def playinlist(self, ctx, *arg):
    if ctx.voice_client is not None:
      if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
      playThis = self.listToInt(arg)

      if len(self.newQ["_"+str(ctx.guild.id)]) > playThis:
        tmp = self.newQ["_"+str(ctx.guild.id)][0]
        self.newQ["_"+str(ctx.guild.id)][0] = self.newQ["_"+str(ctx.guild.id)][playThis]
        self.newQ["_"+str(ctx.guild.id)][playThis] = tmp

        await self.playing(ctx, self.newQ["_"+str(ctx.guild.id)][0])
      else:
        await ctx.send('```Listede o kadar parça yok bilader```')
    
  @commands.command(name='skip', aliases=['sk','geç','gec','siradaki'])
  async def skip(self, ctx):
    if ctx.voice_client is not None:
      ctx.voice_client.stop()
    if not len(self.newQ["_"+str(ctx.guild.id)]) == 0:
      self.newQ["_"+str(ctx.guild.id)].pop(0)
    if len(self.newQ["_"+str(ctx.guild.id)]) > 0:
      await self.playing(ctx, self.newQ["_"+str(ctx.guild.id)][0])
    return True

  @commands.command(name='pause', aliases=['bekle','duraklat'])
  async def pause(self, ctx):
    ctx.voice_client.pause()
    await ctx.send('```Duraklattim bakalim```')

  @commands.command(name='resume', aliases=['r','devam','devamet'])
  async def resume(self, ctx):
    ctx.voice_client.resume()
    await ctx.send('```Muzik devam ediyor```')

  @commands.command(name='list', aliases=['l','liste','q'])
  async def list(self, ctx):
    if not "_"+str(ctx.guild.id) in self.newQ:
      await ctx.send('```Liste Boş```')
      return
    if len(self.newQ["_"+str(ctx.guild.id)]) == 0:
      await ctx.send('```Liste Boş```')
      return
    cikti = "Liste\n\n"
    for idx, song in enumerate(self.newQ["_"+str(ctx.guild.id)], start=0):
      if idx == 0:
        cikti += self.playIcon+"- " +song.name+" ("+song.duration+")\n"
      else:
        cikti += str(idx)+"- " +song.name+" ("+song.duration+")\n"
    await ctx.send('```'+cikti+'```')
  
  @commands.command(name='selcuk')
  async def selcuk(self, ctx):
    msg = await ctx.send("\N{sparkling heart}")

    for name in self.selcuk:
        emoji = dcGet(ctx.guild.emojis, name=name)
        await msg.add_reaction(emoji or name)
  
  @commands.command(name='ali', aliases=["alifii"])
  async def ali(self, ctx):
    msg = await ctx.send("\N{smiling face with sunglasses}")

    for name in self.alifii:
        emoji = dcGet(ctx.guild.emojis, name=name)
        await msg.add_reaction(emoji or name)

  @commands.command(name='yardim', aliases=['komutlar','yardım'])
  async def yardim(self, ctx):
    await ctx.send("```diff\n-Komutlar\n\n```")
    await ctx.send("```Fix\n#Cagirma: $join $j $gel $gelburaya\n#Gonderme: $disconnect $dc $git $defol\n#Calma: $play $p $cal $çal\n#Durdurma: $stop $s $sus $dur\n#Duraklatma: $pause $bekle $duraklat\n#Listeleme: $list $liste $l $q\n#Temizleme: $clear $temizle $lt $c\n```")
    await ctx.send("```CSS\n#Ekstra: $selcuk $ali\n```")

  async def playing(self, ctx, song):
    vc = ctx.voice_client
    FFMPEG_OPTIONS = {'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    source = await discord.FFmpegOpusAudio.from_probe(song.url2, **FFMPEG_OPTIONS)
    vc.play(source)

    msg = await ctx.send(f"```diff\n-Çalan Parça: {song.name}\n-Süre       : {song.duration}\n-URL        : {song.webpage_url}\n```")

    for name in self.reactions:
        emoji = dcGet(ctx.guild.emojis, name=name)
        await msg.add_reaction(emoji or name)
    if ctx.voice_client is not None:
      while ctx.voice_client.is_connected():
        # checks if the bot is the only one in the channel
        if len(ctx.voice_client.channel.members) == 1:
          # disconnects
          self.newQ["_"+str(ctx.guild.id)] = []
          await ctx.voice_client.disconnect()
          break
        # checks if client is pause
        elif ctx.voice_client.is_paused():
          await asyncio.sleep(1)
        # Checks if client is playing
        elif ctx.voice_client.is_playing():
          await asyncio.sleep(1)
        # if nothing of the above is fulfilled
        elif not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
          await self.is_playing_checker(ctx)
          break
        else:
          # disconnect
          self.newQ["_"+str(ctx.guild.id)] = []
          await ctx.voice_client.disconnect()
          break

    return True
  # END OF PLAYING ##################

  def listToString(self, s): 
    str1 = "" 
    if len(s) == 1:
      return s[0]
    for ele in s: 
        str1 += ele + " " 
    return str1 

  def listToInt(self, s): 
    val = 0 
    if len(s) == 0:
      val = 0
    else:
      val = int(s[0])
    print(val)
    return val
  
  def search(self, arg):
    YDL_OPTIONS = {'format':'bestaudio'}
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
      try:
          get(arg) 
      except:
          video = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
      else:
          video = ydl.extract_info(arg, download=False)

    return video

  def addList(self, info, ctx):
    if 'entries' in info:
      for s in info['entries']:
        name = s['title']
        duration = time.strftime('%H:%M:%S', time.gmtime(s["duration"]))
        totalSec = s["duration"]
        webpage_url = s["webpage_url"]
        url2 = s['formats'][0]['url']
        self.newQ["_"+str(ctx.guild.id)].append(song(name=name,duration=duration,totalSec=totalSec,webpage_url=webpage_url,url2=url2)) 
    else:
      name = info['title']
      duration = time.strftime('%H:%M:%S', time.gmtime(info["duration"]))
      totalSec = info["duration"]
      webpage_url = info["webpage_url"]
      url2 = info['formats'][0]['url']
      self.newQ["_"+str(ctx.guild.id)].append(song(name=name,duration=duration,totalSec=totalSec,webpage_url=webpage_url,url2=url2))
  

def setup(client):
  client.add_cog(music(client))