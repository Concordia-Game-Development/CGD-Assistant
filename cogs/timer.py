from discord.ext import commands
from discord import SelectOption, ui, Button, ButtonStyle, Interaction
# from discord import app_commands
import asyncio
from typing import Final


class sDropdown(ui.Select):
    def __init__(self) -> None:
        options: Final[list[SelectOption]] = []
        for i in range (60):
            if i % 15 == 0:
                options.append(SelectOption(label=f"{i}", value=f"{i}"))
        print(options)

        super().__init__(placeholder="Seconds", options=options, custom_id="selectSeconds", min_values=1, max_values=1)

    @ui.select(custom_id="selectSeconds")
    async def select_seconds(self, interaction: Interaction, select: ui.Select) -> None:
        self.seconds = int(select.values[0])
        await interaction.response.send_message(f"Seconds set to {self.seconds}", ephemeral=True)

class mDropdown(ui.Select):
    def __init__(self) -> None:
        options: Final[list[SelectOption]] = []
        for i in range (60):
            if i % 15 == 0:
                options.append(SelectOption(label=f"{i}", value=f"{i}"))
        print(options)
            
        super().__init__(placeholder="Minutes", options=options, custom_id="selectMinutes", min_values=1, max_values=1)

    @ui.select(custom_id="selectMinutes")
    async def select_minutes(self, interaction: Interaction, select: ui.Select) -> None:
        self.minutes = int(select.values[0])
        await interaction.response.send_message(f"Minutes set to {self.minutes}", ephemeral=True)

class hDropdown(ui.Select):
    def __init__(self) -> None:
        options: Final[list[SelectOption]] = []
        for i in range (5):
            options.append(SelectOption(label=f"{i}", value=f"{i}"))
        print(options)
            
        super().__init__(placeholder="Hours", options=options, custom_id="selectHours", min_values=1, max_values=1)   

    @ui.select(custom_id="selectHours")
    async def select_hours(self, interaction: Interaction, select: ui.Select) -> None:
        self.hours = int(select.values[0])
        await interaction.response.send_message(f"Hours set to {self.hours}", ephemeral=True)

class TimerView(ui.View):
    def __init__(self) -> None:
        super().__init__()
        self.add_item(sDropdown())
        self.add_item(mDropdown())
        self.add_item(hDropdown())
        self.seconds = 0
        self.minutes = 0
        self.hours = 0
    
    async def calculate_total_seconds(self) -> int:
        total_seconds = self.seconds + (self.minutes * 60) + (self.hours * 3600)
        return total_seconds
    
    async def interaction_check(self, interaction: Interaction) -> bool:
        # Allow only the user who initiated the command to interact
        return interaction.user == interaction.message.interaction.user


class Timer(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client= client

    @commands.command(aliases=["t"])
    async def timer(self, ctx: commands.Context) -> None:
        view = TimerView()
        await ctx.send("Please provide the time using the dropdowns below:", view=view)

        # Wait for user to interact with the dropdowns
        await asyncio.sleep(15)  # Wait some time for the user to make selections

        total_seconds = await view.calculate_total_seconds()
        if total_seconds <= 0:
            await ctx.send("You need to set a time greater than 0 seconds.")
            return

        await ctx.send(f"Timer set for {total_seconds} seconds. I'll remind you!")
        await asyncio.sleep(total_seconds)
        await ctx.send(f"Time's up! gimme your money")


async def setup(client: commands.Bot):
    await client.add_cog(Timer(client))