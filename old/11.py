"""
Polygon Visualizer v0.11

The polygon vertices are now
stored in a Polygon class.
The canvas methods are now
stored in a Canvas class.
"""

import tkinter as tk
import tkinter.ttk as ttk
import math

# constants
TITLE = "Polygon Visualizer v0.11"
DESCRIPTION = "\nThis script rotates polygons when you press the buttons."
WIDTH = 350
HEIGHT = 400
RADIUS = 100
ROTANGLE = math.pi/12
BGCOLOUR = "#CCC"
DELAY = 28    # 28 ms per pi/12 rotation = 3 rotations every 2 seconds

class Main(ttk.Frame):
    
    def __init__(self, parent):
        # class variables
        self.mousePressed = False
        self.isDrawing = False
        
        self.parent = parent    # parent = root
        self.parent.title(TITLE)
        self.parent.geometry('{}x{}+{}+{}'.format(WIDTH, HEIGHT, (self.parent.winfo_screenwidth() - WIDTH) // 2,
                                                  (self.parent.winfo_screenheight() - HEIGHT) // 2))    # center the application window
        self.parent.minsize(WIDTH, HEIGHT)    # so widgets cannot disappear
        self.makeMenus()
        
        ttk.Frame.__init__(self, parent)
        self.pack(fill=tk.BOTH, expand=1)
        self.initUI()
        
    # initialize main GUI placement and binds buttons
    def initUI(self):
        # must keep reference to avoid garbage-collection
        self.upButton = tk.PhotoImage(file="upButtonEleven.gif")
        self.downButton = tk.PhotoImage(file="downButtonEleven.gif")
        
        # set ttk styles
        style = ttk.Style()
        style.configure("TFrame", background=BGCOLOUR)
        style.configure("TLabel", background=BGCOLOUR)
        
        # pack GUI widgets
        titleLabel = ttk.Label(self, text=TITLE)
        titleLabel.pack()
        self.canvas = Canvas(self)
        self.canvas.bind("<Button-1>", self.canvas.drawPoint)
        self.canvas.pack(fill=tk.BOTH, padx=10, expand=1)
        guiFrame = ttk.Frame(self)
        guiFrame.columnconfigure(0, minsize=100, weight=1)    # only the column without buttons expands
        guiFrame.pack(fill=tk.X, padx=10, pady=10, expand=0)    # guiFrame does not expand vertically
        
        # grid guiFrame widgets: 3 rows, 6 columns
        self.statusText = tk.StringVar()    # Tk variables are traced, so widgets update when variable changes
        self.statusLabel = ttk.Label(guiFrame, textvariable=self.statusText, foreground="red")
        self.statusLabel.grid(row=0, column=0, sticky=tk.W)    # sticks to left side
        self.inputText = tk.StringVar()
        self.inputBox = ttk.Entry(guiFrame, textvariable=self.inputText)
        self.inputBox.bind('<Return>', self.canvas.takeInput)    # pressing enter in inputBox sends input to takeInput
        self.inputBox.grid(row=1, column=0, padx=(0,10), sticky=tk.E+tk.W)    # no padding on left, 10px padding on right
        self.inputBox.focus()
        
        # Tkinter calls what is given: calling a function gives Tkinter its return value, so must give a lambda with the argument
        xUpRotButton = tk.Button(guiFrame, height=20, width=20, image=self.upButton, background=BGCOLOUR, command=lambda: self.canvas.rotate('xUpRot'))
        xUpRotButton.bind("<Button-1>", lambda event: self.onMouseDown('xUpRot'))    # binding gives an event argument, so lambda must take it
        xUpRotButton.bind("<ButtonRelease-1>", self.onMouseUp)
        xUpRotButton.bind("<Return>", lambda event: self.canvas.rotate('xUpRot'))
        xUpRotButton.grid(row=0, column=1)
        yUpRotButton = tk.Button(guiFrame, height=20, width=20, image=self.upButton, background=BGCOLOUR, command=lambda: self.canvas.rotate('yUpRot'))
        yUpRotButton.bind("<Button-1>", lambda event: self.onMouseDown('yUpRot'))
        yUpRotButton.bind("<ButtonRelease-1>", self.onMouseUp)
        yUpRotButton.bind("<Return>", lambda event: self.canvas.rotate('yUpRot'))
        yUpRotButton.grid(row=0, column=2)
        zUpRotButton = tk.Button(guiFrame, height=20, width=20, image=self.upButton, background=BGCOLOUR, command=lambda: self.canvas.rotate('zUpRot'))
        zUpRotButton.bind("<Button-1>", lambda event: self.onMouseDown('zUpRot'))
        zUpRotButton.bind("<ButtonRelease-1>", self.onMouseUp)
        zUpRotButton.bind("<Return>", lambda event: self.canvas.rotate('zUpRot'))
        zUpRotButton.grid(row=0, column=3)
        # not yet implemented, so buttons are disabled
        fourUpRotButton = tk.Button(guiFrame, height=20, width=20, image=self.upButton, background=BGCOLOUR, state=tk.DISABLED)
        fourUpRotButton.grid(row=0, column=4)
        fiveUpRotButton = tk.Button(guiFrame, height=20, width=20, image=self.upButton, background=BGCOLOUR, state=tk.DISABLED)
        fiveUpRotButton.grid(row=0, column=5)
        
        # static text labels
        xrotLabel = ttk.Label(guiFrame, text="x")
        xrotLabel.grid(row=1, column=1)
        yrotLabel = ttk.Label(guiFrame, text="y")
        yrotLabel.grid(row=1, column=2)
        zrotLabel = ttk.Label(guiFrame, text="z")
        zrotLabel.grid(row=1, column=3)
        fourrotLabel = ttk.Label(guiFrame, text="4")
        fourrotLabel.grid(row=1, column=4)
        fiverotLabel = ttk.Label(guiFrame, text="5")
        fiverotLabel.grid(row=1, column=5)
        
        xDownRotButton = tk.Button(guiFrame, height=20, width=20, image=self.downButton, background=BGCOLOUR, command=lambda: self.canvas.rotate('xDownRot'))
        xDownRotButton.bind("<Button-1>", lambda event: self.onMouseDown('xDownRot'))
        xDownRotButton.bind("<ButtonRelease-1>", self.onMouseUp)
        xDownRotButton.bind("<Return>", lambda event: self.canvas.rotate('xDownRot'))
        xDownRotButton.grid(row=2, column=1)
        yDownRotButton = tk.Button(guiFrame, height=20, width=20, image=self.downButton, background=BGCOLOUR, command=lambda: self.canvas.rotate('yDownRot'))
        yDownRotButton.bind("<Button-1>", lambda event: self.onMouseDown('yDownRot'))
        yDownRotButton.bind("<ButtonRelease-1>", self.onMouseUp)
        yDownRotButton.bind("<Return>", lambda event: self.canvas.rotate('yDownRot'))
        yDownRotButton.grid(row=2, column=2)
        zDownRotButton = tk.Button(guiFrame, height=20, width=20, image=self.downButton, background=BGCOLOUR, command=lambda: self.canvas.rotate('zDownRot'))
        zDownRotButton.bind("<Button-1>", lambda event: self.onMouseDown('zDownRot'))
        zDownRotButton.bind("<ButtonRelease-1>", self.onMouseUp)
        zDownRotButton.bind("<Return>", lambda event: self.canvas.rotate('zDownRot'))
        zDownRotButton.grid(row=2, column=3)
        fourDownRotButton = tk.Button(guiFrame, height=20, width=20, image=self.downButton, background=BGCOLOUR, state=tk.DISABLED)
        fourDownRotButton.grid(row=2, column=4)
        fiveDownRotButton = tk.Button(guiFrame, height=20, width=20, image=self.downButton, background=BGCOLOUR, state=tk.DISABLED)
        fiveDownRotButton.grid(row=2, column=5)
        
    # make dropdown menus
    def makeMenus(self):
        menuBar = tk.Menu(self.parent)
        self.parent.config(menu=menuBar)
        # make cascades
        fileMenu = tk.Menu(menuBar)
        fileMenu.add_command(label="About", command=lambda: self.popUp('About'), underline=0)    # underline sets position of keyboard shortcut
        fileMenu.add_command(label="Help", command=lambda: self.popUp('Help'), underline=0)
        fileMenu.add_command(label="Exit", command=self.onExit, underline=1)
        menuBar.add_cascade(label="File", menu=fileMenu)
        
    # make pop-up windows
    def popUp(self, popUpType):
        # set individual window data
        if popUpType == 'About':
            titleText = "About this application..."
            messageText = TITLE + '\n' + DESCRIPTION
            buttonText = "OK"
            frameWidth = 400
            frameHeight = 200
        elif popUpType == 'Help':
            titleText = "Help"
            messageText = "Click the buttons to rotate the polygon about each axis."
            buttonText = "Dismiss"
            frameWidth = 400
            frameHeight = 120
        # create pop-up window, each with a title, a message, and a close button
        popUpFrame = tk.Toplevel(self.parent, background=BGCOLOUR)
        popUpFrame.title(titleText)
        popUpMessage = tk.Message(popUpFrame, text=messageText, width=frameWidth, background=BGCOLOUR)
        popUpMessage.pack()
        popUpButton = ttk.Button(popUpFrame, text=buttonText, command=popUpFrame.destroy)
        popUpButton.pack()
        popUpFrame.geometry('{}x{}+{}+{}'.format(frameWidth, frameHeight, self.parent.winfo_rootx() + (self.parent.winfo_width() - frameWidth) // 2,
                                                 self.parent.winfo_rooty() + (self.parent.winfo_height() - frameHeight) // 2))    # center in root window
        popUpButton.focus()    # so space can close the window
        
    # handle continuous mouse presses
    def poll(self, button):    # after(t, foo, arg) calls foo(arg) once after t ms and returns an alarm identifier
        if self.mousePressed:    # only polls if mouse is being pressed
            self.press(button)    # poll makes after call poll so poll calls press every t ms
            self.afterPollID = self.parent.after(DELAY, self.poll, button)
    def onMouseDown(self, button):
        self.mousePressed = True
        self.poll(button)
    def onMouseUp(self, event):
        self.mousePressed = False
        self.parent.after_cancel(self.afterPollID)    # cancel alarm callback if provided with alarm identifier
    def press(self, button):
        self.canvas.rotate(button)
        
    # handle status changes
    def setStatus(self, event):
        # clear status
        if event == "clear":
            self.statusText.set('')
        # switch drawing state
        elif event == "draw":
            self.isDrawing = not self.isDrawing
            if self.isDrawing:
                self.statusText.set("DRAWING")
            elif not self.isDrawing:
                self.setStatus('clear')
        # prevent drawing on generated polytope
        elif event == "nodraw":
            self.statusText.set("Cannot draw!")
            self.isDrawing = False
            self.statusLabel.after(1000, self.setStatus, 'clear')    # clears message after 1000 ms
            self.inputBox.focus()
            
    # close application
    def onExit(self):
        self.parent.destroy()



class Canvas(tk.Canvas):
    
    def __init__(self, parent):
        # class variables
        self.currPolytope = Polytope([])
        
        self.parent = parent    # parent = main
        tk.Canvas.__init__(self, parent, background="white", width=300, height=200)
        
    # draw points from mouse click
    def drawPoint(self, event):
        if self.parent.isDrawing:
            if self.currPolytope.isDrawn:
                self.currPolytope.addPoint((event.x - self.winfo_width()//2,    # subtract half of canvas dimensions because event is uncentered
                                            event.y - self.winfo_height()//2))
                self.render()
            elif not self.currPolytope.isDrawn:    # prevent drawing on generated polytope
                self.parent.setStatus('nodraw')
                
    # rotate polytope from rotButtons
    def rotate(self, rotType, rotAngle=ROTANGLE):
        if rotType == "xUpRot":
            self.currPolytope.xRotate(rotAngle)
        elif rotType == "xDownRot":
            self.currPolytope.xRotate(-rotAngle)    # backwards rotations rotate forwards by negative angle
        elif rotType == "yUpRot":
            self.currPolytope.yRotate(rotAngle)
        elif rotType == "yDownRot":
            self.currPolytope.yRotate(-rotAngle)
        elif rotType == "zUpRot":
            self.currPolytope.zRotate(rotAngle)
        elif rotType == "zDownRot":
            self.currPolytope.zRotate(-rotAngle)
        self.render()
        
    # take text input from inputBox
    def takeInput(self, event):
        self.currPolytope = self.translate(self.parent.inputText.get())
        self.render()
        self.parent.inputText.set('')    # clear inputBox
        
    # translate text input into Polytope object
    def translate(self, entry):
        # clear canvas, return empty polytope for render to process
        if entry == '' or entry == "clear":
            self.delete(tk.ALL)
            return Polytope([])
        # toggle drawing, return empty polytope that allows drawing
        elif entry == "draw":
            self.parent.setStatus('draw')
            return Polytope([], isDrawn=self.parent.isDrawing)
        # exit application
        elif entry == "quit" or entry == "exit":
            self.parent.onExit()
            
        # Schlafli symbol: {p/d}
        elif entry[0] == "{":
            return Polytope(self.schlafli(entry[1:-1]))
        # (x,y) is a point, (xn,yn) vectors: vx,y;x1,y1;x2,y2; ... xn,yn
        elif entry[0] == "v":
            return Polytope(self.vectorList(entry[1:]))
            
    # return Cartesian coordinates of {p/d} polygon
    def schlafli(self, entry):
        num = entry.split('/')
        p = int(num[0])    # number of vertices
        d = 1    # default density: vertex skip-number
        if len(num) > 1:
            d = int(num[1])
        r = RADIUS
        return self.circumcircle(p,d,r)
        
    # return Cartesian coordinates of p points spaced at angle d around a circle
    def circumcircle(self, p, d, r):
        rs = [r]*p    # polar coordinates, rs = magnitudes, thetas = angles
        thetas = [(2*k*d*math.pi/p)%(2*math.pi) for k in range(p)]
        return self.polarToCartesian(p, rs, thetas)
        
    # convert polar coordinates to Cartesian coordinates
    def polarToCartesian(self, number, rs, thetas):
        points = []
        count = 0
        while count < number:
            points.append((rs[count]*math.cos(thetas[count]), rs[count]*math.sin(thetas[count])))    # (r,t) -> (r cos t, r sin t)
            count += 1
        return points
        
    # return Cartesian coordinates of shape created by adding vectors to a point
    def vectorList(self, vectors):
        vectors = vectors.split(';')    # 'x1,y1;x2,y2' -> ('x1,y1'), ('x2,y2')
        point = [0,0]
        points = []
        count = 0
        while count < len(vectors):
            point[0] += float(vectors[count].split(',')[0])
            point[1] += float(vectors[count].split(',')[1])
            points.append((point[0],point[1]))    # ('x1,y1') -> (point[0]+x,point[1]+y)
            count += 1
        return(points)
        
    # render Polytope object
    def render(self):
        self.delete(tk.ALL)    # clear canvas
        if len(self.currPolytope.getPoints()) > 0:    # test for empty polytope
            w = self.winfo_width()//2    # so does not need to recalculate in list comprehension
            h = self.winfo_height()//2
            points = [(point[0]+w, point[1]+h) for point in self.currPolytope.getPoints()]    # center polygon on screen
            self.create_polygon(points, outline='#000', fill='#EEE', width=2)    # create polygon by joining list of points



class Polytope():
    
    def __init__(self, vertices, isDrawn=False):
        # class variables
        self.vertices = vertices    # actual vertices of shape
        self.points = vertices    # displayed vertices of shape
        self.isDrawn = isDrawn
        self.xrotAngle = 0
        self.yrotAngle = 0
        self.zrotAngle = 0
        
    # add point to drawn shapes
    def addPoint(self, point):
        if self.isDrawn:
            self.vertices.append(point)
            
    # return list of points
    def getPoints(self):
        return self.points
        
    # rotate polytope about x-axis
    def xRotate(self, rotAngle):
        self.xrotAngle += rotAngle    # so keeps track of current rotation
        c = math.cos(self.xrotAngle)    # so does not need to recalculate in list comprehension
        s = math.sin(self.xrotAngle)    # (x,y) -> (x cos t - y sin t, x sin t + y cos t)
        self.points = [(vertex[0]*c-vertex[1]*s, vertex[0]*s+vertex[1]*c) for vertex in self.vertices]
        
    # rotate polytope about y-axis
    def yRotate(self, rotAngle):
        self.yrotAngle += rotAngle
        c = math.cos(self.yrotAngle)    # (x,y) -> (x, y cos t)
        self.points = [(vertex[0], vertex[1]*c) for vertex in self.vertices]
        
    # rotate polytope about z-axis
    def zRotate(self, rotAngle):
        self.zrotAngle += rotAngle
        c = math.cos(self.zrotAngle)    # (x,y) -> (x cos t, y)
        self.points = [(vertex[0]*c, vertex[1]) for vertex in self.vertices]



root = tk.Tk()
main = Main(root)
