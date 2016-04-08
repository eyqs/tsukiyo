"""
Polyhedron Visualizer v0.19

This script displays the vertices of regular polyhedra.
"""

import tkinter as tk
import tkinter.ttk as ttk
import math

TITLE = "Polyhedron Visualizer v0.19"
DESCRIPTION = "\nThis script displays the regular polyhedra."
WIDTH = 400
HEIGHT = 400
RADIUS = 100
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
        self.parent.protocol("WM_DELETE_WINDOW", self.close)
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

        viewLabel = ttk.Label(guiFrame, text="Views:")
        viewLabel.grid(row=2, column=0, sticky=tk.E)
        xViewBtn = ttk.Button(guiFrame, text="x", width=2,
                              command=lambda: self.canvas.newView('x'))
        xViewBtn.bind("<Key-Return>", lambda event: self.canvas.newView('x'))
        xViewBtn.grid(row=2, column=1)
        yViewBtn = ttk.Button(guiFrame, text="y", width=2,
                              command=lambda: self.canvas.newView('y'))
        yViewBtn.bind("<Key-Return>", lambda event: self.canvas.newView('y'))
        yViewBtn.grid(row=2, column=2)
        zViewBtn = ttk.Button(guiFrame, text="z", width=2,
                              command=lambda: self.canvas.newView('z'))
        zViewBtn.bind("<Key-Return>", lambda event: self.canvas.newView('z'))
        zViewBtn.grid(row=2, column=3, padx=(0,10))

        # Tkinter calls what is given: calling a function gives Tkinter
        # its return value, so must give a lambda with the argument.
        xUpBtn = ttk.Button(guiFrame, image=self._upBtn,
                            command=lambda: self.canvas.rotate('xUp'))
        xUpBtn.bind("<Button-1>", lambda event: self._mouse_down('xUp'))
        xUpBtn.bind("<ButtonRelease-1>", self._mouse_up)
        xUpBtn.bind("<Key-Return>", lambda event: self.canvas.rotate('xUp'))
        xUpBtn.grid(row=0, column=4)
        yUpBtn = ttk.Button(guiFrame, image=self._upBtn,
                              command=lambda: self.canvas.rotate('yUp'))
        yUpBtn.bind("<Button-1>", lambda event: self._mouse_down('yUp'))
        yUpBtn.bind("<ButtonRelease-1>", self._mouse_up)
        yUpBtn.bind("<Key-Return>", lambda event: self.canvas.rotate('yUp'))
        yUpBtn.grid(row=0, column=5)
        zUpBtn = ttk.Button(guiFrame, image=self._upBtn,
                            command=lambda: self.canvas.rotate('zUp'))
        zUpBtn.bind("<Button-1>", lambda event: self._mouse_down('zUp'))
        zUpBtn.bind("<ButtonRelease-1>", self._mouse_up)
        zUpBtn.bind("<Key-Return>", lambda event: self.canvas.rotate('zUp'))
        zUpBtn.grid(row=0, column=6)
        thetaUpBtn = ttk.Button(guiFrame, image=self._upBtn, state=tk.DISABLED,
                                command=lambda: self.canvas.rotate('tUp'))
        # thetaUpBtn.bind("<Button-1>", lambda event: self._mouse_down('tUp'))
        # thetaUpBtn.bind("<ButtonRelease-1>", self._mouse_up)
        # thetaUpBtn.bind("<Key-Return>", lambda event:self.canvas.rotate('tUp'))
        thetaUpBtn.grid(row=0, column=7)
        phiUpBtn = ttk.Button(guiFrame, image=self._upBtn, state=tk.DISABLED,
                              command=lambda: self.canvas.rotate('pUp'))
        # phiUpBtn.bind("<Button-1>", lambda event: self._mouse_down('pUp'))
        # phiUpBtn.bind("<ButtonRelease-1>", self._mouse_up)
        # phiUpBtn.bind("<Key-Return>", lambda event: self.canvas.rotate('pUp'))
        phiUpBtn.grid(row=0, column=8)

        xRotLabel = ttk.Label(guiFrame, text="x")
        xRotLabel.grid(row=1, column=4)
        yRotLabel = ttk.Label(guiFrame, text="y")
        yRotLabel.grid(row=1, column=5)
        zRotLabel = ttk.Label(guiFrame, text="z")
        zRotLabel.grid(row=1, column=6)
        thetaRotLabel = ttk.Label(guiFrame, text="θ")
        thetaRotLabel.grid(row=1, column=7)
        phiRotLabel = ttk.Label(guiFrame, text="Φ")
        phiRotLabel.grid(row=1, column=8)

        xDownBtn = ttk.Button(guiFrame, image=self._downBtn,
                              command=lambda: self.canvas.rotate('xDown'))
        xDownBtn.bind("<Button-1>", lambda event: self._mouse_down('xDown'))
        xDownBtn.bind("<ButtonRelease-1>", self._mouse_up)
        xDownBtn.bind("<Key-Return>", lambda event:self.canvas.rotate('xDown'))
        xDownBtn.grid(row=2, column=4)
        yDownBtn = ttk.Button(guiFrame, image=self._downBtn,
                              command=lambda: self.canvas.rotate('yDown'))
        yDownBtn.bind("<Button-1>", lambda event: self._mouse_down('yDown'))
        yDownBtn.bind("<ButtonRelease-1>", self._mouse_up)
        yDownBtn.bind("<Key-Return>", lambda event:self.canvas.rotate('yDown'))
        yDownBtn.grid(row=2, column=5)
        zDownBtn = ttk.Button(guiFrame, image=self._downBtn,
                              command=lambda: self.canvas.rotate('zDown'))
        zDownBtn.bind("<Button-1>", lambda event: self._mouse_down('zDown'))
        zDownBtn.bind("<ButtonRelease-1>", self._mouse_up)
        zDownBtn.bind("<Key-Return>", lambda event:self.canvas.rotate('zDown'))
        zDownBtn.grid(row=2, column=6)
        thetaDownBtn = ttk.Button(guiFrame, image=self._downBtn,
                                  state=tk.DISABLED,
                                  command=lambda: self.canvas.rotate('tDown'))
        # thetaDownBtn.bind("<Button-1>", lambda event:self._mouse_down('tDown'))
        # thetaDownBtn.bind("<ButtonRelease-1>", self._mouse_up)
        # thetaDownBtn.bind("<Key-Return>",
        #                   lambda event: self.canvas.rotate('tDown'))
        thetaDownBtn.grid(row=2, column=7)
        phiDownBtn = ttk.Button(guiFrame, image=self._downBtn,
                                state=tk.DISABLED,
                                command=lambda: self.canvas.rotate('pDown'))
        # phiDownBtn.bind("<Button-1>", lambda event: self._mouse_down('pDown'))
        # phiDownBtn.bind("<ButtonRelease-1>", self._mouse_up)
        # phiDownBtn.bind("<Key-Return>",
        #                 lambda event: self.canvas.rotate('pDown'))
        phiDownBtn.grid(row=2, column=8)

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
                           "polygon or change the viewpoint.")
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
        if button.endswith('w'):
            self.canvas.newView(button[0])
        else:
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
        self._viewPoint = 'z'

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

    def newView(self, viewPoint):
        """Change the current viewpoint."""
        self._viewPoint = viewPoint
        self._render()

    def view(self, points):
        """Return a Cartesian double depending on the viewpoint."""
        if self._viewPoint == 'x':
            return [(point[1],point[2]) for point in points]
        elif self._viewPoint == 'y':
            return [(point[0],point[2]) for point in points]
        elif self._viewPoint == 'z':
            return [(point[0],point[1]) for point in points]

    def rotate(self, rotType, rotAngle=ROTANGLE):
        """Rotate polytope on button press by ROTANGLE radians."""
        if rotType == "xUp":
            self.currPolytope.rotate_x(rotAngle)
        elif rotType == "xDown":
            self.currPolytope.rotate_x(-rotAngle)
        elif rotType == "yUp":
            self.currPolytope.rotate_y(rotAngle)
        elif rotType == "yDown":
            self.currPolytope.rotate_y(-rotAngle)
        elif rotType == "zUp":
            self.currPolytope.rotate_z(rotAngle)
        elif rotType == "zDown":
            self.currPolytope.rotate_z(-rotAngle)
        elif rotType == "tUp":
            self.currPolytope.rotate_theta(rotAngle)
        elif rotType == "tDown":
            self.currPolytope.rotate_theta(-rotAngle)
        elif rotType == "pUp":
            self.currPolytope.rotate_phi(rotAngle)
        elif rotType == "pDown":
            self.currPolytope.rotate_phi(-rotAngle)
        self._render()

    def take_input(self, event):
        """Take text input from input box."""
        try:
            self.currPolytope = self._translate(self.parent.inputText.get())
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
        elif entry == "quit" or entry == "exit":
            self.parent.close()

        # Schlafli symbol: {p/d}
        elif entry.startswith("{") and entry.endswith("}"):
            if ',' in entry:
                return Polytope(self._schlafli3D(entry[1:-1]))
            return Polytope(self._schlafli(entry[1:-1]))

        # (x,y) is a point, (xn,yn) vectors: vx,y;x1,y1;x2,y2; ... xn,yn
        # elif entry.startswith("v"):
        #    return Polytope(self._vector_list(entry[1:]))

        else:
            raise ValueError

    def _schlafli(self, entry):
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
        return rs, thetas, phis

    def _schlafli3D(self, entry):

        # Take 3D Schlafli symbol and return its spherical coordinates.
        # Currently only returns coordinates of the first ring.
        # No support for star polyhedra.

        num = entry.split(',')
        p = int(num[0])
        q = int(num[1])
        r = RADIUS

        # Coordinates of the north pole
        rs = [r]
        thetas = [0]
        phis = [0]

        # Coordinates of the first ring
        rs += [r]*q
        thetas += [(2*k*math.pi/q) for k in range(q)]
        firstPhi = 2*math.acos(math.sqrt((1-math.cos(math.pi*(1-2/p)))/
                                         (1-math.cos(2*math.pi/q))))
        phis += [firstPhi]*q

        if round(firstPhi) <= round(math.pi/2,4):    # Rounding for float errors
            # Coordinates of the south pole
            rs += [r]
            thetas += [0]
            phis += [math.pi]

            if round(firstPhi) < round(math.pi/2,4):
                # Coordinates of the bottom ring
                rs += [r]*q
                thetas += [(2*k+1)*math.pi/q for k in range(q)]
                phis += [(math.pi-firstPhi)]*q

                if p == 5:
                    # Coordinates of the second ring
                    # Coordinates of the second-bottom ring
                    pass

        return rs, thetas, phis

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
        if self.currPolytope.get_points():   # Empty lists are False
            w = self.winfo_width()//2
            h = self.winfo_height()//2
            points = [(point[0]+w, point[1]+h)
                      for point in self.view(self.currPolytope.get_points())]
            self.create_polygon(points, outline='#000', fill='#EEE', width=2)



