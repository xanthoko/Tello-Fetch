import keyboard
from time import time

from tello import Tello

cmd_map = {
    't': 'takeoff',
    'l': 'land',
    'up': 'up 20',
    'down': 'down 20',
    'w': 'forward 20',
    's': 'back 20',
    'a': 'left 20',
    'd': 'right 20',
    'right': 'cw 20',
    'left': 'ccw 20'
}

SESSION_TIMEOUT = 200  # seconds


class Controller:
    """Uses the keyboard to controll the tello."""

    def __init__(self, session_id):
        """Initializes Tello object with the given session id
        and setup listeners on key pressing events."""
        self.tello = Tello(session_id)
        # all command keys have the same callback except "i"
        keyboard.on_press_key('i', self.connect)
        keyboard.on_press_key('t', self.exec_cmd)
        keyboard.on_press_key('l', self.exec_cmd)
        keyboard.on_press_key('up', self.exec_cmd)
        keyboard.on_press_key('down', self.exec_cmd)
        keyboard.on_press_key('left', self.exec_cmd)
        keyboard.on_press_key('right', self.exec_cmd)
        keyboard.on_press_key('w', self.exec_cmd)
        keyboard.on_press_key('s', self.exec_cmd)
        keyboard.on_press_key('a', self.exec_cmd)
        keyboard.on_press_key('d', self.exec_cmd)

    def connect(self, event):
        """Uppon pressing "i", tello is initialized with the
        "command" command and the session begins"""
        self.tello.initialize()

    def exec_cmd(self, event):
        """Sends to tello the command mapped by the key
        pressed."""
        try:
            # event.name = name of the key pressed
            command = cmd_map[event.name]
            self.tello.send_command(command)
        except KeyError:
            print('[ERROR]: Cannot handle this command key.')

    def command_loop(self):
        """Waits for keys to be pressed.

        Exits after "esc" press and timeouts after TIMEOUT seconds.
        """
        start = time()
        while True:
            key = keyboard.read_event().name
            if key == 'esc':
                self.tello.write_session()
                break
            if time() - start > SESSION_TIMEOUT:
                break


session_name = input('Enter session id/name: ')
obj = Controller(session_name)
obj.command_loop()
