import discord
from discord.ext import tasks, commands

from datas import datas

MY_GUILD = discord.Object(id=datas.MY_GUILD)
intents = discord.Intents.all()
bot=commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    try:
        await bot.load_extension('cogs.courses.courses')
        synced = await bot.tree.sync()
        print(f"synced {len(synced) } command(s)")
    except Exception as e:
        print(e)

bot.run(datas.TOKEN)
