import discord
import os
from discord import app_commands
from discord.ext import commands
import threading
from flask import Flask
import random
import re

app = Flask(__name__)
guildname = guild.name

@app.route("/")
def home():
    return "Hello World!"

# Renderのための処理
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()
TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True
intents.reactions=True
intents.members=True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    print('ログインしました')
    await tree.sync()

#正誤判定の関数
def d(value):
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
    log,number,colorset=d(successvalue)
    
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
                log,number,colorset=d(successvalue)
    
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

async def cbrb_command(interaction: discord.Interaction,successvalue1:app_commands.Range[int, 1, None],successvalue2:app_commands.Range[int,1,None],ability1:str=None,ability2:str=None):
    # ダイスの出目判定
    log,number,colorset=d(successvalue1)
    
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
    
    # logがどの技能のものなのかを示す
    ability_log1=f"{log}({ability1})" or log
    ability_log2=f"{log2}({ability2})" or log2
    
    # successvalue1が成功か失敗かで埋め込みメッセージの色を変える
    if colorset == 1:
        # successvalue1が成功
        embed = discord.Embed(
            title=f"{ability_log1},{ability_log2}",
            description=f"**1D100<={successvalue1},{successvalue2}**\n ->{number}",
            color=0x3773FF
        )
    else:
        # successvalue2が失敗
        embed = discord.Embed(
            title=f"{ability_log1},{ability_log2}",
            description=f"**1D100<={successvalue1},{successvalue2}**\n ->{number}",
            color=0xe60628
        )
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url
    )
    embed.set_footer(text=f"{ability1},{ability2}" or "")
    await interaction.response.send_message(embed=embed)

# /dice
@tree.command(name="dice", description="ダイスを振ります")

async def dice_command(interaction: discord.Interaction,amount:app_commands.Range[int, 1, None],sides:app_commands.Range[int,1,None]):
    num_list=[]
    for i in range(amount):
        num_list.append(random.randint(1,sides))
    
    # 正誤がないので色は統一
    number=sum(num_list)
    
    # 表示時複数の結果を表示するか単独の結果かの判定
    if len(num_list)==1:
        embed = discord.Embed(
            description=f"**{amount}D{sides}**\n ->{number}",
            color=0xbef604
        )
    else:
        embed = discord.Embed(
            description=f"**{amount}D{sides}**\n ->{num_list}\n ->{number}",
            color=0xbef604
        )
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url
    )
    await interaction.response.send_message(embed=embed)

# シークレットダイス
# /s_ccb
@tree.command(name="s_ccb", description="技能判定用シークレットクトゥルフダイスを振ります")

async def sccb_command(interaction: discord.Interaction,successvalue:app_commands.Range[int, 1, None],ability:str=None):
    
    # ダイスの出目判定
    log,number,colorset=d(successvalue)
    
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
    await interaction.user.send(embed=embed)
    await interaction.response.send_message("🎲シークレットダイス")

# /s_resb
@tree.command(name="s_resb", description="対抗ロール用シークレットクトゥルフダイスを振ります")

async def sresb_command(interaction: discord.Interaction,yourstatus:app_commands.Range[int, 1, None],enemystatus:app_commands.Range[int,1,None],ability:str=None):
    
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
                log,number,colorset=d(successvalue)
    
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
    await interaction.user.send(embed=embed)
    await interaction.response.send_message("🎲シークレットダイス")

# /s_cbrb
@tree.command(name="s_cbrb", description="組み合わせロール用シークレットクトゥルフダイスを振ります")

async def scbrb_command(interaction: discord.Interaction,successvalue1:app_commands.Range[int, 1, None],successvalue2:app_commands.Range[int,1,None],ability1:str=None,ability2:str=None):
    
    # ダイスの出目判定
    log,number,colorset=d(successvalue1)
    
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
    
    # logがどの技能のものなのかを示す
    ability_log1=f"{log}({ability1})" or log
    ability_log2=f"{log2}({ability2})" or log2
    
    # successvalue1が成功か失敗かで埋め込みメッセージの色を変える
    if colorset == 1:
        # successvalue1が成功
        embed = discord.Embed(
            title=f"{ability_log1},{ability_log2}",
            description=f"**1D100<={successvalue1},{successvalue2}**\n ->{number}",
            color=0x3773FF
        )
    else:
        # successvalue2が失敗
        embed = discord.Embed(
            title=f"{ability_log1},{ability_log2}",
            description=f"**1D100<={successvalue1},{successvalue2}**\n ->{number}",
            color=0xe60628
        )
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url
    )
    embed.set_footer(text=f"{ability1},{ability2}" or "")
    await interaction.user.send(embed=embed)
    await interaction.response.send_message("🎲シークレットダイス")

