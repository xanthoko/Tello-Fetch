from time import time
from datetime import datetime
from collections import namedtuple

cmdPoint = namedtuple('cmdPoint', ['command', 'sTime', 'rTime'])


class Logger:
    def __init__(self):
        # list of command with their timestamp
        self.commands = []
        self.starting_time = None
        self.start_stamp = None

        self.command_tuples = []

    def start_session(self):
        self.starting_time = datetime.now().strftime('%A %w. %B, %H:%M')
        self.start_stamp = time()

    def add_command(self, command):
        send_tuple = (command, time())
        self.commands.append(send_tuple)

    def log_response(self, response):
        rsp_time = time()
        latest_cmd = self.commands[-1]
        cmd_tuple = cmdPoint(
            command=latest_cmd[0], sTime=latest_cmd[1], rTime=rsp_time)
        self.command_tuples.append(cmd_tuple)

    def is_live(self):
        return self.starting_time is not None

    def __str__(self):
        return ''
