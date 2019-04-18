from time import time
from datetime import datetime
from collections import namedtuple

cmdPoint = namedtuple('cmdPoint', ['command', 'sTime', 'rTime'])


class Logger:
    def __init__(self):
        self.starting_time = datetime.now().strftime('%A %d. %B, %H:%M')
        self.start_stamp = time()

        # list of command with their timestamp
        self.commands = []
        self.command_tuples = []
        self.initialized = False

        self.status = 'Not connected'

    def add_command(self, command):
        """Add command to commands list along with the sending time."""
        send_tuple = (command, time() - self.start_stamp)
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
        rsp_time = time() - self.start_stamp
        latest_cmd = self.commands[-1]
        # form the cmdPoint tuple
        cmd_tuple = cmdPoint(
            command=latest_cmd[0], sTime=latest_cmd[1], rTime=rsp_time)
        self.command_tuples.append(cmd_tuple)

        # update tello's status
        self.update_status(latest_cmd[0])

        if latest_cmd[0] == 'command':
            # if the response refers to the "command" command start the session
            self.initialized = True

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
                f.write('\n{cmd.command}\t {cmd.sTime} {cmd.rTime}'.format(
                    cmd=cmd))

    def update_status(self, cmd):
        """Updates the status according to the executed command."""
        if cmd == 'command':
            self.status = 'Connected'
        elif cmd == 'takeoff':
            self.status = 'In air'
        elif cmd == 'land':
            self.status = 'Landed'
