import keyboard
from tello import Tello


class Controller:
    def __init__(self, session_id):
        self.tello = Tello(session_id)
        keyboard.on_press_key('i', self.connect)
        keyboard.on_press_key('t', self.takeoff)
        keyboard.on_press_key('l', self.land)
        keyboard.on_press_key('up', self.move_up)
        keyboard.on_press_key('down', self.move_down)
        keyboard.on_press_key('w', self.move_forward)
        keyboard.on_press_key('s', self.move_back)
        keyboard.on_press_key('a', self.move_left)
        keyboard.on_press_key('d', self.move_right)

    def connect(self, event):
        self.tello.initialize()

    def takeoff(self, event):
        self.tello.send_command('takeoff')

    def land(self, event):
        self.tello.send_command('land')

    def move_up(self, event):
        self.tello.send_command('up 20')

    def move_down(self, event):
        self.tello.send_command('down 20')

    def move_forward(self, event):
        self.tello.send_command('forward 20')

    def move_back(self, event):
        self.tello.send_command('back 20')

    def move_left(self, event):
        self.tello.send_command('left 20')

    def move_right(self, event):
        self.tello.send_command('right 20')

    def command_loop(self):
        from time import time
        start = time()
        while True:
            key = keyboard.read_event().name
            if key == 'esc':
                self.tello.write_session()
                break
            if time() - start > 200:
                break


obj = Controller(4)
obj.command_loop()
