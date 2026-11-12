import discord

import os

from discord import app_commands

import threading

from Flask import flask

app = Flask(__name__)

@app.route("/")
def home():
    return "happy"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()
client.run(TOKEN)

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

tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
  await tree.sync()

@tree.command(name="hello", description="おはよう世界") 
async def hello(interaction: discord.Interaction):
  await interaction.response.send_message("Hello, World!")
    
client.run(TOKEN)
