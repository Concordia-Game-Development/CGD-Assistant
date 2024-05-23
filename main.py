from typing import Final
import os, asyncio
from dotenv import load_dotenv
from discord import Intents, Client, Message, Embed, File
from discord.ext import commands
from responses import getResponse

# Load environment variables
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")
extensions: Final[list[str]] = ["cogs.timer"]

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
    file = File("img/pink.png", filename="pink.png")
    help_embed = Embed(
        title="How to use CGDAssistant",
        description="List of available commands:",
        color=0xcf3a65,
        timestamp=ctx.message.created_at
    )
    help_embed.set_thumbnail(url="attachment://pink.png")
    help_embed.add_field(name="!help", value="Display all available commands", inline=True)
    help_embed.add_field(name="!reminder", value="Create a reminder for a task or a reccuring event", inline=True)
    help_embed.add_field(name="!timer", value="Create a timer for the weekly meetings", inline=True)
    await ctx.send(file = file,embed=help_embed)

async def loadCogs() -> None:
    for extension in extensions:
        await client.load_extension(extension)


# Main entry point
async def main() -> None:
    await loadCogs()
    await client.start(token=TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
