#!/usr/bin/env python

import asyncio
import irc_agent
import os
import signal
import slack_agent
import sys

class TerminationController:
    to_terminate = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.to_terminate = True

async def fetch_from_irc(termination_controller, irc_client, slack_client):
    while (not termination_controller.to_terminate):
        irc_client.process_once(0.1)
        for message in irc_client.iter_messages():
            message_str = 'IRC: ' + message
            print(message_str)
            # slack_client.
        await asyncio.sleep(0.1)

async def fetch_from_slack(termination_controller, slack_client, irc_client):
    while (not termination_controller.to_terminate):
        messages = slack_client.rtm_read()
        for message in messages:
            if message['type'] == 'message':
                message_str = 'Slack: @{0}: {1} (#{2})'.format(
                    str(message['user']),
                    str(message['text']),
                    str(message['channel']))
                print(message_str)
                irc_client.privmsg('#prosymtest', message_str)
        await asyncio.sleep(0.2)

def main(argv):
    termination_controller = TerminationController()
    loop = asyncio.get_event_loop()
    irc_client = irc_agent.Irc('localhost', 6667, 'rubot', ['#prosymtest'])
    slack_client = slack_agent.Slack(os.getenv("SLACK_TOKEN"))
    tasks = asyncio.wait([fetch_from_irc(termination_controller, irc_client, slack_client),
                          fetch_from_slack(termination_controller, slack_client, irc_client)])
    loop.run_until_complete(tasks)
    print("")
    print("Finished correctly.")

if __name__ == "__main__":
    main(sys.argv)
