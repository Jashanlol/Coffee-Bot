import discord
import os
import datetime

from .utils.dataIO import dataIO
from discord.ext import commands

class ptags:

    def __init__(self, bot):
        self.bot = bot
        self.ptags = dataIO.load_json("data/ptags/ptags.json")

    def save_settings(self):
        dataIO.save_json("data/ptags/ptags.json", self.ptags)

    @commands.group(invoke_without_command=True)
    async def ptag(self, ctx, *, name: str):
        """Calls a tag that belongs to you and only to you.
        You can only retrieve tags you own."""
        if name in self.ptags[str(ctx.author.id)]:
            await ctx.send(self.ptags[str(ctx.author.id)][name]['content'])
            self.ptags[str(ctx.author.id)]['uses'] +=1
            self.save_settings()
        else:
            await ctx.send('Tag not found in your personal tags.')

    @ptag.command()
    async def create(self, ctx, name: str, *, content: str):
        """Create a personal tag.
        This will create a tag that only you can use."""
        if name in ['create','tag','delete','all']:
            return await ctx.send(f'{name} is a reserved name and cannot be created.')
        if str(ctx.author.id) in self.ptags:
            if name in self.ptags[str(ctx.author.id)]:
                return await ctx.send('Personal tag already exists.')
            else:
                self.ptags[str(ctx.author.id)][name] = {'content': content, 'time': str(datetime.date.today()), 'uses':0,
                                                        'secret':False}
        else:
            self.ptags[str(ctx.author.id)] = {name: {'content': content, 'time': str(datetime.date.today()), 'uses':0,
                                                     'secret':False}}
        self.save_settings()
        await ctx.send('Personal tag successfully created.')

    @ptag.command()
    async def delete(self, ctx, *, name: str):
        """Delete a personal tag.
        This deletes a personal tag that you own."""
        if name in ['create','tag','delete','all']:
            return await ctx.send(f'{name} is reserved name and cannot be deleted.')
        if name in self.ptags[str(ctx.author.id)]:
            self.ptags[str(ctx.author.id)].pop(name)
            self.save_settings()
            await ctx.send('Personal tag successfully deleted.')
        else:
            await ctx.send('Tag not found in your personal tags.')

    @ptag.command()
    async def all(self, ctx):
        """List of all your personal tags.
        Retrieves all of your personal tags."""
        if str(ctx.author.id) in self.ptags:
            e = discord.Embed(title=f'{ctx.author.name}\'s personal tags', description='\n'.join(key for key in
                                                                    self.ptags[str(ctx.author.id)].keys()))
            await ctx.send(embed=e, delete_after=30)
        else:
            await ctx.send('You have no personal tags.')

    @ptag.command()
    async def edit(self, ctx, name: str, *, newcontent: str):
        """Edit a personal tag.
        Edit a tag you own."""
        if str(ctx.author.id) in self.ptags:
            if name in self.ptags[str(ctx.author.id)]:
                self.ptags[str(ctx.author.id)]['content'] = newcontent
                self.save_settings()
                await ctx.send('Tag successfully edited.')
            else:
                await ctx.send('Personal tag not found.')
        else:
            await ctx.send('You have no personal tags.')

    @ptag.command(aliases=['owner'])
    async def info(self, ctx, *, name: str):
        """Info for a personal tag.
        Get the date of creation and number of uses of your tag."""
        if str(ctx.author.id) in self.ptags:
            if name in self.ptags[str(ctx.author.id)]:
                e = discord.Embed(title=name, color=ctx.guild.me.color)
                member = self.bot.get_user(id=self.ptags[str(ctx.guild.id)][name]['author'])
                e.set_author(name=member, icon_url=member.avatar_url_as(format=None))
                e.add_field(name='Owner', value=member.mention)
                e.add_field(name='Uses', value=self.ptags[str(ctx.guild.id)][name]['uses'])
                await ctx.send(embed=e)

    @ptag.command()
    async def hide(self, ctx, *, name: str):
        """Hides a tag.
        This makes it so no one can copy your tag."""
        if str(ctx.author.id) in self.ptags:
            if name in self.ptags[str(ctx.author.id)]:
                self.ptags[str(ctx.author.id)][name]['secret'] = True
                self.save_settings()
                await ctx.send('Personal tag is now secret.')
            else:
                await ctx.send('Personal tag not found.')
        else:
            await ctx.send('You have no personal tags.')

    @ptag.command()
    async def unhide(self, ctx, *, name: str):
        """Unhides a tag.
        This makes it so anyone can copy your tag."""
        if str(ctx.author.id) in self.ptags:
            if name in self.ptags[str(ctx.author.id)]:
                self.ptags[str(ctx.author.id)][name]['secret'] = False
                self.save_settings()
                await ctx.send('Personal tag is no longer secret.')
            else:
                await ctx.send('Personal tag not found.')
        else:
            await ctx.send('You have no personal tags.')

    @ptag.command()
    async def copy(self, ctx, member: discord.Member, *, name: str):
        """Copies another users tag.
        Copy a another user's tag name and information."""
        if str(member.id) in self.ptags:
            if name in self.ptags[str(member.id)]:
                if self.ptags[str(member.id)][name]['secret'] is True:
                    return await ctx.send('Personal tag cannot be copied.')
                content = self.ptags[str(member.id)][name]['content']
                if str(ctx.author.id) in self.ptags:
                    if name in self.ptags[str(ctx.author.id)]:
                        await ctx.send('You already own a personal tag with this name.')
                    else:
                        self.ptags[str(ctx.author.id)][name] = {'content': content, 'time': str(datetime.date.today()),
                                                                'uses':0, 'secret':False}
                        self.save_settings()
                        await ctx.send(f'Personal tag {name} copied.')
                else:
                    self.ptags[str(ctx.author.id)] = {name: {'content': content, 'time': str(datetime.date.today()),
                                                             'uses': 0, 'secret': False}}
                    self.save_settings()
                    await ctx.send(f'Personal tag {name} copied.')
            else:
                return await ctx.send('Personal tag not found.')
        else:
            return await ctx.send('Member has no personal tags.')

def check_folders():
    if not os.path.exists("data/ptags"):
        print("Creating data/ptags folder...")
        os.makedirs("data/ptags")

def check_files():
    if not os.path.exists("data/ptags/ptags.json"):
        print("Creating data/ptags/ptags.json file...")
        dataIO.save_json("data/ptags/ptags.json", {})

def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(ptags(bot))