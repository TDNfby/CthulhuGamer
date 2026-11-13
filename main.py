import discord
import os
from discord import app_commands
from discord.ext import commands
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

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(name="ccb", description="技能判定用クトゥルフダイスを振ります")

async def ccb_command(interaction: discord.Interaction,app_commands.Range[int, 1, None],ability:text＝None):
    # ダイスの出目判定
    import random
    
    def dice(value):
        number=random.randint(1,100)
        if number<=value/5:
            colorset=1
            if number<=5:
                return "成功/決定的成功(クリティカル)/スペシャル"
            else:
                return "成功/スペシャル"
        else:
            if number<=value:
                colorset=1
                if number<=5:
                    return "成功/決定的成功(クリティカル)"
                else:
                    return "成功"
            else:
                coloset=0
                if number>=96:
                    return "失敗/致命的失敗(ファンブル)"
                else:
                    return "失敗"
    log=dice(successvalue)
    
    # 失敗か成功かで埋め込みメッセージの色を変える
    if colorset=1:
        # 埋め込みメッセージとして送信
        embed = discord.Embed(
            title=log,
            description="**1D100<=successvalue** —> number",
            color=e60628
        )
    else:
        embed = discord.Embed(
            title=log,
            description="**1D100<=successvalue** —> number",
            color=3773FF
        )
    embed.set_author(
        name=author.display_name
        icon_url=author.display_name
    )
    embed.set_footer(text=ability)

client.run(TOKEN)
