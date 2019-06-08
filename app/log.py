from time import time
from datetime import datetime
from collections import namedtuple

cmdPoint = namedtuple('cmdPoint', ['command', 'sTime', 'rTime'])


class Logger:
    def __init__(self):
        self.starting_time = datetime.now().strftime('%A %d. %B, %H:%M')
        self.start_stamp = time()

        self.command_sent = ()  # tuple with the command sent and its timestamp
        self.command_tuples = []  # list of cmdPoints

        self.battery = None
        self.status = 'Not connected'

    def set_command_sent(self, command):
        """Sets the command sent."""
        self.command_sent = (command, time() - self.start_stamp)

    def reset(self):
        """Empties the command_sent tuple."""
        self.command_sent = ()

    def log_response(self, response):
        """Handles tello's response."""
        rsp_time = time() - self.start_stamp

        if response == 'Error':
            # tello failed to execute command
            self.reset()
            return False

        try:
            # form the cmdPoint tuple
            cmd_tuple = cmdPoint(command=self.command_sent[0],
                                 sTime=self.command_sent[1],
                                 rTime=rsp_time)
            self.command_tuples.append(cmd_tuple)
        except IndexError:
            # IndexError: command_sent is an empty tuple
            return False

        # update tello's status
        self.update_status(self.command_sent[0])

        if self.command_sent[0] == 'battery?':
            self.battery = response

        return True

    def get_pathing_commands(self):
        """Returns a list of the grouped pathing commands.

        Pathing commands have the following format: {direction} {value}
        Same commands are grouped, that means that they are represented
        as {direction} {sum_value}.
        """
        pathing_command_list = [
            'up', 'down', 'left', 'right', 'forward', 'back', 'cw', 'ccw'
        ]
        filtered_commands = list(
            filter(lambda x: x.command.split(' ')[0] in pathing_command_list,
                   self.command_tuples))

        last_cmd = None
        sum_value = 0  # value of consecutive same commands
        grouped = []
        for ind, cmd in enumerate(filtered_commands):
            direction, value = cmd.command.split(' ')
            value = int(value)

            if not ind:
                # if first command, just set last command to current
                # and increase the sum_value
                last_cmd = direction
                sum_value += value
                continue

            if last_cmd == direction:
                # if same command just increase the sum_value
                sum_value += value
            else:
                # if commands diviate, append to grouped the last command
                # with the sum_value
                grouped.append('{} {}'.format(last_cmd, sum_value))
                last_cmd = direction
                # sum_value must be set to current value and not 0!
                sum_value = value

            if ind == len(filtered_commands) - 1:
                # if the last command, add it to grouped along with the
                # sum value
                grouped.append('{} {}'.format(direction, sum_value))
        return grouped

    def reverse_path_cmd(self):
        """Iterates through the grouped pathing commands and returns their
        reveresed."""
        # path_cmd is a list of cmdPoints
        path_cmd = self.get_pathing_commands()

        reverse_cmd_map = {
            'forward': 'back',
            'back': 'forward',
            'left': 'right',
            'right': 'left',
            'up': 'down',
            'down': 'up',
            'cw': 'ccw',
            'ccw': 'cw'
        }

        reversed_path_cmd = []
        for cmd in reversed(path_cmd):
            direction, value = cmd.split(' ')
            try:
                reversed_dir = reverse_cmd_map[direction]
                reversed_cmd = '{} {}'.format(reversed_dir, value)
                reversed_path_cmd.append(reversed_cmd)
            except KeyError:
                # direction not found in reverse_cmd_map
                print('Invalid direction')
        return reversed_path_cmd

    def to_text(self, txt_name):
        """Creates a text to with the starting datetime and the
        pathing commands."""
        if self.starting_time is None:
            print('[INFO] Empty session.')
            return
        with open(txt_name, 'w') as f:
            f.write(self.starting_time + '\n')
            for cmd in self.command_tuples:
                f.write('\n{cmd.command}\t {cmd.sTime} {cmd.rTime}'.format(cmd=cmd))

    def update_status(self, cmd):
        """Updates the status according to the executed command."""
        if cmd == 'command':
            self.status = 'Connected'
        elif cmd == 'takeoff':
            self.status = 'In air'
        elif cmd == 'land':
            self.status = 'Landed'
