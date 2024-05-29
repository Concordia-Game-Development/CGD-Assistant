from discord.ext import commands
from discord import SelectOption, ui, Button, ButtonStyle, Interaction
import asyncio
from typing import Final

### seconds class ###
class sDropdown(ui.Select):
    def __init__(self) -> None:
        options: Final[list[SelectOption]] = []
        for i in range (60):
            if i % 15 == 0:
                options.append(SelectOption(label=f"{i}", value=f"{i}", default=(i==0)))
        super().__init__(placeholder="Seconds", options=options, custom_id="selectSeconds", min_values=1, max_values=1)

    async def callback(self, interaction: Interaction) -> None:
        self.view.seconds = int(self.values[0])
        await interaction.response.defer()

### minutes class ###
class mDropdown(ui.Select):
    def __init__(self) -> None:
        options: Final[list[SelectOption]] = []
        for i in range (60):
            if i % 15 == 0:
                options.append(SelectOption(label=f"{i}", value=f"{i}", default=(i==0)))
        super().__init__(placeholder="Minutes", options=options, custom_id="selectMinutes", min_values=1, max_values=1)

    async def callback(self, interaction: Interaction) -> None:
        self.view.minutes = int(self.values[0])
        await interaction.response.defer()

### hours class ###
class hDropdown(ui.Select):
    def __init__(self) -> None:
        options: Final[list[SelectOption]] = []
        for i in range (5):
            options.append(SelectOption(label=f"{i}", value=f"{i}", default=(i==0)))
        super().__init__(placeholder="Hours", options=options, custom_id="selectHours", min_values=1, max_values=1)

    async def callback(self, interaction: Interaction) -> None:
        self.view.hours = int(self.values[0])
        await interaction.response.defer()

### confirm button class ###
class ConfirmButton(ui.Button):
    def __init__(self):
        super().__init__(label="Confirm", style=ButtonStyle.green, custom_id="confirmButton")

    async def callback(self, interaction: Interaction):
        total_seconds = self.view.seconds + (self.view.minutes * 60) + (self.view.hours * 3600)
        if total_seconds <= 0:
            await interaction.response.send_message("You need to set a time greater than 0 seconds.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Timer set for {total_seconds} seconds. I'll remind you!", ephemeral=True)
            await asyncio.sleep(total_seconds)
            await interaction.followup.send("Time's up! gimme your money", ephemeral=True)

### Viewing class ###
class TimerView(ui.View):
    def __init__(self) -> None:
        super().__init__()
        self.seconds = 0
        self.minutes = 0
        self.hours = 0
        self.add_item(hDropdown()) 
        self.add_item(mDropdown())
        self.add_item(sDropdown())
        self.add_item(ConfirmButton())
    
    async def interaction_check(self, interaction: Interaction) -> bool:
        # Allow only the user who initiated the command to interact
        return interaction.user == interaction.message.interaction.user

### Timer command class ###
class Timer(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client= client

    @commands.command(aliases=["t"])
    async def timer(self, ctx: commands.Context) -> None:
        view = TimerView()
        await ctx.send("Please provide the time using the dropdowns below:", view=view, ephemeral=True)

        # Wait for user to interact with the dropdowns
        await asyncio.sleep(15)  # Wait some time for the user to make selections

        total_seconds = await view.calculate_total_seconds()
        if total_seconds <= 0:
            await ctx.send("You need to set a time greater than 0 seconds.", ephemeral=True)
            return

        await ctx.send(f"Timer set for {total_seconds} seconds. I'll remind you!", ephemeral=True)
        await asyncio.sleep(total_seconds)
        await ctx.send(f"Time's up! gimme your money", ephemeral=True)


async def setup(client: commands.Bot):
    await client.add_cog(Timer(client))