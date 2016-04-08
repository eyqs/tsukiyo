"""
ZetCode Tkinter Tutorial v0.04

In this script, we draw basic 
shapes on the canvas.
"""

from tkinter import Tk, Text, Canvas, BOTH, N, S, E, W, Menu, StringVar
from tkinter.ttk import Frame, Button, Entry, Style
from random import randint      #to randomly generate shape positions

class Example(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent        
        self.initUI()
        
    def initUI(self):
      
        self.parent.title("Shapes")
        self.pack(fill=BOTH, expand=1)

        style = Style()
        style.configure("TFrame", background="#CCC")    #new TFrame background style
        #style.configure("TButton", padding=6, relief="flat", background="red")     #too hard to configure TButton style for white background

        self.rowconfigure(0, weight=1)                  #weight = relative weight for apportioning extra space among columns/rows
        self.columnconfigure(1, weight=1)

        cbtn = Button(self, text="Close", command=self.onExit)
        cbtn.grid(row=1, column=0, pady=4, sticky=W)
        self.content = StringVar()                      #self.content is the variable in the entry field
        textBox = Entry(self, textvariable=self.content)
        textBox.bind('<Return>', self.callback)         #binds enter key to callback
        textBox.grid(row=1, column=1, sticky=W+E)
        self.canvas = Canvas(self, background="white")       #can create various shapes on the canvas
        self.canvas.grid(row=0, column=0, columnspan=2, sticky=N+S+E+W)
        
        self.centerWindow()
        self.makeMenus()

    def callback(self, event):
        self.render(self.content.get())                      #tells render() to draw the entry
        self.content.set('')                            #clears the entry field

    def render(self, entry):
        xnum = randint(0, 600)
        ynum = randint(0, 600)
        if entry == "o":
            self.canvas.create_oval(xnum, ynum, xnum+70, ynum+70, outline="red", fill="green", width=2)    #bounding box of oval
            self.canvas.create_oval(xnum+200, ynum+200, xnum+300, ynum+270, outline="#f11", fill="#1f1", width=2)
        elif entry == "r":
            self.canvas.create_rectangle(xnum, ynum, xnum+60, ynum+50, outline="#f11", fill="#1f1", width=2)
        elif entry == "a":
            self.canvas.create_line(xnum, ynum, xnum+60, ynum+100, fill="#1f1", width=2)
        elif entry == "p":
            points = [xnum, ynum, xnum+50, ynum+20, xnum+90, ynum+80, xnum+60, ynum+100, xnum, ynum+50, xnum-50, ynum+100]
            self.canvas.create_polygon(points, outline='red', fill='green', width=2)                        #give list of coordinates to create polygon
        elif entry == "quit" or entry == "exit":
            self.onExit()
        else:
            pass
        
    def makeMenus(self):
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
    ex = Example(root)
    root.mainloop()  

if __name__ == '__main__':
    main()
