from discord.ext import commands
# from discord import app_commands
import asyncio

class Timer(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client= client

    @commands.command(aliases=["t"])
    async def timer(self, ctx, seconds: int):
        if seconds is None:
            await ctx.send("Please provide a number of seconds.")
            return
        if seconds <= 0:
            await ctx.send("Please provide a positive number of seconds.")
            return

        await ctx.send(f"Timer set for {seconds} seconds. I'll remind you!")
        await asyncio.sleep(seconds)
        await ctx.send(f"Time's up mf! gimme your money")

async def setup(client: commands.Bot):
    await client.add_cog(Timer(client))