# /s_dice
@tree.command(name="s_dice", description="シークレットダイスを振ります")

async def sdice_command(interaction: discord.Interaction,amount:app_commands.Range[int, 1, None],sides:app_commands.Range[int,1,None]):
    
    num_list=[]
    for i in range(amount):
        num_list.append(random.randint(1,sides))
    
    # 正誤がないので色は統一
    number=sum(num_list)
    
    # 表示時複数の結果を表示するか単独の結果かの判定
    if len(num_list)==1:
        embed = discord.Embed(
            description=f"**{amount}D{sides}**\n ->{number}",
            color=0xbef604
        )
    else:
        embed = discord.Embed(
            description=f"**{amount}D{sides}**\n ->{num_list}\n ->{number}",
            color=0xbef604
        )
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url
    )
    await interaction.user.send(embed=embed)
    await interaction.response.send_message("🎲シークレットダイス")

# /rolepannel
@tree.command(name="rolepannel", description="PL等を管理するためのロールパネルを作成します(管理者専用)")
@app_commands.default_permissions(administrator=True)
async def rolepannel_command(
    interaction: discord.Interaction,
    role: discord.Role,
    role2: discord.Role = None,
    role3: discord.Role = None,
    role4: discord.Role = None,
    role5: discord.Role = None
):
    # 追加するテキストとリアクションのリストを準備
    add_description = ""
    reactions = ["🇦"]

    # role2〜role5 が指定されている場合（Noneではない場合）のみ追記する
    extra_roles = [
        (role2, "🇧"),
        (role3, "🇨"),
        (role4, "🇩"),
        (role5, "🇪")
    ]

    for r, emoji in extra_roles:
        if r is not None:
            add_description += f"\n<@&{r.id}>:{emoji}"
            reactions.append(emoji)

    # Embedの作成
    embed = discord.Embed(
        description=f"<@&{role.id}>:🇦{add_description}\n\n-# リアクションを押すとロールを取得・解除できます。",
        color=0xbef604
    )
    embed.set_footer(text="Reaction Role Panel")
    
    await interaction.response.send_message(embed=embed)
    panel_message = await interaction.original_response()
    
    # 指定された分のリアクションを順番につける
    try:
        for emoji in reactions:
            await panel_message.add_reaction(emoji)
    except discord.HTTPException:
        await interaction.followup.send("エラー: リアクションの付与に失敗しました。", ephemeral=True)

# メッセージからロールIDを取り出す関数
async def get_role_from_panel(payload: discord.RawReactionActionEvent, guild: discord.Guild):
    channel = client.get_channel(payload.channel_id) or await client.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    
    # Bot自身のメッセージか、埋め込み(Embed)があるか確認
    if message.author.id != client.user.id or not message.embeds:
        return None
    
    embed = message.embeds[0]
    
    # フッターが「Reaction Role Panel」のパネルだけを対象にする
    if not embed.footer or embed.footer.text != "Reaction Role Panel":
        return None

    # 説明文の中から「<@&ロールID>:押された絵文字」の行を探してロールIDを抜き出す
    pattern = rf"<@&(\d+)>\s*:\s*{re.escape(str(payload.emoji))}"
    match = re.search(pattern, embed.description or "")
    
    if match:
        role_id = int(match.group(1))
        return guild.get_role(role_id)
    return None

# ロール付与処理
@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.user_id == client.user.id or not payload.guild_id:
        return

    guild = client.get_guild(payload.guild_id)
    role = await get_role_from_panel(payload, guild)
    
    if role:
        member = payload.member or await guild.fetch_member(payload.user_id)
        if member:
            await member.add_roles(role)
            await member.send(f"{guildname}でロール:{role.name}を付与しました。")

# ロール解除
@client.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    if payload.user_id == client.user.id or not payload.guild_id:
        return

    guild = client.get_guild(payload.guild_id)
    role = await get_role_from_panel(payload, guild)
    
    if role:
        member = guild.get_member(payload.user_id) or await guild.fetch_member(payload.user_id)
        if member:
            await member.remove_roles(role)
            await member.send(f"{guildname}でロール:{role.name}を解除しました。")


client.run(TOKEN)
