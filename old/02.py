"""
ZetCode Tkinter Tutorial v0.02

This script centers a small
window on the screen and creates
two quit buttons. When we press
a button, the program terminates.
There is also an input bar.
"""

from tkinter import Tk, Frame, RIGHT, BOTH, RAISED
from tkinter.ttk import Button, Style

class Example(Frame):
  
    def __init__(self, parent, bg):
        Frame.__init__(self, parent, background=bg)
        
        self.parent = parent
        self.initUI()

    def initUI(self):

        self.parent.title("Centered window with quit buttons")
        self.style = Style()
        self.style.theme_use("default")         #different themes show different buttons

        frame = Frame(self, relief=RAISED, bg="red", borderwidth=1) 
        frame.pack(fill=BOTH, expand=1)         #creates another red frame that pushes down to the bottom buttons

        self.pack(fill=BOTH, expand=1)
        self.centerWindow()
        
        quitButton = Button(self, text="Quit", command=self.parent.destroy)
        quitButton.place(x=90, y=50)            #places button at those coordinates
        noButton = Button(self, text="No")
        noButton.pack(side=RIGHT, padx=5, pady=5)#padx and pady puts some space between the widgets
        okButton = Button(self, text="OK")
        okButton.pack(side=RIGHT)               #packs button into frame

    def centerWindow(self):
      
        w = 300                                 #width and height of application window
        h = 150

        sw = self.parent.winfo_screenwidth()    #width and height of screen
        sh = self.parent.winfo_screenheight()
        
        x = (sw - w)/2
        y = (sh - h)/2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))


def main():
    root = Tk()
    ex = Example(root, bg="green")              #green base frame
    root.mainloop()

if __name__ == '__main__':
    main()
