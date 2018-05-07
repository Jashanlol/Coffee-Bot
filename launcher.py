import datetime
import traceback
import discord

from discord.ext import commands

from safety import token

initial_cogs = ['cogs.utilities', 'cogs.admin']

bot = commands.Bot(command_prefix=['c ','coffee '])

@bot.event
async def on_ready():
    print('Ready!')
    print(bot.user.name)
    print(bot.user.id)
    print('------------')
    bot.uptime = datetime.datetime.utcnow()
    await bot.change_presence(activity=discord.Game(name='Prefix is c or coffee'), status=discord.Status.idle)

for cog in initial_cogs:
    try:
        bot.load_extension(cog)
    except Exception as exc:
        traceback_text = "\n".join(traceback.format_exception(type(exc), exc, exc.__traceback__, 4))
        print(traceback_text)

bot.run(token)