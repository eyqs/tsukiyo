"""
Polyhedron Visualizer v0.30

This script displays the regular polyhedra, except the dodecahedron.
Distance, radius, rotation axis, and projection axis can now be changed.
"""

import tkinter as tk
import tkinter.ttk as ttk
import math

TITLE = "Polyhedron Visualizer v0.30"
DESCRIPTION = "\nThis script displays the regular polyhedra."
WIDTH = 400
HEIGHT = 400
RADIUS = 100
DISTANCE = 5
ROTANGLE = math.pi/12
BGCOLOUR = "#CCC"
DELAY = 28    # 28 ms per pi/12 rotation = 3 rotations every 2 seconds

def normalize(points, vector=[1]):
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
    isDrawing

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
        self._leftBtn = tk.PhotoImage(file="leftButtonTwentyFour.gif")
        self._rightBtn = tk.PhotoImage(file="rightButtonTwentyFour.gif")

        style = ttk.Style()
        style.configure("TFrame", background=BGCOLOUR)
        style.configure("TLabel", background=BGCOLOUR)
        style.configure("TButton", background=BGCOLOUR)

        titleLabel = ttk.Label(self, text=TITLE)
        titleLabel.pack()
        self.canvas = Canvas(self)
        self.canvas.pack(fill=tk.BOTH, padx=10, expand=1)
        guiFrame = ttk.Frame(self)
        guiFrame.columnconfigure(0, weight=1)
        guiFrame.pack(fill=tk.X, padx=10, pady=10, expand=0)

        # grid guiFrame widgets: 3 rows, 8 columns
        self.statusText = tk.StringVar()
        self.statusLabel = ttk.Label(
            guiFrame, textvariable=self.statusText, foreground="red")
        self.statusLabel.grid(row=0, column=0, columnspan=4, sticky=tk.W)
        self.inputText = tk.StringVar()
        self._inputBox = ttk.Entry(guiFrame, textvariable=self.inputText)
        self._inputBox.bind('<Key-Return>', self.canvas.take_input)
        # No padding on left, 10px padding on right
        self._inputBox.grid(row=1, column=0, columnspan=4,
                            padx=(0,10), sticky=tk.E+tk.W)
        self._inputBox.focus()

        viewLabel = ttk.Label(guiFrame, text="Views: ")
        viewLabel.grid(row=2, column=0, sticky=tk.E)
        xViewBtn = ttk.Button(guiFrame, text="x", width=2, command=lambda:
                              self.canvas.new_view([0, math.pi/2]))
        xViewBtn.bind("<Key-Return>", lambda event:
                      self.canvas.new_view([0, math.pi/2]))
        xViewBtn.grid(row=2, column=1)
        yViewBtn = ttk.Button(guiFrame, text="y", width=2, command=lambda:
                              self.canvas.new_view([math.pi/2, math.pi/2]))
        yViewBtn.bind("<Key-Return>", lambda event:
                      self.canvas.new_view([math.pi/2, math.pi/2]))
        yViewBtn.grid(row=2, column=2)
        zViewBtn = ttk.Button(guiFrame, text="z", width=2, command=lambda:
                              self.canvas.new_view([0,0]))
        zViewBtn.bind("<Key-Return>",lambda event:
                      self.canvas.new_view([0,0]))
        zViewBtn.grid(row=2, column=3, padx=(0,10))

        leftRotBtn = ttk.Button(guiFrame, image=self._leftBtn,
                                 command=lambda: self.canvas.rotate(0))
        leftRotBtn.bind("<Button-1>", lambda event: self._mouse_down(0))
        leftRotBtn.bind("<ButtonRelease-1>", self._mouse_up)
        leftRotBtn.bind("<Key-Return>", lambda event: self.canvas.rotate(0))
        leftRotBtn.grid(row=0, column=4, rowspan=2, sticky=tk.E)
        rightRotBtn = ttk.Button(guiFrame, image=self._rightBtn,
                                command=lambda: self.canvas.rotate(1))
        rightRotBtn.bind("<Button-1>", lambda event: self._mouse_down(1))
        rightRotBtn.bind("<ButtonRelease-1>", self._mouse_up)
        rightRotBtn.bind("<Key-Return>", lambda event: self.canvas.rotate(1))
        rightRotBtn.grid(row=0, column=5, rowspan=2, columnspan=2, sticky=tk.W)

        rotateLabel = ttk.Label(guiFrame, text="Rotate: ")
        rotateLabel.grid(row=2, column=4, sticky=tk.E)
        xRotBtn = ttk.Button(guiFrame, text="x", width=2,
                             command=lambda: self.canvas.new_axis('x'))
        xRotBtn.bind("<Key-Return>", lambda event: self.canvas.new_axis('x'))
        xRotBtn.grid(row=2, column=5)
        yRotBtn = ttk.Button(guiFrame, text="y", width=2,
                             command=lambda: self.canvas.new_axis('y'))
        yRotBtn.bind("<Key-Return>", lambda event: self.canvas.new_axis('y'))
        yRotBtn.grid(row=2, column=6)
        zRotBtn = ttk.Button(guiFrame, text="z", width=2,
                             command=lambda: self.canvas.new_axis('z'))
        zRotBtn.bind("<Key-Return>", lambda event: self.canvas.new_axis('z'))
        zRotBtn.grid(row=2, column=7)

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
            messageText = ("Click the buttons to rotate the "
                           "polyhedron or change the view.")
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

        # Set all focus on the pop up, stop mainloop in main
        popUpFrame.grab_set()
        popUpButton.focus()
        self.wait_window(popUpFrame)

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
    new_view
    new_axis
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

    def new_view(self, viewAxis):
        """Change the current view. Takes spherical coordinates of the axis."""
        #Check that inputs satisfy restrictions
        while viewAxis[1] > math.pi or viewAxis[1] < 0:
            viewAxis[1] = 2*math.pi - viewAxis[1]
        while viewAxis[0] > 2*math.pi:
            viewAxis[0] -= 2*math.pi
        while viewAxis[0] < 0:
            viewAxis[0] += 2*math.pi
        self._viewAxis = viewAxis
        self._render()

    def _view(self, points):
        """Return a Cartesian double depending on the viewAxis."""
        # Formula derived on 14/09/27
        xa = math.sin(self._viewAxis[1])*math.cos(self._viewAxis[0])
        ya = math.sin(self._viewAxis[1])*math.sin(self._viewAxis[0])
        za = math.cos(self._viewAxis[1])
        d = self._distance*self._radius
        q = (self._radius*xa, self._radius*ya, self._radius*za)
        if self._viewAxis[1] != 0:
            w = normalize([-ya, xa, 0])    # Simplified cross product calculations
            h = normalize([xa*za, ya*za, -ya*ya - xa*xa])
        num = len(points)
        count = 0
        result = []
        while count < num:
            x = points[count][0]
            y = points[count][1]
            z = points[count][2]
            l = normalize([x - d*xa, y - d*ya, z - d*za])
            t = (self._radius - d)/(l[0]*xa + l[1]*ya + l[2]*za)
            i = (d*xa + t*l[0], d*ya + t*l[1], d*za + t*l[2])
            if self._viewAxis[1] == 0:
                n = i[0] - q[0]
                m = i[1] - q[1]
            else:
                m = (i[2] - q[2])/h[2]
                if abs(w[0]) > 0:
                    n = (i[0] - q[0] - (i[2] - q[2])*h[0]/h[2])/w[0]
                else:
                    n = (i[1] - q[1] - (i[2] - q[2])*h[1]/h[2])/w[1]
            result.append((n, m))
            count += 1
        return result
        
    def new_axis(self, rotAxis):
        if rotAxis == "x":
            self.currPolytope.set_axis(0, math.pi/2)
        elif rotAxis == 'y':
            self.currPolytope.set_axis(math.pi/2, math.pi/2)
        elif rotAxis == 'z':
            self.currPolytope.set_axis(0, 0)
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

        # Set axis of rotation
        elif entry.startswith("r"):
            rotAxis = entry[1:].split(',')
            self.currPolytope.set_axis(float(rotAxis[0]), float(rotAxis[1]))

        # Set axis of projection
        elif entry.startswith("v"):
            self.new_view([float(num) for num in entry[1:].split(',')])

        # Set polyhedron radius
        elif entry.startswith("s"):
            self._radius = float(entry[1:])

        # Set projection distance
        elif entry.startswith("d"):
            if float(entry[1:]) == 1:
                self.parent.set_status('badinput')
            else:
                self._distance = float(entry[1:])

        # Schlafli symbol: {p/d}
        elif entry.startswith("{") and entry.endswith("}"):
            if ',' in entry:
                return Polytope(self._schlafli3D(entry[1:-1]))
            else:
                return Polytope(self._schlafli2D(entry[1:-1]))

        else:
            raise ValueError

    def _schlafli2D(self, entry):
        # Take 2D Schlafli symbol and return its spherical coordinates.
        num = entry.split('/')
        p = int(num[0])
        d = 1
        if len(num) > 1:
             d = int(num[1])
        r = RADIUS
        rs = [r]*p
        thetas = [(2*k*d*math.pi/p+math.pi/2) for k in range(p)]
        phis = [math.pi/2]*p
        edges = [(k-1,k) for k in range(p)]
        return rs, thetas, phis, edges

    def _schlafli3D(self, entry):

        # Take 3D Schlafli symbol and return spherical coordinates and edges.
        # Currently only returns coordinates of the first ring.
        # No support for star polyhedra.
        # Formula derived from 14/09/18 to 14/09/21

        num = entry.split(',')
        p = int(num[0])
        q = int(num[1])
        r = self._radius
        ap = math.pi*(1-2/p)
        aq = 2*math.pi/q

        if p == 5 and q == 3:
            self.parent.set_status('badinput')
            return []

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
                # Coordinates of the last ring
                rs += [r]*q
                thetas += [(k+1/2)*aq for k in range(q)]
                phis += [math.pi-firstPhi]*q

            # Coordinates of the south pole
            rs += [r]
            thetas += [0]
            phis += [math.pi]

            # Edges of the last ring
            n = len(rs)
            edges += [(n-1,n-q+k) for k in range(-1,q-1)]
            if p == 3:
                edges += [(n-q+k-1,n-q+k) for k in range(0,q-1)]
                edges += [(n-2,q+1)]

            if n > 2*q:
                # Edges of the middle rings
                edges += [(k,q+k) for k in range(1,q+1)]
                edges += [(k+1,q+k) for k in range(1,q)]
                edges += [(1,2*q)]
        return rs, thetas, phis, edges

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
                                 fill='#CCC', width=5)

    def _reset(self):
        self.delete(tk.ALL)
        self._radius = RADIUS
        self._distance = DISTANCE
        self.new_axis('x')
        self.new_view([0,0])



