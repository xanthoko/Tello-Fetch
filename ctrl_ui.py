import os

import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog

from tello import Tello

# dimensions of the ui window
win_width = 1000
win_height = 700

# functionality buttons dimensions
btn_width = 95
btn_height = 35

# attributes of functionality frame
func_f = {'x': 0, 'y': 150, 'width': btn_width + 10, 'height': win_height}

# attributes of moving frame
move_f = {
    'x': btn_width + 10,
    'y': 400,
    'width': win_width - btn_height + 10,
    'height': 300
}

# y coordinate of the first functionality button
first_btn_y = 0

cmd_map = {
    'tkoff': 'takeoff',
    'land': 'land',
    'up': 'up 20',
    'down': 'down 20',
    'w': 'forward 20',
    's': 'back 20',
    'a': 'left 20',
    'd': 'right 20',
    'cw': 'cw 20',
    'ccw': 'ccw 20'
}


class ControlUI:
    """Creates the UI to control the tello."""

    def __init__(self):
        """Creates tello object and the control UI."""
        self.root = tk.Tk()
        self.root.title('Tello drone')
        self.root.geometry("{}x{}".format(win_width, win_height))

        w = tk.Label(self.root, text='Control your tello')
        w.place(x=win_width / 2 - 60, y=10, width=120, height=50)

        # functions frame

        func_frame = tk.Frame(self.root)
        func_frame.place(**func_f)

        self.status_label = tk.Label(self.root, text='Status: Not connected')
        self.status_label.place(x=10, y=50)

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

        save = tk.Button(func_frame, text='Save session')
        save.place(
            x=10, y=first_btn_y + 200, width=btn_width, height=btn_height)
        save.bind('<Button-1>', self.save_session)

        replay = tk.Button(
            func_frame, text='Replay session', command=self.replay)
        replay.place(
            x=10, y=first_btn_y + 250, width=btn_width, height=btn_height)

        quit_btn = tk.Button(func_frame, text='Quit', fg='red', command=quit)
        quit_btn.place(
            x=10, y=win_height - 205, width=btn_width, height=btn_height)

        # moves frame

        move_frame = tk.Frame(self.root, bd=1)
        move_frame.place(**move_f)

        photo_for = tk.PhotoImage(file="assets/up-arrow.png")
        photo_back = tk.PhotoImage(file="assets/down-arrow.png")
        photo_left = tk.PhotoImage(file="assets/left-arrow.png")
        photo_right = tk.PhotoImage(file="assets/right-arrow.png")
        photo_up = tk.PhotoImage(file="assets/double_up.png")
        photo_down = tk.PhotoImage(file="assets/double_down.png")
        photo_cw = tk.PhotoImage(file="assets/cw.png")
        photo_ccw = tk.PhotoImage(file="assets/ccw.png")

        for_im = tk.Button(
            move_frame, image=photo_for, command=lambda: self.action('w'))
        for_im.place(x=150, y=20, width=60, height=60)

        back = tk.Button(
            move_frame, image=photo_back, command=lambda: self.action('s'))
        back.place(x=150, y=160, width=60, height=60)

        left = tk.Button(
            move_frame, image=photo_left, command=lambda: self.action('a'))
        left.place(x=70, y=95, width=60, height=60)

        right = tk.Button(
            move_frame, image=photo_right, command=lambda: self.action('d'))
        right.place(x=230, y=95, width=60, height=60)

        up = tk.Button(
            move_frame, image=photo_up, command=lambda: self.action('up'))
        up.place(x=600, y=20, width=60, height=60)

        down = tk.Button(
            move_frame, image=photo_down, command=lambda: self.action('down'))
        down.place(x=600, y=160, width=60, height=60)

        cw = tk.Button(
            move_frame, image=photo_cw, command=lambda: self.action('cw'))
        cw.place(x=520, y=95, width=60, height=60)

        ccw = tk.Button(
            move_frame, image=photo_ccw, command=lambda: self.action('ccw'))
        ccw.place(x=680, y=95, width=60, height=60)

        self.root.mainloop()

    def initialize(self):
        """Initializes tello and updates displayed status."""
        self.tello = Tello()
        self.tello.initialize()
        self.update_status()

    def save_session(self, event):
        """Waits for user to input the session id and saves it in a txt file."""
        answer = simpledialog.askstring(
            "Input", "Enter session's name", parent=self.root)
        if answer is not None:
            # if user did not press the cancel button
            session_id = answer
            try:
                self.tello.write_session(session_id)
            except AttributeError:
                self._show_warning()

    def reverse(self):
        try:
            self.tello.fetch()
        except AttributeError:
            # tello not initialized
            self._show_warning()

    # def save_session(self):
    #     try:
    #         self.tello.write_session()
    #     except AttributeError:
    #         # tello not initialized
    #         self._show_warning()

    def replay(self):
        """User chooses a session file and tello reruns its commands."""
        try:
            # available file types
            my_filetypes = [('text files', '.txt')]
            answer = filedialog.askopenfilename(
                parent=self.root,
                initialdir=os.getcwd(),
                title="Please select a file:",
                filetypes=my_filetypes)

            if answer:
                # a txt file is chosen
                self.tello.replay_session(answer)
        except AttributeError:
            self._show_warning()

    def action(self, name):
        """Map the button identifier to a valid tello command"""
        try:
            # map to a tello-valid command
            command = cmd_map[name]
            self.tello.send_command(command)
            self.update_status()
        except KeyError:
            # name not in cmd_map
            print('[ERROR]: Cannot handle this command key.')
        except AttributeError:
            # tello not initialized
            self._show_warning()

    def update_status(self):
        """Gets the tello status and refreshes the status label."""
        new_status = self.tello.get_status()
        self.status_label['text'] = new_status

    def _show_warning(self):
        """Displays a message box with a warning text."""
        messagebox.showwarning(
            title='Action denied', message='You must be connected to tello')


ob = ControlUI()
