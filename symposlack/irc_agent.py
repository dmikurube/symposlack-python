# -*- coding: utf-8 -*-

import collections
import irc.client
import sys

class Irc(object):
    def __init__(self, host, port, nick, targets):
        self.reactor = irc.client.Reactor()
        try:
            self.connection = self.reactor.server().connect(host, port, nick)
        except irc.client.ServerConnectionError:
            print(sys.exc_info()[1])
            raise SystemExit(1)
        self.targets = targets
        # This Irc class assumes single-threaded.
        self.messages = collections.deque()
        self.connection.add_global_handler("welcome", self.on_welcome)
        self.connection.add_global_handler("join", self.on_join)
        self.connection.add_global_handler("disconnect", self.on_disconnect)
        self.connection.add_global_handler("pubmsg", self.on_pubmsg)
        self.connection.add_global_handler("pubnotice", self.on_pubmsg)
        self.connection.add_global_handler("quit", self.on_quit)
        self.connection.add_global_handler("part", self.on_quit)
        self.connection.add_global_handler("nick", self.on_nick)
        self.connection.add_global_handler("topic", self.on_topic)

    def on_welcome(self, connection, event):
        self.messages.append("Welcome: " + str(event))
        for target in self.targets:
            if irc.client.is_channel(target):
                connection.join(target)

    def on_join(self, connection, event):
        self.messages.append("Joined: " + str(event))

    def on_disconnect(self, connection, event):
        self.messages.append("Disconnected: " + str(event))

    def on_pubmsg(self, connection, event):
        nick = irc.client.NickMask(event.source).nick
        message = event.arguments[0]
        self.messages.append("({0:>10s}) {1}".format(nick, message))

    def on_quit(self, connection, event):
        nick = irc.client.NickMask(event.source).nick
        self.messages.append("* {0} {1} ({2})".format(nick, event.type, event.arguments[0]))

    def on_nick(self, connection, event):
        nick = irc.client.NickMask(event.source).nick
        new = event.target
        self.messages.append("* nick: {0} -> {1}".format(nick, new))

    def on_topic(self, connection, event):
        nick = irc.client.NickMask(event.source).nick
        topic = event.arguments[0]
        self.messages.append("* {0} topic: {1}".format(nick, topic))

    def privmsg(self, target, line):
        self.connection.privmsg(target, line)

    def process_once(self, timeout):
        self.reactor.process_once(timeout)

    def iter_messages(self):
        while self.messages:
            yield self.messages.popleft()
