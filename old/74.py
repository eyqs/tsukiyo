"""
Polyhedron Shader v0.74

This program shades convex polyhedra.
_wythoff is split into three parts: _wythoff to find the generating point,
_wythoff_snub to randomly find it, and _schwarz to reflect it everywhere.
In the snub case (| p q r), _wythoff runs until an actual polyhedron returns.
"""
import tkinter as tk
import tkinter.ttk as ttk
import math
import random

TITLE = 'Polyhedron Shader v0.74'
DESCRIPTION = '\nThis script displays shaded polyhedra.'
pi = math.pi
WIDTH = 600
HEIGHT = 550
BGCOLOUR = '#CCC'

RADIUS = 100
ZOOM = 50
RETINA = 10
CHANGE = 10     # 10 pixels change in radius and 0.1r change in distance
DELAY = 28      # 28 ms per pi/24 rotation = 3 rotations every 4 seconds
ROTANGLE = pi/24
SPHERENUM = 12
EPSILON = 0.00001

def distance(head, tail=[0,0,0,0]):
    """Return the distance squared between two points."""
    return sum([(head[i] - tail[i])**2 for i in range(len(head))])

def normalize(points, vector=[1]):
    """
    Normalizes a vector.

    Takes two vectors as lists and creates a new vector with
    the magnitude of the second and the direction of the first.
    Default length of the second vector is 1.
    """
    norm = math.sqrt(distance(points))
    magnitude = math.sqrt(distance(vector))
    if norm == 0:
        return [0 for x in points]
    return [x/norm*magnitude for x in points]

def cross3D(u, v, vector=[1]):
    """
    Finds the 3D cross product of two vectors.

    Takes three vectors as lists and creates a new vector
    perpendicular to the first two with the magnitude of the third.
    Default length of the third vector is 1.
    """
    uxv = (u[1]*v[2]-u[2]*v[1],
           u[2]*v[0]-u[0]*v[2],
           u[0]*v[1]-u[1]*v[0])
    return normalize(uxv, vector)

