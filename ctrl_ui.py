import tkinter as tk

from tello import Tello

# dimensions of the ui window
win_width = 1000
win_height = 700

# functionality buttons dimensions
btn_width = 75
btn_height = 35

# attributes of functionality frame
func_f = {'x': 0, 'y': 0, 'width': btn_width + 10, 'height': win_height}

# attributes of moving frame
move_f = {
    'x': btn_width + 10,
    'y': 400,
    'width': win_width - btn_height + 10,
    'height': 300
}

# y coordinate of the first functionality button
first_btn_y = 150

cmd_map = {
    'tkoff': 'takeoff',
    'land': 'land',
    'up': 'up 20',
    'down': 'down 20',
    'w': 'forward 20',
    's': 'back 20',
    'a': 'left 20',
    'd': 'right 20',
    'right': 'cw 20',
    'left': 'ccw 20'
}


class ControlUI:
    """Creates the UI to control the tello."""

    def __init__(self, session_id):
        """Creates tello object and the control UI."""
        self.tello = Tello(session_id)

        self.root = tk.Tk()
        self.root.title('Tello drone')
        self.root.geometry("{}x{}".format(win_width, win_height))

        w = tk.Label(self.root, text='Control your tello')
        w.place(x=win_width / 2 - 60, y=10, width=120, height=50)

        # functions frame

        func_frame = tk.Frame(self.root)
        func_frame.place(**func_f)

        connect = tk.Button(
            func_frame, text='Connect', command=self.initialize)
        connect.place(x=10, y=first_btn_y, width=btn_width, height=btn_height)

        takeoff = tk.Button(
            func_frame, text='Takeoff', command=lambda: self.action('tkoff'))
        takeoff.place(
            x=10, y=first_btn_y + 50, width=btn_width, height=btn_height)

        land = tk.Button(
            func_frame, text='Land', command=lambda: self.action('land'))
        land.place(
            x=10, y=first_btn_y + 100, width=btn_width, height=btn_height)

        reverse = tk.Button(func_frame, text='Call back', command=self.reverse)
        reverse.place(
            x=10, y=first_btn_y + 150, width=btn_width, height=btn_height)

        quit_btn = tk.Button(func_frame, text='Quit', fg='red', command=quit)
        quit_btn.place(
            x=10, y=win_height - 55, width=btn_width, height=btn_height)

        # moves frame

        move_frame = tk.Frame(self.root, bd=1)
        move_frame.place(**move_f)

        photo_for = tk.PhotoImage(file="assets/up-arrow.png")
        photo_back = tk.PhotoImage(file="assets/down-arrow.png")
        photo_left = tk.PhotoImage(file="assets/left-arrow.png")
        photo_right = tk.PhotoImage(file="assets/right-arrow.png")
        photo_up = tk.PhotoImage(file="assets/double_up.png")
        photo_down = tk.PhotoImage(file="assets/double_down.png")

        for_im = tk.Button(
            move_frame, image=photo_for, command=lambda: self.action('w'))
        for_im.place(x=150, y=20, width=70, height=70)

        back = tk.Button(
            move_frame, image=photo_back, command=lambda: self.action('s'))
        back.place(x=150, y=160, width=70, height=70)

        left = tk.Button(
            move_frame, image=photo_left, command=lambda: self.action('a'))
        left.place(x=70, y=95, width=70, height=70)

        right = tk.Button(
            move_frame, image=photo_right, command=lambda: self.action('d'))
        right.place(x=230, y=95, width=70, height=70)

        up = tk.Button(
            move_frame, image=photo_up, command=lambda: self.action('up'))
        up.place(x=600, y=20, width=70, height=70)

        down = tk.Button(
            move_frame, image=photo_down, command=lambda: self.action('down'))
        down.place(x=600, y=160, width=70, height=70)

        self.root.mainloop()

    def initialize(self):
        self.tello.initialize()

    def reverse(self):
        self.tello.fetch()

    def action(self, name):
        try:
            command = cmd_map[name]
            self.tello.send_command(command)
        except KeyError:
            print('[ERROR]: Cannot handle this command key.')


ob = ControlUI(1)
