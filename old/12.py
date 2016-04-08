"""
Polygon Visualizer v0.12

This script displays various rotated squares in 3D.
This is a testing version with GODMODE on.
Therefore, everything is broken and the only inputs are taken from DATA.
"""

import tkinter as tk
import tkinter.ttk as ttk
import math

TITLE = "Polygon Visualizer v0.12"
DESCRIPTION = "\nThis script rotates polygons in 3D."
WIDTH = 350
HEIGHT = 400
RADIUS = 100
ROTANGLE = math.pi/12
BGCOLOUR = "#CCC"
DELAY = 28    # 28 ms per pi/12 rotation = 3 rotations every 2 seconds
GODMODE = True
# Lists of squares in various rotations. Violating 79-column limit because these are only for testing in GODMODE:
DATA = [
    (100,100,100,100),(0,math.pi/2,math.pi,3*math.pi/2),(math.pi/2,math.pi/2,math.pi/2,math.pi/2)]    # in xy plane
    #(100,100,100,100),(0,math.pi/2,math.pi,3*math.pi/2),(math.pi/2,0,math.pi/2,math.pi)]    # in xz plane
    #(100,100,100,100),(0,math.pi/2,math.pi,3*math.pi/2),(math.pi, math.pi/2,0,math.pi/2)]    # in yz plane
    #(100,100,100,100),(0,math.pi/2,math.pi,3*math.pi/2),(math.pi/2,math.pi/4,math.pi/2,3*math.pi/4)]    # in xz plane, then rotated about x-axis by math.pi
    #(100,100,100,100),(0,math.pi/2,math.pi,3*math.pi/2),(3*math.pi/4,math.pi/2,math.pi/4,math.pi/2)]    # in yz plane, then rotated about y-axis by math.pi/4/4


