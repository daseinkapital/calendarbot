import os
import time
from slackclient import SlackClient
from calendar_call import StripEventName, CalendarResponse

import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()


BOT_NAME = 'calendarbot'

#set id to environment variable
BOT_ID = your_bot_id_here

#constants
AT_BOT = "<@" + BOT_ID + ">"
WHEN_COMMAND = "when"
WHERE_COMMAND = "where"


slack_client = SlackClient(your_secret_here)
       
        
def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    first, second = StripEventName(command)
    if first:
        response = CalendarResponse(first, second, command)
    else:
        response = "Not sure what you mean. Use the *" + WHEN_COMMAND + \
           "* or the *" + WHERE_COMMAND + "* command with numbers, delimited by spaces."

    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)      

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")