class Polytope():

    """
    Drawing class that stores polytope coordinates and manages rotations.

    Public methods:
    get_points
    get_axes
    get_edges
    set_axis
    rotate
    """

    def __init__(self, data):
        """Construct Polytope class."""
        if data:
            self._number = len(data[0])
            self._rs = data[0]
            self._thetas = data[1]
            self._phis = data[2]
            self._edges = data[3]
            self._check_restrictions()
        elif not data:
            self._number = 0
            self._rs = []
            self._thetas = []
            self._phis = []
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

    def _check_restrictions(self):
        """Check to make spherical coordinates meet restrictions."""
        n = 0
        while n < self._number:
            if self._phis[n] > math.pi or self._phis[n] < 0:
                self._phis[n] = 2*math.pi - self._phis[n]
            if self._thetas[n] > 2*math.pi:
                self._thetas[n] -= 2*math.pi
            elif self._thetas[n] < 0:
                self._thetas[n] += 2*math.pi
            n += 1

    def set_axis(self, theta, phi):
        self._axis_theta = theta
        self._axis_phi = phi

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
            o = (axis[0]*t, axis[1]*t, axis[2]*t)
            op = (p[0]-o[0], p[1]-o[1], p[2]-o[2])
            if op != (0,0,0):                
                oq = (axis[1]*op[2] - axis[2]*op[1],
                      axis[2]*op[0] - axis[0]*op[2],
                      axis[0]*op[1] - axis[1]*op[0])
                oq = normalize(oq, op)
                cos = math.cos(rotAngle)
                sin = math.sin(rotAngle)
                rotP = (op[0]*cos + oq[0]*sin + o[0],
                        op[1]*cos + oq[1]*sin + o[1],
                        op[2]*cos + oq[2]*sin + o[2])
                self._thetas[n] = math.atan2(rotP[1],rotP[0])
                # math.floor because of floating point issues
                self._phis[n] = abs(math.acos(math.floor(rotP[2])/self._rs[n]))
            n += 1
        self._check_restrictions()



root = tk.Tk()
main = Main(root)

