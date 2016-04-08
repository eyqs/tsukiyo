"""
Polygon Visualizer v0.05

This script uses a point and
a list of vectors to draw
a p-gon on the screen.
"""

import tkinter as tk
import tkinter.ttk as ttk
import math

class Main(tk.Frame):
    
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        self.parent.title("Polygon Visualizer")
        self.pack(fill=tk.BOTH, expand=1)

        style = ttk.Style()
        style.configure("TFrame", background="#CCC")    #new TFrame background style
        #style.configure("TButton", padding=6, relief="flat", background="red")     #too hard to configure TButton style for white background
        
        self.rowconfigure(0, weight=1)                  #weight = relative weight for apportioning extra space among columns/rows
        self.columnconfigure(1, weight=1)
        
        cbtn = ttk.Button(self, text="Close", command=self.exit)
        cbtn.grid(row=1, column=0, pady=4, sticky=tk.W)
        self.inputText = tk.StringVar()                      #self.inputText is the variable in the entry field
        inputBox = ttk.Entry(self, textvariable=self.inputText)
        inputBox.bind('<Return>', self.takeInput)            #binds enter key to callback
        inputBox.grid(row=1, column=1, sticky=tk.W+tk.E)
        self.canvas = tk.Canvas(self, background="white")       #can create various shapes on the canvas
        self.canvas.grid(row=0, column=0, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)

        w = 800
        h = 600
        x = (self.parent.winfo_screenwidth() - w) // 2
        y = (self.parent.winfo_screenheight() - h) // 2
        self.parent.geometry('{}x{}+{}+{}'.format(w, h, x, y))
        self.makeMenus()
        
    def makeMenus(self):
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)                        #regular Menu widget configured to menubar of root window
        
        fileMenu = tk.Menu(menubar)
        fileMenu.add_command(label="Exit", command=self.exit, underline=1) #adds the "Exit" command
        fileMenu.add_command(label="Help", command=self.openHelp, underline=0)
        menubar.add_cascade(label="File", menu=fileMenu)        #adds the menu to the menubar
        
        
    def exit(self):
        self.parent.destroy()
        
    def openHelp(self):
        helpFrame = tk.Toplevel(self.parent, background="white")
        helpFrame.title("About this application...")
        helpMessage = tk.Message(helpFrame, text="Hi.")
        helpMessage.pack()
        helpButton = ttk.Button(helpFrame, text="Dismiss", command=helpFrame.destroy)
        helpButton.pack()
        w = 100
        h = 100
        x = self.parent.winfo_rootx() - w + self.parent.winfo_width() // 2
        y = self.parent.winfo_rooty() - h + self.parent.winfo_height() // 2
        helpFrame.geometry('{}x{}+{}+{}'.format(w, h, x, y))
        
    def takeInput(self, event):
        self.render(self.inputText.get())                    #tells translate() to translate the entry into homogeneous coordinates
        self.inputText.set('')                                  #clears the entry field
        
        
    def render(self, entry):
        p = int(entry)
        count = p
        r = 30
        s = 2*r*math.sin(math.pi/p)
        theta = 0
        points = [0,0]
        point = [0,0]
        vector = [s,0]
        while count > 0:
            point[0] += vector[0]
            point[1] += vector[1]
            points.append(point[0])
            points.append(point[1])
            theta += 2*math.pi/p
            vector[0] = s*math.cos(theta)
            vector[1] = s*math.sin(theta)
            count -= 1
        self.canvas.create_polygon(points, outline='red', fill='green', width=2)      #give list of coordinates to create polygon
        if entry == "quit" or entry == "exit":
            self.exit()
        else:
            pass
        
        
def main():
    root = tk.Tk()
    main = Main(root)
    root.mainloop()

if __name__ == '__main__':
    main()
