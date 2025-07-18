import os
import discord
from discord.ext import commands, tasks
from discord.utils import get

import requests
import urllib3
from datetime import datetime, timedelta, timezone
from dateutil import parser as date_parser
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from dotenv import load_dotenv

# Define your intents
intents = discord.Intents.default()
intents.members = False  # Disable typing events, if needed
intents.presences = False  # Disable presence events, if needed
intents.message_content = True    # Enable message content updates (required for commands)

# environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHAN_NAME = os.getenv('CHAN')
KEV_ID = os.getenv('KEV_ID')

STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
STRAVA_REFRESH_TOKEN = os.getenv('STRAVA_REFRESH_TOKEN')
STRAVA_AUTH_CODE = os.getenv('STRAVA_AUTH_CODE')

#Minimum quota
MIN_COUNT = 4

client = discord.Client(intents=discord.Intents.default())

# Initialize the bot with the intents
bot = commands.Bot(command_prefix='^', intents=intents, help_command=None)

def format_seconds(seconds):
    return str(timedelta(seconds=seconds))

def display_strava_summary(activities):
    print(f"{'Name':<45} | {'Sport':<15} | {'Duration':<10} | {'Start Date':<20} | Kudos")
    print("-" * 105)
    
    for activity in activities:
        name = activity.get('name', 'N/A')[:45]
        sport = activity.get('sport_type', 'N/A')
        duration = format_seconds(activity.get('moving_time', 0))
        start_date = activity.get('start_date_local', 'N/A')
        kudos = activity.get('kudos_count', 0)
        
        print(f"{name:<45} | {sport:<15} | {duration:<10} | {start_date:<20} | {kudos}")

def get_weekly_activity_count(activities):
    now = datetime.now(timezone.utc)

    # Get start of the current week (Monday 00:00 UTC)
    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

    count = 0
    for activity in activities:
        start_date_str = activity.get("start_date") or activity.get("start_date_local")
        if not start_date_str:
            continue

        try:
            start_dt = date_parser.isoparse(start_date_str)
        except Exception:
            continue

        if start_dt >= start_of_week:
            count += 1

    return count

def getActivities():
    auth_url = "https://www.strava.com/oauth/token"
    payload = {
        'client_id': STRAVA_CLIENT_ID,
        'client_secret': STRAVA_CLIENT_SECRET,
        'refresh_token': STRAVA_REFRESH_TOKEN,
        'grant_type': "refresh_token",
        'f': 'json'
    }

    res = requests.post(auth_url, data=payload, verify=False)
    strava_token = res.json()['access_token']

    activities_url = "https://www.strava.com/api/v3/activities"

    header = {'Authorization': 'Bearer ' + strava_token}
    param = {'per_page': 200, 'page': 1}

    my_dataset = requests.get(activities_url, headers=header, params=param).json()
    return my_dataset
    

# Event when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

#Check this week activities
@bot.command(name='check')
async def check(ctx):
    activities = getActivities()
    
    now = datetime.now(timezone.utc)
    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

    weekly_activities = []
    for activity in activities:
        start_date_str = activity.get("start_date")
        if not start_date_str:
            continue
        try:
            start_dt = date_parser.isoparse(start_date_str)
        except Exception:
            continue
        if start_dt >= start_of_week:
            weekly_activities.append(activity)

    if not weekly_activities:
        return "```\n📆 No activities found for this week.\n```"

    # Build output with code block
    output = "```"
    output += f"\n📆 Activities for the Current Week ({start_of_week.date()} → {now.date()}):\n"
    output += f"{'Name':<45} | {'Sport':<15} | {'Duration':<10} | {'Start Date':<20}\n"
    output += "-" * 105 + "\n"

    for activity in weekly_activities:
        name = activity.get('name', 'N/A')[:45]
        sport = activity.get('sport_type', 'N/A')
        duration = format_seconds(activity.get('moving_time', 0))
        start_date_local = activity.get('start_date_local', 'N/A')
        output += f"{name:<45} | {sport:<15} | {duration:<10} | {start_date_local:<20}\n"

    output += "```"
    await ctx.send(output)

#trigger callout (DEBUG)
@bot.command(name='trigger')
async def trigger(ctx):
    for guild in bot.guilds:
            channel = discord.utils.get(guild.channels, name=CHAN_NAME)
            if channel:
                activities = getActivities()
                count = get_weekly_activity_count(activities)
                if(count < MIN_COUNT): #True means I failed to meet the quota
                    await channel.send(f"Hey everyone, time to call out <@{KEV_ID}> for not meeting the minimum fitness quota of {MIN_COUNT} activities")
                    await channel.send(f"Activities this week: {count}")

# Task that checks hourly and check if I'm slacking on Sunday at 8PM
@tasks.loop(hours=1)  # Check every hour
async def weekly_leaderboard():
    # Get the current time in the system's local timezone
    current_time = datetime.datetime.now()

    if current_time.weekday() == 6 and current_time.hour == 20: # 6 = Sunday, 20 = 8 PM
        for guild in bot.guilds:
            channel = discord.utils.get(guild.channels, name=CHAN_NAME)
            if channel:
                activities = getActivities()
                count = get_weekly_activity_count(activities)
                if(count < MIN_COUNT): #True means I failed to meet the quota
                    await channel.send(f"Hey everyone, time to call out <@{KEV_ID}> for not meeting the minimum fitness quota of {MIN_COUNT} activities")
                    await channel.send(f"Activities this week: {count}")

# Start the bot
bot.run(TOKEN)
