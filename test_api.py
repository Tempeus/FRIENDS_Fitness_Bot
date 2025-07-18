import requests
import urllib3
from datetime import datetime, timedelta, timezone
from dateutil import parser as date_parser
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import os
from dotenv import load_dotenv
load_dotenv()

STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
STRAVA_REFRESH_TOKEN = os.getenv('STRAVA_REFRESH_TOKEN')
STRAVA_AUTH_CODE = os.getenv('STRAVA_AUTH_CODE')

# This is code for getting the Authorization code to get the new refresh token with permission to read stuff
# auth_url = "https://www.strava.com/oauth/token"
# payload = {
#     'client_id': STRAVA_CLIENT_ID,
#     'client_secret': STRAVA_CLIENT_SECRET,
#     'code': STRAVA_AUTH_CODE,
#     'grant_type': "authorization_code",
#     'f': 'json'
# }

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

# Format output
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

def check_weekly_activity_count(activities, min_count=4):
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

    if count < min_count:
        print(f"Hey everyone, time to call out @Tempeus for not meeting the minimum fitness quota of {min_count} activities")
        print(f"Activities this week: {count}")

display_strava_summary(my_dataset)

check_weekly_activity_count(my_dataset, 3)
