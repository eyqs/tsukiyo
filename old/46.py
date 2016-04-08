"""
Wythoff Visualizer v0.46

This program uses an iterative algorithm to reflect Schwarz triangles.
The algorithm currently has many overlapping triangles, so is too slow.
"""

import tkinter as tk
import tkinter.ttk as ttk
import math

TITLE = "Wythoff Visualizer v0.46"
DESCRIPTION = "\nThis script displays the uniform polyhedra."
pi = math.pi
WIDTH = 600
HEIGHT = 600
BGCOLOUR = "#CCC"

RADIUS = 100
ZOOM = 40
DISTANCE = 5
RETINA = 10
CHANGE = 10    # 10 pixels change in radius and 0.1r change in distance
DELAY = 28    # 28 ms per pi/24 rotation = 3 rotations every 4 seconds
ROTANGLE = pi/24
EPSILON = 0.00001

def normalize(points, vector=[1]):
    """
    Normalizes a vector.

    Takes two vectors as lists and creates a new vector with
    the magnitude of the second and the direction of the first.
    Default length of the second vector is 1.
    """
    norm = math.sqrt(sum([x**2 for x in points]))
    magnitude = math.sqrt(sum([x**2 for x in vector]))
    return [x/norm*magnitude for x in points]

def convert(point, toCartesian):
    """Converts between spherical and Cartesian coordinates."""
    # spherical to Cartesian
    if toCartesian == True:
        x = point[0]*math.sin(point[3])*math.sin(point[2])*math.cos(point[1])
        y = point[0]*math.sin(point[3])*math.sin(point[2])*math.sin(point[1])
        z = point[0]*math.sin(point[3])*math.cos(point[2])
        w = point[0]*math.cos(point[3])
        return (x, y, z, w)
    # Cartesian to spherical
    elif toCartesian == False:
        r = math.sqrt(point[3]**2+point[2]**2+point[1]**2+point[0]**2)
        if point[0] == 0 and point[1] == 0:
            theta = 0
        elif point[0] >= 0:
            theta = math.acos(point[1]/math.sqrt(point[1]**2+point[0]**2))
        elif point[0] <= 0:
            theta = 2*pi-math.acos(point[1]/math.sqrt(point[1]**2+point[0]**2))
        if point[0] == 0 and point[1] == 0 and point[2] == 0:
            phi = 0
        else:
            phi = abs(math.acos(
                point[2]/math.sqrt(point[2]**2+point[1]**2+point[0]**2)))
        omega = abs(math.acos(point[3]/r))
        return (r, theta, phi, omega)

