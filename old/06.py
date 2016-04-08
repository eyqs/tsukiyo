"""
Polygon Visualizer v0.06

This script separates the render
function into subfunctions and
calculates polygon vertices
by looking at their circumcircle.
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
        menuBar = tk.Menu(self.parent)
        self.parent.config(menu=menuBar)                        #regular Menu widget configured to menubar of root window
        
        fileMenu = tk.Menu(menuBar)
        fileMenu.add_command(label="Exit", command=self.exit, underline=1) #adds the "Exit" command
        fileMenu.add_command(label="Help", command=self.openHelp, underline=0)
        menuBar.add_cascade(label="File", menu=fileMenu)        #adds the menu to the menubar
        
        
    def exit(self):
        self.parent.destroy()
        
    def openHelp(self):
        helpFrame = tk.Toplevel(self.parent, background="white")    #opens a popup message
        helpFrame.title("About this application...")
        helpMessage = tk.Message(helpFrame, text="Hi.")
        helpMessage.pack()
        helpButton = ttk.Button(helpFrame, text="Dismiss", command=helpFrame.destroy)   #closes helpFrame
        helpButton.pack()
        w = 100
        h = 100
        x = self.parent.winfo_rootx() - w + self.parent.winfo_width() // 2      #rootx() is position of main window, places box in middle
        y = self.parent.winfo_rooty() - h + self.parent.winfo_height() // 2
        helpFrame.geometry('{}x{}+{}+{}'.format(w, h, x, y))

        
    def takeInput(self, event):
        self.translate(self.inputText.get())    #tells translate() to translate the entry into homogeneous coordinates
        self.inputText.set('')                  #clears the entry field
        
        
    def translate(self, entry):
        if entry == "quit" or entry == "exit":
            self.exit()
        elif entry[0] == "{":
            self.schlafli(entry[1:-1])          #strips brackets off of Schlafli
        else:
            pass
        
    def schlafli(self, entry):
        num = entry.split('/')                  #splits 2D Schlafli symbols into order and density {p/d}
        p = int(num[0])
        d = 0
        if len(num) == 2:
            d = int(num[1])
        r = 30                                  #radius of circumcircle
        
        #self.circumcircle(p,d,r)               #circumcircle calculation
        
        #vector list representation, ugly and ~1.2x slower than circumcircle
        s = 2*r*math.sin(math.pi/p)             #side length
        vectors = [(0,0)]
        theta = 0                               #starting angle
        count = p
        while count > 0:
            vector = (s*math.cos(theta), s*math.sin(theta))     #side vectors
            vectors.append(vector)
            theta += 2*math.pi/p
            count -= 1
        self.vectorList(p, [0,0], vectors)
        
        
    def circumcircle(self, p, d, r):
        points = [0,0]
        count = 0
        while count < p-1:
            theta = 2*count*math.pi/p
            points.append(r*math.cos(theta))
            points.append(r*math.sin(theta))
            count += 1
        self.render(points)
        
    def vectorList(self, number, point, vectors):
        count = 0
        points = point
        while count < number:                   #goes through all vectors in list, and applies them successively to each point, to get list of points
            point[0] += vectors[count][0]
            point[1] += vectors[count][1]
            points.append(point[0])
            points.append(point[1])
            count += 1
        self.render(points)
        
    def render(self, points):
        self.canvas.create_polygon(points, outline='red', fill='green', width=2)      #give list of coordinates to create polygon
        
        
def main():
    root = tk.Tk()
    main = Main(root)
    root.mainloop()

if __name__ == '__main__':
    main()