def cross4D(u, v, w, vector=[1]):
    """
    Finds the 4D cross product of two vectors.

    Takes four vectors as lists and creates a new vector
    perpendicular to the first three with the magnitude of the fourth.
    Default length of the fourth vector is 1.
    """
    uvw = [u[1]*(v[2]*w[3]-v[3]*w[2]) - u[2]*(v[1]*w[3]-v[3]*w[1]) + u[3]*(v[1]*w[2]-v[2]*w[1]),
           -u[0]*(v[2]*w[3]-v[3]*w[2]) + u[2]*(v[0]*w[3]-v[3]*w[0]) - u[3]*(v[0]*w[2]-v[2]*w[0]),
           u[0]*(v[1]*w[3]-v[3]*w[1]) - u[1]*(v[0]*w[3]-v[3]*w[0]) + u[3]*(v[0]*w[1]-v[1]*w[0]),
           -u[0]*(v[1]*w[2]-v[2]*w[1]) + u[1]*(v[0]*w[2]-v[2]*w[0]) - u[2]*(v[0]*w[1]-v[1]*w[0])]
    return normalize(uvw, vector)

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
        theta = math.atan2(point[1], point[0])
        if point[0] == 0 and point[1] == 0 and point[2] == 0:
            phi = 0
        else:
            phi = math.acos(point[2]/
                            math.sqrt(point[2]**2+point[1]**2+point[0]**2))
        if r == 0:
            omega = 0
        else:
            omega = math.acos(point[3]/r)
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
    sphere
    wire
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

        self._leftBtn = tk.PhotoImage(file='leftButtonFifty.gif')
        self._rightBtn = tk.PhotoImage(file='rightButtonFifty.gif')
        self._upBtn = tk.PhotoImage(file='upButtonEleven.gif')
        self._downBtn = tk.PhotoImage(file='downButtonEleven.gif')

        style = ttk.Style()
        style.configure('TFrame', background=BGCOLOUR)
        style.configure('TLabel', background=BGCOLOUR)
        style.configure('TButton', background=BGCOLOUR)
        style.configure('TCheckbutton', background=BGCOLOUR)

        # Grid main widget frames

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        titleLabel = ttk.Label(self, text=TITLE)
        titleLabel.grid(row=0, column=0, columnspan=2, pady=10)
        self.canvas = Canvas(self)
        self.canvas.grid(row=1, column=0, padx=10,
                         sticky=tk.N+tk.E+tk.S+tk.W)
        _guiRight = ttk.Frame(self)
        # 10px padding on right, 0px on left, as canvas is already padded
        _guiRight.grid(row=1, column=1, padx=(0,10), sticky=tk.N)
        _guiBottom = ttk.Frame(self)
        _guiBottom.columnconfigure(0, weight=1)
        _guiBottom.grid(row=2, column=0, columnspan=2,
                        padx=10, pady=(0,20), sticky=tk.E+tk.W)

        # Grid _guiRight widgets: 8 rows, 3 columns

        _rotateLabel = ttk.Label(_guiRight, text='Rotate: ')
        _rotateLabel.grid(row=0, column=0, columnspan=3)
        _leftRotBtn = ttk.Button(_guiRight, image=self._leftBtn,
                                 command=lambda: self.canvas.rotate(0))
        _leftRotBtn.bind('<Button-1>', lambda event: self._mouse_down(0))
        _leftRotBtn.bind('<ButtonRelease-1>', self._mouse_up)
        _leftRotBtn.bind('<Key-Return>', lambda event: self.canvas.rotate(0))
        _leftRotBtn.grid(row=1, column=0, columnspan=2, sticky=tk.W)
        _rightRotBtn = ttk.Button(_guiRight, image=self._rightBtn,
                                  command=lambda: self.canvas.rotate(1))
        _rightRotBtn.bind('<Button-1>', lambda event: self._mouse_down(1))
        _rightRotBtn.bind('<ButtonRelease-1>', self._mouse_up)
        _rightRotBtn.bind('<Key-Return>', lambda event: self.canvas.rotate(1))
        _rightRotBtn.grid(row=1, column=1, columnspan=2, sticky=tk.E)

        _xwRotBtn = ttk.Button(_guiRight, text="xw", width=5,
                               command=lambda: self.canvas.set_rotaxis('xw'))
        _xwRotBtn.bind('<Key-Return>',lambda event:self.canvas.set_rotaxis('xw'))
        _xwRotBtn.grid(row=2, column=0)
        _ywRotBtn = ttk.Button(_guiRight, text="yw", width=5,
                               command=lambda: self.canvas.set_rotaxis('yw'))
        _ywRotBtn.bind('<Key-Return>',lambda event:self.canvas.set_rotaxis('yw'))
        _ywRotBtn.grid(row=2, column=1)
        _zwRotBtn = ttk.Button(_guiRight, text="zw", width=5,
                               command=lambda: self.canvas.set_rotaxis('zw'))
        _zwRotBtn.bind('<Key-Return>',lambda event:self.canvas.set_rotaxis('zw'))
        _zwRotBtn.grid(row=2, column=2)
        _xyRotBtn = ttk.Button(_guiRight, text="xy", width=5,
                               command=lambda: self.canvas.set_rotaxis('xy'))
        _xyRotBtn.bind('<Key-Return>',lambda event:self.canvas.set_rotaxis('xy'))
        _xyRotBtn.grid(row=3, column=0)
        _yzRotBtn = ttk.Button(_guiRight, text="yz", width=5,
                               command=lambda: self.canvas.set_rotaxis('yz'))
        _yzRotBtn.bind('<Key-Return>',lambda event:self.canvas.set_rotaxis('yz'))
        _yzRotBtn.grid(row=3, column=1)
        _xzRotBtn = ttk.Button(_guiRight, text="xz", width=5,
                               command=lambda: self.canvas.set_rotaxis('xz'))
        _xzRotBtn.bind('<Key-Return>',lambda event:self.canvas.set_rotaxis('xz'))
        _xzRotBtn.grid(row=3, column=2)

        _wythoffLabel = ttk.Label(_guiRight, text="Wythoff: ")
        _wythoffLabel.grid(row=4, column=0, columnspan=3, pady=(20,0))
        _aBarBtn = ttk.Button(_guiRight, text="(pqs)", width=5,
                              command=lambda: self.canvas.set_selection('a'))
        _aBarBtn.bind('<Key-Return>', lambda event:self.canvas.set_selection('a'))
        _aBarBtn.grid(row=5, column=0)
        _bBarBtn = ttk.Button(_guiRight, text="(|pqs)", width=5,
                              command=lambda: self.canvas.set_selection('b'))
        _bBarBtn.bind('<Key-Return>', lambda event:self.canvas.set_selection('b'))
        _bBarBtn.grid(row=5, column=1)
        _cBarBtn = ttk.Button(_guiRight, text="(pqs|)", width=5,
                              command=lambda: self.canvas.set_selection('c'))
        _cBarBtn.bind('<Key-Return>', lambda event:self.canvas.set_selection('c'))
        _cBarBtn.grid(row=5, column=2)
        _pBarBtn = ttk.Button(_guiRight, text="(p|qs)", width=5,
                              command=lambda: self.canvas.set_selection('p'))
        _pBarBtn.bind('<Key-Return>', lambda event:self.canvas.set_selection('p'))
        _pBarBtn.grid(row=6, column=0)
        _qBarBtn = ttk.Button(_guiRight, text="(q|sp)", width=5,
                              command=lambda: self.canvas.set_selection('q'))
        _qBarBtn.bind('<Key-Return>', lambda event:self.canvas.set_selection('q'))
        _qBarBtn.grid(row=6, column=1)
        _sBarBtn = ttk.Button(_guiRight, text="(s|pq)", width=5,
                              command=lambda: self.canvas.set_selection('s'))
        _sBarBtn.bind('<Key-Return>', lambda event:self.canvas.set_selection('s'))
        _sBarBtn.grid(row=6, column=2)
        _pqBarBtn = ttk.Button(_guiRight, text="(pq|s)", width=5,
                              command=lambda: self.canvas.set_selection('pq'))
        _pqBarBtn.bind('<Key-Return>', lambda event:self.canvas.set_selection('pq'))
        _pqBarBtn.grid(row=7, column=0)
        _qsBarBtn = ttk.Button(_guiRight, text="(qs|p)", width=5,
                              command=lambda: self.canvas.set_selection('qs'))
        _qsBarBtn.bind('<Key-Return>', lambda event:self.canvas.set_selection('qs'))
        _qsBarBtn.grid(row=7, column=1)
        _spBarBtn = ttk.Button(_guiRight, text="(sp|q)", width=5,
                              command=lambda: self.canvas.set_selection('sp'))
        _spBarBtn.bind('<Key-Return>', lambda event:self.canvas.set_selection('sp'))
        _spBarBtn.grid(row=7, column=2)

        # Grid _guiBottom widgets: 5 rows, 7 columns

        self.statusText = tk.StringVar()
        self.statusLabel = ttk.Label(
            _guiBottom, textvariable=self.statusText, foreground="red")
        self.statusLabel.grid(row=0, column=0, columnspan=7, sticky=tk.W)
        self.inputText = tk.StringVar()
        _inputBox = ttk.Entry(_guiBottom, textvariable=self.inputText)
        _inputBox.bind('<Key-Return>', self.canvas.take_input)
        _inputBox.grid(row=1, column=0, columnspan=7, sticky=tk.E+tk.W)
        _inputBox.focus()
        self.sphere = tk.IntVar()
        _sphereCheck = ttk.Checkbutton(_guiBottom, text='Overlay',
                                       variable=self.sphere, command=lambda:
                                       self.change('s'))
        _sphereCheck.grid(row=2, column=0, sticky=tk.W)

        _viewLabel = ttk.Label(_guiBottom, text='Views: ')
        _viewLabel.grid(row=2, column=1, columnspan=2, sticky=tk.E)
        _xViewBtn = ttk.Button(_guiBottom, text='x', width=2, command=lambda:
                               self.canvas.set_viewaxis([0, pi/2, pi/2]))
        _xViewBtn.bind('<Key-Return>', lambda event:
                       self.canvas.set_viewaxis([0, pi/2, pi/2]))
        _xViewBtn.grid(row=2, column=3)
        _yViewBtn = ttk.Button(_guiBottom, text='y', width=2, command=lambda:
                               self.canvas.set_viewaxis([pi/2, pi/2, pi/2]))
        _yViewBtn.bind('<Key-Return>', lambda event:
                       self.canvas.set_viewaxis([pi/2, pi/2, pi/2]))
        _yViewBtn.grid(row=2, column=4)
        _zViewBtn = ttk.Button(_guiBottom, text='z', width=2, command=lambda:
                               self.canvas.set_viewaxis([0, 0, pi/2]))
        _zViewBtn.bind('<Key-Return>', lambda event:
                       self.canvas.set_viewaxis([0, 0, pi/2]))
        _zViewBtn.grid(row=2, column=5)
        _wViewBtn = ttk.Button(_guiBottom, text='w', width=2, command=lambda:
                               self.canvas.set_viewaxis([0, 0, 0]))
        _wViewBtn.bind('<Key-Return>', lambda event:
                       self.canvas.set_viewaxis([0, 0, 0]))
        _wViewBtn.grid(row=2, column=6)

        self.wire = tk.IntVar()
        self.wireCheck = ttk.Checkbutton(_guiBottom, text='Wireframe',
                                         variable=self.wire, command=lambda:
                                         self.change('w'))
        self.wireCheck.grid(row=3, column=0, sticky=tk.W)
        _zoomLabel = ttk.Label(_guiBottom, text='zoom: ')
        _zoomLabel.grid(row=3, column=1, sticky=tk.E)
        _zUpBtn = ttk.Button(_guiBottom, image=self._upBtn, command=lambda:
                             self.change('zUp'))
        _zUpBtn.bind('<Button-1>', lambda event: self._mouse_down('zUp'))
        _zUpBtn.bind('<ButtonRelease-1>', self._mouse_up)
        _zUpBtn.bind('<Key-Return>', lambda event:
                     self.change('rUp'))
        _zUpBtn.grid(row=3, column=2, sticky=tk.E)
        _zDownBtn = ttk.Button(_guiBottom, image=self._downBtn, command=lambda:
                               self.change('zDown'))
        _zDownBtn.bind('<Button-1>', lambda event: self._mouse_down('zDown'))
        _zDownBtn.bind('<ButtonRelease-1>', self._mouse_up)
        _zDownBtn.bind('<Key-Return>', lambda event:
                       self.change('zDown'))
        _zDownBtn.grid(row=3, column=3)
        _distanceLabel = ttk.Label(_guiBottom, text='d: ')
        _distanceLabel.grid(row=3, column=4, sticky=tk.E)
        _dUpBtn = ttk.Button(_guiBottom, image=self._upBtn, command=lambda:
                             self.change('dUp'))
        _dUpBtn.bind('<Button-1>', lambda event: self._mouse_down('dUp'))
        _dUpBtn.bind('<ButtonRelease-1>', self._mouse_up)
        _dUpBtn.bind('<Key-Return>', lambda event:
                     self.change('dUp'))
        _dUpBtn.grid(row=3, column=5, sticky=tk.E)
        _dDownBtn = ttk.Button(_guiBottom, image=self._downBtn, command=lambda:
                               self.change('dDown'))
        _dDownBtn.bind('<Button-1>', lambda event: self._mouse_down('dDown'))
        _dDownBtn.bind('<ButtonRelease-1>', self._mouse_up)
        _dDownBtn.bind('<Key-Return>', lambda event:
                       self.change('dDown'))
        _dDownBtn.grid(row=3, column=6)

        self.zoom = tk.IntVar()
        self.zoom.set(ZOOM)
        _zoomDisplay = ttk.Label(_guiBottom, textvariable=self.zoom)
        _zoomDisplay.grid(row=4, column=0, columnspan=4, sticky=tk.E)
        self.distance = tk.IntVar()
        self.unitDistance = 20
        self.distance.set(int(ZOOM*RADIUS*RETINA/(self.unitDistance**(3/2))))
        _distanceDisplay = ttk.Label(_guiBottom, textvariable=self.distance)
        _distanceDisplay.grid(row=4, column=4, columnspan=3, sticky=tk.E)

    def _make_menus(self):
        # Initialize dropdown menus.
        _menuBar = tk.Menu(self.parent)
        self.parent.config(menu=_menuBar)
        _fileMenu = tk.Menu(_menuBar)
        # underline sets position of keyboard shortcut
        _fileMenu.add_command(label='About', underline=0,
                              command=lambda: self._make_popups('About'))
        _fileMenu.add_command(label='Help', underline=0,
                              command=lambda: self._make_popups('Help'))
        _fileMenu.add_command(label='Exit', underline=1,
                              command=self.close)
        _menuBar.add_cascade(label='File', menu=_fileMenu)

    def _make_popups(self, popUpType):

        # Make pop-up windows based on popUpType.

        # Set individual window data
        if popUpType == 'About':
            titleText = 'About this application...'
            messageText = '\n'.join((TITLE, DESCRIPTION))
            buttonText = 'OK'
            frameWidth = 400
            frameHeight = 200
        elif popUpType == 'Help':
            titleText = 'Help'
            messageText = ('Click the buttons to rotate the '
                            'object or change the view.')
            buttonText = 'Dismiss'
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
            self.change('zUp')
        elif button == 'zDown':
            self.change('zDown')
        elif button == 'dUp':
            self.change('dUp')
        elif button == 'dDown':
            self.change('dDown')
        else:
            self.canvas.rotate(button)

    def set_status(self, event):
        """Handle and display status changes."""
        if event == 'clear':
            self.statusText.set('')

        elif event == 'badinput':
            self.statusText.set('Bad input!')
            self.statusLabel.after(1000, self.set_status, 'clear')

        elif event == 'view':
            self.statusText.set('New view angle: ' + self.canvas.get_data('view'))

        elif event == 'rot':
            self.statusText.set('New rotation axes: ' + self.canvas.get_data('rot'))

        elif event == 'faces':
            name = {3:' triangle', 4:' square', 5:' pentagon', 6:' hexagon',
                    7:' heptagon', 8:' octagon', 9:' nonagon', 10:' decagon',
                    13:' triangle', 14:' line', 15:' pentagram', 16:' hexagram',
                    17:' heptagram', 18:' octagram', 19:' nonagram', 20:' decagram'}
            text = ''
            faces = self.canvas.get_data('faces')
            for i in range(3,21):
                if faces[i] == 1:
                    text += str(faces[i]) + name[i] + ' '
                if faces[i] > 1:
                    text += str(faces[i]) + name[i] + 's '
            self.statusText.set(text)

    def change(self, change, value=0):
        """
        Change various values, such as radius and viewpoint distance,
        toggle sphere or wireframe, and re-render the polytope.
        """
        if change == 's':
            pass
        elif change == 'w':
            pass
        elif change == 'wire':
            self.wire.set(1)
            self.wireCheck.config(state=tk.DISABLED)

        elif change == 'z':
            self.zoom.set(min(value, ZOOM*RADIUS*RETINA/2))
        elif change == 'zUp':
            self.zoom.set(min(self.zoom.get() + 5, ZOOM*RADIUS*RETINA/2))
        elif change == 'zDown':
            self.zoom.set(max(self.zoom.get() - 5, 0))

        elif change == 'd':
            self.distance.set(min(value, ZOOM*RADIUS*RETINA))
            self.unitDistance = math.ceil((ZOOM*RADIUS*RETINA/value)**(2/3))
            if self.unitDistance >= 100:
                self.unitDistance = 100
            if self.unitDistance**(3/2) > ZOOM*RETINA:
                self.change('wire')
        elif change == 'dUp':
            self.unitDistance -= 1
            if self.unitDistance < 1:
                self.unitDistance = 1
            self.distance.set(int(ZOOM*RADIUS*RETINA/(self.unitDistance**(3/2))))
            if (self.unitDistance**(3/2) < ZOOM*RETINA
                and self.canvas.get_data('star') == 0):
                self.wireCheck.config(state=tk.NORMAL)
        elif change == 'dDown':
            self.unitDistance += 1
            self.distance.set(int(ZOOM*RADIUS*RETINA/(self.unitDistance**(3/2))))
            if self.unitDistance**(3/2) > ZOOM*RETINA:
                self.change('wire')

        elif change == 'reset':
            try:                        # Canvas initializes before zoom
                self.zoom.set(ZOOM)
                self.unitDistance = 20  # Distance follows a x^(-3/2) curve
                self.distance.set(int(ZOOM*RADIUS*RETINA/(self.unitDistance**(3/2))))
                self.wireCheck.config(state=tk.NORMAL)
            except:
                return
        self.canvas.render()

    def close(self):
        """Close the application."""
        self.parent.destroy()