class Main(ttk.Frame):

    """
    GUI class that manages all windows and actions except the canvas.

    Public methods:
    set_status
    close

    Instance variables:
    mousePressed

    Object variables:
    parent
    canvas
    statusLabel
    statusText
    inputText
    """

    def __init__(self, parent):
        """Construct Main class."""
        self.mousePressed = False
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
        self._leftBtn = tk.PhotoImage(file="leftButtonTwentyFour.gif")
        self._rightBtn = tk.PhotoImage(file="rightButtonTwentyFour.gif")
        self._upBtn = tk.PhotoImage(file="upButtonEleven.gif")
        self._downBtn = tk.PhotoImage(file="downButtonEleven.gif")

        style = ttk.Style()
        style.configure("TFrame", background=BGCOLOUR)
        style.configure("TLabel", background=BGCOLOUR)
        style.configure("TButton", background=BGCOLOUR)

        titleLabel = ttk.Label(self, text=TITLE)
        titleLabel.pack()
        self.canvas = Canvas(self)
        self.canvas.pack(fill=tk.BOTH, padx=10, expand=1)
        _guiFrame = ttk.Frame(self)
        _guiFrame.columnconfigure(0, weight=1)
        _guiFrame.pack(fill=tk.X, padx=10, pady=10, expand=0)

        # grid _guiFrame widgets: 4 rows, 11 columns
        self.statusText = tk.StringVar()
        self.statusLabel = ttk.Label(
            _guiFrame, textvariable=self.statusText, foreground="red")
        self.statusLabel.grid(row=0, column=0, columnspan=7, sticky=tk.W)
        self.inputText = tk.StringVar()
        self._inputBox = ttk.Entry(_guiFrame, textvariable=self.inputText)
        self._inputBox.bind('<Key-Return>', self.canvas.take_input)
        # No padding on left, 10px padding on right
        self._inputBox.grid(row=1, column=0, columnspan=7,
                            padx=(0,10), sticky=tk.E+tk.W)
        self._inputBox.focus()

        _viewLabel = ttk.Label(_guiFrame, text="Views: ")
        _viewLabel.grid(row=2, column=0, columnspan=3, sticky=tk.E)
        _xViewBtn = ttk.Button(_guiFrame, text="x", width=2, command=lambda:
                               self.canvas.set_viewaxis([0, pi/2, pi/2]))
        _xViewBtn.bind("<Key-Return>", lambda event:
                       self.canvas.set_viewaxis([0, pi/2, pi/2]))
        _xViewBtn.grid(row=2, column=3)
        _yViewBtn = ttk.Button(_guiFrame, text="y", width=2, command=lambda:
                               self.canvas.set_viewaxis([pi/2, pi/2, pi/2]))
        _yViewBtn.bind("<Key-Return>", lambda event:
                       self.canvas.set_viewaxis([pi/2, pi/2, pi/2]))
        _yViewBtn.grid(row=2, column=4)
        _zViewBtn = ttk.Button(_guiFrame, text="z", width=2, command=lambda:
                               self.canvas.set_viewaxis([0, 0, pi/2]))
        _zViewBtn.bind("<Key-Return>", lambda event:
                       self.canvas.set_viewaxis([0, 0, pi/2]))
        _zViewBtn.grid(row=2, column=5)
        _wViewBtn = ttk.Button(_guiFrame, text="w", width=2, command=lambda:
                               self.canvas.set_viewaxis([0, 0, 0]))
        _wViewBtn.bind("<Key-Return>", lambda event:
                       self.canvas.set_viewaxis([0, 0, 0]))
        _wViewBtn.grid(row=2, column=6, padx=(0,10))

        _zoomLabel = ttk.Label(_guiFrame, text="zoom: ")
        _zoomLabel.grid(row=3, column=1, sticky=tk.E)
        _zUpBtn = ttk.Button(_guiFrame, image=self._upBtn, command=lambda:
                             self.canvas.change('zUp'))
        _zUpBtn.bind("<Button-1>", lambda event: self._mouse_down('zUp'))
        _zUpBtn.bind("<ButtonRelease-1>", self._mouse_up)
        _zUpBtn.bind("<Key-Return>", lambda event:
                     self.canvas.change('rUp'))
        _zUpBtn.grid(row=3, column=2)
        _zDownBtn = ttk.Button(_guiFrame, image=self._downBtn, command=lambda:
                               self.canvas.change('zDown'))
        _zDownBtn.bind("<Button-1>", lambda event: self._mouse_down('zDown'))
        _zDownBtn.bind("<ButtonRelease-1>", self._mouse_up)
        _zDownBtn.bind("<Key-Return>", lambda event:
                       self.canvas.change('zDown'))
        _zDownBtn.grid(row=3, column=3)
        _distanceLabel = ttk.Label(_guiFrame, text="d: ")
        _distanceLabel.grid(row=3, column=4, sticky=tk.E)
        _dUpBtn = ttk.Button(_guiFrame, image=self._upBtn, command=lambda:
                             self.canvas.change('dUp'))
        _dUpBtn.bind("<Button-1>", lambda event: self._mouse_down('dUp'))
        _dUpBtn.bind("<ButtonRelease-1>", self._mouse_up)
        _dUpBtn.bind("<Key-Return>", lambda event:
                     self.canvas.change('dUp'))
        _dUpBtn.grid(row=3, column=5)
        _dDownBtn = ttk.Button(_guiFrame, image=self._downBtn, command=lambda:
                               self.canvas.change('dDown'))
        _dDownBtn.bind("<Button-1>", lambda event: self._mouse_down('dDown'))
        _dDownBtn.bind("<ButtonRelease-1>", self._mouse_up)
        _dDownBtn.bind("<Key-Return>", lambda event:
                       self.canvas.change('dDown'))
        _dDownBtn.grid(row=3, column=6, padx=(0,10))

        _leftRotBtn = ttk.Button(_guiFrame, image=self._leftBtn,
                                 command=lambda: self.canvas.rotate(0))
        _leftRotBtn.bind("<Button-1>", lambda event: self._mouse_down(0))
        _leftRotBtn.bind("<ButtonRelease-1>", self._mouse_up)
        _leftRotBtn.bind("<Key-Return>", lambda event: self.canvas.rotate(0))
        _leftRotBtn.grid(row=0, column=7, rowspan=2, sticky=tk.E)
        _rightRotBtn = ttk.Button(_guiFrame, image=self._rightBtn,
                                  command=lambda: self.canvas.rotate(1))
        _rightRotBtn.bind("<Button-1>", lambda event: self._mouse_down(1))
        _rightRotBtn.bind("<ButtonRelease-1>", self._mouse_up)
        _rightRotBtn.bind("<Key-Return>", lambda event: self.canvas.rotate(1))
        _rightRotBtn.grid(row=0, column=8, rowspan=2, columnspan=2, sticky=tk.W)

        _rotateLabel = ttk.Label(_guiFrame, text="Rotate: ")
        _rotateLabel.grid(row=2, column=7, sticky=tk.E)
        _xwRotBtn = ttk.Button(_guiFrame, text="xw", width=3,
                               command=lambda: self.canvas.set_rotaxis('xw'))
        _xwRotBtn.bind("<Key-Return>",lambda event:self.canvas.set_rotaxis('xw'))
        _xwRotBtn.grid(row=2, column=8)
        _ywRotBtn = ttk.Button(_guiFrame, text="yw", width=3,
                               command=lambda: self.canvas.set_rotaxis('yw'))
        _ywRotBtn.bind("<Key-Return>",lambda event:self.canvas.set_rotaxis('yw'))
        _ywRotBtn.grid(row=2, column=9)
        _zwRotBtn = ttk.Button(_guiFrame, text="zw", width=3,
                               command=lambda: self.canvas.set_rotaxis('zw'))
        _zwRotBtn.bind("<Key-Return>",lambda event:self.canvas.set_rotaxis('zw'))
        _zwRotBtn.grid(row=2, column=10)
        _xyRotBtn = ttk.Button(_guiFrame, text="xy", width=3,
                               command=lambda: self.canvas.set_rotaxis('xy'))
        _xyRotBtn.bind("<Key-Return>",lambda event:self.canvas.set_rotaxis('xy'))
        _xyRotBtn.grid(row=3, column=8)
        _yzRotBtn = ttk.Button(_guiFrame, text="yz", width=3,
                               command=lambda: self.canvas.set_rotaxis('yz'))
        _yzRotBtn.bind("<Key-Return>",lambda event:self.canvas.set_rotaxis('yz'))
        _yzRotBtn.grid(row=3, column=9)
        _xzRotBtn = ttk.Button(_guiFrame, text="xz", width=3,
                               command=lambda: self.canvas.set_rotaxis('xz'))
        _xzRotBtn.bind("<Key-Return>",lambda event:self.canvas.set_rotaxis('xz'))
        _xzRotBtn.grid(row=3, column=10)

    def _make_menus(self):
        # Initialize dropdown menus.
        _menuBar = tk.Menu(self.parent)
        self.parent.config(menu=_menuBar)
        _fileMenu = tk.Menu(_menuBar)
        # underline sets position of keyboard shortcut
        _fileMenu.add_command(label="About", underline=0,
                              command=lambda: self._make_popups('About'))
        _fileMenu.add_command(label="Help", underline=0,
                              command=lambda: self._make_popups('Help'))
        _fileMenu.add_command(label="Exit", underline=1,
                              command=self.close)
        _menuBar.add_cascade(label="File", menu=_fileMenu)

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
            messageText = ("Click the buttons to rotate the "
                            "object or change the view.")
            buttonText = "Dismiss"
            frameWidth = 400
            frameHeight = 120

        # Create pop-up window, each with title, message, and close button
        _popUpFrame = tk.Toplevel(self.parent, background=BGCOLOUR)
        _popUpFrame.title(titleText)
        _popUpMessage = tk.Message(_popUpFrame, text=messageText,
                                   width=frameWidth, background=BGCOLOUR)
        _popUpMessage.pack()
        _popUpButton = ttk.Button(_popUpFrame, text=buttonText,
                                  command=_popUpFrame.destroy)
        _popUpButton.pack()

        # Center in root window
        _popUpFrame.geometry('{}x{}+{}+{}'.format(
            frameWidth, frameHeight,
            self.parent.winfo_rootx() +
            (self.parent.winfo_width() - frameWidth) // 2,
            self.parent.winfo_rooty() +
            (self.parent.winfo_height() - frameHeight) // 2))

        # Set all focus on the pop up, stop mainloop in main
        _popUpFrame.grab_set()
        _popUpButton.focus()
        self.wait_window(_popUpFrame)

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
        if button == 'zUp':
            self.canvas.change('zUp')
        elif button == 'zDown':
            self.canvas.change('zDown')
        elif button == 'dUp':
            self.canvas.change('dUp')
        elif button == 'dDown':
            self.canvas.change('dDown')
        else:
            self.canvas.rotate(button)

    def set_status(self, event):
        """Handle and display status changes."""
        if event == "clear":
            self.statusText.set('')
        elif event == "badinput":
            self.statusText.set("Bad input!")
            self.statusLabel.after(1000, self.set_status, 'clear')

    def close(self):
        """Close the application."""
        self.parent.destroy()



class Canvas(tk.Canvas):

    """
    Display class that manages polytope creation, edits, and display.

    Public methods:
    set_viewaxis
    set_rotaxis
    change
    rotate
    take_input

    Object variables:
    parent
    currPolytope
    """

    def __init__(self, parent):
        """Construct Canvas class."""
        self.parent = parent
        tk.Canvas.__init__(self, parent, background="white",
                           relief=tk.GROOVE, borderwidth=5,
                           width=300, height=200)
        self.currPolytope = Polytope([])
        self._reset()

    def change(self, change, amount=CHANGE):
        """Change the polytope radius and viewpoint distance."""
        if change == 'zUp':
            self._zoom += amount
        elif change == 'zDown':
            self._zoom -= amount
        elif change == 'dUp':
            self._distance += amount*0.1
        elif change == 'dDown':
            self._distance -= amount*0.1
        self._render()

    def set_viewaxis(self, viewAxis):
        """Change the current view. Takes hyperspherical axis coordinates."""
        #Check that inputs satisfy restrictions
        for n in range(3):
            while viewAxis[n] >= 2*pi:
                viewAxis[n] -= 2*pi
            while viewAxis[n] < 0:
                viewAxis[n] += 2*pi
        if viewAxis[2] > pi:
            viewAxis[2] = 2*pi - viewAxis[2]
        if viewAxis[1] > pi:
            viewAxis[1] = 2*pi - viewAxis[2]
        self._viewAxis = (viewAxis)
        self._render()

    def _view(self, points):
        """Return a Cartesian double depending on the viewAxis."""
        # Formula derived on 14/10/21
        so = math.sin(self._viewAxis[2])
        co = math.cos(self._viewAxis[2])
        sp = math.sin(self._viewAxis[1])
        cp = math.cos(self._viewAxis[1])
        st = math.sin(self._viewAxis[0])
        ct = math.cos(self._viewAxis[0])

        u = (so*sp*ct, so*sp*st, so*cp, co)
        w = (-st, ct, 0, 0)
        h = (cp*ct, cp*st, -sp, 0)
        b = (-co*sp*ct, -co*sp*st, -co*cp, so)
        d = self._distance*RADIUS
        f = d + RETINA

        result = []
        for count in range(len(points)):
            x = points[count][0]
            y = points[count][1]
            z = points[count][2]
            w = points[count][3]
            t = (f-x*u[0]-y*u[1]-z*u[2]-w*u[3])/(d-x*u[0]-y*u[1]-z*u[2]-w*u[3])

            if abs(self._viewAxis[2]) < EPSILON:
                if abs(self._viewAxis[1] - pi/2) < EPSILON:
                    m = (1-t)*-z*sp
                    if (abs(self._viewAxis[0]) < EPSILON or
                        abs(self._viewAxis[0] - pi) < EPSILON):
                        n = (1-t)*y*ct
                        p = (1-t)*(-x*co*sp*ct)
                    else:
                        n = (1-t)*(x-y*ct/st)*-st
                        p = ((1-t)*y-n*ct)/(-co*sp*st)
                else:
                    if (abs(self._viewAxis[0]) < EPSILON or
                        abs(self._viewAxis[0] - pi) < EPSILON):
                        n = (1-t)*y*ct
                        m = (1-t)*(x-z*sp/cp*ct)*cp/ct
                    else:
                        n = (1-t)*(x-y*ct/st)*(st/(ct*ct-st*st))
                        m = ((1-t)*(y-z*sp/cp*st)+n*ct)*cp/st
                    p = ((1-t)*z+m*sp)/(-co*cp)

            else:
                p = ((1-t)*w+(d*t-f)*co)/so
                if abs(self._viewAxis[1]) < EPSILON:
                    if (abs(self._viewAxis[0]) < EPSILON or
                        abs(self._viewAxis[0] - pi) < EPSILON):
                        n = (1-t)*y*ct
                        m = (1-t)*x*cp*ct
                    else:
                        n = (1-t)*(x-y*ct/st)*-st
                        m = ((1-t)*y-n*ct)/(cp*st)
                else:
                    m = -((1-t)*z+(d*t-f)*so*sp+p*co*cp)/sp
                    if (abs(self._viewAxis[0]) < EPSILON or
                        abs(self._viewAxis[0] - pi) < EPSILON):
                        n = (1-t)*y*ct
                    else:
                        n = -((1-t)*x+(d*t-f)*so*sp*ct-m*cp*ct+p*co*sp*ct)/st
            result.append((m*self._zoom, n*self._zoom))
        return result

    def set_rotaxis(self, rotAxis):
        """Change the current rotation axis-plane."""
        if rotAxis == "xw":
            self.currPolytope.set_rotaxis((1,0,0,0),(0,0,0,1))
        elif rotAxis == 'yw':
            self.currPolytope.set_rotaxis((0,1,0,0),(0,0,0,1))
        elif rotAxis == 'zw':
            self.currPolytope.set_rotaxis((0,0,1,0),(0,0,0,1))
        elif rotAxis == 'xy':
            self.currPolytope.set_rotaxis((1,0,0,0),(0,1,0,0))
        elif rotAxis == 'yz':
            self.currPolytope.set_rotaxis((0,1,0,0),(0,0,1,0))
        elif rotAxis == 'xz':
            self.currPolytope.set_rotaxis((1,0,0,0),(0,0,1,0))
        self._render()

    def rotate(self, direction, rotAngle=ROTANGLE):
        """Rotate polytope on button press by ROTANGLE radians."""
        if direction == 0:
            self.currPolytope.rotate(rotAngle)
        elif direction == 1:
            self.currPolytope.rotate(-rotAngle)
        self._render()

    def take_input(self, event):
        """Take text input from input box."""
        try:
            translatedInput = self._translate(self.parent.inputText.get())
            if translatedInput:
                self.currPolytope = translatedInput
                self._reset()
        except ValueError:
            self.parent.set_status('badinput')
        self._render()
        self.parent.inputText.set('')

    def _translate(self, entry):

        # Translate text input to return a Polytope object.

        # Clear canvas, return empty polytope for _render to process
        if entry == ('' or "clear" or "reset"):
            return Polytope([])

        # Exit application
        if entry == "quit" or entry == "exit" or entry == "close":
            self.parent.close()

        # Set rotation axis
        # elif entry.startswith("r"):
        #     rotAxis = entry[1:].split(',')
        #     self.currPolytope.set_rotaxis(float(rotAxis[0]), float(rotAxis[1]))

        # Set axis of projection
        elif entry.startswith("v"):
            self.set_viewaxis([float(num) for num in entry[1:].split(',')])

        # Pentachoron coordinates, side-length 4r
        elif entry == "{3,3,3}":
            r = 2*RADIUS
            return Polytope(([[r/math.sqrt(10),r/math.sqrt(6),r/math.sqrt(3),r],
                              [r/math.sqrt(10),r/math.sqrt(6),r/math.sqrt(3),-r],
                              [r/math.sqrt(10),r/math.sqrt(6),-2*r/math.sqrt(3),0],
                              [r/math.sqrt(10),-r*math.sqrt(3/2),0,0],
                              [-2*r*math.sqrt(2/5),0,0,0]],
                             ((0,1),(0,2),(0,3),(0,4),(1,2),
                              (1,3),(1,4),(2,3),(2,4),(3,4)),
                             [(k, '#000') for k in range(5)]))

        # Tesseract coordinates, side-length 2r
        elif entry == "{4,3,3}":
            r = RADIUS
            return Polytope(([[r,r,r,r],[r,r,r,-r],[r,r,-r,r],[r,r,-r,-r],
                            [r,-r,r,r],[r,-r,r,-r],[r,-r,-r,r],[r,-r,-r,-r],
                            [-r,r,r,r],[-r,r,r,-r],[-r,r,-r,r],[-r,r,-r,-r],
                            [-r,-r,r,r],[-r,-r,r,-r],[-r,-r,-r,r],[-r,-r,-r,-r]],
                            ((0,1),(1,3),(3,2),(2,0),(12,13),(13,15),(15,14),(14,12),
                            (4,5),(5,7),(7,6),(6,4),(8,9),(9,11),(11,10),(10,8),
                            (0,4),(1,5),(2,6),(3,7),(8,12),(9,13),(10,14),(11,15),
                            (0,8),(1,9),(2,10),(3,11),(4,12),(5,13),(6,14),(7,15)),
                             [(k, '#000') for k in range(16)]))

        # Hexadecachoron coordinates, side-length 4r
        elif entry == "{3,3,4}":
            r = 2*RADIUS
            return Polytope(([[r,0,0,0],[-r,0,0,0],[0,r,0,0],[0,-r,0,0],
                              [0,0,r,0],[0,0,-r,0],[0,0,0,r],[0,0,0,-r]],
                             ((0,2),(0,3),(0,4),(0,5),(0,6),(0,7),
                              (1,2),(1,3),(1,4),(1,5),(1,6),(1,7),
                              (2,4),(2,5),(2,6),(2,7),(3,4),(3,5),
                              (3,6),(3,7),(4,6),(4,7),(5,6),(5,7)),
                             [(k, '#000') for k in range(8)]))

        # Schlafli symbol: {p/d}
        elif entry.startswith("{") and entry.endswith("}"):
            if ',' in entry:
                return Polytope(self._schlafli3D(entry[1:-1]))
            else:
                return Polytope(self._schlafli2D(entry[1:-1]))

        # Wythoff symbol: (p q s)
        elif entry.startswith("(") and entry.endswith(")"):
            return Polytope(self._wythoff(entry[1:-1]))

        else:
            raise ValueError

    def _schlafli2D(self, entry):
        # Take 2D Schlafli symbol and return its polar coordinates.
        num = entry.split('/')
        p = int(num[0])
        d = 1
        if len(num) > 1:
             d = int(num[1])
        rs = [RADIUS]*p
        thetas = [(2*k*d*pi/p+pi/2) for k in range(p)]
        phis = [pi/2]*p
        omegas = [pi/2]*p
        edges = [(k,(k+1)%p) for k in range(p)]

        points = []
        for n in range(len(thetas)):
            points.append(convert((rs[n], thetas[n], phis[n], omegas[n]), True))
        colours = [(k, '#000') for k in range(len(thetas))]
        return points, edges, colours

    def _schlafli3D(self, entry):

        # Take 3D Schlafli symbol and return its spherical coordinates and edges.
        # No support for star polyhedra.

        num = entry.split(',')
        p = int(num[0])
        q = int(num[1])
        r = RADIUS
        a = (p-2)*pi/p
        b = 2*pi/q

        # Coordinates of the north pole
        thetas = [0]
        phis = [0]
        edges = []

        # Coordinates of the first ring
        thetas += [k*b for k in range(q)]
        rs = math.sqrt((1-math.cos(a))/(1-math.cos(b)))
        firstPhi = 2*math.acos(rs)
        phis += [firstPhi]*q

        # Edges of the first ring
        edges += [(0,k) for k in range(1,q+1)]
        if p == 3:
            edges += [(k,k+1) for k in range(1,q)]
            edges += [(q,1)]

        if round(firstPhi,4) <= round(math.pi/2,4):
            if round(firstPhi,4) < round(math.pi/2,4):
                # Coordinates of the last ring, excludes octahedron
                thetas += [(k+1/2)*b for k in range(q)]
                phis += [pi-firstPhi]*q

            # Coordinates of the south pole
            thetas += [0]
            phis += [pi]

            # Edges of the last ring
            n = len(thetas)
            edges += [(n-1,n-q+k) for k in range(-1,q-1)]

            if p == 3:    # Icosahedron edges
                edges += [(n-q+k-1,n-q+k) for k in range(0,q-1)]
                edges += [(n-2,q+1)]

            if p == 5:
                # Coordinates of the middle dodecahedron rings
                s = math.sqrt(2*r**2*(1-math.cos(firstPhi)))
                t = math.sqrt(2*s**2*(1-math.cos(a)))
                secondPhi = math.acos(1-t**2/r**2/2)
                r2 = r*math.sin(secondPhi)
                secondTheta = math.acos(1-t**2/r2**2/2)/2

                thetas += [k*b+secondPhi for k in range(q)]
                thetas += [k*b-secondPhi for k in range(q)]
                phis += [secondPhi]*2*q

                thetas += [(k+1/2)*b+secondPhi for k in range(q)]
                thetas += [(k+1/2)*b-secondPhi for k in range(q)]
                phis += [pi-secondPhi]*2*q

                # Edges of the middle dodecahedron rings
                edgeTypes = ((1,7,0), (1,9,1), (4,10,0), (4,12,1),
                             (8,3,0), (14,3,0), (8,8,1), (11,3,0))
                for edge in edgeTypes:
                    edges += [(k%3+edge[0], k+edge[0]+edge[1])
                               for k in range(0+edge[2],3+edge[2])]

            elif n > 2*q:
                # Edges of the middle nondodecahedron rings
                edges += [(k,q+k) for k in range(1,q+1)]
                edges += [(k+1,q+k) for k in range(1,q)]
                edges += [(1,2*q)]

        rs = [RADIUS]*len(thetas)
        omegas = [pi/2]*len(thetas)
        points = []
        for n in range(len(thetas)):
            points.append(convert((rs[n], thetas[n], phis[n], omegas[n]), True))
        colours = [(k, '#000') for k in range(len(thetas))]
        return points, edges, colours

    def _wythoff(self, entry):

        # Take Wythoff symbol and return its spherical coordinates.

        p = int(entry.split()[0])
        q = int(entry.split()[1])
        s = int(entry.split()[2])
        r = RADIUS
        depth = 7
        triangles = []
        points = []
        edges = []
        colours = []

        if s > 2 or q > 3 or (q == 3 and p > 5):
            raise ValueError
        sPhi = math.acos(math.cos(pi/q)/math.sin(pi/p))
        qPhi = math.acos(math.cos(pi/q)*math.cos(pi/p)/
                         math.sin(pi/q)/math.sin(pi/p))

        # Fundamental triangle
        triangles += [[convert(point, True) for point in [
            (r,0,0,pi/2), (r,pi/p,qPhi,pi/2), (r,0,sPhi,pi/2)]]]

        # Reflect each unreflected triangle thrice

        while depth > 0:
            for triangle in reversed(triangles):   # Reversed to avoid loop
                # Find normals to great circles
                op = triangle[0]
                oq = triangle[1]
                os = triangle[2]
                qs = normalize((oq[1]*os[2]-oq[2]*os[1],
                      oq[2]*os[0]-oq[0]*os[2],
                      oq[0]*os[1]-oq[1]*os[0]))
                ps = normalize((op[1]*os[2]-op[2]*os[1],
                      op[2]*os[0]-op[0]*os[2],
                      op[0]*os[1]-op[1]*os[0]))
                pq = normalize((op[1]*oq[2]-op[2]*oq[1],
                      op[2]*oq[0]-op[0]*oq[2],
                      op[0]*oq[1]-op[1]*oq[0]))

                # Reflect points across great circles
                dp = sum([qs[t]*oq[t] for t in range(3)])
                dq = sum([ps[t]*os[t] for t in range(3)])
                ds = sum([pq[t]*op[t] for t in range(3)])
                kp = sum([dp - op[t]*qs[t] for t in range(3)])
                kq = sum([dq - oq[t]*ps[t] for t in range(3)])
                ks = sum([ds - os[t]*pq[t] for t in range(3)])
                newp = tuple([op[t] + 2*kp*qs[t] for t in range(3)] + [0])
                newq = tuple([oq[t] + 2*kq*ps[t] for t in range(3)] + [0])
                news = tuple([os[t] + 2*ks*pq[t] for t in range(3)] + [0])

                # Make new triangles from results and remove old triangle
                triangles.append([newp, oq, os])
                triangles.append([op, newq, os])
                triangles.append([op, oq, news])
                points += triangle
                triangles.remove(triangle)
            depth -= 1

        # Display points according to type of connection
        n = 2
        while n < len(points):
            edges += [(n-2,n-1), (n-2,n), (n-1,n)]
            colours += [(n-2, '#F00'), (n-1, '#000'), (n, '#00F')]
            n += 3
        return points, edges, colours

    def _render(self):
        # Clear the canvas, center, and display Polytope object.
        self.delete(tk.ALL)
        if self.currPolytope.get_edges():
            w = self.winfo_width()//2
            h = self.winfo_height()//2
            points = [(-point[0]+w, point[1]+h) for point in
                      self._view(self.currPolytope.get_points())]
            edges = self.currPolytope.get_edges()
            colours = self.currPolytope.get_colours()
            for edge in edges:
                self.create_line(points[edge[0]], points[edge[1]],
                                 fill='#000', width=5)
                self.create_line(points[edge[0]], points[edge[1]],
                                 fill='#CCC', width=3)
            for colour in colours:
                self.create_oval([p-5 for p in points[colour[0]]],
                                 [p+5 for p in points[colour[0]]],
                                 fill=colour[1])

    def _reset(self):
        self.delete(tk.ALL)
        self._zoom = ZOOM
        self._distance = DISTANCE
        self.set_rotaxis('xw')
        self.set_viewaxis([0, 0, 0])



class Polytope():

    """
    Drawing class that stores polytope coordinates and manages rotations.

    Public methods:
    get_points
    get_edges
    get_colours
    set_rotaxis
    rotate
    """

    def __init__(self, data):
        """Construct Polytope class."""
        if data:
            self._number = len(data[0])
            self._points = data[0]
            self._edges = data[1]
            self._colours = data[2]
        elif not data:
            self._number = 0
            self._points = []
            self._edges = []
            self._colours = []

    def get_points(self):
        """Return a list of points of the polytope."""
        return self._points

    def get_edges(self):
        """Return a list of edges of the polytope."""
        return self._edges

    def get_colours(self):
        """Return a list of colours of the polytope."""
        return self._colours

    def set_rotaxis(self, i, j):
        self._axis_i = i
        self._axis_j = j

    def rotate(self, rotAngle):
        """
        Rotate the current polytope by rotAngle about the plane
        defined by i and j, where i and j are quadruples.
        """
        i = self._axis_i
        j = self._axis_j
        cos = math.cos(rotAngle)
        sin = math.sin(rotAngle)
        n = 0
        for n in range(self._number):
            p = self._points[n]
            r = sum([p[t]*i[t] for t in range(4)])
            s = sum([p[t]*j[t] for t in range(4)])
            I = [i[t]*r+j[t]*s for t in range(4)]
            ip = [p[t]-I[t] for t in range(4)]
            if ip != [0,0,0,0]:    # If I = P, then there is no rotation
                iq = [ip[1]*(i[2]*j[3]-i[3]*j[2]) - ip[2]*(i[1]*j[3]-i[3]*j[1]) + ip[3]*(i[1]*j[2]-i[2]*j[1]),
                      -ip[0]*(i[2]*j[3]-i[3]*j[2]) + ip[2]*(i[0]*j[3]-i[3]*j[0]) - ip[3]*(i[0]*j[2]-i[2]*j[0]),
                      ip[0]*(i[1]*j[3]-i[3]*j[1]) - ip[1]*(i[0]*j[3]-i[3]*j[0]) + ip[3]*(i[0]*j[1]-i[1]*j[0]),
                      -ip[0]*(i[1]*j[2]-i[2]*j[1]) + ip[1]*(i[0]*j[2]-i[2]*j[0]) - ip[2]*(i[0]*j[1]-i[1]*j[0])]
                iq = normalize(iq, ip)
                self._points[n] = [ip[t]*cos + iq[t]*sin + I[t] for t in range(4)]


root = tk.Tk()
main = Main(root)
