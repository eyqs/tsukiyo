"""
ZetCode Tkinter Tutorial v0.01

This script shows a simple window
on the screen.
"""

from tkinter import Tk, Frame, BOTH

class Example(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")   
        self.parent = parent            #parent = Tk root window
        self.initUI()
    
    def initUI(self):
        self.parent.title("Simple")     #title of frame
        self.pack(fill=BOTH, expand=1)  #fill = BOTH expands in both directions
        

def main():
  
    root = Tk()
    root.geometry("250x150+300+300")
    app = Example(root)                 #application class
    root.mainloop()  


if __name__ == '__main__':
    main()
