# -*- coding: utf-8 -*-

import slackclient

class Slack(object):
    def __init__(self, token):
        self.slack_client = slackclient.SlackClient(token)
        if self.slack_client.rtm_connect():
            self.rtm = True
        else:
            self.rtm = False

    def rtm_read(self):
        if self.rtm:
            return self.slack_client.rtm_read()
        else:
            return []

    def post(self, channel, line, user):
        self.slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=line,
            user=user)
