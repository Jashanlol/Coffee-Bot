import discord
import os
import datetime

from discord.ext import commands
from .utils.dataIO import dataIO


class Tags:

    def __init__(self, bot):
        self.bot = bot
        self.tags = dataIO.load_json("data/tags/tags.json")

    def save_settings(self):
        dataIO.save_json("data/tags/tags.json", self.tags)

    @commands.group(invoke_without_command=True)
    async def tag(self, ctx, *, name: str):
        """Calls an existing tag for the server.
        Essentially creating commands. kinda..."""
        if name in self.tags[str(ctx.guild.id)]:
            await ctx.send(self.tags[str(ctx.guild.id)][name]['content'])
            self.tags[str(ctx.guild.id)][name]['uses'] +=1
            self.save_settings()
        else:
            await ctx.send('Tag not found.')

    @tag.command()
    async def create(self, ctx, name: str, *, content: str):
        """Creates a tag.
        Tag name has to not already exist within the server."""
        if name in ['create','tag','delete', 'info', 'owner', 'edit', 'all', 'walkthrough', 'make', 'remove']:
            return await ctx.send(f'{name} is a reserved name and cannot be created.')
        if str(ctx.guild.id) in self.tags:
            if name in self.tags[str(ctx.guild.id)]:
                return await ctx.send('Tag already exists.')
            else:
                self.tags[str(ctx.guild.id)][name] = {'content': content, 'time': str(datetime.date.today()), 'author':ctx.author.id, 'uses':0}
        else:
            self.tags[str(ctx.guild.id)] = {name: {'content': content, 'time': str(datetime.date.today()), 'author':ctx.author.id, 'uses':0}}
        self.save_settings()
        await ctx.send(f'Tag {name} successfully created.')

    @tag.command(aliases=['remove'])
    async def delete(self, ctx, *, name: str):
        """Deletes a tag.
        You need to own the tag and it has to exist in the server."""
        if name in ['create','tag','delete', 'info', 'owner', 'edit', 'all', 'remove', 'walkthrough', 'make']:
            return await ctx.send(f'{name} is a reserved name and cannot be deleted.')
        elif str(ctx.guild.id) in self.tags:
            if name in self.tags[str(ctx.guild.id)]:
                if self.tags[str(ctx.guild.id)][name]["author"] == ctx.author.id:
                    self.tags[str(ctx.guild.id)].pop(name)
                else:
                    await ctx.send("You are not the owner of this tag.")
                    return
            else:
                await ctx.send("Tag not found.")
                return
            self.save_settings()
            await ctx.send('Tag successfully deleted.')
        else:
            await ctx.send('Guild has no tags. :frowning:')

    @tag.command()
    async def all(self, ctx):
        """All server tags.
        Gets all the tags in that exist in the server."""
        if str(ctx.guild.id) in self.tags:
            if self.tags[(str(ctx.guild.id))]:
                e = discord.Embed(title=f'Tags for {ctx.guild.name}:',
                                  description="\n".join(key for key in self.tags[str(ctx.guild.id)].keys()))
                await ctx.send(embed=e)
        else:
            await ctx.send('No tags. 🤔')

    @tag.command(aliases=['owner'])
    async def info(self, ctx, *, name: str):
        """Gets the info of a tag.
        When was it creates, owner, and uses."""
        if str(ctx.guild.id) in self.tags:
            if name in self.tags[str(ctx.guild.id)]:
                e = discord.Embed(title=name, color=ctx.guild.me.color)
                member = self.bot.get_user(id=self.tags[str(ctx.guild.id)][name]['author'])
                e.set_author(name=member, icon_url=member.avatar_url_as(format=None))
                e.add_field(name='Owner', value=member.mention)
                e.add_field(name='Uses', value=self.tags[str(ctx.guild.id)][name]['uses'])
                await ctx.send(embed=e)

    @tag.command()
    async def edit(self, ctx, name: str, *, newcontent: str):
        """Edits a tag.
        Edit a tag that is owned by you and is in the server."""
        if str(ctx.guild.id) in self.tags:
            if name in self.tags[str(ctx.guild.id)]:
                if self.tags[str(ctx.guild.id)][name]["author"] == ctx.author.id:
                    self.tags[str(ctx.guild.id)][name]['content'] = newcontent
                else:
                    await ctx.send("You are not the owner of this tag.")
                    return
            else:
                await ctx.send("Tag not found.")
                return
            self.save_settings()
            await ctx.send('Tag successfully edited.')
        else:
            await ctx.send('Guild has no tags!')

    @tag.command()
    async def claim(self, ctx, *, name: str):
        """Claims a tag as your own.
        If the owner of the tag leaves the server, claim it to becomes its new owner."""
        if str(ctx.guild.id) in self.tags:
            if name in self.tags[str(ctx.guild.id)]:
                user = self.bot.get_user(id=self.tags[str(ctx.guild.id)][name]['author'])
                if user not in ctx.guild.members:
                    self.tags[str(ctx.guild.id)][name]['author'] = ctx.author.id
                    self.save_settings()
                    await ctx.send(f'{ctx.author.name} you now own the tag {name}.')
                else:
                    await ctx.send(f'Member is still in the guild.')
            else:
                await ctx.send('Tag not found.')
        else:
            await ctx.send('Guild has no tags. :frowning2:')

    @tag.command(aliases=['make'])
    async def walkthrough(self, ctx):
        """Need help making a tag?
        The bot will walk you through on how to make a tag."""
        await ctx.send('Great, you wanna make a tag! What do you want to name your command?')
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        msg = await self.bot.wait_for('message', check=check)
        name = f'Great the tag name would be `\"{msg.content}\"`\nNow what do you want the content of the tag to be?'
        await ctx.send(name)
        msg2 = await self.bot.wait_for('message', check=check)
        content = f'Great the tag content would be `{msg2.content}`'
        await ctx.send(content)
        await ctx.send(f'Here is what the command would look like: \n`c tag create \"{msg.content}\" {msg2.content}`'
                       f'\nor\n`coffee tag create \"{msg.content}\"{msg2.content}`')


def check_folders():
    if not os.path.exists("data/tags"):
        print("Creating data/tags folder...")
        os.makedirs("data/tags")

def check_files():
    if not os.path.exists("data/tags/tags.json"):
        print("Creating data/tags/tags.json file...")
        dataIO.save_json("data/tags/tags.json", {})

def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(Tags(bot))
