from tkinter import Tk, font, Label

root = Tk()
root.geometry('1820x980')
root.title("Available fonts")
font_families = font.families()

col = 0
row = 0
for ind, ff in enumerate(font_families):
    if ind % 30 == 0:
        col += 1
        row = 0
    t = (ff, 12)
    lab = Label(root, text=ff, font=t)
    lab.grid(row=row, column=col)
    row += 1

root.mainloop()