class Canvas(tk.Canvas):

    """
    Display class that manages polytope creation, edits, and display.

    Public methods:
    set_viewaxis
    set_rotaxis
    set_selection
    rotate
    take_input
    get_data
    render

    Object variables:
    parent
    """

    def __init__(self, parent):
        """Construct Canvas class."""
        self.parent = parent
        tk.Canvas.__init__(self, parent, background='#FFF',
                           relief=tk.GROOVE, borderwidth=5,
                           width=300, height=200)
        self._currPolytope = Polytope([])
        self._currWythoff = ['2','2','2']
        self._reset()

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
        self.render()
        if self._currPolytope.get_points():
            self.parent.set_status('view')

    def _view(self, points):

        # Return a Cartesian double depending on the viewAxis.

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
        d = self.parent.distance.get()
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
            result.append((m*self.parent.zoom.get(), n*self.parent.zoom.get()))
        return result

    def set_rotaxis(self, rotAxis):
        """Change the current rotation axis-plane."""
        if rotAxis == 'xw':
            self.rotAxis = [(1,0,0,0),(0,0,0,1)]
        elif rotAxis == 'yw':
            self.rotAxis = [(0,1,0,0),(0,0,0,1)]
        elif rotAxis == 'zw':
            self.rotAxis = [(0,0,1,0),(0,0,0,1)]
        elif rotAxis == 'xy':
            self.rotAxis = [(1,0,0,0),(0,1,0,0)]
        elif rotAxis == 'yz':
            self.rotAxis = [(0,1,0,0),(0,0,1,0)]
        elif rotAxis == 'xz':
            self.rotAxis = [(1,0,0,0),(0,0,1,0)]
        else:
            self.rotAxis = rotAxis
        self._currPolytope.set_rotaxis(self.rotAxis)
        self._sphere.set_rotaxis(self.rotAxis)
        self.render()
        if self._currPolytope.get_points():
            self.parent.set_status('rot')

    def rotate(self, direction, rotAngle=ROTANGLE):
        """Rotate polytope on button press by ROTANGLE radians."""
        if direction == 0:
            self._currPolytope.rotate(rotAngle)
            self._sphere.rotate(rotAngle)
        elif direction == 1:
            self._currPolytope.rotate(-rotAngle)
            self._sphere.rotate(-rotAngle)
        self.render()

    def set_selection(self, select):
        """Change the point reflected by the Wythoff triangle mirrors."""
        self._currPolytope = Polytope(self._wythoff(selection=select))
        self._reset()
        self.render()

    def take_input(self, event):
        """Take text input from input box."""
        translatedInput = self._translate(self.parent.inputText.get())
        if translatedInput == ValueError:
            self.render()
            self.parent.set_status('badinput')
        elif translatedInput:
            self._currPolytope = translatedInput
            self._reset()
        self.parent.inputText.set('')

    def get_data(self, event):
        """Return data about the current Polytope and toggle wireframe mode."""
        if event == 'view':
            return ', '.join([str(float(int(self._viewAxis[i]*100)/100))
                              for i in range(3)])   # Converts 1.5708 to 1.57
        if event == 'rot':
            u = ', '.join([str(float(int(self.rotAxis[0][i]*100)/100))
                           for i in range(4)])
            v = ', '.join([str(float(int(self.rotAxis[1][i]*100)/100))
                           for i in range(4)])
            return u + ' and ' + v
        if event == 'faces':
            return self._currPolytope.get_face_sides()
        if event == 'star':
            return self._currPolytope.star

    def _translate(self, entry):

        # Translate text input to return a Polytope object.

        # Clear canvas, return empty polytope for _renderLines to process
        if entry == ('' or 'clear' or 'reset'):
            self.parent.set_status('clear')
            return Polytope([])

        # Exit application
        if entry == 'quit' or entry == 'exit' or entry == 'close':
            self.parent.close()

        # Set zoom
        elif entry.startswith('z'):
            try:
                zoom = int(entry[1:])
                if zoom < 1:
                    return ValueError
            except:
                return ValueError
            self.parent.change('z', zoom)
            return

        # Set distance between viewer and polytope
        elif entry.startswith('d'):
            try:
                distance = int(entry[1:])
                if distance < 1:
                    return ValueError
            except:
                return ValueError
            self.parent.change('d', distance)
            return

        # Set viewing axis
        # v1,2 sets view axis to [1,2,3]
        elif entry.startswith('v'):
            try:
                viewAxis = [float(num) for num in entry[1:].split(',')]
                if len(viewAxis) < 3:
                    viewAxis.append(pi/2)
                if len(viewAxis) != 3:
                    return ValueError
                self.set_viewaxis(viewAxis)
                return
            except:
                return ValueError

        # Set rotation axis
        # r1,2,3 sets view axis to [1,2,3,0]
        # r1,2,3,4/5,6,7,8 sets view axis to [1,2,3,4], [5,6,7,8]
        elif entry.startswith('r'):
            try:
                rotAxis = entry[1:].split('/')
                if len(rotAxis) == 2:           # 3D rotation plane, two vectors
                    u = list(map(float, rotAxis[0].split(',')))
                    v = list(map(float, rotAxis[1].split(',')))
                    if (len(u) != 4 or len(v) != 4):
                        return ValueError
                    self.set_rotaxis((u, v))
                elif len(rotAxis) == 1:         # 2D rotation axis, one vector
                    u = list(map(float, rotAxis[0].split(',')))
                    if len(u) == 3:
                        u.append(0)
                    if len(u) != 4:
                        return ValueError
                    v = [0,0,0,1]
                else:
                    return ValueError
                self.set_rotaxis((u, v))
                return
            except:
                return ValueError

        # Pentachoron coordinates, side-length 4r
        elif entry == '{3,3,3}':
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
        elif entry == '{4,3,3}':
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
        elif entry == '{3,3,4}':
            r = 2*RADIUS
            return Polytope(([[r,0,0,0],[-r,0,0,0],[0,r,0,0],[0,-r,0,0],
                              [0,0,r,0],[0,0,-r,0],[0,0,0,r],[0,0,0,-r]],
                             ((0,2),(0,3),(0,4),(0,5),(0,6),(0,7),
                              (1,2),(1,3),(1,4),(1,5),(1,6),(1,7),
                              (2,4),(2,5),(2,6),(2,7),(3,4),(3,5),
                              (3,6),(3,7),(4,6),(4,7),(5,6),(5,7)),
                             [(k, '#000') for k in range(8)]))

        # Schlafli symbol: {p/d}
        elif entry.startswith('{') and entry.endswith('}'):
            if ',' in entry:
                return Polytope(self._schlafli3D(entry[1:-1]))
            else:
                return Polytope(self._schlafli2D(entry[1:-1]))

        # Wythoff symbol: (p q s)
        elif entry.startswith('(') and entry.endswith(')'):
            while True:     # Las Vegas algorithm, keep on repeating snub cases
                polytope = Polytope(self._wythoff(entry[1:-1]))
                if polytope.get_points():
                    return Polytope(self._wythoff(entry[1:-1]))
        else:
            return ValueError

    def _schlafli2D(self, entry):
        # Take 2D Schlafli symbol and return its coordinate data.
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
        colours = [(k,'#000') for k in range(p)]
        points = []
        points.extend([convert((rs[n], thetas[n], phis[n], omegas[n]), True)
                       for n in range(len(thetas))])
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
        r1 = math.sqrt((1-math.cos(a))/(1-math.cos(b)))
        firstPhi = 2*math.acos(r1)
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

                thetas += [k*b+secondTheta for k in range(q)]
                thetas += [(k+1)*b-secondTheta for k in range(q)]
                phis += [secondPhi]*2*q

                thetas += [(k+1/2)*b+secondTheta for k in range(q)]
                thetas += [(k+3/2)*b-secondTheta for k in range(q)]
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
        points.extend([convert((rs[n], thetas[n], phis[n], omegas[n]), True)
                      for n in range(len(thetas))])
        colours = [(k, '#000') for k in range(len(thetas))]
        return points, edges, colours

    def _wythoff(self, entry='', selection='a', colour='#000'):

        # Take Wythoff symbol and return its spherical coordinates.

        r = RADIUS
        edges = []
        colours = []

        # a = all triangles, b = (|pqs), c = (pqs|)
        # p = (p|qs), q = (q|sp), s = (s|pq)
        # pq = (pq|s), qs = (qs|p), sp = (sp|q)
        if len(entry) > 0:
            symbol = entry.split()
            if len(symbol) > 3:
                if symbol.index('|') == 0:
                    selection = 'b'
                elif symbol.index('|') == 1:
                    selection = 'p'
                elif symbol.index('|') == 2:
                    selection = 'pq'
                elif symbol.index('|') == 3:
                    selection = 'c'
                symbol.remove('|')
        else:
            symbol = self._currWythoff
        if '/' in symbol[0]:
            p = int(symbol[0].split('/')[0])/int(symbol[0].split('/')[1])
        else:
            p = int(symbol[0])
        if '/' in symbol[1]:
            q = int(symbol[1].split('/')[0])/int(symbol[1].split('/')[1])
        else:
            q = int(symbol[1])
        if '/' in symbol[2]:
            s = int(symbol[2].split('/')[0])/int(symbol[2].split('/')[1])
        else:
            s = int(symbol[2])
        if p == 1 or q == 1 or s == 1:
            raise ValueError

        # Check Wythoff symbol validity, then save current Wythoff polyhedron
        lpq = math.acos((math.cos(pi/s) + math.cos(pi/p)*math.cos(pi/q))/
                        (math.sin(pi/p)*math.sin(pi/q)))
        lqs = math.acos((math.cos(pi/p) + math.cos(pi/q)*math.cos(pi/s))/
                        (math.sin(pi/q)*math.sin(pi/s)))
        lsp = math.acos((math.cos(pi/q) + math.cos(pi/s)*math.cos(pi/p))/
                        (math.sin(pi/s)*math.sin(pi/p)))
        self._currWythoff = symbol

        # Fundamental triangle
        triangles = [[[0.0 if abs(x) < EPSILON else x for x in
                       convert(point, True)] for point in
                      [(r,0,0,pi/2), (r,0,lpq,pi/2), (r,pi/p,lsp,pi/2)]]]
        op = triangles[0][0]
        oq = triangles[0][1]
        os = triangles[0][2]
        pq = cross3D(op, oq)
        qs = cross3D(oq, os)
        sp = cross3D(os, op)

        # Find the generating point
        if selection == 'a':
            n = [0.0,0.0,0.0,0.0]
        elif selection == 'c':
            # Find angle bisectors on two sides
            op = normalize(triangles[0][0], [r])
            oq = triangles[0][1]
            os = triangles[0][2]
            lpn = math.atan2(math.sin(lsp), (
                math.cos(lsp)*math.cos(pi/p)+
                math.sin(pi/p)*math.cos(pi/s/2)/math.sin(pi/s/2)))
            pq = cross3D(op, oq)
            un = cross3D(pq, op, [r])
            on = [op[t]*math.cos(lpn) + un[t]*math.sin(lpn)
                 for t in range(3)] + [0.0]
            lpm = math.atan2(math.sin(lpq), (
                math.cos(lpq)*math.cos(pi/p)+
                math.sin(pi/p)*math.cos(pi/q/2)/math.sin(pi/q/2)))
            ps = cross3D(op, os)
            um = cross3D(ps, op, [r])
            om = [op[t]*math.cos(lpm) + um[t]*math.sin(lpm)
                 for t in range(3)] + [0.0]
            # Find intersection of bisecting great circles
            ns = cross3D(on, os)
            mq = cross3D(om, oq)
            n = cross3D(mq, ns, [r]) + [0.0]
        elif selection == 'p':
            n = triangles[0][0]
            colour = '#F00'
        elif selection == 'q':
            n = triangles[0][1]
            colour = '#000'
        elif selection == 's':
            n = triangles[0][2]
            colour = '#00F'
        elif selection == 'pq':
            # Find length on great circle pq
            pn = math.atan2(math.sin(lsp), (
                math.cos(lsp)*math.cos(pi/p)+
                math.sin(pi/p)*math.cos(pi/s/2)/math.sin(pi/s/2)))
            # Parametrize great circle with normal vector pq
            op = normalize(triangles[0][0], [r])
            oq = triangles[0][1]
            pq = cross3D(op, oq)
            ot = cross3D(pq, op, [r])
            n = [op[t]*math.cos(pn) + ot[t]*math.sin(pn)
                 for t in range(3)] + [0.0]
        elif selection == 'qs':
            qn = math.atan2(math.sin(lpq), (
                math.cos(lpq)*math.cos(pi/q)+
                math.sin(pi/q)*math.cos(pi/p/2)/math.sin(pi/p/2)))
            oq = normalize(triangles[0][1], [r])
            os = triangles[0][2]
            qs = cross3D(oq, os)
            ot = cross3D(qs, oq, [r])
            n = [oq[t]*math.cos(qn) + ot[t]*math.sin(qn)
                 for t in range(3)] + [0.0]
        elif selection == 'sp':
            sn = math.atan2(math.sin(lqs), (
                math.cos(lqs)*math.cos(pi/s)+
                math.sin(pi/s)*math.cos(pi/q/2)/math.sin(pi/q/2)))
            os = normalize(triangles[0][2], [r])
            op = triangles[0][0]
            sp = cross3D(os, op)
            ot = cross3D(sp, os, [r])
            n = [os[t]*math.cos(sn) + ot[t]*math.sin(sn)
                 for t in range(3)] + [0.0]

        if selection == 'b':
            points, side = self._wythoff_snub(p, q, s)
        if selection != 'b':
            points, side = self._schwarz(selection, triangles, n)
        # Display points according to type of connection
        if selection == 'a':
            points.remove([0.0,0.0,0.0,0.0])
            n = 2
            while n < len(points):
                edges += [(n-2,n-1), (n-2,n), (n-1,n)]
                colours += [(n-2, '#F00'), (n-1, '#000'), (n, '#00F')]
                n += 3
        else:
            for n in range(len(points)):
                for k in range(n+1, len(points)):
                    if abs(sum([(points[n][t]-points[k][t])**2
                                for t in range(3)]) - side) < 2:
                        edges.append((n,k))
            colours = [(k, colour) for k in range(len(points))]
        return points, edges, colours

    def _schwarz(self, selection, triangles, n):

        # Take fundamental triangle and reflect generating point everywhere.
        depth = 16
        side = 0

        # Make coordinate identification system without negative zeros
        triangles[0].append(n)
        points = [n]
        if selection == 'b':
            points = []
        numa = '{:=+04.0f}{:=+04.0f}{:=+04.0f}'.format(*triangles[0][0])
        numb = '{:=+04.0f}{:=+04.0f}{:=+04.0f}'.format(*triangles[0][1])
        numc = '{:=+04.0f}{:=+04.0f}{:=+04.0f}'.format(*triangles[0][2])
        numn = '{:=+04.0f}{:=+04.0f}{:=+04.0f}'.format(*triangles[0][3])
        tricoords = [''.join(sorted([numa, numb, numc]))+numn]
        pointcoords = [numn]

        # Reflect each unreflected triangle thrice
        while depth > 0:
            for triangle in reversed(triangles):
                # Reversed to avoid loop
                if selection == 'a':
                    points.extend([triangle[t] for t in range(3)])

                # Find normals to great circles
                op = triangle[0]
                oq = triangle[1]
                os = triangle[2]
                on = triangle[3]
                qs = cross3D(oq, os)
                sp = cross3D(os, op)
                pq = cross3D(op, oq)

                # Reflect points across great circles
                # |qs| = 1, oq.qs = 0, and k = -op.qs
                kp = sum([op[t]*qs[t] for t in range(3)])
                kq = sum([oq[t]*sp[t] for t in range(3)])
                ks = sum([os[t]*pq[t] for t in range(3)])
                knp = sum([on[t]*qs[t] for t in range(3)])
                knq = sum([on[t]*sp[t] for t in range(3)])
                kns = sum([on[t]*pq[t] for t in range(3)])
                newp = [0.0 if abs(x) < EPSILON else x for x in
                        [op[t] - 2*kp*qs[t] for t in range(3)]] + [0]
                newq = [0.0 if abs(x) < EPSILON else x for x in
                        [oq[t] - 2*kq*sp[t] for t in range(3)]] + [0]
                news = [0.0 if abs(x) < EPSILON else x for x in
                        [os[t] - 2*ks*pq[t] for t in range(3)]] + [0]
                newnp = [0.0 if abs(x) < EPSILON else x for x in
                         [on[t] - 2*knp*qs[t] for t in range(3)]] + [0]
                newnq = [0.0 if abs(x) < EPSILON else x for x in
                         [on[t] - 2*knq*sp[t] for t in range(3)]] + [0]
                newns = [0.0 if abs(x) < EPSILON else x for x in
                         [on[t] - 2*kns*pq[t] for t in range(3)]] + [0]

                # Identify triangle points with unique coordinate strings
                nump = '{:=+04.0f}{:=+04.0f}{:=+04.0f}'.format(*op)
                numq = '{:=+04.0f}{:=+04.0f}{:=+04.0f}'.format(*oq)
                nums = '{:=+04.0f}{:=+04.0f}{:=+04.0f}'.format(*os)
                nuwp = '{:=+04.0f}{:=+04.0f}{:=+04.0f}'.format(*newp)
                nuwq = '{:=+04.0f}{:=+04.0f}{:=+04.0f}'.format(*newq)
                nuws = '{:=+04.0f}{:=+04.0f}{:=+04.0f}'.format(*news)
                nuwnp = '{:=+04.0f}{:=+04.0f}{:=+04.0f}'.format(*newnp)
                nuwnq = '{:=+04.0f}{:=+04.0f}{:=+04.0f}'.format(*newnq)
                nuwns = '{:=+04.0f}{:=+04.0f}{:=+04.0f}'.format(*newns)

                # Make new triangles from results and remove old triangle
                numa = ''.join(sorted([nuwp, numq, nums])) + nuwnp
                numb = ''.join(sorted([nump, nuwq, nums])) + nuwnq
                numc = ''.join(sorted([nump, numq, nuws])) + nuwns
                if numa not in tricoords:
                    tricoords.append(numa)
                    triangles.append([newp, oq, os, newnp])
                    if nuwnp not in pointcoords:
                        if selection != 'b' or depth % 2 != 1:
                            points.append(newnp)
                        pointcoords.append(nuwnp)
                if numb not in tricoords:
                    tricoords.append(numb)
                    triangles.append([op, newq, os, newnq])
                    if nuwnq not in pointcoords:
                        if selection != 'b' or depth % 2 != 1:
                            points.append(newnq)
                        pointcoords.append(nuwnq)
                if numc not in tricoords:
                    tricoords.append(numc)
                    triangles.append([op, oq, news, newns])
                    if nuwns not in pointcoords:
                        if selection != 'b' or depth % 2 != 1:
                            points.append(newns)
                        pointcoords.append(nuwns)
                triangles.remove(triangle)

                # Find the square of the side length
                if side == 0:
                    if selection == 'a':
                        side = 1
                    elif selection == 'b':
                        side = sum([(newnp[t]-newnq[t])**2 for t in range(3)])
                    else:
                        side = (max(knp, knq, kns)*2)**2
            depth -= 1
        return points, side

    def _wythoff_snub(self, p, q, s):

        # Take Wythoff symbol of snub polyhedron and return its coordinates.
        r = RADIUS
        snubdepth = 4
        snubfreq = 1024
        snubradius = pi/8
        snubdiv = 8
        snubtheta = 0.1
        snubphi = 0.1
        variance = 1e16

        # Check Wythoff symbol validity
        lpq = math.acos((math.cos(pi/s) + math.cos(pi/p)*math.cos(pi/q))/
                        (math.sin(pi/p)*math.sin(pi/q)))
        lqs = math.acos((math.cos(pi/p) + math.cos(pi/q)*math.cos(pi/s))/
                        (math.sin(pi/q)*math.sin(pi/s)))
        lsp = math.acos((math.cos(pi/q) + math.cos(pi/s)*math.cos(pi/p))/
                        (math.sin(pi/s)*math.sin(pi/p)))

        # Fundamental triangle
        triangles = [[[0.0 if abs(x) < EPSILON else x for x in
                       convert(point, True)] for point in
                      [(r,0,0,pi/2), (r,0,lpq,pi/2), (r,pi/p,lsp,pi/2)]]]
        op = triangles[0][0]
        oq = triangles[0][1]
        os = triangles[0][2]
        pq = cross3D(op, oq)
        qs = cross3D(oq, os)
        sp = cross3D(os, op)

        # Systematically divide fundamental triangle to find closest region
        phi = max(lsp, lpq)
        while phi > 0:
            theta = pi/p
            while theta > 0:
                on = convert((r, theta, phi, pi/2), True)
                knp = sum([on[t]*qs[t] for t in range(3)])
                knq = sum([on[t]*sp[t] for t in range(3)])
                kns = sum([on[t]*pq[t] for t in range(3)])
                newnp = [0.0 if abs(x) < EPSILON else x for x in
                         [on[t] - 2*knp*qs[t] for t in range(3)]]
                newnq = [0.0 if abs(x) < EPSILON else x for x in
                         [on[t] - 2*knq*sp[t] for t in range(3)]]
                newns = [0.0 if abs(x) < EPSILON else x for x in
                         [on[t] - 2*kns*pq[t] for t in range(3)]]
                dpq = sum((newnp[t] - newnq[t])**2 for t in range(3))
                dqs = sum((newnq[t] - newns[t])**2 for t in range(3))
                dsp = sum((newns[t] - newnp[t])**2 for t in range(3))
                mean = (dpq + dqs + dsp)/3
                var = (dpq-mean)**2 + (dqs-mean)**2 + (dsp-mean)**2
                if var < variance:
                    variance = var
                    n = on
                theta -= snubtheta/phi
            phi -= snubphi

        # Randomly sample the region to find the closest point
        while snubdepth > 0:
            trials = snubfreq
            n = convert(n, False)
            thetalow = n[1] - snubradius
            thetahigh = n[1] + snubradius
            philow = n[2] - snubradius
            phihigh = n[2] + snubradius
            if thetalow < 0:
                thetalow = 0
            if thetahigh > pi/p:
                thetahigh = pi/p
            if philow < 0:
                philow = 0
            if phihigh > max(lsp, lpq):
                phihigh = max(lsp, lpq)
            while trials > 0:
                # Find random points in spherical coordinates
                randtheta = random.uniform(thetalow, thetahigh)
                randphi = random.uniform(philow, phihigh)
                on = convert((r, randtheta, randphi, pi/2), True)
                knp = sum([on[t]*qs[t] for t in range(3)])
                knq = sum([on[t]*sp[t] for t in range(3)])
                kns = sum([on[t]*pq[t] for t in range(3)])
                newnp = [0.0 if abs(x) < EPSILON else x for x in
                         [on[t] - 2*knp*qs[t] for t in range(3)]]
                newnq = [0.0 if abs(x) < EPSILON else x for x in
                         [on[t] - 2*knq*sp[t] for t in range(3)]]
                newns = [0.0 if abs(x) < EPSILON else x for x in
                         [on[t] - 2*kns*pq[t] for t in range(3)]]
                dpq = sum((newnp[t] - newnq[t])**2 for t in range(3))
                dqs = sum((newnq[t] - newns[t])**2 for t in range(3))
                dsp = sum((newns[t] - newnp[t])**2 for t in range(3))
                mean = (dpq + dqs + dsp)/3
                var = (dpq-mean)**2 + (dqs-mean)**2 + (dsp-mean)**2
                if var < variance:
                    variance = var
                    n = on
                trials -= 1
            snubradius /= snubdiv
            snubdepth -= 1

        return self._schwarz('b', triangles, n)

    def render(self):
        # Clear the canvas, center the frame, and display the sphere.
        self.delete(tk.ALL)
        w = self.winfo_width()//2
        h = self.winfo_height()//2

        if w != 0 and h != 0 and self.parent.sphere.get() == 1:
            points = [(-point[0]+w, point[1]+h) for point in
                      self._view(self._sphere.get_points())]
            edges = self._sphere.get_edges()
            for edge in edges:
                self.create_line(points[edge[0]], points[edge[1]],
                                 fill='#FD9', width=1)
            axes = [(-point[0]+w, point[1]+h) for point in
                    self._view(self._sphere.get_axes())]
            self.create_line(axes[0],axes[1], fill='#F00', width=5)
            self.create_line(axes[2],axes[3], fill='#0F0', width=5)
            self.create_line(axes[4],axes[5], fill='#00F', width=5)

        if self._currPolytope.get_points():
            self.parent.set_status('faces')
            points = [(-point[0]+w, point[1]+h) for point in
                      self._view(self._currPolytope.get_points())]
            camera = convert([self.parent.distance.get()]+self._viewAxis,True)

            if self.parent.wire.get() == 0:     # Display by drawing polygons
                self._currPolytope.shade_faces(camera)
                faces = self._currPolytope.get_faces()
                centres = self._currPolytope.get_face_centres()
                colours = self._currPolytope.get_face_colours()
                distances = {}
                for face in faces:
                    distances[face] = distance(centres[face], camera)
                order = sorted(distances, key=distances.get, reverse=True)
                for face in order:
                    if colours[face] == [0, 0, 0]:
                        continue
                    colour = [format(int(num), '02x') for num in colours[face]]
                    rgb = '#' + ''.join(colour)
                    edges = [points[side] for side in faces[face]]
                    self.create_polygon(edges, outline='#000', width=3, fill=rgb)

            elif self.parent.wire.get() == 1:   # Display by drawing lines
                edges = self._currPolytope.get_edges()
                centres = self._currPolytope.get_edge_centres()
                colours = self._currPolytope.get_point_colours()
                for colour in colours:
                    self.create_oval([p-5 for p in points[colour[0]]],
                                     [p+5 for p in points[colour[0]]],
                                     fill=colour[1])

                distances = {}
                for i in range(len(edges)):
                    distances[i] = distance(centres[i], camera)
                order = sorted(distances, key=distances.get, reverse=True)
                quintile = 0            # Group edges into distance quintiles
                fifth = len(order)/5
                greys = ['#EEE', '#BBB', '#999', '#666', '#333', '#000']
                count = 0
                for e in order:
                    if count >= quintile*fifth:
                        quintile += 1
                    count += 1
                    self.create_line(points[edges[e][0]], points[edges[e][1]],
                                     fill=greys[quintile], width=quintile)

    def _reset(self):
        self.delete(tk.ALL)
        self._sphere = Sphere(SPHERENUM, RADIUS)
        self.set_rotaxis('xw')
        self.set_viewaxis([0, 0, pi/2])
        self.parent.change('reset')
        if self.get_data('star') == 1:
            self.parent.change('wire')



