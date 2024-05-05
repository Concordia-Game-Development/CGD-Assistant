from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, Embed
from discord.ext import commands
from responses import getResponse

# Load environment variables
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

# Bot Setup
intents: Intents = Intents.default()
intents.message_content = True
client: Client = commands.Bot(command_prefix="!",intents=intents, help_command=None)

# Event: Bot is ready
@client.event
async def on_ready() -> None:
    print(f"{client.user} has connected to Discord!")

#Simple Commands
@client.command(aliases=["h"])
async def help(ctx) -> None:
    help_embed = Embed(
        title="Help Center",
        description="List of available commands:",
        color=0xcf3a65,
        timestamp=ctx.message.created_at
    )
    help_embed.add_field(name="!reminder", value="Create a reminder for a task or a reccuring event", inline=False)
    help_embed.add_field(name="!timer", value="Create a timer for the weekly meetings", inline=False)
    await ctx.send(embed=help_embed)

# Main entry point
def main()-> None:
    client.run(token=TOKEN)


if __name__ == "__main__":
    main()

