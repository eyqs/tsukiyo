"""
Polygon Visualizer v0.09

This script rotates
polygons by pressing
the rotate button.
"""

import tkinter as tk
import tkinter.ttk as ttk
import math

WIDTH = 600
HEIGHT = 800
RADIUS = 300
ROTANGLE = math.pi/12

class Main(tk.Frame):
    
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        self.parent.title("Polygon Visualizer")
        self.pack(fill=tk.BOTH, expand=1)
        global currPoints
        
        style = ttk.Style()
        style.configure("TFrame", background="#CCC")    #new TFrame background style
        #style.configure("TButton", padding=6, relief="flat", background="red")     #too hard to configure TButton style for white background
        
        self.rowconfigure(0, weight=1)                  #weight = relative weight for apportioning extra space among columns/rows
        self.columnconfigure(1, weight=1)
        
        rotButton = ttk.Button(self, text="Rotate", command=self.rotate2D)
        rotButton.grid(row=1, column=0, pady=4, sticky=tk.W)
        self.inputText = tk.StringVar()                      #self.inputText is the variable in the entry field
        inputBox = ttk.Entry(self, textvariable=self.inputText)
        inputBox.bind('<Return>', self.takeInput)            #binds enter key to callback
        inputBox.grid(row=1, column=1, sticky=tk.W+tk.E)
        inputBox.focus()
        self.canvas = tk.Canvas(self, background="white")       #can create various shapes on the canvas
        self.canvas.grid(row=0, column=0, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)

        x = (self.parent.winfo_screenwidth() - WIDTH) // 2
        y = (self.parent.winfo_screenheight() - HEIGHT) // 2
        self.parent.geometry('{}x{}+{}+{}'.format(WIDTH, HEIGHT, x, y))
        self.makeMenus()
        
    def makeMenus(self):
        menuBar = tk.Menu(self.parent)
        self.parent.config(menu=menuBar)                        #regular Menu widget configured to menubar of root window
        
        fileMenu = tk.Menu(menuBar)
        fileMenu.add_command(label="Exit", command=self.onExit, underline=1) #adds the "Exit" command
        fileMenu.add_command(label="Help", command=self.openHelp, underline=0)
        menuBar.add_cascade(label="File", menu=fileMenu)        #adds the menu to the menubar
        
        
    def onExit(self):
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
        self.render(self.translate(self.inputText.get()))
        self.inputText.set('')                  #clears the entry field
                
    def translate(self, entry):                 #sends off input to turn into list of points
        if entry == "quit" or entry == "exit":
            self.onExit()
        else:
            try:
                if entry[0] == "{":
                    return self.schlafli(entry[1:-1])  #strips brackets off of Schlafli
            except:
                pass

    def rotate2D(self):
        c = math.cos(ROTANGLE)                      #2D rotation matrix + listcomp for points
        s = math.sin(ROTANGLE)
        self.render([(point[0]*c-point[1]*s, point[0]*s+point[1]*c) for point in self.currPoints])

    def schlafli(self, entry):
        num = entry.split('/')                  #splits 2D Schlafli symbols into order and density {p/d}
        p = int(num[0])
        r = RADIUS
        d = 1                                   #{p/1} = {p}
        if len(num) == 2:
            d = int(num[1])
        return (self.circumcircle(p,r)*d)[::d]
        
    def circumcircle(self, p, r):
        rs = [r]*p
        thetas = [2*k*math.pi/p for k in range(p)]
        return self.polarToCartesian(p, rs, thetas)

    def polarToCartesian(self, number, rs, thetas): #also correctly centres points so that (0,0) is at centre of screen
        points = []
        count = 0
        while count < number:                       #(r,t)->(rcost, rsint)
            points.append((rs[count]*math.cos(thetas[count]), rs[count]*math.sin(thetas[count])))
            count += 1
        return points
        
    def center(self, points):
        w = self.parent.winfo_width()//2            #self.parent.winfo_width()//2 is centre
        h = self.parent.winfo_height()//2
        return [(point[0]+w, point[1]+h) for point in points]
        
    def vectorList(self, number, point, vectors):
        count = 0
        points = point
        while count < number:                   #goes through all vectors in list, and applies them successively to each point, to get list of points
            point[0] += vectors[count][0]
            point[1] += vectors[count][1]
            points.append(point[0])
            points.append(point[1])
            count += 1
        return points
        
        
    def render(self, points):
        self.currPoints = points
        self.canvas.delete("all")
        self.canvas.create_polygon(self.center(points), outline='red', fill='green', width=2)      #give list of coordinates to create polygon
        
        
        
def main():
    root = tk.Tk()
    main = Main(root)
    root.mainloop()

if __name__ == '__main__':
    main()
