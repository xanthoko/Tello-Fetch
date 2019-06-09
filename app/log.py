from time import time
from datetime import datetime
from collections import namedtuple

cmdPoint = namedtuple('cmdPoint', ['command', 'sTime', 'rTime'])


class Logger:
    """Handles the logs of a tello session.

    Attributes:
        starting_time: The starting datetime of the session
        start_stamp: Starting timestamp
        command_sent: A list tuple containing the body and the time of the
            command sent to tello
        command_tuples: A list of cmdPoint tuples
        battery: The battery level of tello
        status: The status of tello
        initialized: A boolean that indicates if tello is initialized
    """

    def __init__(self):
        self.starting_time = datetime.now().strftime('%A %d. %B, %H:%M')
        self.start_stamp = time()

        self.command_sent = ()  # tuple with the command sent and its timestamp
        self.command_tuples = []  # list of cmdPoints

        self.battery = None
        self.status = 'Not connected'

        self.initialized = False

    def set_command_sent(self, command):
        self.command_sent = (command, time() - self.start_stamp)

    def reset(self):
        """Sets the command_sent attribute to an empty tuple."""
        self.command_sent = ()

    def received(self, response):
        """Handles tello's response.

        If it is not an error response, updates the command_tuples list,
        the status and the battery level.

        Args:
            response (string): The body of the response
        Returns:
            bool: True if execution was successful, False if response was
            "Error" or a command was not sent
        """
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
        """Forms a list of the grouped pathing commands.

        Pathing commands have the following format: {direction} {value}
        Same commands are grouped, that means that they are represented
        as {direction} {sum_value}.

        Returns:
            List of strings: The grouped command strings.
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
        reveresed.

        The reverse of a command is defined by the reverse_cmd_map dictionary.

        Returns:
            List of strings: The reversed pathing commands
        """
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
        """Generates a txt file with the commands of the current session.

        Args:
            txt_name (string): The name of the generated file
        """
        if self.starting_time is None:
            print('[INFO] Empty session.')
            return
        with open(txt_name, 'w') as f:
            f.write(self.starting_time + '\n')
            for cmd in self.command_tuples:
                f.write(
                    '\n{cmd.command}\t {cmd.sTime} {cmd.rTime}'.format(cmd=cmd))

    def update_status(self, cmd):
        """Updates the status according to the executed command.

        Args:
            cmd (string): The body of the command executed
        """
        if cmd == 'command':
            self.initialized = True
            self.status = 'Connected'
        elif cmd == 'takeoff':
            self.status = 'In air'
        elif cmd == 'land':
            self.status = 'Landed'
