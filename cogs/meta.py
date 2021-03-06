import asyncio
import datetime
import os
import platform
import unicodedata

import aiohttp
import discord
import pkg_resources
import psutil
from discord.ext import commands

from .utils.dataIO import dataIO


class Meta:
    """Commands most bots have.
    Entertainment and use"""

    def __init__(self, bot):
        self.bot = bot
        self.stats = dataIO.load_json("data/stats/stats.json")

    def save_settings(self):
        dataIO.save_json("data/stats/stats.json", self.stats)

    def chunks(self, l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    async def on_message(self, message):
        if str(self.bot.user.id) in self.stats:
            self.stats[str(self.bot.user.id)]['messages'] += 1
        else:
            self.stats[str(self.bot.user.id)] = {'messages': 1}
        self.save_settings()

    async def on_command(self, ctx):
        if str(self.bot.user.id) in self.stats:
            if 'commands' in self.stats[str(self.bot.user.id)]:
                self.stats[str(self.bot.user.id)]['commands'] += 1
            else:
                self.stats[str(self.bot.user.id)] = {'commands': 1}
        self.save_settings()

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        else:
            try:
                await ctx.send(f'```asciidoc\n= {error} = ```')
            except:
                await ctx.send('Could not execute command, either it is not a registered command or the request would be '
                               'over 2000 characters.')

    @commands.command()
    async def hello(self, ctx):
        """Hello, this is my opening greeting."""
        e = discord.Embed(description=f"Hello there, I am Coffee bot. My avatar can be found [here]"
                                      f"({self.bot.user.avatar_url}) and my creator is Jashan. I hope you enjoy testing my commands "
                                      f"and while you're at it, get some Coffee.", color=
                          ctx.guild.me.color)
        await ctx.send(embed=e)

    @commands.command()
    async def uptime(self, ctx):
        """How long have I been awake?
        Check by using uptime."""
        now = datetime.datetime.utcnow()
        delta = now - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        await ctx.send(f"{days}d, {hours}h, {minutes}m, {seconds}s")

    @commands.command(aliases=['remind','remindme'])
    async def reminder(self, ctx, time: int, *, reminder: str):
        """Never forget another task again!
        Coffee will remind you what to do and when to do it."""

        await ctx.send(f"{ctx.author.name}, I'll remind you: {reminder} in {str(time)} seconds.")
        await asyncio.sleep(time)

        await ctx.send(f'{ctx.author.mention} you asked me {time} seconds ago to remind you: {reminder}')

    @commands.command(aliases=['ping'])
    async def latency(self, ctx):
        """Whats my delay?
        Use latency to find out."""
        resp = await ctx.send('Ping loading...')
        diff = resp.created_at - ctx.message.created_at
        await resp.edit(content=f'Pong! That took...{1000*diff.total_seconds():.1f}ms.')

    @commands.command()
    async def feedback(self, ctx, *, feedback):
        """Please give feedback if you have any!
        It means a lot to me! You can request features or fix existing ones.
        Thanks!"""
        channel = self.bot.get_channel(id=446106442848796674)

        e = discord.Embed(color=ctx.author.color)
        e.add_field(name='Feedback', value=f'```Guild: {ctx.guild.name} '
                                           f'(ID:{ctx.guild.id})\nUser: {ctx.author} (ID: {ctx.author.id})```', inline=False)
        e.add_field(name='Message', value=feedback, inline=False)
        await channel.send(embed=e)

        await ctx.send('Thanks for your feedback! It means a lot! :heart:')

    @commands.command(hidden=True)
    async def respond(self, ctx, id: int, *, message):

        user = self.bot.get_user(id=id)
        e = discord.Embed(title=f'{user.name}', description=message, color=ctx.author.color)

        await user.send(embed=e)

    @commands.command(aliases=['charinfo','infochar'])
    async def char(self, ctx, *, characters: str):
        """Get the info of an emoji.
        Just do c char <list of emojis>"""
        def convert(e):
            emoji = unicodedata.name(e)
            numbers = f'{ord(e):x}'
            name = emoji.replace(' ', '-')
            return f'`\\U{numbers:>08}` — [{e} {emoji}](https://emojipedia.org/{name.lower()})'
        def uni(f):
            numbers = f'{ord(f):x}'
            return f'\\U{numbers:>08}'

        message = '\n'.join(map(convert, characters))
        unicode = ''.join(map(uni, characters))
        e = discord.Embed(description=f'{message}\n\nRaw: `{unicode}`', color=ctx.guild.me.color)
        if len(message) > 2048:
            return await ctx.send('Message would be too large. Try again with less emojis!')
        await ctx.send(embed=e)

    @commands.command(aliases=['discriminator'])
    async def discrim(self, ctx, *, discriminator: str):
        """See if you are unique."""
        if str(ctx.guild.id) == "336642139381301249":
            if discriminator == "0001":
                return await ctx.send('Sorry to inform you, but this is not a unique discriminator.')
        if len(f'{discriminator}') != 4:
            return await ctx.send(f'A discriminator is 4 numbers, not {len(discriminator)}.')
        all = list(self.chunks([str(user) for user in self.bot.users if user.discriminator == discriminator], 54))
        for i in all:
            f = "\n".join(i)
            await ctx.send(f'```{f}```')

    @commands.group(invoke_without_command=True)
    async def about(self, ctx):
        """My info!
        Find out more about me."""
        now = datetime.datetime.utcnow()
        delta = now - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        total_members = sum(1 for _ in self.bot.get_all_members())
        total_online = len({m.id for m in self.bot.get_all_members() if m.status is discord.Status.online})
        total_idle = len({m.id for m in self.bot.get_all_members() if m.status is discord.Status.idle})
        total_dnd = len({m.id for m in self.bot.get_all_members() if m.status is discord.Status.dnd})
        total_offline = len({m.id for m in self.bot.get_all_members() if m.status is discord.Status.offline})
        bots = len({m.id for m in self.bot.get_all_members() if m.bot is True})
        o = '<:online:313956277808005120>'
        i = '<:away:313956277220802560>'
        d = '<:dnd:313956276893646850>'
        of ='<:offline:313956277237710868>'
        total_unique = len(self.bot.users)
        cpu = psutil.cpu_percent()
        voice_channels = []
        text_channels = []
        for guild in self.bot.guilds:
            voice_channels.extend(guild.voice_channels)
            text_channels.extend(guild.text_channels)
        text = len(text_channels)
        voice = len(voice_channels)
        owner = self.bot.get_user(id=294894701708967936)
        messages = self.stats[str(self.bot.user.id)]['messages']

        e = discord.Embed(description=f'[Join the Official Support Server](https://discord.gg/sCht25q)',color=ctx.guild.me.color)
        e.set_author(name=owner, icon_url=owner.avatar_url)
        e.add_field(name='Member Status', value=f'{o} {total_online} '
                                                f'{i} {total_idle} {d} {total_dnd} {of} {total_offline}', inline=False)
        e.add_field(name='Member Stats', value=f'{total_members} total\n{total_unique} unique\n{bots} unique bot users')
        e.add_field(name='Channels Stats', value=f'{text+voice} total\n{text} text\n{voice} voice')
        e.add_field(name='Other Stats', value=f"{messages} messages seen \n{self.stats[str(self.bot.user.id)]['commands']}"
                                              f" commands run\n"
                                              f"{len(self.bot.guilds)} guilds")
        e.add_field(name='Process', value=f"{round(psutil.Process().memory_full_info().uss / 2 ** 20, 2)} MiB"
                                          f"\n{round(cpu)} % CPU")
        e.add_field(name='Connection', value=f'{round(self.bot.latency*1000)} ms')
        e.add_field(name='Uptime', value=f"{days}d, {hours}h, {minutes}m, {seconds}s")
        e.set_footer(text=f"Made with Python {platform.python_version()} and discord.py version "
                          f"{pkg_resources.get_distribution('discord.py').version}", icon_url="http://i.imgur.com/5BFecvA.png")
        e.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=e)

    @commands.command()
    async def info(self, ctx, *members: discord.Member):
        """Get the info of multiple members.
        Remember to put spaces in between each member and put quotes around their name if it is longer than a word."""
        if not members:
            return await ctx.send('Members is a required message that is missing.')
        if len(members) > 3:
            await ctx.send('To reduce spam, you can only request info for 3 members at a time.')
            return
        for member in members:
            if member.voice is not None:
                vc = member.voice.channel
                others = len(vc.members) - 1
                voice = f'{vc.name} with {others} others' if others else f'{vc.name} by themselves'
            else:
                voice = 'Not connected.'
            shared = sum(1 for m in self.bot.get_all_members() if m.id == member.id)
            roles = [role.name.replace('@', '@\u200b') for role in member.roles]

            e = discord.Embed(title=str(member), color=member.color)
            e.set_thumbnail(url=member.avatar_url_as(format=None))
            e.add_field(name='ID', value=member.id)
            e.add_field(name='Servers', value=f'{shared} shared')
            e.add_field(name='Created', value=member.created_at)
            e.add_field(name='Voice', value=voice)
            e.add_field(name='Roles', value=', '.join(roles) if len(roles) < 10 else f'{len(roles)} roles')
            e.set_footer(text='Member since').timestamp = member.joined_at

            await ctx.send(embed=e)

    @about.command(aliases=['guild'])
    async def server(self, ctx):
        """Server info!
        Find out more about your server."""
        total_members = len(ctx.guild.members)
        total_online = len({m.id for m in ctx.guild.members if m.status is discord.Status.online})
        total_idle = len({m.id for m in ctx.guild.members if m.status is discord.Status.idle})
        total_dnd = len({m.id for m in ctx.guild.members if m.status is discord.Status.dnd})
        total_offline = len({m.id for m in ctx.guild.members if m.status is discord.Status.offline})
        o = '<:online:313956277808005120>'
        i = '<:away:313956277220802560>'
        d = '<:dnd:313956276893646850>'
        of ='<:offline:313956277237710868>'
        x = '<:xmark:314349398824058880>'
        ch = '<:check:314349398811475968>'
        if (len(ctx.guild.features)) >= 3:
            c = f'{ch}: Parterned'
        else:
            c = f'{x}: Partnered'
        if ctx.guild.explicit_content_filter is discord.ContentFilter.disabled:
            f = f'{x}: Scanning Images'
        else:
            f = f'{ch}: Scanning Images'
        if ctx.guild.large is False:
            l = f'{x}: Large'
        else:
            l = f'{ch}: Large'

        e = discord.Embed(title=f'Info for {ctx.guild.name}', color=ctx.guild.me.color)
        if ctx.guild.icon:
            e.set_thumbnail(url=ctx.guild.icon_url_as(format='png'))
        e.add_field(name='ID', value=ctx.guild.id)
        e.add_field(name='Owner', value=ctx.guild.owner)
        e.add_field(name='Info', value=f'{c}\n{f}\n{l}')
        e.add_field(name='Channels', value=f'Text {len(ctx.guild.text_channels)}\nVoice {len(ctx.guild.voice_channels)}')
        e.add_field(name='Members', value=f'{o} {total_online} {i} {total_idle} {d} {total_dnd} {of} {total_offline}\n'
                                          f'Total: {total_members}')
        e.add_field(name='Roles', value=f'{len(ctx.guild.roles)} roles')

        await ctx.send(embed=e)

    async def say_permissions(self, ctx, member, channel):

        permissions = channel.permissions_for(member)
        e = discord.Embed(color=member.color)
        allowed, denied = [], []
        for name, value in permissions:
            name = name.replace('_', ' ').replace('guild', 'server').title()
            if value:
                allowed.append(name)
            else:
                denied.append(name)

        e.add_field(name='Allowed', value='\n'.join(allowed))
        e.add_field(name='Denied', value='\n'.join(denied))

        await ctx.send(embed=e)

    @commands.command(aliases=['perms'])
    async def permissions(self, ctx, member: discord.Member = None, channel: discord.TextChannel = None):
        """Find out a members perms in a specific channel.
        If no member or channel is provided, defaults to author of message and channel of message."""
        if member is None:
            member = ctx.author

        channel = channel or ctx.channel

        await self.say_permissions(ctx, member, channel)

    @commands.command(aliases=['invite'])
    async def join(self, ctx):
        """Invite me!
        Want me to join your server? Use this."""
        p = discord.Permissions.none()
        p.read_messages = True
        p.external_emojis = True
        p.send_messages = True
        p.manage_roles = True
        p.manage_channels = True
        p.ban_members = True
        p.kick_members = True
        p.manage_messages = True
        p.embed_links = True
        p.read_message_history = True
        p.attach_files = True
        p.add_reactions = True
        p.connect = True
        p.use_voice_activation = True
        p.speak = True

        await ctx.send(f'<{discord.utils.oauth_url(self.bot.user.id, permissions=p)}>')

    @commands.command()
    async def countdown(self, ctx, time: int):
        """Racing?
        Use this to start fairly! No number over 10."""
        if time > 10:
            return await ctx.send(f'To reduce spam, you cannot start a countdown from {time} seconds.')
        for i in range(time):
            await ctx.send(time - i)
            await asyncio.sleep(1)
        await ctx.send('Go!')

    @commands.command()
    async def shared(self, ctx, *, user: discord.User = None):
        """See what servers you share with me.
        Just type the users name or use their id. You can also use their mention, but not recommended."""
        if user is None:
            user = ctx.author
        shared = "\n".join([g.name for g in self.bot.guilds if user in g.members])
        e = discord.Embed(color=0x36393E, description=f'```fix\n{shared}```')
        e.set_footer(text=f'Shared with {user}')
        e.set_thumbnail(url=user.avatar_url_as(format=None))
        await ctx.send(embed=e)

    @commands.command()
    async def avatar(self, ctx, *members: discord.Member):
        """Get multiple avatars.
        Remember to put spaces in between each of the people and quotes if their name is longer than one word."""
        if len(members) is 0:
            return await ctx.send('Members is a required message that is missing.')
        if len(members) > 3:
            return await ctx.send('To reduce spam, you can only get the avatar of 3 members at a time.')
        images = []
        for member in members:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(url=member.avatar_url_as(format=None, size=1024)) as f:
                    if member.is_avatar_animated():
                        images.append(discord.File(await f.read(), filename=f'{member}.gif'))
                    else:
                        images.append(discord.File(await f.read(), filename=f'{member}.png'))
        await ctx.send(files=images)


    @commands.command()
    async def talk(self, ctx, *, message: str):
        """Send messages to my owner through me.
        Don't spam!"""
        user = self.bot.get_user(id=294894701708967936)
        await user.send(f'In {ctx.channel.mention} for server {ctx.guild.name}, {ctx.author.mention} said: {message}')
        await ctx.send(f'I have sent your message to {user}')

    @commands.command()
    async def die(self, ctx):
        """1 v 4? No problem.
        Now you can kill 3 people at once in your guild."""
        files = []
        f = 'https://steamusercontent-a.akamaihd.net/ugc/19968052724714266'
        '0/5FEE28B1D22D8D41101ACF82A99F0372E69CE8E6/'
        async with aiohttp.ClientSession() as r:
            async with r.get(url='https://steamusercontent-a.akamaihd.net/ugc/19968052724714266'
                                 '0/5FEE28B1D22D8D41101ACF82A99F0372E69CE8E6/') as img:
                files.append(discord.File(await img.read(), filename=f'{f}.gif'))
                await ctx.send(files=files)
            r.close()

def check_folders():
    if not os.path.exists("data/stats"):
        print("Creating data/stats folder...")
        os.makedirs("data/stats")

def check_files():
    if not os.path.exists("data/stats/stats.json"):
        print("Creating data/stats/stats.json file...")
        dataIO.save_json("data/stats/stats.json", {})

def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(Meta(bot))