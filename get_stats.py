import requests
import logging
import os

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime, timedelta

def get_change(current, previous):
    if current == previous:
        return 0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return 100

SLACK_TOKEN = os.environ['SLACK_TOKEN'] #You need a Slack App with a Bot Token that has chat:write permissions in the channel
SLACK_CHANNEL = os.environ['SLACK_CHANNEL'] #ID of slack channel, note that your Bot needs access to write to the channel AND you need to add the bot to the channel
PLAUSIBLE_HOST = os.environ['PLAUSIBLE_HOST']
PLAUSIBLE_TOKEN = os.environ['PLAUSIBLE_TOKEN']
SITE_ID = os.environ['SITE_ID']

today = datetime.today()
yesterDay = today - timedelta(1)
lastweek = yesterDay - timedelta(7)
date = yesterDay.strftime('%Y-%m-%d')
lastweekDate = lastweek.strftime('%Y-%m-%d')


#realtimeUrl = f'https://{PLAUSIBLE_HOST}/api/v1/stats/realtime/visitors?site_id={SITE_ID}'
headers = {'Authorization': f'Bearer {PLAUSIBLE_TOKEN}'}
#r = requests.get(realtimeUrl, NULL, headers=headers)

yDayUrl = f'https://{PLAUSIBLE_HOST}/api/v1/stats/aggregate?site_id={SITE_ID}&period=day&date={date}&metrics=visitors,pageviews'
wDayUrl = f'https://{PLAUSIBLE_HOST}/api/v1/stats/aggregate?site_id={SITE_ID}&period=day&date={lastweekDate}&metrics=visitors,pageviews'

y = requests.get(yDayUrl, None, headers=headers)
w = requests.get(wDayUrl, None, headers=headers)

yResponse = y.json()
visitors = yResponse['results']['visitors']['value']
pageViews = yResponse['results']['pageviews']['value']

wResponse = w.json()
wVisitors = wResponse['results']['visitors']['value']
wPageViews = wResponse['results']['pageviews']['value']

cVisitors = get_change(visitors,wVisitors)
cVisitorsTxt = "%.2f" % cVisitors
cPageViews = get_change(pageViews,wPageViews)
cPageViewsTxt = "%.2f" % cPageViews

visitorChange = ''
if visitors > wVisitors:
    visitorChange = 'more'
else:
    visitorChange = 'fewer'

pageViewChange = ''
if pageViews > cPageViews:
    pageViewChange = 'more'
else:
    pageViewChange = 'fewer'

try:
    client = WebClient(token=SLACK_TOKEN)

    response = client.chat_postMessage(
        channel=SLACK_CHANNEL,
        text=f'Your site {SITE_ID} had {pageViews} pageviews from {visitors} visitors yesterday!\nThat\'s {cPageViewsTxt}% {pageViewChange} pageviews and {cVisitorsTxt}% {visitorChange} visitors than last week'
    )
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["error"]  
