import asyncio
import datetime
from discord.ext import commands, tasks
from discord import (
    app_commands,
    ButtonStyle,
    Guild,
    Interaction,
    ScheduledEvent,
    SelectOption,
    TextChannel,
    ui
)
from typing import Final


### Reminder info class ###
class ReminderObject():
    def __init__(self, timestamp: datetime, roles: list[int], members: list[int]):
        self.timestamp = timestamp
        self.roles = roles
        self.members = members

event_dict: dict[int, list[ReminderObject]] = {}
reminder_timestamps: list[datetime.datetime] = []


### Roles dropdown ###
class RoleDropdown(ui.Select):
    def __init__(self, interaction: Interaction):
        options: Final[list[SelectOption]] = []
        for role in interaction.guild.roles:
            if (role != interaction.guild.default_role):
                options.append(SelectOption(label=f"{role.name}", value=f"{role.id}"))
        super().__init__(
            placeholder="Roles",
            options=options,
            custom_id="SelectRoles",
            min_values=0,
            max_values=options.__len__(),
        )

    async def callback(self, interaction: Interaction) -> None:
        self.view.roles = list[int](self.values)
        await interaction.response.defer()


### Members dropdown ###
class MemberDropdown(ui.Select):
    def __init__(self, interaction: Interaction):
        options: Final[list[SelectOption]] = []
        for member in interaction.guild.members:
            options.append(SelectOption(label=f"{member.name}", value=f"{member.id}"))
        super().__init__(
            placeholder="Members",
            options=options,
            custom_id="SelectMembers",
            min_values=0,
            max_values=options.__len__(),
        )

    async def callback(self, interaction: Interaction) -> None:
        self.view.members = list[int](self.values)
        await interaction.response.defer()


### Event selection confirm button ###
class MemberConfirmButton(ui.Button):
    def __init__(self):
        super().__init__(
            label="Confirm",
            style=ButtonStyle.green,
            custom_id="memberConfirmButton",
        )

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()

        view = self.view
        if (view.event_id not in event_dict):
            event_dict[view.event_id] = []
        event_dict[view.event_id].append(ReminderObject(view.reminder_timestamp, view.roles, view.members))
        reminder_timestamps.append(view.reminder_timestamp)
        reminder_timestamps.sort()
        interaction.client.get_cog("Reminder").monitorReminders.restart()

        await interaction.followup.send(
            f"Succesfully added reminder for event " +
                f"**{interaction.guild.get_scheduled_event(view.event_id).name}** on " +
                f"{view.reminder_timestamp.astimezone().strftime('**%m/%d** at **%H:%M**')}!",
            ephemeral=True
        )


### Members and roles view menu class
class MemberSelectionView(ui.View):
    def __init__(self, interaction: Interaction, event_id: int, reminder_timestamp: datetime):
        super().__init__()

        self.event_id = event_id
        self.reminder_timestamp = reminder_timestamp
        self.roles: list[int] = []
        self.members: list[int] = []

        self.add_item(RoleDropdown(interaction=interaction))
        self.add_item(MemberDropdown(interaction=interaction))
        self.add_item(MemberConfirmButton())


### Minutes class ###
class mDropdown(ui.Select):
    def __init__(self) -> None:
        options: Final[list[SelectOption]] = []
        for i in range(60):
            if i % 5 == 0:
                options.append(SelectOption(label=f"{i} minutes", value=f"{i}"))
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


### Hours class ###
class hDropdown(ui.Select):
    def __init__(self) -> None:
        options: Final[list[SelectOption]] = []
        for i in range(24):
            options.append(SelectOption(label=f"{i} hours", value=f"{i}"))
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


### Days class ###
class dDropdown(ui.Select):
    def __init__(self) -> None:
        options: Final[list[SelectOption]] = []
        for i in range(5):
            options.append(SelectOption(label=f"{i} days", value=f"{i}"))
        super().__init__(
            placeholder="Days",
            options=options,
            custom_id="SelectDays",
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: Interaction) -> None:
        self.view.days = int(self.values[0])
        await interaction.response.defer()


### Confirm timestamp button ###
class TimeConfirmButton(ui.Button):
    def __init__(self):
        super().__init__(
            label="Confirm",
            style=ButtonStyle.green,
            custom_id="timeConfirmButton",
        )

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()
        total_minutes = (
            self.view.minutes + (self.view.hours * 60) + (self.view.days * 24 * 60)
        )
        event = interaction.guild.get_scheduled_event(self.view.event_id)
        reminder_timestamp = event.start_time - datetime.timedelta(minutes=total_minutes)
        if (reminder_timestamp < datetime.datetime.now(datetime.timezone.utc)):
            await interaction.followup.send(
                "Cannot set a reminder in the past.",
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            "Select the members and roles to ping for the reminder.",
            view=MemberSelectionView(
                interaction=interaction,
                event_id=self.view.event_id,
                reminder_timestamp=reminder_timestamp,
            ),
            ephemeral=True,
        )


