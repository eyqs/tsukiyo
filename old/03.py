"""
ZetCode Tkinter Tutorial v0.03

In this script, we use the grid
manager to create a more complicated
layout. We will also create a menu.
"""

from tkinter import Tk, Text, BOTH, W, N, E, S, Menu
from tkinter.ttk import Frame, Button, Label, Style

class Example(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()
        
    def initUI(self):
      
        self.parent.title("Windows")
        self.centerWindow()
        self.pack(fill=BOTH, expand=1)

        s = Style()
        s.configure("TFrame", background="#CCC")  #new TFrame background style
        #s.configure("TButton", padding=6, relief="flat", background="red")     #too hard to configure TButton style for white background

        self.columnconfigure(1, weight=1)                       #define spaces among widgets in the grid
        self.columnconfigure(3, pad=7)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(5, pad=7)
        
        lbl = Label(self, text="Windows")                       #first column/row assumed
        lbl.grid(sticky=W, pady=4, padx=5)
        
        area = Text(self)       #starts from second row, first column; spans 2 columns, 4 rows; grows in all directions
        area.grid(row=1, column=0, columnspan=2, rowspan=4, padx=5, sticky=E+W+S+N)
        abtn = Button(self, text="Activate")       #other buttons, with new button styles
        abtn.grid(row=1, column=3)

        cbtn = Button(self, text="Close", command=self.onExit)
        cbtn.grid(row=2, column=3, pady=4)
        
        hbtn = Button(self, text="Help")
        hbtn.grid(row=5, column=0, padx=5)

        obtn = Button(self, text="OK")
        obtn.grid(row=5, column=3)

        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)                        #regular Menu widget configured to menubar of root window
        
        fileMenu = Menu(menubar)                                #Menu is a popup window with commands
        submenu = Menu(fileMenu)
        submenu.add_command(label="New feed")
        submenu.add_command(label="Bookmarks")
        submenu.add_command(label="Mail")
        
        fileMenu.add_cascade(label='Import', menu=submenu, underline=0) #underline defines character position of keyboard shortcut
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=self.onExit) #adds the "Exit" command
        menubar.add_cascade(label="File", menu=fileMenu)        #adds the menu to the menubar

    def onExit(self):
        self.parent.destroy()

    def centerWindow(self):
      
        w = 600                                 #width and height of application window
        h = 800
        sw = self.parent.winfo_screenwidth()    #width and height of screen
        sh = self.parent.winfo_screenheight()
        x = (sw - w)/2
        y = (sh - h)/2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y)) 


def main():
    root = Tk()
    app = Example(root)
    root.mainloop()  

if __name__ == '__main__':
    main()
