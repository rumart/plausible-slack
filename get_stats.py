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
PERIOD = os.environ.get('PERIOD', 'day') #Either day or week (7d)
TOPPAGE = True#os.environ.get('TOPCOUNTRY', True) #Pull top page visits
TOPCOUNTRY = True#os.environ.get('TOPCOUNTRY', True) #Pull top country

plausibleLink = f"https://{PLAUSIBLE_HOST}/{SITE_ID}"

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
topPageUrl = f'https://{PLAUSIBLE_HOST}/api/v1/stats/breakdown?site_id={SITE_ID}&period={PERIOD}&date={date}&property=event:page&limit=1'
topContryUrl = f'https://{PLAUSIBLE_HOST}/api/v1/stats/breakdown?site_id={SITE_ID}&period={PERIOD}&date={date}&property=visit:country&limit=1'

thisReq = requests.get(thisPerUrl, None, headers=headers)
prevReq = requests.get(prevPerUrl, None, headers=headers)

thisResponse = thisReq.json()
visitors = thisResponse['results']['visitors']['value']
pageViews = thisResponse['results']['pageviews']['value']

prevResponse = prevReq.json()
prevVisitors = prevResponse['results']['visitors']['value']
prevPageViews = prevResponse['results']['pageviews']['value']

if TOPPAGE == True:
    pageReq = requests.get(topPageUrl, None, headers=headers)
    pageResponse = pageReq.json()
    topPage = pageResponse['results'][0]['page']
    pageVisitors = pageResponse['results'][0]['visitors']

if TOPCOUNTRY == True:
    countryReq = requests.get(topContryUrl, None, headers=headers)
    countryResponse = countryReq.json()
    topCountry = countryResponse['results'][0]['country']
    countryVisitors = countryResponse['results'][0]['visitors']

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
        text=f'Your site {SITE_ID} had {pageViews} pageviews from {visitors} visitors {periodTxt}!\nThat\'s *{cPageViewsTxt}%* {pageViewChange} pageviews and *{cVisitorsTxt}%* {visitorChange} visitors than {prevPeriodTxt}\nThe most visited page was *{topPage}* with *{pageVisitors}* visitors\nMost requests came from *{topCountry}* with *{countryVisitors}* visitors\n{plausibleLink}'
    )
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["error"]  
