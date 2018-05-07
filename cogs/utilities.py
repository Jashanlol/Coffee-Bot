import discord
import datetime

from discord.ext import commands

class Utilites:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def uptime(self, ctx):
        # Get's process id and returns uptime in seconds
        now = datetime.datetime.utcnow()
        delta = now - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        await ctx.send(f"{days}d, {hours}h, {minutes}m, {seconds}s")


def setup(bot):
    bot.add_cog(Utilites(bot))