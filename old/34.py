"""
Polychoron Visualizer v0.34

This script displays the regular polyhedra and the hypercube.
Pressing the zoom or d buttons changes the object size and viewpoint distance.
The viewscreen is a constant value away from the viewpoint, RETINA.
RADIUS is now also a constant, and size is fully controled by canvas._zoom.
"""

import tkinter as tk
import tkinter.ttk as ttk
import math

TITLE = "Polychoron Visualizer v0.34"
DESCRIPTION = "\nThis script displays the regular polyhedra and the hypercube."
pi = math.pi
WIDTH = 500
HEIGHT = 450
BGCOLOUR = "#CCC"

RADIUS = 100
ZOOM = 50
DISTANCE = 5
RETINA = 10
CHANGE = 5    # 5 pixels change in radius and 0.5r change in distance
DELAY = 28    # 28 ms per pi/12 rotation = 3 rotations every 2 seconds
ROTANGLE = pi/12
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
        _wViewBtn = ttk.Button(_guiFrame, text="w", width=2, state=tk.DISABLED)
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
        _xyRotBtn = ttk.Button(_guiFrame, text="xy", width=3, state=tk.DISABLED)
        _xyRotBtn.grid(row=3, column=8)
        _yzRotBtn = ttk.Button(_guiFrame, text="yz", width=3, state=tk.DISABLED)
        _yzRotBtn.grid(row=3, column=9)
        _xzRotBtn = ttk.Button(_guiFrame, text="xz", width=3, state=tk.DISABLED)
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
                            "polyhedron or change the view.")
            buttonText = "Dismiss"
            frameWidth = 400
            frameHeight = 120

        # Create pop-up window, each with title, message, and close button
        _popUpFrame = tk.Toplevel(self.parent, background=BGCOLOUR)
        _popUpFrame.title(titleText)
        _popUpMessage = tk.Message(_popUpFrame, text=messageText,
                                   width=_frameWidth, background=BGCOLOUR)
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
        while viewAxis[2] > pi or viewAxis[2] < 0:
            viewAxis[2] = 2*pi - viewAxis[2]
        while viewAxis[1] > pi or viewAxis[1] < 0:
            viewAxis[1] = 2*pi - viewAxis[1]
        while viewAxis[0] > 2*pi:
            viewAxis[0] -= 2*pi
        while viewAxis[0] < 0:
            viewAxis[0] += 2*pi
        self._viewAxis = viewAxis
        self._render()

    def _view(self, points):
        """Return a Cartesian double depending on the viewAxis."""
        # Formula derived on 14/10/17
        st = math.sin(self._viewAxis[0])
        ct = math.cos(self._viewAxis[0])
        sp = math.sin(self._viewAxis[1])
        cp = math.cos(self._viewAxis[1])
        u = (sp*ct, sp*st, cp)
        w = (-st, ct, 0)
        h = (cp*ct, cp*st, -sp)
        d = self._distance*RADIUS
        f = d + RETINA
        q = (f*u[0], f*u[1], f*u[2])
        l = f*(u[0]**2 + u[1]**2 + u[2]**2)
        num = len(points)
        count = 0
        result = []
        while count < num:
            x = points[count][0]
            y = points[count][1]
            z = points[count][2]
            t = (l-x*u[0]-y*u[1]-z*u[2])/(d-x*u[0]-y*u[1]-z*u[2])
            if abs(self._viewAxis[1]) < EPSILON:
                if (abs(self._viewAxis[0] - pi/2) < EPSILON or
                    abs(self._viewAxis[0] - 3*pi/2) < EPSILON):
                    n = (t*x-x)*st
                    m = (y-t*y)*st
                else:
                    n = ct*(y-t*y)-st*(x-t*x)
                    m = (n*st+x-t*x)/ct
            else:
                m = (t*z-z-(d*t-f)*cp)/sp
                if (abs(self._viewAxis[0] - pi/2) < EPSILON or
                    abs(self._viewAxis[0] - 3*pi/2) < EPSILON):
                    n = (t*x-x)*st
                else:
                    n = (y-t*y+(d*t-f)*sp*st-m*cp*st)/ct
            result.append((n*self._zoom, m*self._zoom))
            count += 1
        return result

    def set_rotaxis(self, rotAxis):
        """Change the current rotation axis-plane."""
        if rotAxis == "xw":
            self.currPolytope.set_rotaxis(0, pi/2, pi/2)
        elif rotAxis == 'yw':
            self.currPolytope.set_rotaxis(pi/2, pi/2, pi/2)
        elif rotAxis == 'zw':
            self.currPolytope.set_rotaxis(0, 0, pi/2)
        else:
            pass
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
        elif entry == "quit" or entry == "exit" or entry == "close":
            self.parent.close()

        # Set rotation axis
        # elif entry.startswith("r"):
        #     rotAxis = entry[1:].split(',')
        #     self.currPolytope.set_rotaxis(float(rotAxis[0]), float(rotAxis[1]))

        # Set axis of projection
        # elif entry.startswith("v"):
        #     self.set_viewaxis([float(num) for num in entry[1:].split(',')])

        # Schlafli symbol: {p/d}
        elif entry.startswith("{") and entry.endswith("}"):
            if ',' in entry:
                return Polytope(self._schlafli3D(entry[1:-1]))
            else:
                return Polytope(self._schlafli2D(entry[1:-1]))

        else:
            raise ValueError

    def _schlafli2D(self, entry):
        # Take 2D Schlafli symbol and return its hyperspherical coordinates.
        num = entry.split('/')
        p = int(num[0])
        d = 1
        if len(num) > 1:
             d = int(num[1])
        rs = [RADIUS]*p
        thetas = [(2*k*d*pi/p+pi/2) for k in range(p)]
        phis = [pi/2]*p
        omegas = [pi/2]*p
        edges = [(k-1,k) for k in range(p)]
        return rs, thetas, phis, omegas, edges

    def _schlafli3D(self, entry):

        # Take 3D Schlafli symbol, return hyperspherical coordinates and edges.
        # No support for star polyhedra.

        num = entry.split(',')
        p = int(num[0])
        q = int(num[1])
        r = RADIUS
        ap = pi*(1-2/p)
        aq = 2*pi/q

        # Coordinates of the north pole
        rs = [r]
        thetas = [0]
        phis = [0]
        edges = []

        # Coordinates of the first ring
        rs += [r]*q
        thetas += [k*aq for k in range(q)]
        firstPhi = 2*math.acos(math.sqrt((1-math.cos(ap))/(1-math.cos(aq))))
        phis += [firstPhi]*q

        # Edges of the first ring
        edges += [(0,k) for k in range(1,q+1)]
        if p == 3:
            edges += [(k,k+1) for k in range(1,q)]
            edges += [(q,1)]

        if round(firstPhi,4) <= round(math.pi/2,4):    # Rounding for float errors
            if round(firstPhi,4) < round(math.pi/2,4):
                # Coordinates of the last ring, excludes octahedron
                rs += [r]*q
                thetas += [(k+1/2)*aq for k in range(q)]
                phis += [pi-firstPhi]*q

            # Coordinates of the south pole
            rs += [r]
            thetas += [0]
            phis += [pi]

            # Edges of the last ring
            n = len(rs)
            edges += [(n-1,n-q+k) for k in range(-1,q-1)]

            if p == 3:    # Icosahedron edges
                edges += [(n-q+k-1,n-q+k) for k in range(0,q-1)]
                edges += [(n-2,q+1)]

            if p == 5:
                # Coordinates of the middle dodecahedron rings
                s = math.sqrt(2*r**2*(1-math.cos(firstPhi)))
                t = math.sqrt(2*s**2*(1-math.cos(ap)))
                secondPhi = math.acos(1-(t/r)**2/2)
                r2 = r*math.sin(secondPhi)
                a = math.acos(1-(t/r2)**2/2)/2
                b = math.acos(1-(s/r2)**2/2)

                rs += [r]*2*q
                thetas += [k*aq+a for k in range(q)]
                thetas += [k*aq+a+b for k in range(q)]
                phis += [secondPhi]*2*q

                rs += [r]*2*q
                thetas += [(k+1/2)*aq+a for k in range(q)]
                thetas += [(k+1/2)*aq+a+b for k in range(q)]
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

        omegas = [pi/2]*len(rs)
        return rs, thetas, phis, omegas, edges

    def _render(self):
        # Clear the canvas, center, and display Polytope object.
        self.delete(tk.ALL)
        if self.currPolytope.get_edges():
            w = self.winfo_width()//2
            h = self.winfo_height()//2
            points = [(point[0]+w, point[1]+h) for point in
                      self._view(self.currPolytope.get_points())]
            edges = self.currPolytope.get_edges()
            axes = [(point[0]+w, point[1]+h) for point in
                      self._view(self.currPolytope.get_axes())]
            self.create_line(axes[0], axes[1], fill='#F00', width=5)
            for edge in edges:
                self.create_line(points[edge[0]], points[edge[1]],
                                 fill='#000', width=5)
                self.create_line(points[edge[0]], points[edge[1]],
                                 fill='#CCC', width=3)

    def _reset(self):
        self.delete(tk.ALL)
        self._zoom = ZOOM
        self._distance = DISTANCE
        self.set_rotaxis('xw')
        self.set_viewaxis([0, 0, pi/2])



