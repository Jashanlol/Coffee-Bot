import discord
import random

from discord.ext import commands
from .utils.constant import ball


class Minigames:

    def __init__(self, bot):
        self.bot = bot

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
        if choice is None:
            await ctx.send('What do you call? heads or tails?')
            def check(m):
                return m.content in ['heads', 'tails'] and m.author == ctx.author and m.channel == ctx.channel
            msg = await self.bot.wait_for('message', check=check)
            choice = random.choice(['heads', 'tails'])
            if choice == msg.content:
                await ctx.send(f'Good work! It is {choice}.')
            else:
                await ctx.send(f'It is {choice}. Maybe next time!')
        else:
            c = random.choice(['heads', 'tails'])
            if c == choice:
                await ctx.send(f'Good work! It is {c}.')
            else:
                await ctx.send(f'It is {c}. Maybe next time!')

    @commands.command(name='8ball')
    async def _ball(self, ctx):
        """8ball. What more do you need?
        Let Coffee answer your questions."""
        e = discord.Embed(color=ctx.author.color, description=f'{ctx.author.mention} {random.choice(ball)}')
        await ctx.send(embed=e)

def setup(bot):
    bot.add_cog(Minigames(bot))