# A simple tool to grab screen coordinates
# use it to find the values for constants.py

from tkinter import *
import pyautogui
    
# window
root = Tk()
root.title('mouse position')
Label(root, text="Current Mouse Position", font=("Helvetica", 16), padx = 20, pady = 5).pack()
label = Label(root, font=("Helvetica", 20), padx = 20, pady = 5)
label.pack()

# ensure that it is on top of all other windows
root.wm_attributes("-topmost", 1)

# get/update mouse position
def update():
    x, y = pyautogui.position()
    label["text"] = f"{x}, {y}"
    root.after(100, update)
update()

# run
root.mainloop()