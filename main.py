import discord
import os
import json
import random
import threading
import traceback
from discord import app_commands

# Flask は無くても Bot 自体は動くようにする
try:
    from flask import Flask
except ImportError:  # flask未インストールでも起動を止めない
    Flask = None

TOKEN = os.environ.get("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("環境変数 DISCORD_TOKEN が設定されていません")

app = Flask(__name__) if Flask else None


def run_web():
    if app is None:
        print("flask がインストールされていないため Web サーバーは起動しません")
        return
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, use_reloader=False, threaded=True)


if app is not None:
    @app.route("/")
    def home():
        return "Hello World!"


# ------------------------------
# Bot クライアント
# ------------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
intents.dm_messages = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    print(f'ログインしました: {client.user}')
    try:
        synced = await tree.sync()
        print(f"スラッシュコマンドを同期しました: {len(synced)}件")
    except Exception:
        print("コマンド同期に失敗しました:")
        traceback.print_exc()


@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    print(f"コマンド実行エラー: {interaction.command.name if interaction.command else 'unknown'}")
    traceback.print_exception(type(error), error, error.__traceback__)
    try:
        if interaction.response.is_done():
            await interaction.followup.send("エラーが発生しました。", ephemeral=True)
        else:
            await interaction.response.send_message("エラーが発生しました。", ephemeral=True)
    except Exception:
        pass


# ------------------------------
# 判定ロジック
# ------------------------------
def d(value):
    """1D100 を振って技能判定。 (ログ文言, 出目) を返す"""
    number = random.randint(1, 100)
    if number <= value / 5:
        if number <= 5:
            return "**成功/決定的成功/スペシャル**", number, 1
        return "**成功/スペシャル**", number, 1
    if number <= value:
        if number <= 5:
            return "**成功/決定的成功**", number, 1
        return "**成功**", number, 1
    if number >= 96:
        return "**失敗/致命的失敗**", number, 0
    return "**失敗**", number, 0


def judge_log(number, value):
    """出目 number を技能値 value で判定した結果の文言だけを返す"""
    if number <= value / 5:
        if number <= 5:
            return "**成功/決定的成功/スペシャル**"
        return "**成功/スペシャル**"
    if number <= value:
        if number <= 5:
            return "**成功/決定的成功**"
        return "**成功**"
    if number >= 96:
        return "**失敗/致命的失敗**"
    return "**失敗**"


SUCCESS_COLOR = 0x3773FF
FAIL_COLOR = 0xe60628
NORMAL_COLOR = 0xbef604


def set_author(embed, interaction, footer=None):
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url
    )
    if footer:
        embed.set_footer(text=footer)
    return embed


# PL毎のステータス等を保存するdic
DATA_FILE = "user_data.json"


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content == '!test':
        await message.channel.send("テスト")


# ------------------------------
# シークレット（DM）送信ヘルパー
# 3秒ルール対策のため必ず先に defer してから DM する
# ------------------------------
async def send_secret(interaction: discord.Interaction, embed: discord.Embed):
    if not interaction.response.is_done():
        try:
            await interaction.response.defer(thinking=True)
        except discord.HTTPException:
            traceback.print_exc()

    try:
        await interaction.user.send(embed=embed)
    except discord.Forbidden:
        print(f"DM送信失敗(Forbidden): {interaction.user} (id={interaction.user.id})")
        await interaction.followup.send(
            "DMを送信できませんでした。\n"
            "Discordの「プライバシー設定」→「サーバーメンバーからのDMを許可」を"
            "ONにしてください（スマホのアプリ設定／各サーバーのプライバシー設定）。",
            ephemeral=True
        )
        return
    except discord.HTTPException as e:
        print(f"DM送信失敗(HTTP {e.status} code={e.code}): {interaction.user}")
        traceback.print_exc()
        await interaction.followup.send(
            f"DM送信に失敗しました（{e.status} / code {e.code}）。", ephemeral=True
        )
        return
    except Exception:
        traceback.print_exc()
        await interaction.followup.send("DM送信に失敗しました。", ephemeral=True)
        return

    await interaction.followup.send("🎲シークレットダイス")