class Main(ttk.Frame):

    """
    GUI class that manages all windows and actions except the canvas.

    Public methods:
    set_status
    close

    Instance variables:
    self.mousePressed
    self.isDrawing

    Object variables:
    self.parent
    self.canvas
    self.statusText
    self.inputText
    """

    def __init__(self, parent):
        """Construct Main class."""
        self.mousePressed = False
        self.isDrawing = False
        self.parent = parent
        self.parent.title(TITLE)
        self.parent.geometry(
            '{}x{}+{}+{}'.format(
                WIDTH, HEIGHT,    # Center the application window
                (self.parent.winfo_screenwidth() - WIDTH) // 2,
                (self.parent.winfo_screenheight() - HEIGHT) // 2))
        self.parent.minsize(WIDTH, HEIGHT)
        self._make_menus()
        ttk.Frame.__init__(self, parent)
        self.pack(fill=tk.BOTH, expand=1)
        self._initUI()

    def _initUI(self):

        # Initialize GUI placement and bind buttons.

        # Must keep reference to avoid garbage-collection
        self._upBtn = tk.PhotoImage(file="upButtonEleven.gif")
        self._downBtn = tk.PhotoImage(file="downButtonEleven.gif")

        style = ttk.Style()
        style.configure("TFrame", background=BGCOLOUR)
        style.configure("TLabel", background=BGCOLOUR)
        style.configure("TButton", background=BGCOLOUR)

        titleLabel = ttk.Label(self, text=TITLE)
        titleLabel.pack()
        self.canvas = Canvas(self)
        self.canvas.bind("<Button-1>", self.canvas.draw_point)
        self.canvas.pack(fill=tk.BOTH, padx=10, expand=1)
        guiFrame = ttk.Frame(self)
        guiFrame.columnconfigure(0, minsize=100, weight=1)
        guiFrame.pack(fill=tk.X, padx=10, pady=10, expand=0)

        # grid guiFrame widgets: 3 rows, 6 columns
        self.statusText = tk.StringVar()
        self._statusLabel = ttk.Label(
            guiFrame, textvariable=self.statusText, foreground="red")
        self._statusLabel.grid(row=0, column=0, sticky=tk.W)
        self.inputText = tk.StringVar()
        self._inputBox = ttk.Entry(guiFrame, textvariable=self.inputText)
        self._inputBox.bind('<Key-Return>', self.canvas.take_input)
        # No padding on left, 10px padding on right
        self._inputBox.grid(row=1, column=0, padx=(0,10), sticky=tk.E+tk.W)
        self._inputBox.focus()

        # Tkinter calls what is given: calling a function gives Tkinter
        # its return value, so must give a lambda with the argument.
        xUpRotBtn = ttk.Button(guiFrame, image=self._upBtn,
                               command=lambda: self.canvas.rotate('xUpRot'))
        xUpRotBtn.bind("<Button-1>",    # Binding gives an event argument
                       lambda event: self._mouse_down('xUpRot'))
        xUpRotBtn.bind("<ButtonRelease-1>", self._mouse_up)
        xUpRotBtn.bind("<Key-Return>",
                       lambda event: self.canvas.rotate('xUpRot'))
        xUpRotBtn.grid(row=0, column=1)
        yUpRotBtn = ttk.Button(guiFrame, image=self._upBtn,
                              command=lambda: self.canvas.rotate('yUpRot'))
        yUpRotBtn.bind("<Button-1>",
                       lambda event: self._mouse_down('yUpRot'))
        yUpRotBtn.bind("<ButtonRelease-1>", self._mouse_up)
        yUpRotBtn.bind("<Key-Return>",
                       lambda event: self.canvas.rotate('yUpRot'))
        yUpRotBtn.grid(row=0, column=2)
        zUpRotBtn = ttk.Button(guiFrame, image=self._upBtn,
                              command=lambda: self.canvas.rotate('zUpRot'))
        zUpRotBtn.bind("<Button-1>",
                       lambda event: self._mouse_down('zUpRot'))
        zUpRotBtn.bind("<ButtonRelease-1>", self._mouse_up)
        zUpRotBtn.bind("<Key-Return>",
                       lambda event: self.canvas.rotate('zUpRot'))
        zUpRotBtn.grid(row=0, column=3)
        # Not yet implemented, so buttons are disabled
        fourUpRotBtn = ttk.Button(guiFrame, image=self._upBtn,
                                 state=tk.DISABLED)
        fourUpRotBtn.grid(row=0, column=4)
        fiveUpRotBtn = ttk.Button(guiFrame, image=self._upBtn,
                                  state=tk.DISABLED)
        fiveUpRotBtn.grid(row=0, column=5)

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

        xDownRotBtn = ttk.Button(guiFrame, image=self._downBtn,
                                command=lambda: self.canvas.rotate('xDownRot'))
        xDownRotBtn.bind("<Button-1>",
                         lambda event: self._mouse_down('xDownRot'))
        xDownRotBtn.bind("<ButtonRelease-1>", self._mouse_up)
        xDownRotBtn.bind("<Key-Return>",
                         lambda event: self.canvas.rotate('xDownRot'))
        xDownRotBtn.grid(row=2, column=1)
        yDownRotBtn = ttk.Button(guiFrame, image=self._downBtn,
                                command=lambda: self.canvas.rotate('yDownRot'))
        yDownRotBtn.bind("<Button-1>",
                         lambda event: self._mouse_down('yDownRot'))
        yDownRotBtn.bind("<ButtonRelease-1>", self._mouse_up)
        yDownRotBtn.bind("<Key-Return>",
                         lambda event: self.canvas.rotate('yDownRot'))
        yDownRotBtn.grid(row=2, column=2)
        zDownRotBtn = ttk.Button(guiFrame, image=self._downBtn,
                                command=lambda: self.canvas.rotate('zDownRot'))
        zDownRotBtn.bind("<Button-1>",
                         lambda event: self._mouse_down('zDownRot'))
        zDownRotBtn.bind("<ButtonRelease-1>", self._mouse_up)
        zDownRotBtn.bind("<Key-Return>",
                        lambda event: self.canvas.rotate('zDownRot'))
        zDownRotBtn.grid(row=2, column=3)
        fourDownRotBtn = ttk.Button(guiFrame, image=self._downBtn,
                                   state=tk.DISABLED)
        fourDownRotBtn.grid(row=2, column=4)
        fiveDownRotBtn = ttk.Button(guiFrame, image=self._downBtn,
                                   state=tk.DISABLED)
        fiveDownRotBtn.grid(row=2, column=5)

        if GODMODE:
            self.update()    # Generally a really bad idea except in testing
            self.canvas.inject_data()

    def _make_menus(self):
        # Initialize dropdown menus.
        menuBar = tk.Menu(self.parent)
        self.parent.config(menu=menuBar)
        fileMenu = tk.Menu(menuBar)
        # underline sets position of keyboard shortcut
        fileMenu.add_command(label="About", underline=0,
                             command=lambda: self._make_popups('About'))
        fileMenu.add_command(label="Help", underline=0,
                             command=lambda: self._make_popups('Help'))
        fileMenu.add_command(label="Exit", underline=1,
                             command=self.close)
        menuBar.add_cascade(label="File", menu=fileMenu)

    def _make_popups(self, popUpType):

        # Make pop-up windows based on popUpType.

        # Set individual window data
        if popUpType == 'About':
            titleText = "About this application..."
            messageText = TITLE + '\n' + DESCRIPTION
            buttonText = "OK"
            frameWidth = 400
            frameHeight = 200
        elif popUpType == 'Help':
            titleText = "Help"
            messageText = ("Click the buttons to rotate "
                           "the polygon about each axis.")
            buttonText = "Dismiss"
            frameWidth = 400
            frameHeight = 120

        # Create pop-up window, each with title, message, and close button
        popUpFrame = tk.Toplevel(self.parent, background=BGCOLOUR)
        popUpFrame.title(titleText)
        popUpMessage = tk.Message(popUpFrame, text=messageText,
                                  width=frameWidth, background=BGCOLOUR)
        popUpMessage.pack()
        popUpButton = ttk.Button(popUpFrame, text=buttonText,
                                 command=popUpFrame.destroy)
        popUpButton.pack()

        # Center in root window
        popUpFrame.geometry('{}x{}+{}+{}'.format(
            frameWidth, frameHeight,
            self.parent.winfo_rootx() +
            (self.parent.winfo_width() - frameWidth) // 2,
            self.parent.winfo_rooty() +
            (self.parent.winfo_height() - frameHeight) // 2))
        popUpButton.focus()    # So space can close the window

    def _poll(self, button):
        # Handle continuous mouse presses on button.
        # after(t, foo, arg) calls foo(arg) once after t ms and returns an ID.
        # after calls _poll when mouse pressed, which calls _press every t ms.
        if self.mousePressed:
            self._press(button)
            self.after_pollID = self.parent.after(DELAY, self._poll, button)
    def _mouse_down(self, button):
        self.mousePressed = True
        self._poll(button)
    def _mouse_up(self, event):
        self.mousePressed = False
        self.parent.after_cancel(self.after_pollID)
    def _press(self, button):
        self.canvas.rotate(button)

    def set_status(self, event):

        """Handle and display status changes."""

        # Clear status
        if event == "clear":
            self.statusText.set('')

        # Switch drawing state
        elif event == "draw":
            self.isDrawing = not self.isDrawing
            if self.isDrawing:
                self.statusText.set("DRAWING")
            elif not self.isDrawing:
                self.set_status('clear')

        # Prevent drawing on generated polytope
        elif event == "nodraw":
            self.statusText.set("Cannot draw!")
            self.isDrawing = False
            # Clear message after 1000 ms
            self.statusLabel.after(1000, self.set_status, 'clear')
            self.inputBox.focus()

    def close(self):
        """Close the application."""
        self.parent.destroy()



class Canvas(tk.Canvas):

    """
    Display class that manages polytope creation, edits, and display.

    Public methods:
    draw_point
    rotate
    take_input
    inject_data

    Object variables:
    self.parent
    self.currPolytope
    """

    def __init__(self, parent):
        """Construct Canvas class."""
        self.parent = parent
        tk.Canvas.__init__(self, parent, background="white",
                           relief=tk.GROOVE, borderwidth=5,
                           width=300, height=200)

    def inject_data(self):
        """Inject data from DATA directly into _render."""
        self.currPolytope = Polytope(DATA)
        self._render()

    def draw_point(self, event):
        """
        Draw point on mouse click if polytope is drawn
        and status is drawing. event is a mouse click.
        """
        if self.parent.isDrawing:
            if self.currPolytope.isDrawn:
                # Subtract half of canvas dimensions since event is uncentered
                self.currPolytope.add_point((event.x - self.winfo_width()//2,
                                            event.y - self.winfo_height()//2))
                self._render()
            elif not self.currPolytope.isDrawn:
                self.parent.set_status('nodraw')

    def rotate(self, rotType, rotAngle=ROTANGLE):
        """Rotate polytope on button press by ROTANGLE radians."""
        if rotType == "xUpRot":
            self.currPolytope.rotate_x(rotAngle)
        elif rotType == "xDownRot":
            self.currPolytope.rotate_x(-rotAngle)
        elif rotType == "yUpRot":
            self.currPolytope.rotate_y(rotAngle)
        elif rotType == "yDownRot":
            self.currPolytope.rotate_y(-rotAngle)
        elif rotType == "zUpRot":
            self.currPolytope.rotate_z(rotAngle)
        elif rotType == "zDownRot":
            self.currPolytope.rotate_z(-rotAngle)
        self._render()

    def take_input(self, event):
        """Take text input from input box."""
        self.currPolytope = self._translate(self.parent.inputText.get())
        self._render()
        self.parent.inputText.set('')

    def _translate(self, entry):

        # Translate text input to return a Polytope object.

        # Clear canvas, return empty polytope for _render to process
        if entry == '' or entry == "clear":
            self.delete(tk.ALL)
            return Polytope([])

        # Toggle drawing, return empty polytope that allows drawing
        elif entry == "draw":
            self.parent.set_status('draw')
            return Polytope([], isDrawn=self.parent.isDrawing)

        # Exit application
        elif entry == "quit" or entry == "exit":
            self.parent.close()

        # Schlafli symbol: {p/d}
        elif entry.startswith("{") and entry.endswith("}"):
            return Polytope(self._schlafli(entry[1:-1]))

        # (x,y) is a point, (xn,yn) vectors: vx,y;x1,y1;x2,y2; ... xn,yn
        elif entry.startswith("v"):
            return Polytope(self._vector_list(entry[1:]))

    def _schlafli(self, entry):
        # Take Schlafli symbol and return its Cartesian coordinates.
        num = entry.split('/')
        p = int(num[0])
        d = 1
        if len(num) > 1:
            d = int(num[1])
        r = RADIUS
        return self._circumcircle(p,d,r)

    def _circumcircle(self, p, d, r):
        # Return coordinates of p points angle d apart on radius r circle.
        rs = [r]*p    # Polar coordinates: rs = magnitudes, thetas = angles
        thetas = [(2*k*d*math.pi/p)%(2*math.pi) for k in range(p)]
        return (rs, thetas)

    def _vector_list(self, vectors):
        # Take list of Cartesian vectors and
        # return its corresponding list of points.
        vectors = vectors.split(';')    # 'x1,y1;x2,y2' -> ('x1,y1'), ('x2,y2')
        point = [0,0]
        points = []
        count = 0
        while count < len(vectors):
            point[0] += float(vectors[count].split(',')[0])
            point[1] += float(vectors[count].split(',')[1])
            points.append((point[0],point[1]))    # ('x1,y1') -> (x0+x,y0+y)
            count += 1
        return(points)

    def _render(self):
        # Clear the canvas, center, and display Polytope object.
        self.delete(tk.ALL)
        if self.currPolytope.get_points():    # Empty lists are False
            w = self.winfo_width()//2
            h = self.winfo_height()//2
            points = [(point[0]+w, point[1]+h)
                      for point in self.currPolytope.get_points()]
            self.create_polygon(points, outline='#000', fill='#EEE', width=2)




class Polytope():

    """
    Drawing class that stores all polytope data and manages rotations.

    Public methods:
    add_point
    get_points

    Instance variables:
    self.isDrawn
    """

    def __init__(self, vertices, isDrawn=False):
        """Construct Polytope class."""
        self.isDrawn = isDrawn
        self.rs = vertices[0]
        self.thetas = vertices[1]
        self.phis = vertices[2]

    def add_point(self, point):
        """Add a point to a drawn shape."""
        if self.isDrawn:
            self._vertices.append(point)

    def get_points(self):
        """Return a list of points."""
        # Convert spherical coordinates (three separate lists)
        # to return Cartesian coordinates (one list of triples)
        total = len(self.rs)
        points = []
        n = 0
        while n < total:
            # (r,t,p) -> (r cos(t)sin(p), r sin(t)sin(p), r cos(p))
            points.append((int(self.rs[n]*math.cos(self.thetas[n])*math.sin(self.phis[n])),
                           int(self.rs[n]*math.sin(self.thetas[n])*math.sin(self.phis[n]))))
            n += 1
        return points



root = tk.Tk()
main = Main(root)
