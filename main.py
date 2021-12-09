import discord
from discord.ext import commands
import music
import os
from keep_alive import keep_alive

token = os.environ['TOKEN']
cogs = [music]

client = commands.Bot(command_prefix='$',intents = discord.Intents.all())

for i in range(len(cogs)):
  cogs[i].setup(client)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="AliFii'yi"))
    print("Bot is ready!")

keep_alive()
client.run(token)