class Polytope():

    """
    Drawing class that stores vertex coordinates and manages rotations.

    Public methods:
    shade_faces
    get_points
    get_edges
    get_faces
    get_face_sides
    get_edge_centres
    get_face_centres
    get_point_colours
    get_face_colours
    set_rotaxis
    rotate

    Object variables:
    star
    """

    def __init__(self, data):
        """Construct Polytope class."""
        if data:
            self._points = data[0]
            self._edges = data[1]
            self._pointColours = data[2]
            self._set_faces()
            self._set_edge_centres()
            self._set_face_centres()
            self._set_colours()
            if len(self._faces)/len(self._points) < 1/3:
                # Not enough faces, probably because of canvas._wythoff_snub
                self.star = False
                self._points = []
            else:
                self._remove_faces()
        else:
            self.star = False
            self._points = []
            self._edges = []
            self._faces = []
            self._faceSides = []
            self._pointColours = []
            self._faceColours = []
            self._edgeCentres = []
            self._faceCentres = []

    def _set_faces(self):
        """Create a dictionary of faces using only a list of edges."""
        self._graph = {}
        for edge in self._edges:    # setdefault ensures that the key exists
            self._graph.setdefault(edge[0], list()).append(edge[1])
            self._graph.setdefault(edge[1], list()).append(edge[0])
        self._faces = {}
        self._faceSides = {i:[] for i in range(3,21)}   # 13 to 20 are stars
        self._visited = set()
        self._triangles = set()
        i = 3           # Iterate across all polygon side numbers
        while i < 11:
            j = 0       # Iterate across all vertices in graph
            while j < len(self._points):
                for start in self._graph[j]:
                    faces = self._bfs(j, start, i)
                    if faces:       # At most two faces can go from start to j
                        for face in faces:
                            if self._has_star(face) == True:
                                self._faceSides[i+10].append(len(self._faces))
                            else:
                                self._faceSides[i].append(len(self._faces))
                            self._faces[len(self._faces)] = face
                j += 1
            i += 1

    def _bfs(self, end, start, length):
        """Breadth-first search to find the only path between start and end."""
        # Run the loop explicitly because triangles do not have enough edges
        # to find two by pathEnd and their vertices can be stored in any order
        frontier = []
        paths = []
        faces = []
        normals = []
        for vertex in self._graph[start]:
            if vertex == end:                   # Avoid drawing lines as faces
                continue
            frontier.append(vertex)
            paths.append([start, vertex])
            u = [self._points[start][i] - self._points[end][i] for i in range(3)]
            v = [self._points[vertex][i] - self._points[start][i] for i in range(3)]
            normals.append(cross3D(u,v))  # Faces must be coplanar

        # If we're finding triangles, we don't have to worry about the frontier
        if length == 3:
            while frontier:
                vertex = frontier.pop()
                if end in self._graph[vertex]:
                    triangle = tuple(sorted([end, start, vertex]))
                    if triangle in self._triangles:
                        continue
                    self._triangles.add(triangle)
                    for i in range(3):
                        pathEnd = [triangle[(i+j)%3] for j in range(3)]
                        two = tuple(sorted([pathEnd, pathEnd[::-1]])[0])
                        self._visited.add(two)
                    faces.append((end, start, vertex))

        # Otherwise, run the loop once without finding pathEnd and two
        else:
            depthTime = len(frontier)
            while depthTime > 0:
                vertex = frontier.pop()
                path = paths.pop()
                normal = normals.pop()
                frontier = [neighbour for neighbour
                            in self._graph[vertex]] + frontier
                paths = [path + [neighbour] for neighbour
                         in self._graph[vertex]] + paths
                normals = [normal for neighbour
                           in self._graph[vertex]] + normals
                depthTime -= 1
        if len(frontier) == 0:
            return faces

        # +1 depth represents depths of next layer;
        # +2 start already went to vertex in _set_faces();
        # +3, +4 loop already ran for the first two layers above
        depth = 4
        depthTime = len(frontier)
        while depth <= length:
            vertex = frontier.pop()
            path = paths.pop()
            normal = normals.pop()
            pathEnd = path[-3:] # Two consecutive edges belong to only one face
            two = tuple(sorted([pathEnd, pathEnd[::-1]])[0])
            if two not in self._visited and two[0] != two[2]:
                a = self._points[pathEnd[0]]      # Compare new edge to
                b = self._points[pathEnd[1]]      # past edges for coplanarity
                c = self._points[pathEnd[2]]
                u = [b[i]-a[i] for i in range(3)]
                v = [c[i]-b[i] for i in range(3)]
                new = cross3D(u,v)
                coplanar = True
                for i in range(3):
                    if (new[i] - normal[i]) > EPSILON:
                        coplanar = False
                if coplanar and depth == length:
                    for neighbour in self._graph[vertex]:
                        if neighbour == end:
                            path.append(end)
                            sides = []
                            for i in range(len(path)):
                                three = [path[(i+j)%len(path)] for j in range(3)]
                                two = tuple(sorted([three, three[::-1]])[0])
                                sides.append(two)
                                if two in self._visited:
                                    break
                            else:   # Only if all sides are unvisited
                                self._visited.update(sides)
                                faces.append(tuple(path))   # Immutable stable
                elif coplanar:
                    frontier = [neighbour for neighbour
                                in self._graph[vertex]] + frontier
                    paths = [path + [neighbour] for neighbour
                             in self._graph[vertex]] + paths
                    normals = [normal for neighbour
                               in self._graph[vertex]] + normals
            depthTime -= 1
            if depthTime == 0:
                if len(frontier) == 0:
                    break
                else:
                    depth += 1
                    depthTime = len(frontier)
        return faces

    def _has_star(self, vertices):
        """Check for star polygons by seeing if a polygon's sides intersect."""
        sides = [(vertices[i], vertices[(i+1)%len(vertices)])
                 for i in range(len(vertices))]
        a = self._points[sides[0][0]]
        b = self._points[sides[0][1]]
        ab = [b[i] - a[i] for i in range(3)]
        for side in sides:
            c = self._points[side[0]]
            d = self._points[side[1]]
            if a == c or b == c or a == d or b == d:
                continue
            bc = [c[i] - b[i] for i in range(3)]
            bd = [d[i] - b[i] for i in range(3)]
            if self._orientation(ab,bc) != self._orientation(ab,bd):
                ac = [c[i] - a[i] for i in range(3)]
                cd = [d[i] - c[i] for i in range(3)]
                if self._orientation(ac,cd) != self._orientation(bc,cd):
                    return True
        return False

    def _orientation(self, ab, bc):
        """Return the relative orientation of three points a, b, and c."""
        orientation = sum([cross3D(ab,bc)[i] for i in range(3)])
        if orientation < EPSILON:
            return 0
        return math.copysign(1, orientation)

    def _set_edge_centres(self):
        """Create a list of centres using a list of edges and their points."""
        self._edgeCentres = [[0,0,0,0] for i in range(len(self._edges))]
        for i in range(len(self._edges)):
            for j in range(4):
                self._edgeCentres[i][j] = (self._points[self._edges[i][0]][j] +
                                           self._points[self._edges[i][1]][j])/2

    def _set_face_centres(self):
        """Create a dictionary of centres using faces and their vertices."""
        self._faceCentres = {face:[0, 0, 0, 0] for face in self._faces}
        for face in self._faces:
            for point in self._faces[face]:
                for i in range(4):
                    self._faceCentres[face][i] += self._points[point][i]
            for i in range(4):
                self._faceCentres[face][i] /= len(self._faces[face])

    def _set_colours(self):
        """Create a dictionary of random colours applied to each face."""
        self._baseColours = {}
        self._faceColours = {}
        for face in self._faces:
            r = 255
            g = 0
            b = 0
            self._baseColours[face] = [r,g,b]
            self._faceColours[face] = [r,g,b]

    def _remove_faces(self):
        """Remove extraneous faces, depending on polytope characteristics."""
        number = sum([len(self._faceSides[i]) for i in range(3,21)])
        if number > 1:          # Not a polygon, remove lots of faces
            self._remove_non_faces()
            self._remove_odd_faces()
            if number > 92:
                self._remove_small_faces()
        for i in range(3,21):   # Replace reference to faces with a count
            self._faceSides[i] = len(self._faceSides[i])
        for i in range(11,21):
            if self._faceSides[i] > 0:
                self.star = True
                break
        else:                   # Not a star, remove inside faces
            self.star = False
            self._remove_inside_faces()

    def _remove_non_faces(self):
        """Remove types of faces that do not exist."""
        nope = [9,13,14,19]
        for i in nope:
            for j in self._faceSides[i]:
                self._faces.pop(j)
                self._faceCentres.pop(j)
            self._faceSides[i] = []

    def _remove_odd_faces(self):
        """Remove types of faces that have an odd number of members."""
        for i in self._faceSides:
            if len(self._faceSides[i])%2 == 1:
                for j in self._faceSides[i]:
                    self._faces.pop(j)
                    self._faceCentres.pop(j)
                self._faceSides[i] = []

    def _remove_small_faces(self):
        """Remove types of faces that have a small number of members."""
        for i in self._faceSides:
            if len(self._faceSides[i]) < 5:
                for j in self._faceSides[i]:
                    self._faces.pop(j)
                    self._faceCentres.pop(j)
                self._faceSides[i] = []

    def _remove_inside_faces(self):
        """Remove faces that are closer to the centre than normal."""
        if len(self._faces) < 32 and self._faceSides[3]/len(self._faces) < 0.6:
            depth = 5000            # Larger depth so outside faces are kept
        else:
            depth = 3000            # Smaller depth so inside faces are removed
        surface = distance(self._faceCentres[0]) - depth
        iterDict = dict(self._faces)        # So dictionary does not change size
        for i in iterDict:
            if distance(self._faceCentres[i]) < surface:
                self._faceSides[len(self._faces[i])] -= 1
                self._faces.pop(i)
                self._faceCentres.pop(i)

    def shade_faces(self, viewAxis):
        """Shade according to the angle between the light ray and the normal."""
        if len(self._faces) == 1:   # Shade both faces if polygon by using abs()
            light = [viewAxis[i] - self._faceCentres[0][i] for i in range(3)]
            a = self._points[self._faces[0][0]]
            b = self._points[self._faces[0][1]]
            c = self._points[self._faces[0][2]]
            u = [a[i] - b[i] for i in range(3)]
            v = [b[i] - c[i] for i in range(3)]
            normal = cross3D(u, v)        # self._centres[0] = [0,0,0,0]
            denominator = math.sqrt(abs(distance(normal) * distance(light)))
            cosine = sum([light[i]*normal[i]/denominator for i in range(3)])
            for i in range(3):
                shade = self._baseColours[0][i]
                self._faceColours[0][i] = abs(shade * cosine)
        else:
            for face in self._faces:
                light = [viewAxis[i] - self._faceCentres[face][i] for i in range(3)]
                normal = self._faceCentres[face]
                denominator = math.sqrt(abs(sum([x**2 for x in normal])
                                            * sum([x**2 for x in light])))
                cosine = sum([light[i]*normal[i]/denominator for i in range(3)])
                for i in range(3):  # Lambert's cosine law for diffuse reflectors
                    shade = self._baseColours[face][i]  # Positive, not brighter
                    self._faceColours[face][i] = max(0, shade * cosine)

    def get_points(self):
        """Return a list of points of the polytope."""
        return self._points

    def get_edges(self):
        """Return a list of edges of the polytope."""
        return self._edges

    def get_faces(self):
        """Return a dictionary of faces of the polytope."""
        return self._faces

    def get_face_sides(self):
        """Return a dictionary of numbers of faces with some amount of sides."""
        return self._faceSides

    def get_edge_centres(self):
        """Return a list of centres of the edges of the polytope."""
        return self._edgeCentres

    def get_face_centres(self):
        """Return a dictionary of centres of the faces of the polytope."""
        return self._faceCentres

    def get_point_colours(self):
        """Return a list of colours of the points of the polytope."""
        return self._pointColours

    def get_face_colours(self):
        """Return a dictionary of colours of the faces of the polytope."""
        return self._faceColours

    def set_rotaxis(self, axes):
        """Set the perpendicular unit axes of rotation of the polytope."""
        self._axis_i = normalize(axes[0])
        self._axis_j = normalize(axes[1])

    def rotate(self, rotAngle):
        """
        Rotate the current polytope by rotAngle about the plane
        defined by i and j, which are perpendicular coplanar 4-vectors.
        """
        i = self._axis_i
        j = self._axis_j
        cos = math.cos(rotAngle)
        sin = math.sin(rotAngle)
        n = 0
        for n in range(len(self._points)):
            p = self._points[n]
            r = sum([p[t]*i[t] for t in range(4)])
            s = sum([p[t]*j[t] for t in range(4)])
            I = [i[t]*r+j[t]*s for t in range(4)]
            ip = [p[t]-I[t] for t in range(4)]
            if ip != [0,0,0,0]:    # If I = P, then there is no rotation
                iq = cross4D(ip, i, j, ip)
                self._points[n] = [ip[t]*cos + iq[t]*sin + I[t] for t in range(4)]
        self._set_edge_centres()
        self._set_face_centres()


