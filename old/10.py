"""
Polygon Visualizer v0.10

This script rotates
polygons in 3D.
"""

import tkinter as tk
import tkinter.ttk as ttk
import math

WIDTH = 350
HEIGHT = 450
RADIUS = 100
ROTANGLE = math.pi/12
BGCOLOUR = "#CCC"
TITLE = "Polygon Visualizer v0.10"

class Main(ttk.Frame):
    
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        self.parent.title(TITLE)
        self.pack(fill=tk.BOTH, expand=1)
        
        self.currPoints = []                                #variables to track polygon state
        self.xrotAngle = 0
        self.yrotAngle = 0
        self.zrotAngle = 0
        
        style = ttk.Style()
        style.configure("TFrame", background=BGCOLOUR)
        style.configure("TLabel", background=BGCOLOUR)
        
        self.rowconfigure(1, weight=1)                      #create 5-row, 6-column grid
        self.columnconfigure(0, minsize=100, weight=1)      #only the canvas row expands

        titleLabel = ttk.Label(self, text=TITLE)
        titleLabel.grid(row=0, column=0, columnspan=6)
        self.canvas = tk.Canvas(self, background="white")
        self.canvas.grid(row=1, column=0, columnspan=6, padx=10, pady=10, sticky=tk.N+tk.S+tk.E+tk.W)
        rotLabel = ttk.Label(self, text="Rotate")
        rotLabel.grid(row=2, column=1, columnspan=3)
        
        self.inputText = tk.StringVar()                     #self.inputText is the variable in the entry field
        inputBox = ttk.Entry(self, textvariable=self.inputText)
        inputBox.bind('<Return>', self.takeInput)           #binds enter key to callback
        inputBox.grid(row=3, column=0, padx=10, sticky=tk.E+tk.W)
        inputBox.focus()

        xrotButton = tk.Button(self, height=1, width=3, text="^", bg=BGCOLOUR, command=self.xRotate)
        xrotButton.grid(row=3, column=1)
        yrotButton = tk.Button(self, height=1, width=3, text="^", bg=BGCOLOUR, command=self.yRotate)
        yrotButton.grid(row=3, column=2)
        zrotButton = tk.Button(self, height=1, width=3, text="^", bg=BGCOLOUR, command=self.zRotate)
        zrotButton.grid(row=3, column=3)
        fourrotButton = tk.Button(self, height=1, width=3, text="^", bg=BGCOLOUR, state=tk.DISABLED)
        fourrotButton.grid(row=3, column=4)
        fiverotButton = tk.Button(self, height=1, width=3, text="^", bg=BGCOLOUR, state=tk.DISABLED)
        fiverotButton.grid(row=3, column=5)
        xrotLabel = ttk.Label(self, text="x")
        xrotLabel.grid(row=4, column=1)
        yrotLabel = ttk.Label(self, text="y")
        yrotLabel.grid(row=4, column=2)
        zrotLabel = ttk.Label(self, text="z")
        zrotLabel.grid(row=4, column=3)
        fourrotLabel = ttk.Label(self, text="4")
        fourrotLabel.grid(row=4, column=4)
        fiverotLabel = ttk.Label(self, text="5")
        fiverotLabel.grid(row=4, column=5)
        
        x = (self.parent.winfo_screenwidth() - WIDTH) // 2
        y = (self.parent.winfo_screenheight() - HEIGHT) // 2
        self.parent.geometry('{}x{}+{}+{}'.format(WIDTH, HEIGHT, x, y))
        self.parent.minsize(WIDTH, HEIGHT)
        self.makeMenus()
        
    def makeMenus(self):
        menuBar = tk.Menu(self.parent)
        self.parent.config(menu=menuBar)        
        fileMenu = tk.Menu(menuBar)                 #Tkinter calls functions by their names; calling a function gives its return value
        fileMenu.add_command(label="About", command=lambda: self.popUp('About'), underline=0)
        fileMenu.add_command(label="Help", command=lambda: self.popUp('Help'), underline=0)
        fileMenu.add_command(label="Exit", command=self.onExit, underline=1)
        menuBar.add_cascade(label="File", menu=fileMenu)

        
    def onExit(self):
        self.parent.destroy()

    def popUp(self, popUpType):
        if popUpType == 'About':
            titleText = "About this application..."
            messageText = TITLE + "\nThis script rotates polygons by pressing the buttons under Rotate."
            buttonText = "OK"
            frameWidth = 400
            frameHeight = 150
        elif popUpType == 'Help':
            titleText = "Help"
            messageText = "Click the buttons to rotate the polygon about each axis."
            buttonText = "Dismiss"
            frameWidth = 400
            frameHeight = 150
            
        popUpFrame = tk.Toplevel(self.parent, background="white")
        popUpFrame.title(popUpType)
        popUpMessage = tk.Message(popUpFrame, text=messageText, width=400, background="white")
        popUpMessage.pack()
        popUpButton = ttk.Button(popUpFrame, text=buttonText, command=popUpFrame.destroy)
        popUpButton.pack()
        x = self.parent.winfo_rootx() + (self.parent.winfo_width() - frameWidth) // 2
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() - frameHeight) // 2
        popUpFrame.geometry('{}x{}+{}+{}'.format(frameWidth, frameHeight, x, y))
        popUpButton.focus()
        
    def takeInput(self, event):
        self.currPoints = self.translate(self.inputText.get())
        self.render(self.currPoints)
        self.inputText.set('')                  #clears the entry field
                
    def translate(self, entry):                 #sends off input to turn into list of points
        if entry == '' or entry == "clear":
            self.canvas.delete(tk.ALL)
            return [(0,0)]
        elif entry == "quit" or entry == "exit":
            self.onExit()
        elif entry[0] == "{":
            return self.schlafli(entry[1:-1])  #strips brackets off of Schlafli

    def schlafli(self, entry):
        num = entry.split('/')
        p = int(num[0])
        d = 1
        if len(num) > 1:
            d = int(num[1])
        r = RADIUS
        return self.circumcircle(p,d,r)
        
    def circumcircle(self, p, d, r):
        rs = [r]*p
        thetas = [(2*k*d*math.pi/p)%(2*math.pi) for k in range(p)]
        return self.polarToCartesian(p, rs, thetas)

    def polarToCartesian(self, number, rs, thetas):
        points = []
        count = 0
        while count < number:                       #(r,t)->(r cos t, r sin t)
            points.append((rs[count]*math.cos(thetas[count]), rs[count]*math.sin(thetas[count])))
            count += 1
        return points

        
    def center(self, points):
        w = self.canvas.winfo_width()//2
        h = self.canvas.winfo_height()//2
        return [(point[0]+w, point[1]+h) for point in points]

    def xRotate(self):
        self.xrotAngle += ROTANGLE
        c = math.cos(self.xrotAngle)                        #2D rotation matrix + listcomp for points
        s = math.sin(self.xrotAngle)
        self.render([(point[0]*c-point[1]*s, point[0]*s+point[1]*c) for point in self.currPoints])

    def yRotate(self):
        self.yrotAngle += ROTANGLE
        c = math.cos(self.yrotAngle)                        #(x, y) -> (x, y cos t), where t = angle from z=0
        self.render([(point[0],point[1]*c) for point in self.currPoints])

    def zRotate(self):
        self.zrotAngle += ROTANGLE
        c = math.cos(self.zrotAngle)
        self.render([(point[0]*c,point[1]) for point in self.currPoints])
        
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
        self.canvas.delete(tk.ALL)
        self.canvas.create_polygon(self.center(points), outline='#000', fill='#EEE', width=2)      #give list of coordinates to create polygon
        
        
        
def main():
    root = tk.Tk()
    main = Main(root)
    root.mainloop()

if __name__ == '__main__':
    main()
