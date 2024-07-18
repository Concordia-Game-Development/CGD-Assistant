from typing import Final
import os, asyncio
from dotenv import load_dotenv
from discord import Intents, Client, Message, Embed, File, app_commands, Interaction
from discord.ext import commands

# Load environment variables
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")
extensions: Final[list[str]] = ["cogs.timer", "cogs.reminder"]

# Bot Setup
intents: Intents = Intents.default()
intents.message_content = True
intents.voice_states = True
client: Client = commands.Bot(intents=intents, help_command=None, command_prefix="!")

# Define a tree for slash commands
tree = client.tree


# Load cogs
async def loadCogs() -> None:
    for extension in extensions:
        await client.load_extension(extension)


# Event: Bot is ready
@client.event
async def on_ready() -> None:
    print(f"{client.user} has connected to Discord!")


# Help Commands
@tree.command(name="help", description="Display all available commands")
async def help(interaction: Interaction) -> None:
    file = File("img/pink.png", filename="pink.png")
    help_embed = Embed(
        title="How to use CGDAssistant",
        description="List of available commands:",
        color=0xCF3A65,
        timestamp=interaction.created_at,
    )
    help_embed.set_thumbnail(url="attachment://pink.png")
    help_embed.add_field(
        name="/help", value="Display all available commands", inline=True
    )
    help_embed.add_field(
        name="/reminder",
        value="Create a reminder for a task or a reccuring event",
        inline=True,
    )
    help_embed.add_field(
        name="/timer set_timer",
        value="Create a timer for the weekly meetings",
        inline=True,
    )
    help_embed.add_field(
        name="/timer set_ringtone",
        value="Change the ringtone for the timer using Youtube API",
        inline=True,
    )
    await interaction.response.send_message(file=file, embed=help_embed)


# Sync commands
@client.command(name="sync", description="Sync commands with Discord")
async def sync(ctx) -> None:
    try:
        await client.tree.sync()
        await ctx.reply("Commands synced with Discord!", ephemeral=True)
    except Exception as e:
        await ctx.reply(f"Failed to sync commands: {str(e)}", ephemeral=True)


# Main entry point
async def main() -> None:
    await loadCogs()
    await client.start(token=TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
