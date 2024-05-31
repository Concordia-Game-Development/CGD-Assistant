from discord.ext import commands
from discord import SelectOption, ui, Button, ButtonStyle, Interaction, Component
import asyncio
from typing import Final


### seconds class ###
class sDropdown(ui.Select):
    def __init__(self) -> None:
        options: Final[list[SelectOption]] = []
        for i in range(60):
            if i % 15 == 0:
                options.append(SelectOption(label=f"{i}", value=f"{i}"))
        super().__init__(
            placeholder="Seconds",
            options=options,
            custom_id="selectSeconds",
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: Interaction) -> None:
        self.view.seconds = int(self.values[0])
        await interaction.response.defer()


### minutes class ###
class mDropdown(ui.Select):
    def __init__(self) -> None:
        options: Final[list[SelectOption]] = []
        for i in range(60):
            if i % 15 == 0:
                options.append(SelectOption(label=f"{i}", value=f"{i}"))
        super().__init__(
            placeholder="Minutes",
            options=options,
            custom_id="selectMinutes",
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: Interaction) -> None:
        self.view.minutes = int(self.values[0])
        await interaction.response.defer()


### hours class ###
class hDropdown(ui.Select):
    def __init__(self) -> None:
        options: Final[list[SelectOption]] = []
        for i in range(5):
            options.append(SelectOption(label=f"{i}", value=f"{i}"))
        super().__init__(
            placeholder="Hours",
            options=options,
            custom_id="selectHours",
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: Interaction) -> None:
        self.view.hours = int(self.values[0])
        await interaction.response.defer()


# ### Join VC Button ###
# class JoinVCButton(ui.Button):
#     def __init__(self, label, style, custom_id):
#         super().__init__(label=label, style=style, custom_id=custom_id)

#     async def callback(self, interaction: Interaction):
#         if self.custom_id == "joinYes":
#             self.view.join_vc = True
#         else:
#             self.view.join_vc = False

#         # Now start the timer
#         await self.start_timer(interaction)

#     async def start_timer(self, interaction: Interaction):
#         await asyncio.sleep(self.view.total_seconds)
#         await interaction.followup.send("Time's up! gimme your money", ephemeral=True)
#         if self.view.join_vc:
#             await interaction.followup.send(
#                 "Joining the voice channel now...", ephemeral=True
#             )
#             # Code to join the voice channel goes here


# ### Join VC View ###
# class JoinVCView(ui.View):
#     def __init__(self, total_seconds):
#         super().__init__()
#         self.total_seconds = total_seconds
#         self.join_vc = False
#         self.add_item(
#             JoinVCButton(label="Yes", style=ButtonStyle.green, custom_id="joinYes")
#         )
#         self.add_item(
#             JoinVCButton(label="No", style=ButtonStyle.danger, custom_id="joinNo")
#         )


### confirm button class ###
class ConfirmButton(ui.Button):
    def __init__(self):
        super().__init__(
            label="Confirm", style=ButtonStyle.green, custom_id="confirmButton"
        )

    def format_time(self, seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        time_str = ""

        if hours > 0:
            time_str += f"{hours} hr{'s' if hours > 1 else ''} "
        if minutes > 0:
            time_str += f"{minutes} min{'s' if minutes > 1 else ''} "
        if seconds > 0 or time_str == "":
            time_str += f"{seconds} sec{'s' if seconds > 1 else ''}"

        return time_str.strip()

    async def callback(self, interaction: Interaction):
        total_seconds = (
            self.view.seconds + (self.view.minutes * 60) + (self.view.hours * 3600)
        )
        if total_seconds <= 0:
            await interaction.response.send_message(
                "You need to set a time greater than 0 seconds.", ephemeral=True
            )
        else:
            formatTime = self.format_time(total_seconds)
            await interaction.response.send_message(
                f"Timer set for {formatTime}. I'll remind you!", ephemeral=True
            )
            await asyncio.sleep(total_seconds)
            await interaction.followup.send(
                "Time's up! gimme your money", ephemeral=True
            )


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


### Timer command class ###
class Timer(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.command(aliases=["t"])
    async def timer(self, ctx: commands.Context) -> None:
        view = TimerView()
        await ctx.send(
            "Please provide the time using the dropdowns below:",
            view=view,
            ephemeral=True,
        )


async def setup(client: commands.Bot):
    await client.add_cog(Timer(client))
