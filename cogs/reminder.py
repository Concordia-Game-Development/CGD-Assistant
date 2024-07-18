from discord.ext import commands
from discord import app_commands, Interaction

@app_commands.command(name="reminder", description="Set a reminder for a specific event")
async def reminder(interaction: Interaction):
    await interaction.response.send_message(
            "placeholder", ephemeral=True
        )

### Reminder command class ###
class Reminder(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        self.client.tree.add_command(reminder)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Cog Reminder is ready")


async def setup(client: commands.Bot):
    await client.add_cog(Reminder(client))