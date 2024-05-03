from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import getResponse

# Load environment variables
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")
print(TOKEN)

# Bot Setup
intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)

# Event: Bot is ready
@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")

# Main entry point
def main()-> None:
    client.run(token=TOKEN)


if __name__ == "__main__":
    main()

