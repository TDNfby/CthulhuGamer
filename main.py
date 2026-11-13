import discord
import os
from discord import app_commands
from discord.ext import commands
import threading
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "happy"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()
TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    print('ログインしました')
    await tree.sync()

@client.event
async def on_message(message):
    if message.author.bot:
        return
    
    if message.content == '!test':
        await message.channel.send("テスト")

@tree.command(name="ccb", description="技能判定用クトゥルフダイスを振ります")

async def ccb_command(interaction: discord.Interaction,successvalue:app_commands.Range[int, 1, None],ability:str=None):
    # ダイスの出目判定
    import random
    
    def dice(value):
        number=random.randint(1,100)
        if number<=value/5:
            colorset=1
            if number<=5:
                return "成功/決定的成功(クリティカル)/スペシャル",number,colorset
            else:
                return "成功/スペシャル",number,colorset
        else:
            if number<=value:
                colorset=1
                if number<=5:
                    return "成功/決定的成功(クリティカル)",number,colorset
                else:
                    return "成功",number,colorset
            else:
                colorset=0
                if number>=96:
                    return "失敗/致命的失敗(ファンブル)",number,colorset
                else:
                    return "失敗",number,colorset
    log,number,colorset=dice(successvalue)
    
    # 失敗か成功かで埋め込みメッセージの色を変える
    if colorset == 1:
        # 埋め込みメッセージとして送信
        embed = discord.Embed(
            title=log,
            description="**1D100<=successvalue** —> number",
            color=0xe60628
        )
    else:
        embed = discord.Embed(
            title=log,
            description=f"**1D100<=successvalue** —> number",
            color=0x3773FF
        )
    embed.set_author(
        name=author.display_name,
        icon_url=author.display_name
    )
    embed.set_footer(text=ability)
    await interaction.response.send_message(embed=embed)
client.run(TOKEN)
