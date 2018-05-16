import datetime
import traceback
import discord
import asyncio

from discord.ext import commands

from safety import token

initial_cogs = ['cogs.meta', 'cogs.admin', 'cogs.tags', 'cogs.ptags', 'cogs.minigames', 'cogs.eval',
                'cogs.tools']

bot = commands.AutoShardedBot(command_prefix=commands.when_mentioned_or('c? ', 'c!', 'c '), description='Coffee Bot')

@bot.event
async def on_ready():
    print('Ready!')
    print(bot.user.name)
    print(bot.user.id)
    print('------------')
    bot.uptime = datetime.datetime.utcnow()
    x = 1
    while True:
        x +=1
        await bot.change_presence(activity=discord.Game(name='Prefix = c or c! or c?'))
        await asyncio.sleep(20)
        await bot.change_presence(activity=discord.Game(name=f'on {len(bot.guilds)} servers with {len(bot.users)} users'))
        await asyncio.sleep(20)

for cog in initial_cogs:
    try:
        bot.load_extension(cog)
    except Exception as exc:
        traceback_text = "\n".join(traceback.format_exception(type(exc), exc, exc.__traceback__, 4))
        print(traceback_text)

bot.run(token)