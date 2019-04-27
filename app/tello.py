import os
import socket
import threading
import numpy as np
from time import time

import libh264decoder

from log import Logger

TIMEOUT = 10


class Tello:
    host = ''
    tello_ip = '192.168.10.1'
    cmd_port = 8889
    state_port = 8890
    video_port = 11111
    cmd_address = (tello_ip, cmd_port)
    state_address = (tello_ip, state_port)
    video_address = (tello_ip, video_port)

    def __init__(self):
        # create command socket and bind it to cmd_port
        self.cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.cmd_socket.bind((self.host, self.cmd_port))

        # create video socket and bind it to video address
        self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.video_socket.bind((self.host, self.video_port))

        # start the receiving command thread
        self.receive_cmd_thread = threading.Thread(
            target=self._receive_cmd_thread)
        self.receive_cmd_thread.start()

        # create the video thread
        self.receive_video_thread = threading.Thread(
            target=self._receive_video_thread)

        # response waiting flag
        self.waiting = False

        # initialize the logger object
        self.log = Logger()

        # tello status
        self.status = 'Not connected'

        # h264 decoder
        self.decoder = libh264decoder.H264Decoder()

        self.frame = None

    def __del__(self):
        self.cmd_socket.close()
        self.video_socket.close()

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
                # when the response arrives, self.waiting is set to False
                if time() - start > TIMEOUT:
                    # when the waiting period exceeds the timeout limit print the
                    # error and set the waiting flag to False, so that the server
                    # can accept a new command
                    print('[ERROR] Command {} timed out.'.format(command))
                    self.log.command_timeout()
                    self.waiting = False
                    break
            else:
                # if command is streamon, start the video receiving thread
                if command == 'streamon':
                    self.receive_video_thread.start()

    def _receive_cmd_thread(self):
        """Waits for a response to come and if client is waiting for a response,
        log the response and set waiting=False."""
        while True:
            try:
                response, ip = self.cmd_socket.recvfrom(1024)
                try:
                    print('[INFO]  Response: {}'.format(
                        response.decode('UTF-8')))
                except UnicodeDecodeError:
                    print('UNCIDECODE ERROR')
                    # print('[INFO]  Response: {}'.format(
                    #     response.decode('latin-1')))
                if self.waiting:
                    # if the server is waiting for a reponse, set the waiting
                    # flag to False, as the response has arrived
                    self.log.log_response(response)
                    self.waiting = False
            except socket.error as e:
                print('[ERROR] {}'.format(e))

    def _receive_video_thread(self):
        """Receives response from the video socket and decodes the incoming
        bytestream to frames. Frames are 960x720."""
        # python 2
        packet_data = ""
        while True:
            try:
                res_string, ip = self.video_socket.recvfrom(2048)
                packet_data += res_string
                # end of frame
                if len(res_string) != 1460:
                    for frame in self._h264_decode(packet_data):
                        self.frame = frame
                    packet_data = ""

            except socket.error as exc:
                print("Caught exception socket.error : %s" % exc)

        # python 3
        # packet_data = bytearray("", encoding='utf8')
        # while True:
        #     try:
        #         response, ip = self.video_socket.recvfrom(2048)
        #         packet_data.extend(response)
        #         if len(response) != 1460:
        #             # decode packet_data to frames
        #             print(len(packet_data))
        #             packet_data.clear()
        #     except socket.error as e:
        #         print('[ERROR] {}'.format(e))

    def _h264_decode(self, packet_data):
        """Decode raw h264 format data from Tello.

        :param packet_data: raw h264 data array

        :return: a list of decoded frame
        """
        res_frame_list = []
        frames = self.decoder.decode(packet_data)
        for framedata in frames:
            (frame, w, h, ls) = framedata
            if frame is not None:
                frame = np.fromstring(
                    frame, dtype=np.ubyte, count=len(frame), sep='')
                frame = (frame.reshape((h, ls / 3, 3)))
                frame = frame[:, :w, :]
                res_frame_list.append(frame)

        return res_frame_list

    def fetch(self):
        """Sends the reversed path commands to tello."""
        print('[INFO] Returning home...')
        r_cmds = self.log.reverse_path_cmd()
        for cmd in r_cmds:
            self.send_command(cmd, reverse=True)

    def replay_session(self, session_file):
        """Reads the command of the session file given and executes them."""
        with open(session_file, 'r') as f:
            lines = f.readlines()
            # line1: date, line2: new_line, line3: "command"
            cmd_tuples = lines[3:]

        # the command part of the tuple
        raw_cmds = list(map(lambda x: x.split('\t')[0], cmd_tuples))
        for cmd in raw_cmds:
            self.send_command(cmd)

    def write_session(self, session_id):
        try:
            os.makedirs('../sessions')
        except FileExistsError:
            # session directory already exists
            pass
        name = '../sessions/session_{}.txt'.format(session_id)
        self.log.to_text(name)

    def get_status(self):
        """Returns the tello's status."""
        return self.log.status

    def initialize(self):
        """Sends 'command' and updates the status to 'Connected'."""
        self.send_command('command')
        self.status = 'Connected'
        return self.log.initialized