class Polytope():

    """
    Drawing class that stores polytope coordinates and manages rotations.

    Public methods:
    get_points
    get_axes
    get_edges
    set_rotaxis
    rotate
    """

    def __init__(self, data):
        """Construct Polytope class."""
        if data:
            self._number = len(data[0])
            self._rs = data[0]
            self._thetas = data[1]
            self._phis = data[2]
            self._omegas = data[3]
            self._edges = data[4]
            self._check_restrictions()
        elif not data:
            self._number = 0
            self._rs = []
            self._thetas = []
            self._phis = []
            self._omegas = []
            self._edges = []

    def get_points(self):
        """
        Convert spherical coordinates (three separate lists)
        to return Cartesian coordinates (one list of triples).
        """
        points = []
        n = 0
        while n < self._number:
            h = self._rs[n]*math.sin(self._phis[n])
            points.append((h*math.cos(self._thetas[n]),
                           h*math.sin(self._thetas[n]),
                           self._rs[n]*math.cos(self._phis[n])))
            n += 1
        return points

    def get_axes(self):
        """Return coordinates of endpoints of rotation axis."""
        axis = (math.sin(self._axis_phi)*math.cos(self._axis_theta),
                math.sin(self._axis_phi)*math.sin(self._axis_theta),
                math.cos(self._axis_phi))
        axes = ([1.5*self._rs[0]*ax for ax in axis],
                [-1.5*self._rs[0]*ax for ax in axis])
        return axes

    def get_edges(self):
        """Return a list of edges of the polytope."""
        return self._edges

    def set_rotaxis(self, theta, phi, omega):
        self._axis_theta = theta
        self._axis_phi = phi
        self._axis_omega = omega

    def rotate(self, rotAngle):
        """
        Rotate the current polytope by rotAngle about the line
        (r, theta, phi), where theta and phi are constants.
        """
        n = 0
        while n < self._number:
            # Formula derived on 14/09/23
            axis = (math.sin(self._axis_phi)*math.cos(self._axis_theta),
                    math.sin(self._axis_phi)*math.sin(self._axis_theta),
                    math.cos(self._axis_phi))
            p = (self._rs[n]*math.sin(self._phis[n])*math.cos(self._thetas[n]),
                 self._rs[n]*math.sin(self._phis[n])*math.sin(self._thetas[n]),
                 self._rs[n]*math.cos(self._phis[n]))
            d = axis[0]*p[0] + axis[1]*p[1] + axis[2]*p[2]
            t = d/(axis[0]**2 + axis[1]**2 + axis[2]**2)
            i = (axis[0]*t, axis[1]*t, axis[2]*t)
            ip = (p[0]-i[0], p[1]-i[1], p[2]-i[2])
            if ip != (0,0,0):
                iq = (axis[1]*ip[2] - axis[2]*ip[1],
                      axis[2]*ip[0] - axis[0]*ip[2],
                      axis[0]*ip[1] - axis[1]*ip[0])
                iq = normalize(iq, ip)
                cos = math.cos(rotAngle)
                sin = math.sin(rotAngle)
                rotP = (ip[0]*cos + iq[0]*sin + i[0],
                        ip[1]*cos + iq[1]*sin + i[1],
                        ip[2]*cos + iq[2]*sin + i[2])
                self._thetas[n] = math.atan2(rotP[1],rotP[0])
                # math.floor because of floating point issues
                self._phis[n] = abs(math.acos(math.floor(rotP[2])/self._rs[n]))
            n += 1
        self._check_restrictions()

    def _check_restrictions(self):
        """Check to make spherical coordinates meet restrictions."""
        n = 0
        while n < self._number:
            if self._omegas[n] > pi or self._omegas[n] < 0:
                self._omegas[n] = 2*pi - self._omegas[n]
            if self._phis[n] > pi or self._phis[n] < 0:
                self._phis[n] = 2*pi - self._phis[n]
            if self._thetas[n] > 2*pi:
                self._thetas[n] -= 2*pi
            elif self._thetas[n] < 0:
                self._thetas[n] += 2*pi
            n += 1



root = tk.Tk()
main = Main(root)