# ------------------------------
# 通常ダイス
# ------------------------------
@tree.command(name="ccb", description="技能判定用クトゥルフダイスを振ります")
async def ccb_command(
    interaction: discord.Interaction,
    successvalue: app_commands.Range[int, 1, None],
    ability: str = None
):
    log, number, colorset = d(successvalue)
    embed = discord.Embed(
        title=log,
        description=f"**1D100<={successvalue}**\n ->{number}",
        color=SUCCESS_COLOR if colorset == 1 else FAIL_COLOR
    )
    set_author(embed, interaction, ability or None)
    await interaction.response.send_message(embed=embed)


@tree.command(name="resb", description="対抗ロール用クトゥルフダイスを振ります")
async def resb_command(
    interaction: discord.Interaction,
    yourstatus: app_commands.Range[int, 1, None],
    enemystatus: app_commands.Range[int, 1, None],
    ability: str = None
):
    successvalue = 50 + (yourstatus - enemystatus) * 5

    if successvalue >= 100:
        embed = discord.Embed(
            title="自動成功",
            description=f"**resb({yourstatus}-{enemystatus})**\n ->自動成功",
            color=SUCCESS_COLOR
        )
    elif successvalue <= 0:
        embed = discord.Embed(
            title="自動失敗",
            description=f"**resb({yourstatus}-{enemystatus})**\n ->自動失敗",
            color=FAIL_COLOR
        )
    else:
        log, number, colorset = d(successvalue)
        embed = discord.Embed(
            title=log,
            description=(
                f"**resb({yourstatus}-{enemystatus})**\n\n"
                f"**1D100<={successvalue}**\n ->{number}"
            ),
            color=SUCCESS_COLOR if colorset == 1 else FAIL_COLOR
        )

    set_author(embed, interaction, ability or None)
    await interaction.response.send_message(embed=embed)


@tree.command(name="cbrb", description="組み合わせロール用クトゥルフダイスを振ります")
async def cbrb_command(
    interaction: discord.Interaction,
    successvalue1: app_commands.Range[int, 1, None],
    successvalue2: app_commands.Range[int, 1, None],
    ability1: str = None,
    ability2: str = None
):
    log, number, colorset = d(successvalue1)
    log2 = judge_log(number, successvalue2)

    ability_log1 = f"{log}({ability1})" if ability1 else log
    ability_log2 = f"{log2}({ability2})" if ability2 else log2
    footer_text = ",".join(a for a in (ability1, ability2) if a)

    embed = discord.Embed(
        title=f"{ability_log1},{ability_log2}",
        description=f"**1D100<={successvalue1},{successvalue2}**\n ->{number}",
        color=SUCCESS_COLOR if colorset == 1 else FAIL_COLOR
    )
    set_author(embed, interaction, footer_text or None)
    await interaction.response.send_message(embed=embed)


@tree.command(name="dice", description="ダイスを振ります")
async def dice_command(
    interaction: discord.Interaction,
    amount: app_commands.Range[int, 1, 1000],
    sides: app_commands.Range[int, 1, 1000000]
):
    num_list = [random.randint(1, sides) for _ in range(amount)]
    number = sum(num_list)

    if len(num_list) == 1:
        embed = discord.Embed(
            description=f"**{amount}D{sides}**\n ->{number}",
            color=NORMAL_COLOR
        )
    else:
        details = ", ".join(str(n) for n in num_list)
        if len(details) > 3500:
            details = details[:3500] + " …"
        embed = discord.Embed(
            description=f"**{amount}D{sides}**\n ->{details}\n ->{number}",
            color=NORMAL_COLOR
        )
    set_author(embed, interaction)
    await interaction.response.send_message(embed=embed)


# ------------------------------
# シークレットダイス（DM送信）
# ------------------------------
@tree.command(name="s_ccb", description="技能判定用シークレットクトゥルフダイスを振ります")
async def sccb_command(
    interaction: discord.Interaction,
    successvalue: app_commands.Range[int, 1, None],
    ability: str = None
):
    log, number, colorset = d(successvalue)
    embed = discord.Embed(
        title=log,
        description=f"**1D100<={successvalue}**\n ->{number}",
        color=SUCCESS_COLOR if colorset == 1 else FAIL_COLOR
    )
    set_author(embed, interaction, ability or None)
    await send_secret(interaction, embed)


