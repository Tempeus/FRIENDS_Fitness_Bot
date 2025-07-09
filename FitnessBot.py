import os
import discord
from discord.ext import commands, tasks
from discord.utils import get
from dotenv import load_dotenv
import datetime

# Define your intents
intents = discord.Intents.default()
intents.members = False  # Disable typing events, if needed
intents.presences = False  # Disable presence events, if needed
intents.message_content = True    # Enable message content updates (required for commands)

# environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHAN_NAME = os.getenv('CHAN')

client = discord.Client(intents=discord.Intents.default())

# Initialize the bot with the intents
bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)

# Event when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Task that checks hourly and posts the weekly leaderboard every Friday at 5 PM
@tasks.loop(hours=1)  # Check every hour
async def weekly_leaderboard():
    # Get the current time in the system's local timezone
    current_time = datetime.datetime.now()

# Start the bot
bot.run(TOKEN)