class Polytope():

    """
    Drawing class that stores all polytope data and manages rotations.

    Public methods:
    add_point
    get_points
    rotate_x
    rotate_y
    rotate_z
    rotate_theta
    rotate_phi

    Instance variables:
    self.isDrawn
    """

    def __init__(self, vertices, isDrawn=False):
        """Construct Polytope class."""
        self.isDrawn = isDrawn
        self._number = len(vertices[0])
        self._rs = vertices[0]
        self._thetas = vertices[1]
        self._phis = vertices[2]

    def add_point(self, point):
        """Add a point to a drawn shape."""
        if self.isDrawn:
            self._vertices.append(point)

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

    def rotate_x(self, rotAngle):
        """Rotate the current polytope about the x-axis by rotAngle."""
        n = 0
        while n < self._number:
            # Formula derived on 14/09/17
            d = self._rs[n]*math.sin(self._phis[n])*math.cos(self._thetas[n])
            h = math.sqrt(self._rs[n]**2 - d**2)
            if self._thetas[n] % math.pi == 0:
                if (self._phis[n] % (2*math.pi) <= math.pi/2 or
                    self._phis[n] % (2*math.pi) > 3*math.pi/2):
                    q = math.pi/2
                elif (self._phis[n] % (2*math.pi) > math.pi/2 and
                      self._phis[n] % (2*math.pi) <= 3*math.pi/2):
                    q = 3*math.pi/2
            else:
                a = d*math.tan(self._thetas[n])
                o = self._rs[n]*math.cos(self._phis[n])
                q = math.atan2(o, a) + rotAngle
            self._thetas[n] = math.atan2(h*math.cos(q),d)
            self._phis[n] = math.pi/2 - math.asin(h*math.sin(q)/self._rs[n])
            n += 1

    def rotate_y(self, rotAngle):
        """Rotate the current polytope about the y-axis by rotAngle."""
        n = 0
        while n < self._number:
            # Formula derived on 14/09/18
            d = self._rs[n]*math.sin(self._phis[n])*math.sin(self._thetas[n])
            h = math.sqrt(self._rs[n]**2 - d**2)
            if self._thetas[n] % math.pi == math.pi/2:
                if (self._phis[n] % (2*math.pi) <= math.pi/2 or
                    self._phis[n] % (2*math.pi) > 3*math.pi/2):
                    q = math.pi/2
                elif (self._phis[n] % (2*math.pi) > math.pi/2 and
                      self._phis[n] % (2*math.pi) <= 3*math.pi/2):
                    q = 3*math.pi/2
            else:
                a = d*math.tan(self._thetas[n] - math.pi/2)
                o = self._rs[n]*math.sin(math.pi/2 - self._phis[n])
                q = math.atan2(o, a) + rotAngle
            self._thetas[n] = math.atan2(h*math.cos(q),d) + math.pi/2
            self._phis[n] = math.pi/2 - math.asin(h*math.sin(q)/self._rs[n])
            n += 1

    def rotate_z(self, rotAngle):
        """Rotate the current polytope about the z-axis by rotAngle."""
        self._thetas = [theta+rotAngle for theta in self._thetas]

    def rotate_theta(self, rotAngle):
        """Increase the value of theta of the current polytope by rotAngle."""
        self._thetas = [theta+rotAngle for theta in self._thetas]

    def rotate_phi(self, rotAngle):
        """Increase the value of phi of the current polytope by rotAngle."""
        self._phis = [phi+rotAngle for phi in self._phis]




root = tk.Tk()
main = Main(root)

