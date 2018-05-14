import os
import discord
import datetime
import time

from .utils.dataIO import dataIO
from chempy import Substance
from discord.ext import commands

class Utils:
    """Utilities.
    Useful commands."""
    def __init__(self, bot):
        self.bot = bot
        self.away = dataIO.load_json("data/away/away.json")

    def save_settings(self):
        dataIO.save_json("data/away/away.json", self.away)

    @commands.command()
    async def mass(self, ctx, *, substance: str):
        """Find the mass of an element or compound!
        It doesn't even have to exist!"""
        compound = Substance.from_formula(substance)
        mass = compound.molar_mass()
        await ctx.send(f'```py\nMolar mass of {compound.unicode_name}: {round(mass, 2)} g/mol```')

    @commands.command(name='away')
    async def _test(self, ctx, *, message: str):
        """Afk? Don't worry use this!
        This will store messages you are mentioned in until you are back. If you're back use c back"""
        if str(ctx.author.id) in self.away:
            await ctx.send('You are already away! If you have just come back, type `c back`')
        else:
            self.away[str(ctx.author.id)] = {'message': message, 'msgs': []}
            await ctx.send(f'```py\nYou are now away with the message: {message}```')
        self.save_settings()

    async def on_message(self, message):
        if message.mentions:
            for mention in message.mentions:
                if mention.name != message.author.name:
                    if str(mention.id) in self.away:
                        self.permissions = message.channel.permissions_for(message.guild.me)
                        if not self.permissions.manage_messages:
                            self.away[str(mention.id)]['msgs'].append(f'{time.ctime()} in '
                                                                      f'{message.channel.mention}: {message.author} said\n {message.content}')
                            self.save_settings()
                            await message.channel.send(f'```py\nI\'ll deliever your message to '
                                                       f'{mention.name} because they are currently afk. They said: '
                                                       f"{self.away[str(mention.id)]['message']}```")
                        else:
                            await message.delete()
                            await message.channel.send(f'```py\nI\'ll deliever your message to '
                                                       f'{mention.name} because they are currently afk. They said: '
                                                       f"{self.away[str(mention.id)]['message']}```", delete_after=15)

    async def on_message_delete(self, message):
        if message.mentions:
            for mention in message.mentions:
                if str(mention.id) in self.away:
                    self.away[str(mention.id)]['msgs'].append(f'{time.ctime()}: in '
                                    f'{message.channel.mention} {message.author} said {message.content}')
                    self.save_settings()

    @commands.command()
    async def back(self, ctx):
        """Back from being afk?
        This will dm you every message you were mentioned in while you were afk."""
        if str(ctx.author.id) in self.away:
            e = discord.Embed(title='Here\'s what you missed',
                description='\n\n'.join(key for key in self.away[str(ctx.author.id)]['msgs']), color=0x80ffff)
            await ctx.author.send(embed=e)
            self.away.pop(str(ctx.author.id))
            self.save_settings()
            await ctx.send(f"{ctx.author} has returned.")

def check_folders():
    if not os.path.exists("data/away"):
        print("Creating data/away folder...")
        os.makedirs("data/away")

def check_files():
    if not os.path.exists("data/away/away.json"):
        print("Creating data/away/away.json file...")
        dataIO.save_json("data/away/away.json", {})

def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(Utils(bot))
