#!/usr/bin/env python

import asyncio
import irc_agent
import os
import signal
import slack_agent
import sys

class MessageSynchronizer:
    def __init__(self):
        self.to_terminate = False
        self.loop = asyncio.get_event_loop()
        self.irc_client = irc_agent.Irc('localhost', 6667, 'rubot', ['#prosymtest'])
        self.slack_client = slack_agent.Slack(os.getenv("SLACK_TOKEN"))
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.to_terminate = True

    def run(self):
        tasks = asyncio.wait([self.fetch_from_irc(), self.fetch_from_slack()])
        self.loop.run_until_complete(tasks)

    async def fetch_from_irc(self):
        while (not self.to_terminate):
            self.irc_client.process_once(0.1)
            for message in self.irc_client.iter_messages():
                message_str = 'IRC: ' + message
                print(message_str)
                # self.slack_client.
            await asyncio.sleep(0.1)

    async def fetch_from_slack(self):
        while (not self.to_terminate):
            messages = self.slack_client.rtm_read()
            for message in messages:
                if message['type'] == 'message':
                    message_str = 'Slack: @{0}: {1} (#{2})'.format(
                        str(message['user']),
                        str(message['text']),
                        str(message['channel']))
                    print(message_str)
                    self.irc_client.privmsg('#prosymtest', message_str)
            await asyncio.sleep(0.2)

def main(argv):
    sync = MessageSynchronizer()
    sync.run()
    print("")
    print("Finished correctly.")

if __name__ == "__main__":
    main(sys.argv)