class Sphere():

    """
    Drawing class that stores rotations and latitude and longitude lines.

    Public methods:
    get_points
    get_edges
    get_axes
    set_rotaxis
    rotate
    """

    def __init__(self, number, radius):
        """Construct Sphere class."""
        n = number
        r = radius
        thetas = [2*k*pi/n for k in range(n)]
        phis = [k*pi/n for k in range(1,n)]
        self._points = [(0,0,r,0),(0,0,-r,0)]
        self._edges = [(0, k*(n-1)+2) for k in range(n)]
        self._edges.extend([(1, (k+1)*(n-1)+1) for k in range(n)])
        for t in range(n-1):
            self._points.extend([convert((r, thetas[t], phis[k], pi/2), True)
                                 for k in range(n-1)])
            self._edges.extend([(t*(n-1)+k+2, t*(n-1)+k+3)
                                for k in range(n-2)])
            self._edges.extend([(k*(n-1)+t+2, ((k+1)*(n-1)%((n-1)*n)+t+2))
                                for k in range(n)])
        self._points.extend([convert((r, thetas[n-1], phis[k], pi/2), True)
                             for k in range(n-1)])
        self._edges.extend([((n-1)*(n-1)+k+2, (n-1)*(n-1)+k+3)
                            for k in range(n-2)])
        self._axes = [(2*r,0,0,0), (-2*r,0,0,0),
                      (0,2*r,0,0), (0,-2*r,0,0),
                      (0,0,2*r,0), (0,0,-2*r,0)]

    def get_points(self):
        """Return a list of points of the sphere."""
        return self._points

    def get_edges(self):
        """Return a list of edges of the sphere."""
        return self._edges

    def get_axes(self):
        """Return a list of points of the Cartesian axes."""
        return self._axes

    def set_rotaxis(self, axes):
        """Set the axis of rotation of the sphere."""
        self._axis_i = axes[0]
        self._axis_j = axes[1]

    def rotate(self, rotAngle):
        """
        Rotate the current sphere by rotAngle about the plane
        defined by i and j, which are perpendicular coplanar 4-vectors.
        """
        i = self._axis_i
        j = self._axis_j
        cos = math.cos(rotAngle)
        sin = math.sin(rotAngle)
        n = 0
        for n in range(len(self._points)):
            p = self._points[n]
            r = sum([p[t]*i[t] for t in range(4)])
            s = sum([p[t]*j[t] for t in range(4)])
            I = [i[t]*r+j[t]*s for t in range(4)]
            ip = [p[t]-I[t] for t in range(4)]
            if ip != [0,0,0,0]:    # If I = P, then there is no rotation
                iq = cross4D(ip, i, j, ip)
                self._points[n] = [ip[t]*cos + iq[t]*sin + I[t] for t in range(4)]
        for n in range(len(self._axes)):
            p = self._axes[n]
            r = sum([p[t]*i[t] for t in range(4)])
            s = sum([p[t]*j[t] for t in range(4)])
            I = [i[t]*r+j[t]*s for t in range(4)]
            ip = [p[t]-I[t] for t in range(4)]
            if ip != [0,0,0,0]:    # If I = P, then there is no rotation
                iq = cross4D(ip, i, j, ip)
                self._axes[n] = [ip[t]*cos + iq[t]*sin + I[t] for t in range(4)]



root = tk.Tk()
main = Main(root)
