"""
Polyhedron Visualizer v0.27

This script displays the regular polyhedra, except the dodecahedron.
Views from the x and y axes can now be selected from a finite distance.
"""

import tkinter as tk
import tkinter.ttk as ttk
import math

TITLE = "Polyhedron Visualizer v0.27"
DESCRIPTION = "\nThis script displays the regular polyhedra."
WIDTH = 400
HEIGHT = 400
RADIUS = 100
DISTANCE = 500
ROTANGLE = math.pi/12
BGCOLOUR = "#CCC"
DELAY = 28    # 28 ms per pi/12 rotation = 3 rotations every 2 seconds
GODMODE = False

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
    self.statusLabel
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
        self._leftBtn = tk.PhotoImage(file="leftButtonTwentyFour.gif")
        self._rightBtn = tk.PhotoImage(file="rightButtonTwentyFour.gif")

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
            messageText = ("Click the buttons to rotate the "
                           "polygon or change the viewAxis.")
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
        self.currPolytope = Polytope([[], [], [], []])
        self.new_view([0,0])
        self.new_axis('x')

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

    def new_view(self, viewAxis, d=DISTANCE):
        """Change the current view. Takes spherical coordinates of the axis."""
        #Check that inputs satisfy restrictions
        while viewAxis[1] > math.pi or viewAxis[1] < 0:
            viewAxis[1] = 2*math.pi - viewAxis[1]
        while viewAxis[0] > 2*math.pi:
            viewAxis[0] -= 2*math.pi
        while viewAxis[0] < 0:
            viewAxis[0] += 2*math.pi
        viewAxis.append(d)
        self._viewAxis = viewAxis
        self._render()

    def view(self, points):

        """Return a Cartesian double depending on the viewAxis."""

        # View axis at phi = 0 or phi = pi
        if abs(self._viewAxis[1]) < 0.1:
            return [(point[0], point[1]) for point in points]

        # Formula derived on 14/09/27
        xa = math.sin(self._viewAxis[1])*math.cos(self._viewAxis[0])
        ya = math.sin(self._viewAxis[1])*math.sin(self._viewAxis[0])
        za = math.cos(self._viewAxis[1])

        d = self._viewAxis[2]
        q = (RADIUS*xa, RADIUS*ya, RADIUS*za)
        w = (-ya, xa, 0)    # Simplified cross product calculations
        h = (xa*za, ya*za, -ya*ya - xa*xa)
        num = len(points)
        count = 0
        result = []
        while count < num:
            x = points[count][0]
            y = points[count][1]
            z = points[count][2]
            l = (x - d*xa, y - d*ya, z - d*za)
            e = math.sqrt(l[0]**2 + l[1]**2 + l[2]**2)
            l = [j/e for j in l]
            t = (RADIUS - d)/(l[0]*xa + l[1]*ya + l[2]*za)
            i = (d*xa + t*l[0], d*ya + t*l[1], d*za + t*l[2])

            # Must account for all possible cases when solving equations
            p = (i[0] - q[0], i[1] - q[1], i[2] - q[2])
            n = p[1]*xa + p[0]*ya
            m = p[2]
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
                self.new_axis('z')
        except ValueError:
            self.parent.set_status('badinput')
        self._render()
        self.parent.inputText.set('')


    def _translate(self, entry):

        # Translate text input to return a Polytope object.

        # Clear canvas, return empty polytope for _render to process
        if entry == '' or entry == "clear":
            self.delete(tk.ALL)
            return Polytope([])

        # Toggle drawing, return empty polytope that allows drawing
        # elif entry == "draw":
        #     self.parent.set_status('draw')
        #     return Polytope([], isDrawn=self.parent.isDrawing)

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

        # Schlafli symbol: {p/d}
        elif entry.startswith("{") and entry.endswith("}"):
            if ',' in entry:
                return Polytope(self._schlafli3D(entry[1:-1]))
            # return Polytope(self._schlafli(entry[1:-1]))

        # (x,y) is a point, (xn,yn) vectors: vx,y;x1,y1;x2,y2; ... xn,yn
        # elif entry.startswith("v"):
        #    return Polytope(self._vector_list(entry[1:]))

        else:
            raise ValueError

    # def _schlafli(self, entry):
    #     # Take 2D Schlafli symbol and return its spherical coordinates.
    #     num = entry.split('/')
    #     p = int(num[0])
    #     d = 1
    #     if len(num) > 1:
    #         d = int(num[1])
    #     r = RADIUS
    #     rs = [r]*p
    #     thetas = [(2*k*d*math.pi/p+math.pi/2) for k in range(p)]
    #     phis = [math.pi/2]*p
    #     return rs, thetas, phis

    def _schlafli3D(self, entry):

        # Take 3D Schlafli symbol and return spherical coordinates and edges.
        # Currently only returns coordinates of the first ring.
        # No support for star polyhedra.
        # Formula derived from 14/09/18 to 14/09/21

        num = entry.split(',')
        p = int(num[0])
        q = int(num[1])
        r = RADIUS
        ap = math.pi*(1-2/p)
        aq = 2*math.pi/q

        if p == 5 and q == 3:
            self.parent.set_status('badinput')
            return([])

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

    # def _vector_list(self, vectors):
    #     # Take list of Cartesian vectors and
    #     # return its corresponding list of points.
    #     vectors = vectors.split(';')    # 'x1,y1;x2,y2' -> ('x1,y1'), ('x2,y2')
    #     point = [0,0]
    #     points = []
    #     count = 0
    #     while count < len(vectors):
    #         point[0] += float(vectors[count].split(',')[0])
    #         point[1] += float(vectors[count].split(',')[1])
    #         points.append((point[0],point[1]))    # ('x1,y1') -> (x0+x,y0+y)
    #         count += 1
    #     return(points)

    def _render(self):
        # Clear the canvas, center, and display Polytope object.
        self.delete(tk.ALL)
        if self.currPolytope.get_edges():
            w = self.winfo_width()//2
            h = self.winfo_height()//2
            points = [(point[0]+w, point[1]+h) for point in
                      self.view(self.currPolytope.get_points())]
            edges = self.currPolytope.get_edges()
            for edge in edges:
                self.create_line(points[edge[0]], points[edge[1]],
                                 fill='#000', width=10)
                self.create_line(points[edge[0]], points[edge[1]],
                                 fill='#CCC', width=5)



