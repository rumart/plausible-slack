# plausible-slack

The script will pull visitor and page view stats for a site from a Plausible host, then do a rudimentary compare against the same day last week and finally post a message to a Slack channel with the results.

Note that the Slack integration expects a [Slack App](https://slack.com/apps) with a [Bot OAuth token](https://api.slack.com/authentication/oauth-v2). The token should be created with ``chat:write`` access to the channel, and the App needs to be added to the channel

The script accepts the environment variables:

- SLACK_TOKEN
    - Bot user OAuth Token
- SLACK_CHANNEL
    - ID of Slack channel to post message to
- PLAUSIBLE_HOST
    - Plausible host that holds your stats, Note! fqdn only
- PLAUSIBLE_TOKEN
    - API token for authenticating with Plausible host
- SITE_ID
    - Site ID as created in the Plausible host
- LOGLEVEL
    - Log level, defaults to INFO
- PERIOD
    - Stat period, day or week (last 7 days) supported. Defaults to day

## Run as a container

Pass environments on the command line

```
docker run --rm -e SLACK_TOKEN=<slack-token> -e SLACK_CHANNEL=<slack-channel> -e PLAUSIBLE_HOST=<plausible-host> -e PLAUSIBLE_TOKEN=<plausible-token> -e SITE_ID=<site-id> rumart/plausibleslack:0.3.0
```

Pass environments in a file

*env.list*

```
LOGLEVEL=debug
PERIOD=week
SLACK_TOKEN=xoxb-xxxxxxxx
SLACK_CHANNEL=Cxxxxxx
PLAUSIBLE_HOST=plausible.xyz
PLAUSIBLE_TOKEN=O-xxxxx
SITE_ID=rudimartinsen.com
```

```
docker run --rm --env-file env.list rumart/plausibleslack:<tag>
```

## Build your own container

```
docker build -t plausibleslack:<tag> .
```
