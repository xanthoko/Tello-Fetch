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
        """Appends to command_tuples (command, sTime, rTime)."""
        rsp_time = time()
        latest_cmd = self.commands[-1]
        # form the cmdPoint tuple
        cmd_tuple = cmdPoint(
            command=latest_cmd[0], sTime=latest_cmd[1], rTime=rsp_time)
        self.command_tuples.append(cmd_tuple)

        if latest_cmd[0] == 'command':
            # if the response refers to the "command" command start the session
            self.start_session()
            self.initialized = True

    def get_pathing_commands(self):
        """Returns a list of the pathing commands.

        Pathing commands have the following format. {direction} {value} 
        """
        pathing_command_list = [
            'up', 'down', 'left', 'right', 'forward', 'back', 'cw', 'ccw'
        ]
        filtered_commands = list(
            filter(lambda x: x.command.split(' ')[0] in pathing_command_list,
                   self.command_tuples))
        return filtered_commands

    def to_text(self, txt_name):
        """Creates a text to with the starting datetime and the
        pathing commands."""
        if self.starting_time is None:
            print('[INFO] Empty session.')
            return
        with open(txt_name, 'w') as f:
            f.write(self.starting_time + '\n')
            for cmd in self.get_pathing_commands():
                f.write('\n' + cmd.command)
