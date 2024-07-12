from discord.ext import commands
from discord import (
    SelectOption,
    ui,
    Button,
    ButtonStyle,
    Interaction,
    app_commands,
    FFmpegPCMAudio,
)
import asyncio
from typing import Final
from cogs.ytRequest import audioDownloadYT
import os


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


### confirm button class ###
class ConfirmButton(ui.Button):
    def __init__(self):
        super().__init__(
            label="Confirm",
            style=ButtonStyle.green,
            custom_id="confirmButton",
        )

    def formatTime(self, seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        finalTime = ""

        if hours > 0:
            finalTime += f"{hours} hr{'s' if hours > 1 else ''} "
        if minutes > 0:
            finalTime += f"{minutes} min{'s' if minutes > 1 else ''} "
        if seconds > 0 or finalTime == "":
            finalTime += f"{seconds} sec{'s' if seconds > 1 else ''}"

        return finalTime.strip()

    ### connectVC function to connect to VC ###
    async def connectVC(self, interaction: Interaction):
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            try:
                # Join the voice channel
                isConnected = await channel.connect()
                # await interaction.followup.send(f"Joined {channel}", ephemeral=True)

                await self.playSound(isConnected)

                # Disconnect after playing the sound
                await isConnected.disconnect()

            except Exception as e:
                await interaction.followup.send(
                    f"An error occurred while trying to join the voice channel: {e}",
                    ephemeral=True,
                )
                await isConnected.disconnect()
        else:
            await interaction.followup.send(
                "You are not connected to a voice channel.", ephemeral=True
            )

    async def playSound(self, isConnected):
        # Play sound
        if customPathExists():
            ALARM_PATH = "sounds/CUSTOM.mp3"  # custom sound set by user
        else:
            ALARM_PATH = "sounds/DONE.mp3"  # default sound

        source = FFmpegPCMAudio(ALARM_PATH)
        isConnected.play(source)

        while isConnected.is_playing():
            await asyncio.sleep(1)

    ### checkTimer function to check if set time is valid ###
    async def checkTimer(self, interaction: Interaction, total_seconds: int):
        if total_seconds <= 0:
            await interaction.response.send_message(
                "You need to set a time greater than 0 seconds.", ephemeral=True
            )
        else:
            formattedTime = self.formatTime(total_seconds)

            await interaction.response.send_message(
                f"Timer set for {formattedTime}. I'll remind you!", ephemeral=True
            )

            await asyncio.sleep(total_seconds)

            await self.connectVC(interaction)

            await interaction.followup.send(
                "Time's up! gimme your money", ephemeral=True
            )

    async def callback(self, interaction: Interaction):
        total_seconds = (
            self.view.seconds + (self.view.minutes * 60) + (self.view.hours * 3600)
        )
        await self.checkTimer(interaction, total_seconds)


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


### TimerGroup class ###
class TimerGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="timer", description="Manage timer")

    ### set_timer command (subcommand #1)###
    @app_commands.command(
        name="set_timer", description="Create a timer for the weekly meetings"
    )
    async def setTimer(self, interaction: Interaction) -> None:
        view = TimerView()
        await interaction.response.send_message(
            "Please provide the time using the dropdowns below:",
            view=view,
            ephemeral=True,
        )

    ### set_alarm command (subcommand #2)###
    @app_commands.command(name="set_ringtone", description="Set timer ringtone")
    @app_commands.describe(
        url="The URL of the YouTube video",
        duration="The duration of the clip in seconds (Integer)",
    )
    async def setRingtone(
        self, interaction: Interaction, url: str, duration: int
    ) -> None:
        # Acknowledge the interaction immediately
        await interaction.response.defer(ephemeral=True)
        # yt-dlp will be used to download the audio
        DOWNLOAD_PATH = "sounds/"

        try:
            # Check if the CUSTOM.mp3 file exists and delete it if it does
            if customPathExists():
                os.remove(DOWNLOAD_PATH + "CUSTOM.mp3")

            audioDownloadYT(url, DOWNLOAD_PATH + "CUSTOM", duration)
            await interaction.followup.send("New timer ringtone set!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(
                f"Failed to set timer ringtone: {str(e)}.\nEnsure that you entered a valid YouTube link as well as a positive integer which is lesser or equal to the length of said video.", ephemeral=True
            )


### Timer command class ###
class Timer(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        self.client.tree.add_command(TimerGroup())

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Cog Timer is ready")


async def setup(client: commands.Bot):
    await client.add_cog(Timer(client))


### functions ###


def customPathExists():
    return os.path.exists("sounds/CUSTOM.mp3")
