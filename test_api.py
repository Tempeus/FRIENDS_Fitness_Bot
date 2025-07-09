import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import os
from dotenv import load_dotenv
load_dotenv()

STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
STRAVA_REFRESH_TOKEN = os.getenv('STRAVA_REFRESH_TOKEN')


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
print(strava_token)

activities_url = "https://www.strava.com/api/v3/athlete/activities"

header = {'Authorization': 'Bearer ' + strava_token}
param = {'per_page': 200, 'page': 1}

my_dataset = requests.get(activities_url, headers=header, params=param).json()

print(my_dataset)



