import discord

TOKEN = DISCORD_TOKEN

client=discord.Client()

@client.event
async def on_message(message):
    if message.author.bot:
        return
    
    if message.content == '!test':
        await message.channel.send("テスト")
