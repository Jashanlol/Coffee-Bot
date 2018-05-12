import discord
import random
import os

from discord.ext import commands
from .utils.constant import ball
from .utils.dataIO import dataIO


class Minigames:

    def __init__(self, bot):
        self.bot = bot
        self.mstats = dataIO.load_json("data/mstats/mstats.json")

    def save_settings(self):
        dataIO.save_json("data/mstats/mstats.json", self.mstats)

    @commands.command(asliases=['dice'])
    async def roll(self, ctx, dice: str):
        """Rolls dice.
        example format: 1d5
        here it will role 1 dice with 5 sides."""
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await ctx.send('Format is NdN!')
            return

        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
        await ctx.send(result)

    @commands.command(aliases=['choose'])
    async def choice(self, ctx, *choices: str):
        """Settle the score.
        Input as many choices as you want and let Coffee do the rest."""
        await ctx.send(random.choice(choices))

    @commands.command()
    async def flip(self, ctx, choice: str = None):
        """Flip a coin.
        You can pick heads or tails and pick none for a simple walk through."""
        c = random.choice(['heads', 'tails'])
        e = discord.Embed(color=ctx.author.color)
        e.add_field(name='Result', value=f'Good work! It is {c}')
        e1 = discord.Embed(color=ctx.author.color)
        e1.add_field(name='Result', value=f'It was {c}. Maybe next time!')
        if choice is None:
            await ctx.send('What do you call? heads or tails?')
            def check(m):
                return m.content in ['heads', 'tails'] and m.author == ctx.author and m.channel == ctx.channel
            msg = await self.bot.wait_for('message', check=check)
            if c == msg.content:
                await ctx.send(embed=e)
            else:
                await ctx.send(embed=e1)
        else:
            if c == choice:
                await ctx.send(embed=e)
            else:
                await ctx.send(embed=e1)

    @commands.command(name='8ball')
    async def _ball(self, ctx):
        """8ball. What more do you need?
        Let Coffee answer your questions."""
        e = discord.Embed(color=ctx.author.color, description=f'{ctx.author.mention} {random.choice(ball)}')
        await ctx.send(embed=e)

    @commands.command()
    async def rps(self, ctx, *, choice: str):
        """Wanna play rock paper scissors?
        Use this command to see if you can beat me!"""
        if str(ctx.author.id) not in self.mstats:
            self.mstats[str(ctx.author.id)] = {"rps":{'wins':0, 'lose':0, "ties":0}}
        if 'rps' not in self.mstats[str(ctx.author.id)]:
            self.mstats[str(ctx.author.id)]= {"rps": {'wins': 0, 'lose': 0, "ties": 0}}
        self.save_settings()
        rand = random.randint(0, 2)
        choices = ["paper", "scissors", "rock"]
        outcome_list = ["draw", "lose", "win"]
        result = (choices.index(choice) + rand) % 3
        g = outcome_list[rand]
        if g == 'win':
            self.mstats[str(ctx.author.id)]['rps']['wins'] +=1
        if g == 'draw':
            self.mstats[str(ctx.author.id)]['rps']['ties'] +=1
        if g == 'lose':
            self.mstats[str(ctx.author.id)]['rps']['lose'] +=1
        self.save_settings()
        wins = self.mstats[str(ctx.author.id)]['rps']['wins']
        loses = self.mstats[str(ctx.author.id)]['rps']['lose']
        ties = self.mstats[str(ctx.author.id)]['rps']['ties']
        f = ("I picked {}, you {}".format(choices[result], g))
        e = discord.Embed(description=f)
        e.set_footer(text=f'Your Stats: {wins} wins, {loses} losses, {ties} ties')
        await ctx.send(embed=e)



    @commands.command()
    async def test(self, ctx, *, choice: str):
        rand = random.randint(0, 2)
        choices = ["paper", "scissors", "rock"]
        outcome_list = ["draw", "lose", "win"]
        result = (choices.index(choice) + rand) % 3
        await ctx.send("I drew {}, you {}".format(choices[result], outcome_list[rand]))


def check_folders():
    if not os.path.exists("data/mstats"):
        print("Creating data/mstats folder...")
        os.makedirs("data/mstats")

def check_files():
    if not os.path.exists("data/mstats/mstats.json"):
        print("Creating data/mstats/mstats.json file...")
        dataIO.save_json("data/mstats/mstats.json", {})

def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(Minigames(bot))