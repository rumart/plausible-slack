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
PERIOD = os.environ['PERIOD'] #Either day or week

today = datetime.today()
thisPer = today - timedelta(1)
prevPer = thisPer - timedelta(7)
date = thisPer.strftime('%Y-%m-%d')
prevPerDate = prevPer.strftime('%Y-%m-%d')

if PERIOD == 'week':
    periodTxt = 'last week'
    prevPeriodTxt = 'two weeks ago'
    PERIOD = '7d'
else:
    periodTxt = 'yesterday'
    prevPeriodTxt = 'last week'

headers = {'Authorization': f'Bearer {PLAUSIBLE_TOKEN}'}

thisPerUrl = f'https://{PLAUSIBLE_HOST}/api/v1/stats/aggregate?site_id={SITE_ID}&period={PERIOD}&date={date}&metrics=visitors,pageviews'
prevPerUrl = f'https://{PLAUSIBLE_HOST}/api/v1/stats/aggregate?site_id={SITE_ID}&period={PERIOD}&date={prevPerDate}&metrics=visitors,pageviews'

thisReq = requests.get(thisPerUrl, None, headers=headers)
prevReq = requests.get(prevPerUrl, None, headers=headers)

thisResponse = thisReq.json()
visitors = thisResponse['results']['visitors']['value']
pageViews = thisResponse['results']['pageviews']['value']

prevResponse = prevReq.json()
prevVisitors = prevResponse['results']['visitors']['value']
prevPageViews = prevResponse['results']['pageviews']['value']

cVisitors = get_change(visitors,prevVisitors)
cVisitorsTxt = "%.2f" % cVisitors
cPageViews = get_change(pageViews,prevPageViews)
cPageViewsTxt = "%.2f" % cPageViews

visitorChange = ''
if visitors > prevVisitors:
    visitorChange = 'more'
else:
    visitorChange = 'fewer'

pageViewChange = ''
if pageViews > prevPageViews:
    pageViewChange = 'more'
else:
    pageViewChange = 'fewer'

try:
    client = WebClient(token=SLACK_TOKEN)

    response = client.chat_postMessage(
        channel=SLACK_CHANNEL,
        text=f'Your site {SITE_ID} had {pageViews} pageviews from {visitors} visitors {periodTxt}!\nThat\'s {cPageViewsTxt}% {pageViewChange} pageviews and {cVisitorsTxt}% {visitorChange} visitors than {prevPeriodTxt}'
    )
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["error"]  
