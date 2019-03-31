import os
import socket
import threading
from time import time

from log import Logger

TIMEOUT = 10


class Tello:
    host = ''
    tello_ip = '192.168.10.1'
    cmd_port = 8889
    state_port = 8890
    cmd_address = (tello_ip, cmd_port)
    state_address = (tello_ip, state_port)

    def __init__(self, session_id):
        # bind command socket to command address
        self.cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.cmd_socket.bind((self.host, self.cmd_port))

        # start the receiving command thread
        self.receive_cmd_thread = threading.Thread(
            target=self._receive_cmd_thread)
        self.receive_cmd_thread.daemon = True
        self.receive_cmd_thread.start()

        # response waiting flag
        self.waiting = False

        self.session_id = session_id

        # initialize the logger object
        self.log = Logger()

    def send_command(self, command, reverse=False):
        if self.waiting:
            # if the server is waiting for a reponse, not further command
            # can be accepted and sent
            print('[ERROR] Another command awaits reponse, please wait')
        else:
            if command != 'command' and not self.log.initialized:
                # if tello is not initialized it cannot accept any commands
                print(
                    '[ERROR]: Tello must be initialized. Run "command" first.')
                return False

            if not reverse:
                # if the command is part of fetching, dont print it
                print('[INFO]  Sending: {}'.format(command))
            # send the command encoded to utf-8
            self.cmd_socket.sendto(command.encode('utf-8'), self.cmd_address)
            self.log.add_command(command)
            # waiting flag is set to True
            self.waiting = True

            start = time()
            while self.waiting:
                if time() - start > TIMEOUT:
                    # when the waiting period exceeds the timeout limit print the
                    # error and set the waiting flag to False, so that the server
                    # can accept a new command
                    print('[ERROR] Command {} timed out.'.format(command))
                    self.log.command_timeout()
                    self.waiting = False
                    break
            else:
                # when the reponse arrives, self.waiting becomes False and
                # the given command is appended to the commands list
                self.log.add_command(command)

    def _receive_cmd_thread(self):
        while True:
            try:
                response, ip = self.cmd_socket.recvfrom(1024)
                print('[INFO]  Response: {}'.format(response.decode()))
                if self.waiting:
                    # if the server is waiting for a reponse, set the waiting
                    # flag to False, as the response has arrived
                    self.log.log_response(response)
                    self.waiting = False
            except socket.error as e:
                print('[ERROR] {}'.format(e))

    def fetch(self):
        """Sends the reversed path commands to tello."""
        print('[INFO] Returning home...')
        r_cmds = self.log.reverse_path_cmd()
        for cmd in r_cmds:
            self.send_command(cmd, reverse=True)

    def write_session(self):
        try:
            os.makedirs('sessions')
        except FileExistsError:
            # session directory already exists
            pass
        name = 'sessions/session_{}.txt'.format(self.session_id)
        self.log.to_text(name)

    def initialize(self):
        self.send_command('command')