class Polytope():

    """
    Drawing class that stores polytope coordinates and manages rotations.

    Public methods:
    add_point
    get_points
    get_edges
    set_axis
    rotate

    Instance variables:
    self.isDrawn
    """

    def __init__(self, data, isDrawn=False):
        """Construct Polytope class."""
        self.isDrawn = isDrawn
        if data:
            self._number = len(data[0])
            self._rs = data[0]
            self._thetas = data[1]
            self._phis = data[2]
            self._edges = data[3]
            self.check_restrictions()
        elif not data:
            self._number = 0
            self._rs = []
            self._thetas = []
            self._phis = []
            self._edges = []

    # def add_point(self, point):
    #     """Add a point to a drawn shape."""
    #     if self.isDrawn:
    #         self._vertices.append(point)

    def get_points(self):
        """
        Convert spherical coordinates (three separate lists)
        to return Cartesian coordinates (one list of triples).
        """
        points = []
        n = 0
        while n < self._number:
            # (r,t,p) -> (r sin(p)cos(t), r sin(p)sin(t), r cos(p))
            h = self._rs[n]*math.sin(self._phis[n])
            points.append((int(h*math.cos(self._thetas[n])),
                           int(h*math.sin(self._thetas[n])),
                           int(self._rs[n]*math.cos(self._phis[n]))))
            n += 1
        return points

    def get_edges(self):
        """Return a list of edges of the polytope."""
        return self._edges

    def check_restrictions(self):
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
            oq = (axis[1]*op[2] - axis[2]*op[1],
                  axis[2]*op[0] - axis[0]*op[2],
                  axis[0]*op[1] - axis[1]*op[0])
            if op != (0,0,0):
                r = math.sqrt((op[0]**2 + op[1]**2 + op[2]**2)/
                              (oq[0]**2 + oq[1]**2 + oq[2]**2))
                oq = [q*r for q in oq]
                cos = math.cos(rotAngle)
                sin = math.sin(rotAngle)
                rotP = (op[0]*cos + oq[0]*sin + o[0],
                        op[1]*cos + oq[1]*sin + o[1],
                        op[2]*cos + oq[2]*sin + o[2])
                self._thetas[n] = math.atan2(rotP[1],rotP[0])
                # math.floor because of floating point issues
                self._phis[n] = abs(math.acos(math.floor(rotP[2])/self._rs[n]))
            n += 1
        self.check_restrictions()



root = tk.Tk()
main = Main(root)

