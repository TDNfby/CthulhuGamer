import discord
import os
from discord import app_commands
from discord.ext import commands
import threading
from flask import Flask
import random

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello World!"

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

def dice(value):
    number=random.randint(1,100)
    if number<=value/5:
        colorset=1
        if number<=5:
            return "**成功/決定的成功/スペシャル**",number,colorset
        else:
            return "**成功/スペシャル**",number,colorset
    else:
        if number<=value:
            colorset=1
            if number<=5:
                return "**成功/決定的成功**",number,colorset
            else:
                return "**成功**",number,colorset
        else:
            colorset=0
            if number>=96:
                return "**失敗/致命的失敗**",number,colorset
            else:
                return "**失敗**",number,colorset


@client.event
async def on_message(message):
    if message.author.bot:
        return
    
    if message.content == '!test':
        await message.channel.send("テスト")

# /ccb
@tree.command(name="ccb", description="技能判定用クトゥルフダイスを振ります")

async def ccb_command(interaction: discord.Interaction,successvalue:app_commands.Range[int, 1, None],ability:str=None):
    # ダイスの出目判定
    log,number,colorset=dice(successvalue)
    
    # 失敗か成功かで埋め込みメッセージの色を変える
    if colorset == 1:
        # 成功
        embed = discord.Embed(
            title=log,
            description=f"**1D100<={successvalue}**\n ->{number}",
            color=0x3773FF
        )
    else:
        # 失敗
        embed = discord.Embed(
            title=log,
            description=f"**1D100<={successvalue}**\n ->{number}",
            color=0xe60628
        )
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url
    )
    embed.set_footer(text=ability or "")
    await interaction.response.send_message(embed=embed)

# /resb
@tree.command(name="resb", description="対抗ロール用クトゥルフダイスを振ります")

async def resb_command(interaction: discord.Interaction,yourstatus:app_commands.Range[int, 1, None],enemystatus:app_commands.Range[int,1,None],ability:str=None):
    # ダイスの出目判定
    successvalue=50+(yourstatus-enemystatus)*5
    
    if successvalue>=100:
        # 自動成功
        embed = discord.Embed(
            title="自動成功",
            description=f"**resb({yourstatus}-{enemystatus})**\n ->自動成功",
            color=0x3773FF
            )
    else:
            if successvalue<=0:
                # 自動失敗
                embed = discord.Embed(
                title="自動失敗",
                description=f"**resb({yourstatus}-{enemystatus})**\n ->自動失敗",
                color=0xe60628
                )
            else:
                log,number,colorset=dice(successvalue)
    
                # 失敗か成功かで埋め込みメッセージの色を変える
                if colorset == 1:
                    # 成功
                    embed = discord.Embed(
                        title=log,
                        description=f"**resb({yourstatus}-{enemystatus})**\n\n**1D100<={successvalue}**\n ->{number}",
                        color=0x3773FF
                    )
                else:
                    # 失敗
                    embed = discord.Embed(
                        title=log,
                        description=f"**resb({yourstatus}-{enemystatus})**\n\n**1D100<={successvalue}**\n ->{number}",
                        color=0xe60628
                    )
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url
    )
    embed.set_footer(text=ability or "")
    await interaction.response.send_message(embed=embed)

# /cbrb
@tree.command(name="cbrb", description="組み合わせロール用クトゥルフダイスを振ります")

async def resb_command(interaction: discord.Interaction,successvalue1:app_commands.Range[int, 1, None],successvalue2:app_commands.Range[int,1,None],ability1:str=None,ability2:str=None):
    # ダイスの出目判定
    log,number,colorset=dice(successvalue1)
    
    # 出目と色判定はsuccessvalue1のまま、判定結果だけをsuccessvalue2で判定し、log2に保存する
    if number<=successvalue2/5:
        if number<=5:
            log2="**成功/決定的成功/スペシャル**"
        else:
            log2="**成功/スペシャル**"
    else:
        if number<=successvalue2:
            if number<=5:
                log2="**成功/決定的成功**"
            else:
                log2="**成功**"
        else:
            if number>=96:
                log2="**失敗/致命的失敗**"
            else:
                log2="**失敗**"
    
    # logがどの技能のものなのかを示す変数を作る
    ability_log1=f"{log}({ability1})" or log
    ability_log2=f"{log}({ability2})" or log
    
    # successvalue1が成功か失敗かで埋め込みメッセージの色を変える
    if colorset == 1:
        # successvalue1が成功
        embed = discord.Embed(
            title=f"{ability_log1},{ability_log2}"
            description=f"**1D100<={successvalue1},{successvalue2}**\n ->{number}",
            color=0x3773FF
        )
    else:
        # successvalue2が失敗
        embed = discord.Embed(
            title=f"{ability_log1},{ability_log2}"
            description=f"**1D100<={successvalue1},{successvalue2}**\n ->{number}",
            color=0xe60628
        )
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url
    )
    embed.set_footer(text=ability1,ability2 or "")
    await interaction.response.send_message(embed=embed)

client.run(TOKEN)