### Time selectiondrop down menus ###
class TimeSelectionView(ui.View):
    def __init__(self, event_id: int) -> None:
        super().__init__()

        self.event_id = event_id
        self.minutes = 0
        self.hours = 0
        self.days = 0

        self.add_item(dDropdown())
        self.add_item(hDropdown())
        self.add_item(mDropdown())
        self.add_item(TimeConfirmButton())


### Event drop down menu ###
class EventDropdown(ui.Select):
    def __init__(self, events: list[ScheduledEvent]) -> None:
        options: Final[list[SelectOption]] = []
        for event in events:
            options.append(SelectOption(label=event.name, value=f"{event.id}"))
        super().__init__(
            placeholder="Events",
            options=options,
            custom_id="selectEvent",
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: Interaction):
        self.view.selected_event = int(self.values[0])
        await interaction.response.defer()


### Event selection confirm button ###
class EventConfirmButton(ui.Button):
    def __init__(self):
        super().__init__(
            label="Confirm",
            style=ButtonStyle.green,
            custom_id="eventConfirmButton",
        )

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()
        await interaction.followup.send(
            "How long before the event do you want the reminder to be sent?",
            view=TimeSelectionView(self.view.selected_event),
            ephemeral=True,
        )


### Reminder selection viewing class ###
class EventSelectionView(ui.View):
    def __init__(self, interaction: Interaction) -> None:
        super().__init__()

        self.selected_event = 0
        events = list(filter(
            lambda x: x.start_time > datetime.datetime.now(datetime.timezone.utc),
            interaction.guild.scheduled_events
        ))

        self.add_item(EventDropdown(events))
        self.add_item(EventConfirmButton())


### Reminder commands group ###
class ReminderGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="reminder", description="Manage reminders")

    ### Reminder command ###
    @app_commands.command(name="set_reminder", description="Set a reminder for a specific event")
    async def setReminder(self, interaction: Interaction) -> None:
        if (list(filter(
                lambda x: x.start_time > datetime.datetime.now(datetime.timezone.utc),
                interaction.guild.scheduled_events
            )).__len__() == 0):
            await interaction.response.send_message(
                "No upcoming events to set reminders for.",
                ephemeral=True,
            )
            return
        
        await interaction.response.send_message(
            "Select an event to set a reminder for.",
            view=EventSelectionView(interaction),
            ephemeral=True,
        )


### Reminder command class ###
class Reminder(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        self.client.tree.add_command(ReminderGroup())
        self.monitorReminders.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Cog Reminder is ready")

    @tasks.loop()
    async def monitorReminders(self):
        if (reminder_timestamps.__len__() == 0):
            try:
                await asyncio.Future()
            except asyncio.exceptions.CancelledError:
                pass
            finally:
                return

        now = datetime.datetime.now(datetime.timezone.utc)
        nextReminder = reminder_timestamps[0]
        reminderToDelete = None

        if (nextReminder <= now):
            for id, reminders in event_dict.items():
                for reminder in reminders:
                    if (reminder.timestamp == nextReminder):
                        
                        current_guild: Guild = None
                        for guild in self.client.guilds:
                            if (guild.get_scheduled_event(id) != None):
                                current_guild = guild
                                break
                        
                        general_channel: TextChannel = None
                        for channel in current_guild.text_channels:
                            if (channel.name == "general"):
                                general_channel = channel
                                break

                        reminder_message = ""
                        for role_id in reminder.roles:
                            reminder_message += f"<@&{role_id}>"
                        for member_id in reminder.members:
                            reminder_message += f"<@{member_id}>"

                        event = current_guild.get_scheduled_event(id)
                        time_till_event = event.start_time - now
                        reminder_text = " Reminder:\n" if time_till_event > datetime.timedelta(hours=1) else " STOP THROWING CHAT!\n"
                        reminder_message += reminder_text + f"[**{event.name}**]({event.url}) event on "
                        reminder_message += f"{event.start_time.astimezone().strftime('**%m/%d** at **%H:%M**')}!\n"
                        await general_channel.send(reminder_message)

                        reminder_timestamps.remove(nextReminder)
                        reminderToDelete = reminder
                        break

                if (reminderToDelete != None):
                    reminders.remove(reminderToDelete)
                    if (reminders.__len__() == 0):
                        event_dict.pop(id)
                    break

        else:
            try:
                await asyncio.sleep((nextReminder-now).total_seconds())
            except asyncio.exceptions.CancelledError:
                pass

    @monitorReminders.before_loop
    async def beforeMonitorReminders(self):
        await self.client.wait_until_ready()



async def setup(client: commands.Bot):
    await client.add_cog(Reminder(client))