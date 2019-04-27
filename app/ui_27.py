import os
import threading

import Tkinter as tk
import tkMessageBox
import tkFileDialog
import tkSimpleDialog

import cv2

from tello import Tello

# dimensions of the ui window
win_width = 1000
win_height = 650

v_split = 0.25

f1_att = {'x': 0, 'y': 0, 'width': v_split * win_width, 'height': win_height}

start_offset = 20

# functionality buttons dimensions
btn_width = 95
btn_height = 40
btn_interv = 15
btn_x = v_split * win_width / 2 - btn_width / 2

dist_bar_y = 0.15 * win_height
angle_bar_y = 0.25 * win_height

# y coordinate of the first functionality button
first_btn_y = 0.38 * win_height

move_map = {
    'w': 'forward',
    's': 'back',
    'a': 'left',
    'd': 'right',
    'Up': 'up',
    'Down': 'down',
    'Left': 'ccw',
    'Right': 'cw'
}


class ControlUI:
    """Creates the UI to control the tello."""

    def __init__(self):
        """Creates tello object and the control UI."""

        self.frame = None
        self.stream_flag = False

        self.root = tk.Tk()
        self.root.title('Tello drone')
        self.root.geometry("{0}x{1}".format(win_width, win_height))
        self.root.wm_protocol("WM_DELETE_WINDOW", self.on_quit)

        self.video_thread = threading.Thread(target=self.video_loop)

        frame1 = tk.Frame(self.root)
        frame1.place(**f1_att)

        # ------------------------ menu -----------------------------------
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        filemenu = tk.Menu(menu)
        menu.add_cascade(label="File ", menu=filemenu)
        filemenu.add_command(label="Load Session", command=self.load_session)
        filemenu.add_command(label="Save Session", command=self.save_session)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.on_quit)

        helpmenu = tk.Menu(menu)
        menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About...", command=show_info)

        # ---------------------- frame 1 -----------------------------------
        status_text_label = tk.Label(
            frame1, text='Status:', font='Helvetica 11 bold')
        status_text_label.place(x=start_offset, y=20)
        self.status_label = tk.Label(
            frame1, text='Not connected', font='Helvetica 11')
        self.status_label.place(x=v_split * win_width / 2 - 20, y=21)

        # sliders
        dist_label = tk.Label(
            frame1, text='Distance (20-500 cm)', font='Helvetica 10 bold')
        dist_label.place(x=start_offset, y=dist_bar_y - 20)

        self.dist_bar = tk.Scale(
            frame1, from_=20, to=500, orient=tk.HORIZONTAL)
        self.dist_bar.place(x=start_offset, y=dist_bar_y, width=200)

        angle_text_label = tk.Label(
            frame1, text='Angle (1-360)', font='Helvetica 10 bold')
        angle_text_label.place(x=start_offset, y=angle_bar_y - 20)

        self.angle_bar = tk.Scale(
            frame1, from_=1, to_=360, orient=tk.HORIZONTAL)
        self.angle_bar.place(x=start_offset, y=angle_bar_y, width=200)

        # buttons
        connect = tk.Button(frame1, text='Connect', command=self.initialize)
        connect.place(
            x=btn_x, y=first_btn_y, width=btn_width, height=btn_height)

        takeoff = tk.Button(
            frame1, text='Takeoff', command=lambda: self.action('takeoff'))
        takeoff.place(
            x=btn_x,
            y=first_btn_y + btn_height + btn_interv,
            width=btn_width,
            height=btn_height)

        reverse = tk.Button(frame1, text='Call back', command=self.reverse)
        reverse.place(
            x=btn_x,
            y=first_btn_y + 2 * btn_height + 2 * btn_interv,
            width=btn_width,
            height=btn_height)

        land = tk.Button(
            frame1, text='Land', command=lambda: self.action('land'))
        land.place(
            x=btn_x,
            y=first_btn_y + 3 * btn_height + 3 * btn_interv,
            width=btn_width,
            height=btn_height)

        streamon = tk.Button(
            frame1, text='Stream On', command=self.start_stream)
        streamon.place(
            x=btn_x,
            y=first_btn_y + 4 * btn_height + 4 * btn_interv,
            width=btn_width,
            height=btn_height)

        streamoff = tk.Button(
            frame1, text='Stream Off', command=self.stop_stream)
        streamoff.place(
            x=btn_x,
            y=first_btn_y + 5 * btn_height + 5 * btn_interv,
            width=btn_width,
            height=btn_height)

        stop = tk.Button(
            frame1,
            text='STOP',
            fg='red',
            command=lambda: self.action('emergency'))
        stop.place(
            x=btn_x,
            y=first_btn_y + 6 * btn_height + 6 * btn_interv,
            width=btn_width,
            height=btn_height)

        # -------------------------- key bindings ----------------------------
        self.root.bind('<KeyPress-w>', self.move)
        self.root.bind('<KeyPress-s>', self.move)
        self.root.bind('<KeyPress-a>', self.move)
        self.root.bind('<KeyPress-d>', self.move)
        self.root.bind('<KeyPress-Up>', self.move)
        self.root.bind('<KeyPress-Down>', self.move)
        self.root.bind('<KeyPress-Left>', self.move)
        self.root.bind('<KeyPress-Right>', self.move)

        self.root.mainloop()

    def initialize(self):
        """Initializes tello and updates displayed status."""
        self.tello = Tello()
        flag = self.tello.initialize()
        if not flag:
            # if initialization fails
            del self.tello
        else:
            self.update_status()

    def save_session(self):
        """Waits for user to input the session id and saves it in a txt file."""
        try:
            # check if tello is connected
            self.tello
        except AttributeError:
            self._show_warning()
            return
        answer = tkSimpleDialog.askstring(
            "Input", "Enter session's name", parent=self.root)
        if answer is not None:
            # if user did not press the cancel button
            session_id = answer
            self.tello.write_session(session_id)

    def reverse(self):
        try:
            self.tello.fetch()
        except AttributeError:
            # tello not initialized
            self._show_warning()

    def load_session(self):
        """User chooses a session file and tello reruns its commands."""
        try:
            self.tello
            # available file types
            my_filetypes = [('text files', '.txt')]
            answer = tkFileDialog.askopenfilename(
                parent=self.root,
                initialdir=os.getcwd(),
                title="Please select a file:",
                filetypes=my_filetypes)

            if answer:
                # a txt file is chosen
                self.tello.replay_session(answer)
        except AttributeError:
            # tello not connected
            self._show_warning()

    def action(self, name):
        """Sends takeoff-land-emergency command to tello."""
        try:
            self.tello.send_command(name)
            self.update_status()
        except AttributeError:
            # tello not initialized
            self._show_warning()

    def move(self, event):
        """Maps key pressed to a valid tello command, gets the distance and
        sends it. If tello is not initialzed, ignores the key press events."""
        key = event.keysym
        direction = move_map[key]
        if direction in ['cw', 'ccw']:
            # if command is rotating, the value comes from the angle bar
            value = self.angle_bar.get()
        else:
            # if command is moving, value comes from the distance bar
            value = self.dist_bar.get()
        cmd = '{} {}'.format(direction, value)

        try:
            self.tello.send_command(cmd)
        except AttributeError:
            # tello not initialized, ignore the event
            pass

    def update_status(self):
        """Gets the tello status and refreshes the status label."""
        new_status = self.tello.get_status()
        self.status_label['text'] = new_status

    def start_stream(self):
        """Sends streamon command and starts the video thread."""
        try:
            self.tello.send_command('streamon')
            # set stream flag to start the video loop
            self.stream_flag = True
            self.video_thread.start()
        except AttributeError:
            self._show_warning()

    def stop_stream(self):
        """Sends streamoff command and sets stream_flag False to stop the
        video looping thread."""
        try:
            self.tello.send_command('streamoff')
            self.stream_flag = False
        except AttributeError:
            self._show_warning()

    def video_loop(self):
        """Reads the tello frame, converts it to PIL image and updates
        the GUI image."""
        # while self.stream_flag:
        while self.stream_flag:
            frame = self.tello.frame
            # while stream flag is True
            if frame is None:
                # skip initial none frames
                continue

            cv2.imshow('ds', frame)
            cv2.waitKey(10)

    def _show_warning(self):
        """Displays a message box with a warning text."""
        tkMessageBox.showwarning(
            title='Action denied', message='You must be connected to tello')

    def on_quit(self):
        self.stream_flag = False
        self.root.destroy()
        cv2.destroyAllWindows()
        exit()


def show_info():
    print('Welcome to drone help')
    return


ob = ControlUI()