@tree.command(name="s_resb", description="対抗ロール用シークレットクトゥルフダイスを振ります")
async def sresb_command(
    interaction: discord.Interaction,
    yourstatus: app_commands.Range[int, 1, None],
    enemystatus: app_commands.Range[int, 1, None],
    ability: str = None
):
    successvalue = 50 + (yourstatus - enemystatus) * 5

    if successvalue >= 100:
        embed = discord.Embed(
            title="自動成功",
            description=f"**resb({yourstatus}-{enemystatus})**\n ->自動成功",
            color=SUCCESS_COLOR
        )
    elif successvalue <= 0:
        embed = discord.Embed(
            title="自動失敗",
            description=f"**resb({yourstatus}-{enemystatus})**\n ->自動失敗",
            color=FAIL_COLOR
        )
    else:
        log, number, colorset = d(successvalue)
        embed = discord.Embed(
            title=log,
            description=(
                f"**resb({yourstatus}-{enemystatus})**\n\n"
                f"**1D100<={successvalue}**\n ->{number}"
            ),
            color=SUCCESS_COLOR if colorset == 1 else FAIL_COLOR
        )

    set_author(embed, interaction, ability or None)
    await send_secret(interaction, embed)


@tree.command(name="s_cbrb", description="組み合わせロール用シークレットクトゥルフダイスを振ります")
async def scbrb_command(
    interaction: discord.Interaction,
    successvalue1: app_commands.Range[int, 1, None],
    successvalue2: app_commands.Range[int, 1, None],
    ability1: str = None,
    ability2: str = None
):
    log, number, colorset = d(successvalue1)
    log2 = judge_log(number, successvalue2)

    ability_log1 = f"{log}({ability1})" if ability1 else log
    ability_log2 = f"{log2}({ability2})" if ability2 else log2
    footer_text = ",".join(a for a in (ability1, ability2) if a)

    embed = discord.Embed(
        title=f"{ability_log1},{ability_log2}",
        description=f"**1D100<={successvalue1},{successvalue2}**\n ->{number}",
        color=SUCCESS_COLOR if colorset == 1 else FAIL_COLOR
    )
    set_author(embed, interaction, footer_text or None)
    await send_secret(interaction, embed)


@tree.command(name="s_dice", description="シークレットダイスを振ります")
async def sdice_command(
    interaction: discord.Interaction,
    amount: app_commands.Range[int, 1, 1000],
    sides: app_commands.Range[int, 1, 1000000]
):
    num_list = [random.randint(1, sides) for _ in range(amount)]
    number = sum(num_list)

    if len(num_list) == 1:
        embed = discord.Embed(
            description=f"**{amount}D{sides}**\n ->{number}",
            color=NORMAL_COLOR
        )
    else:
        details = ", ".join(str(n) for n in num_list)
        if len(details) > 3500:
            details = details[:3500] + " …"
        embed = discord.Embed(
            description=f"**{amount}D{sides}**\n ->{details}\n ->{number}",
            color=NORMAL_COLOR
        )
    set_author(embed, interaction)
    await send_secret(interaction, embed)


# ------------------------------
# ロールパネル
# ------------------------------
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
            await member.send(f"**{guild.name}**でロール:**{role.name}**を付与しました。")

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
            await member.send(f"**{guild.name}**でロール:**{role.name}**を解除しました。")

# ------------------------------
# 起動
# ------------------------------
if __name__ == "__main__":
    # PORT が設定されている環境でのみ Web サーバーを起動
    if app is not None and os.environ.get("PORT"):
        threading.Thread(target=run_web, daemon=True).start()
        print("Web キープアライブを開始しました")

    try:
        client.run(TOKEN)
    except discord.LoginFailure:
        print("ログイン失敗: DISCORD_TOKEN が無効です。値を確認してください。")
    except Exception:
        print("起動時に致命的エラーが発生しました:")
        traceback.print_exc()
