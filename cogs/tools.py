import os
import discord
import asyncio
import datetime
import time

from .utils.dataIO import dataIO
from chempy import Substance
from chempy import balance_stoichiometry
from chempy import Reaction
from discord.ext import commands

class Utils:
    """Utilities.
    Useful commands."""
    def __init__(self, bot):
        self.bot = bot
        self.away = dataIO.load_json("data/away/away.json")
        self.search = dataIO.load_json("data/search/search.json")

    def save_settings(self):
        dataIO.save_json("data/away/away.json", self.away)
        dataIO.save_json("data/search/search.json", self.search)

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
            await ctx.send('You are already away!')
        else:
            await ctx.send(f'```py\nYou will be away in 30 seconds with the message: {message}```', delete_after=15)
            self.away[str(ctx.author.id)] = {'message': message, 'collecting': False, 'msgs': []}
        self.save_settings()
        await asyncio.sleep(30)
        self.away[str(ctx.author.id)]['collecting'] = True

    async def on_message(self, message):
        self.search[str(message.id)] = {'channel': str(message.channel.id)}
        self.save_settings()
        if not message.guild:
            return
        for member in message.guild.members:
            if member.name.lower() in message.content.lower():
                if str(member.id) in self.away:
                    if member.name != message.author.name:
                        if message.author != self.bot.user:
                            self.away[str(member.id)]['msgs'].append(f'{time.ctime()} in '
                                                                     f'{message.channel.mention}: '
                                                                     f'{message.author.mention} said\n {message.content}')
                            self.save_settings()
                            self.permissions = message.channel.permissions_for(message.guild.me)
                            if not self.permissions.manage_messages:
                                await message.channel.send(f'```py\nI\'ll deliever your message to '
                                                           f'{member.name} because they are currently afk. They said: '
                                                           f"{self.away[str(member.id)]['message']}```", delete_after=15)
                            else:
                                await message.delete()
                                await message.channel.send(f'```py\nI\'ll deliever your message to '
                                                           f'{member.name} because they are currently afk. They said: '
                                                           f"{self.away[str(member.id)]['message']}```", delete_after=15)
        if message.mentions:
            for mention in message.mentions:
                if mention.name != message.author.name:
                    if str(mention.id) in self.away:
                        self.away[str(mention.id)]['msgs'].append(f'{time.ctime()} in '
                                                                  f'{message.channel.mention}: {message.author.mention} said\n {message.content}')
                        self.save_settings()
                        self.permissions = message.channel.permissions_for(message.guild.me)
                        if not self.permissions.manage_messages:
                            await message.channel.send(f'```py\nI\'ll deliever your message to '
                                                       f'{mention.name} because they are currently afk. They said: '
                                                       f"{self.away[str(mention.id)]['message']}```", delete_after=15)
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

    async def on_typing(self, channel, user, when):
        if str(user.id) in self.away:
            if self.away[str(user.id)]['collecting'] is True:
                e = discord.Embed(title='Here\'s what you missed',
                    description='\n\n'.join(key for key in self.away[str(user.id)]['msgs']), color=0x80ffff)
                try:
                    await user.send(embed=e)
                except Exception:
                    return await channel.send('DM failed! Messages deleted.')
                self.away.pop(str(user.id))
                self.save_settings()
                await channel.send(f"{user} has returned.")

    @commands.command(aliases=['stoichiometry'])
    async def balance(self, ctx, *, equation: str):
        """Balances a chemical equation."""
        try:
            reac, prod = equation.split('=')
        except ValueError:
            reac, prod = equation.split('->')
        reac = [r.strip().lstrip('0123456789') for r in reac.split('+')]
        prod = [p.strip().lstrip('0123456789') for p in prod.split('+')]
        balanced = await self.bot.loop.run_in_executor(None, balance_stoichiometry, reac, prod)
        answer = Reaction(*balanced)
        msg = await ctx.send('<a:loading:393852367751086090>')
        await msg.edit(content=f'```py\nNonbalanced Equation: {equation}```\n\n<a:loading:393852367751086090>')
        await msg.edit(content=f'```py\nNonbalanced Equation: {equation}\n\nBalanced Equation: {answer.string()}```')

    @commands.command(name='search')
    async def cmd_name(self, ctx, *, id: int):
        """Don't know where an id came from? Search it!
        This function is compatible with guild ids, channel ids, emoji ids, and message ids!"""
        if str(id) in self.search:
            chan1 = self.search[str(id)]['channel']
            chan = self.bot.get_channel(int(chan1))
            msg = await chan.get_message(id=id)
            f = discord.Embed(description=msg.content, color=ctx.guild.me.color)
            f.set_author(name=msg.author, icon_url=msg.author.avatar_url_as(format=None))
            f.timestamp = datetime.datetime.utcnow()
            return await ctx.send(embed=f)
        content = []
        guild = self.bot.get_guild(id=id)
        channel = self.bot.get_channel(id=id)
        emoji = self.bot.get_emoji(id=id)
        e = discord.Embed(color=ctx.guild.me.color)
        if guild is not None:
            content.append(f'**Type:** Guild\n**Name:** {guild.name}\n**ID:** {id}\n**Owner:** {guild.owner}'
                           f'\n**Created:** {guild.created_at}')
            thumbnail = guild.icon_url
            e.set_thumbnail(url=thumbnail)
        if channel is not None:
            content.append(f'**Type:** Channel\n**Name:** {channel.name}\n**ID:** {channel.id}\n**Guild:** '
                           f'{channel.guild.name} ({channel.guild.id})\n**Mention:** {channel.mention}\n**Created:** {channel.created_at}')
            thumbnail = channel.guild.icon_url
            e.set_thumbnail(url=thumbnail)
        if emoji is not None:
            content = f'**Type:** Emoji\n**Name:** {emoji.name}\n**ID:** {emoji.id}\n**Is Animated:** {emoji.animated}\n' \
                      f'**Guild:** {emoji.guild.name} ({emoji.guild.id})\n**Created:** {emoji.created_at}'
            thumbnail = emoji.url
            e.set_thumbnail(url=thumbnail)
        e.description = '\n\n'.join(content)
        await ctx.send(embed=e)

def check_folders():
    if not os.path.exists("data/away"):
        print("Creating data/away folder...")
        os.makedirs("data/away")
    if not os.path.exists("data/search"):
        print("Creating data/search folder...")
        os.makedirs("data/search")

def check_files():
    if not os.path.exists("data/away/away.json"):
        print("Creating data/away/away.json file...")
        dataIO.save_json("data/away/away.json", {})
    if not os.path.exists("data/search/search.json"):
        print("Creating data/search/search.json file...")
        dataIO.save_json("data/search/search.json", {})

def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(Utils(bot))
