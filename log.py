from time import time
from datetime import datetime
from collections import namedtuple

cmdPoint = namedtuple('cmdPoint', ['command', 'sTime', 'rTime'])


class Logger:
    def __init__(self):
        self.starting_time = None
        self.start_stamp = None

        # list of command with their timestamp
        self.commands = []
        self.command_tuples = []
        self.initialized = False

    def start_session(self):
        self.starting_time = datetime.now().strftime('%A %w. %B, %H:%M')
        self.start_stamp = time()

    def add_command(self, command):
        send_tuple = (command, time())
        self.commands.append(send_tuple)

    def command_timeout(self):
        """If the command sent times out, delete it from commnads list."""
        try:
            del self.commands[-1]
            return True
        except IndexError:
            return False

    def log_response(self, response):
        rsp_time = time()
        latest_cmd = self.commands[-1]
        cmd_tuple = cmdPoint(
            command=latest_cmd[0], sTime=latest_cmd[1], rTime=rsp_time)
        self.command_tuples.append(cmd_tuple)

        if latest_cmd[0] == 'command':
            # if the response refers to the "command" command start the session
            self.start_session()
            self.initialized = True

    def __str__(self):
        return ''
