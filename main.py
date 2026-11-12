import discord

import os

TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('ログインしました')

@client.event
async def on_message(message):
    if message.author.bot:
        return
    
    if message.content == '!test':
        await message.channel.send("テスト")

from discord import app_commands

tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
  await tree.sync()

@tree.command(name="hello", description="おはよう世界") 
async def hello(interaction: discord.Interaction):
  await interaction.response.send_message("Hello, World!")
    
client.run(TOKEN)
