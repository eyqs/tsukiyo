"""
Polytope Player v0.80

This program lets you play with polytopes!
Light intensity is now controlled by a sliding scale by Main,
using change and not using set_status, set_light, nor get_data.
"""
import tkinter as tk
import tkinter.ttk as ttk
import math
import random

TITLE = 'Polytope Player v0.80'
DESCRIPTION = '\nThis script lets you play with polytopes.'
WIDTH = 600
HEIGHT = 550
pi = math.pi
EPSILON = 0.00001

RADIUS = 100    # Radius of the initial polytope
RETINA = 10     # Distance between focus and projection plane
ZOOM = 50       # ZOOM * RADIUS * RETINA / 2 gives maximum possible zoom
                # ZOOM * RADIUS * RETINA gives maximum possible distance
                # ZOOM * RADIUS * RETINA / 1000 gives the least distance
FADEDELAY = 1000# Time for bad input status to fade away
DELAY = 28      # Time between polling when mouse is held on a button
ROTANGLE = pi/24# 28 ms per pi/24 rotation = 3 rotations every 4 seconds
SPHERENUM = 12  # Number of longitude/latitude sections on the radial sphere
SNUBABLE = (['2','3','3'], ['2','3','4'], ['2','3','5'], ['2','3','5/3'],
            ['2','5','5/2'], ['2','5','5/3'], ['2','3/2','3/2'],
            ['2','3/2','4'], ['2','3/2','4/3'], ['2','3/2','5/3'],
            ['3/2','4','4'], ['3','5','5/3'])   # All the (|pqr) combinations
POLYGONS = {0:'notgon', 1:'monogon', 2:'digon', # Polygon names
            3:'triangle', 4:'square', 5:'pentagon', 6:'hexagon',
            7:'heptagon', 8:'octagon', 9:'nonagon', 10:'decagon',
            13:'triangle', 14:'line', 15:'pentagram', 16:'hexagram',
            17:'heptagram', 18:'octagram', 19:'nonagram', 20:'decagram'}
COLOURS = [('#000', '#F00', '#00F'),    # Temporary hardcoded constant colours
           ('#EEE', '#BBB', '#999', '#666', '#333', '#000'),
           {3:'#719',4:'#1B1',5:'#04D',6:'#F8C',7:'#630',8:'#E00',9:'#9DF',
           10:'#098', 11:'#F70', 12:'#9F7', 13:'#C07', 14:'#FF1', 15:'#7BF',
           16:'#999', 17:'#8F0', 18:'#B7F', 19:'#90E', 20:'#030', 21:'#0CA'},
           ('#FD9', '#F00', '#0F0', '#00F'), ('#CCC', '#FFF', '#F00')]



def distance(head, tail=[0,0,0,0]):
    """
    Find the distance squared between two points.

    head: the position vector of the first point (list)
    tail: the position vector of the second point (list)
          default [0,0,0,0] to find the magnitude of head
    return: the distance squared between head and tail (float)
    """
    return sum([(head[i] - tail[i])**2 for i in range(len(head))])

def normalize(points, unit=[1]):
    """
    Normalize a vector.

    points: the first vector (list)
    unit: the second vector (list), default [1] to make unit vector
    return: vector with magnitude of unit in the direction of points (list)
    """
    norm = math.sqrt(distance(points))
    if norm == 0:
        return [0 for x in points]
    magnitude = math.sqrt(distance(unit))
    return [x/norm*magnitude for x in points]

def cross3D(u, v, unit=[1]):
    """
    Find the 3D cross product of two vectors.

    u: the first vector (list, len=3)
    v: the second vector (list, len=3)
    unit: the third vector (list), default [1] to make unit vector
    return: vector with magnitude of unit perpendicular to u and v (list)
    """
    uxv = (u[1]*v[2]-u[2]*v[1],
           u[2]*v[0]-u[0]*v[2],
           u[0]*v[1]-u[1]*v[0])
    return normalize(uxv, unit)

def cross4D(u, v, w, unit=[1]):
    """
    Find the 4D cross product of two vectors.

    u: the first vector (list, len=4)
    v: the second vector (list, len=4)
    w: the third vector (list, len=4)
    unit: the fourth vector (list), default [1] to make unit vector
    return: vector with magnitude of unit perpendicular to u, v, and w (list)
    """
    uvw = [u[1]*(v[2]*w[3]-v[3]*w[2]) - u[2]*(v[1]*w[3]-v[3]*w[1]) +
           u[3]*(v[1]*w[2]-v[2]*w[1]),
           -u[0]*(v[2]*w[3]-v[3]*w[2]) + u[2]*(v[0]*w[3]-v[3]*w[0])
           -u[3]*(v[0]*w[2]-v[2]*w[0]),
           u[0]*(v[1]*w[3]-v[3]*w[1]) - u[1]*(v[0]*w[3]-v[3]*w[0]) +
           u[3]*(v[0]*w[1]-v[1]*w[0]),
           -u[0]*(v[1]*w[2]-v[2]*w[1]) + u[1]*(v[0]*w[2]-v[2]*w[0])
           -u[2]*(v[0]*w[1]-v[1]*w[0])]
    return normalize(uvw, unit)

def satisfy_axis_restrictions(axis):
    """
    Make an axis in spherical coordinates satisfy the restrictions:
    0 <= theta < 2pi, 0 <= phi < pi, 0 <= omega < pi.

    axis: the spherical coordinates of the axis, excluding r (list, len=3)
    return: equivalent coordinates that satisfy the restrictions (list, len=3)
    """
    for angle in axis:
        while angle >= 2*pi:
            angle -= 2*pi
        while angle < 0:
            angle += 2*pi
    if axis[1] > pi:
        axis[1] = 2*pi - axis[1]
    if axis[2] > pi:
        axis[2] = 2*pi - axis[2]
    return axis

def convert(point, toCartesian):
    """
    Convert between spherical and Cartesian coordinates.

    point: the position vector of the point (list, len=4)
    toCartesian: whether to convert from spherical to Cartesian (bool)
    return: the converted coordinates (list, len=4)
    """

    # Spherical to Cartesian
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
            phi = 0         # Avoiding division by zero
        else:
            phi = math.acos(point[2]/
                            math.sqrt(point[2]**2+point[1]**2+point[0]**2))
        if r == 0:          # r = math.sqrt(point[3]**2 + ... )
            omega = 0
        else:
            omega = math.acos(point[3]/r)
        return (r, theta, phi, omega)



class Main(ttk.Frame):

    """
    GUI class that manages all windows and actions except the canvas.

    Public methods:
    set_status          Display status changes on the status bar.
    change              Change GUI values and re-render.
    close               Close the program.

    Public variables:
    parent              Parent of class (tk.Tk)
    canvas              Instance of Canvas class (Canvas)
    statusLabel         To allow statusText to clear itself (ttk.Label)
    statusText          To display the current status (tk.StringVar)
    inputText           To display the current input (tk.StringVar)
    bBrBtn              To allow the button to be disabled (ttk.Button)
    lint                To keep track of light intensity (tk.DoubleVar)
    sphere              To keep track of sphere check (tk.IntVar)
    wire                To keep track of wire check (tk.IntVar)
    wireCheck           To allow the check to be disabled (ttk.Checkbutton)
    zoom                To keep track of the current zoom (tk.IntVar)
    dist                To keep track of the current distance (tk.IntVar)
    unitDist            To change dist depending on the distance (int)

    Private methods:
    __init__            Construct Main class.
    _make_menus         Initialize dropdown menus.
    _make_popups        Create the actual pop-up windows.
    _initUI             Initialize GUI placement and bind buttons.
    _poll               Handle events when buttons are pressed.
    _mouse_down
    _mouse_up
    _press

    Private variables:
    _mousePressed       To keep track of when mouse is pressed down (bool)
    _leftBtn            To avoid garbage collection (tk.PhotoImage)
    _rightBtn
    _upBtn
    _downBtn
    _after_pollID       To call _poll again after DELAY milliseconds (str)
    """

    def __init__(self, parent):
        """
        Construct Main class.
        parent: the parent of main (tk.Tk)
        """
        self._mousePressed = False
        self.parent = parent
        self.parent.title(TITLE)
        self.parent.geometry(
            '{}x{}+{}+{}'.format(
                WIDTH, HEIGHT,      # Center the program window
                (self.parent.winfo_screenwidth() - WIDTH) // 2,
                (self.parent.winfo_screenheight() - HEIGHT) // 2))
        self.parent.minsize(WIDTH, HEIGHT)
        self._make_menus()
        ttk.Frame.__init__(self, parent)
        self.pack(fill=tk.BOTH, expand=1)
        self._initUI()

    def _make_menus(self):
        # Initialize dropdown menus.
        menuBar = tk.Menu(self.parent)
        self.parent.config(menu=menuBar)
        fileMenu = tk.Menu(menuBar)
        # underline sets position of keyboard shortcut
        fileMenu.add_command(label='About', underline=0,
                             command=lambda: self._make_popups('About'))
        fileMenu.add_command(label='Help', underline=0,
                             command=lambda: self._make_popups('Help'))
        fileMenu.add_command(label='Exit', underline=1,
                             command=self.close)
        menuBar.add_cascade(label='File', menu=fileMenu, underline=0)

    def _make_popups(self, popUpType):

        # Create the actual pop-up windows.
        # popUpType: the type of pop-up window to make (str)
        #            'About', 'Help'

        # Set individual window data based on popUpType
        if popUpType == 'About':
            titleText = 'About this program...'
            messageText = '\n'.join((TITLE, DESCRIPTION))
            buttonText = 'OK'
            frameWidth = 400
            frameHeight = 200
        elif popUpType == 'Help':
            titleText = 'Help'
            messageText = ('Click the buttons to experience the magic!')
            buttonText = 'Dismiss'
            frameWidth = 400
            frameHeight = 120

        # Create pop-up window, each with title, message, and close button
        popUpFrame = tk.Toplevel(self.parent, background=COLOURS[4][0])
        popUpFrame.title(titleText)
        popUpMessage = tk.Message(popUpFrame, text=messageText,
                                  width=frameWidth, background=COLOURS[4][0])
        popUpMessage.pack()
        popUpButton = ttk.Button(popUpFrame, text=buttonText,
                                 command=popUpFrame.destroy)
        popUpButton.pack()

        # Center the pop-up with respect to the main window
        popUpFrame.geometry('{}x{}+{}+{}'.format(
            frameWidth, frameHeight,
            self.parent.winfo_rootx() +
            (self.parent.winfo_width() - frameWidth) // 2,
            self.parent.winfo_rooty() +
            (self.parent.winfo_height() - frameHeight) // 2))

        # Set all focus on the pop-up and stop mainloop in main window
        popUpFrame.grab_set()
        popUpButton.focus()
        self.wait_window(popUpFrame)

    def _initUI(self):

        # Initialize GUI placement and bind buttons.

        # Must keep references to avoid garbage-collection
        self._leftBtn = tk.PhotoImage(file='leftButtonTwentyFour.gif')
        self._rightBtn = tk.PhotoImage(file='rightButtonTwentyFour.gif')
        self._upBtn = tk.PhotoImage(file='upButtonEleven.gif')
        self._downBtn = tk.PhotoImage(file='downButtonEleven.gif')

        # Set consistent background colour to all ttk widgets
        style = ttk.Style()
        style.configure('TFrame', background=COLOURS[4][0])
        style.configure('TLabel', background=COLOURS[4][0])
        style.configure('TButton', background=COLOURS[4][0])
        style.configure('TCheckbutton', background=COLOURS[4][0])

        # Grid main widget frames
        # Title on top, canvas and guiRight on middle, guiBottom on bottom

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        titleLabel = ttk.Label(self, text=TITLE)
        titleLabel.grid(row=0, column=0, columnspan=2, pady=10)
        self.canvas = Canvas(self)
        self.canvas.grid(row=1, column=0, padx=10,
                         sticky=tk.N+tk.E+tk.S+tk.W)
        guiRight = ttk.Frame(self)
        # 10px padding on right but 0px on left since canvas is already padded
        guiRight.grid(row=1, column=1, padx=(0,10), sticky=tk.N)
        guiBottom = ttk.Frame(self)
        guiBottom.columnconfigure(0, weight=1)
        guiBottom.grid(row=2, column=0, columnspan=2,
                        padx=10, pady=(0,20), sticky=tk.E+tk.W)


        # Grid guiRight widgets: 12 rows, 3 columns

        # Grid rotate label, 2 rotate buttons, and 6 rotation axis buttons
        rotateLabel = ttk.Label(guiRight, text='Rotate: ')
        rotateLabel.grid(row=0, column=0, columnspan=3)
        leftRotBtn = ttk.Button(guiRight, image=self._leftBtn,
                                command=lambda: self.canvas.rotate(0))
        leftRotBtn.bind('<Button-1>', lambda event: self._mouse_down('r0'))
        leftRotBtn.bind('<ButtonRelease-1>', self._mouse_up)
        leftRotBtn.bind('<Key-Return>', lambda event: self.canvas.rotate(0))
        leftRotBtn.grid(row=1, column=0, columnspan=2, sticky=tk.W)
        rightRotBtn = ttk.Button(guiRight, image=self._rightBtn,
                                 command=lambda: self.canvas.rotate(1))
        rightRotBtn.bind('<Button-1>', lambda event: self._mouse_down('r1'))
        rightRotBtn.bind('<ButtonRelease-1>', self._mouse_up)
        rightRotBtn.bind('<Key-Return>', lambda event: self.canvas.rotate(1))
        rightRotBtn.grid(row=1, column=1, columnspan=2, sticky=tk.E)

        # Loop through buttons and grid them in 2 rows, 3 columns
        rotBtns = ['xw', 'yw', 'zw', 'xy', 'yz', 'xz']
        for i,t in enumerate(rotBtns):
            # Use default variable to ensure lambdas have different arguments
            b = ttk.Button(guiRight, text=t, width=5,
                           command=lambda t=t: self.canvas.set_rotax(t))
            b.bind('<Key-Return>', lambda event,t=t: self.canvas.set_rotax(t))
            b.grid(row=int(2+i/3), column=i%3)

        # Grid Wythoff label and 9 Wythoff bar buttons
        wythoffLabel = ttk.Label(guiRight, text='Wythoff: ')
        wythoffLabel.grid(row=4, column=0, columnspan=3, pady=(20,0))
        barBtns = [('(pqs)', 'a'), ('(|pqs)', 'b'), ('(pqs|)', 'c'),
                   ('(p|qs)', 'p'), ('(q|sp)', 'q'), ('(s|pq)', 's'),
                   ('(pq|s)', 'pq'), ('(qs|p)', 'qs'), ('(sq|q)', 'sp')]
        self.bBrBtn = ttk.Button(guiRight, text='(|pqs)', width=5,
                                 command=lambda: self.canvas.set_bar('b'))
        self.bBrBtn.bind('<Key-Return>',lambda event:self.canvas.set_bar('b'))
        self.bBrBtn.grid(row=5, column=1)
        for i,(t,c) in enumerate(barBtns):
            if i == 1:      # bBrBtn already gridded, since it can change
                continue
            b = ttk.Button(guiRight, text=t, width=5,
                           command=lambda c=c: self.canvas.set_bar(c))
            b.bind('<Key-Return>', lambda event,c=c: self.canvas.set_bar(c))
            b.grid(row=int(5+i/3), column=i%3)

        # Grid light intensity label, scale, and display
        lintLabel = ttk.Label(guiRight, text='Light Intensity: ')
        lintLabel.grid(row=9, column=0, columnspan=3)
        self.lint = tk.DoubleVar()
        lintDisplay = ttk.Label(guiRight, textvariable=self.lint)
        lintDisplay.grid(row=10, column=1)
        lintScale = ttk.Scale(guiRight, orient=tk.VERTICAL,
                              variable=self.lint, from_=0, to=2,
                              command=lambda event: self.change('s'))
        lintScale.grid(row=11, column=1)


        # Grid guiBottom widgets: 5 rows, 7 columns

        # Grid status label, text box, and link them to statusText, inputText
        self.statusText = tk.StringVar()
        self.statusLabel = ttk.Label(
            guiBottom, textvariable=self.statusText, foreground=COLOURS[4][2])
        self.statusLabel.grid(row=0, column=0, columnspan=7, sticky=tk.W)
        self.inputText = tk.StringVar()
        inputBox = ttk.Entry(guiBottom, textvariable=self.inputText)
        inputBox.bind('<Key-Return>', self.canvas.take_input)
        inputBox.grid(row=1, column=0, columnspan=7, sticky=tk.E+tk.W)
        inputBox.focus()    # Put initial keyboard focus on inputBox

        # Grid 2 checkbuttons for toggling sphere and wireframe
        self.sphere = tk.IntVar()
        sphereCheck = ttk.Checkbutton(guiBottom, text='Sphere',
                                      variable=self.sphere,
                                      command=lambda: self.change())
        sphereCheck.grid(row=2, column=0, sticky=tk.W)
        self.wire = tk.IntVar()
        self.wireCheck = ttk.Checkbutton(guiBottom, text='Wireframe',
                                         variable=self.wire,
                                         command=lambda: self.change())
        self.wireCheck.grid(row=3, column=0, sticky=tk.W)

        # Grid view label and 4 view axis buttons
        viewLabel = ttk.Label(guiBottom, text='Views: ')
        viewLabel.grid(row=2, column=1, columnspan=2, sticky=tk.E)
        viewBtns = [('x', [0, pi/2, pi/2]), ('y', [0, pi/2, pi/2]),
                    ('z', [0, 0, pi/2]), ('w', [0, 0, 0])]
        for i,(t,c) in enumerate(viewBtns):
            b = ttk.Button(guiBottom, text=t, width=2,
                           command=lambda c=c: self.canvas.set_view(c))
            b.bind('<Key-Return>', lambda event,c=c: self.canvas.set_view(c))
            b.grid(row=2, column=3+i)

        # Grid zoom label, distance label, and 4 zoom/dist buttons
        zoomLabel = ttk.Label(guiBottom, text='zoom: ')
        zoomLabel.grid(row=3, column=1, sticky=tk.E)
        distLabel = ttk.Label(guiBottom, text='d: ')
        distLabel.grid(row=3, column=4, sticky=tk.E)
        upDownBtns = ['z+', 'z-', 'd+', 'd-']
        for i,c in enumerate(upDownBtns):
            if i%2 == 0:    # Even indexes are up buttons
                im = self._upBtn
            else:
                im = self._downBtn
            b = ttk.Button(guiBottom, image=im,
                           command=lambda c=c: self.change(c))
            b.bind('<Button-1>', lambda event,c=c: self._mouse_down(c))
            b.bind('<ButtonRelease-1>', self._mouse_up)
            b.bind('<Key-Return>', lambda event,c=c: self.change(c))
            b.grid(row=3, column=2+i+int(i/2))  # Gap to put distLabel

        # Grid zoom display, distance display, and link them to zoom, dist
        self.zoom = tk.IntVar()
        zoomDisplay = ttk.Label(guiBottom, textvariable=self.zoom)
        zoomDisplay.grid(row=4, column=0, columnspan=4, sticky=tk.E)
        self.dist = tk.IntVar()
        distDisplay = ttk.Label(guiBottom, textvariable=self.dist)
        distDisplay.grid(row=4, column=4, columnspan=3, sticky=tk.E)
        self.change('r')    # Set initial zoom and distance in change


    def _poll(self, button):
        # Call _press every HELAY milliseconds while mouse is held down.
        # after(t, foo, arg) calls foo(arg) once after t ms and returns an ID
        # after calls _poll when mouse pressed, which calls _press every t ms
        if self._mousePressed:
            self._press(button)
            self._after_pollID = self.parent.after(DELAY, self._poll, button)
    def _mouse_down(self, button):
        # Call _poll when mouse is held down.
        self._mousePressed = True
        self._poll(button)
    def _mouse_up(self, event):
        # Stop _poll when mouse is released.
        self._mousePressed = False
        self.parent.after_cancel(self._after_pollID)    # Cancel polling
    def _press(self, button):
        # Handle events when buttons are pressed.
        # button: the button that is pressed (str)
        #         'r0', 'r1', 'z+', 'z-', 'd+', 'd-'
        if button[0] == 'r':
            self.canvas.rotate(int(button[1]))
        else:
            self.change(button)

    def set_status(self, event):
        """
        Display status changes on the status bar.
        event: the type of status change (str)
               'clear', 'badinput', 'view', 'rot',
               'laxis', 'lcol', 'faces'
        """
        if event == 'clear':
            self.statusText.set('')
        elif event == 'badinput':
            self.statusText.set('Bad input!')   # Keep status on for FADEDELAY
            self.statusLabel.after(FADEDELAY, self.set_status, 'clear')
        elif event == 'view':
            self.statusText.set('New view angle: ' +
                                self.canvas.get_data('view'))
        elif event == 'rot':
            self.statusText.set('New rotation axes: ' +
                                self.canvas.get_data('rot'))
        elif event == 'laxis':
            self.statusText.set('New light position: ' +
                                self.canvas.get_data('laxis'))
        elif event == 'lcol':
            self.statusText.set('New light colour: ' +
                                self.canvas.get_data('lcol'))
        elif event == 'faces':      # Display number and types of faces
            faceText = ''
            faces = self.canvas.get_data('faces')
            for i in range(3,21):
                if faces[i] == 1:   # No -s ending for singular nouns
                    faceText += str(faces[i]) + ' ' + POLYGONS[i] + ' '
                if faces[i] > 1:
                    faceText += str(faces[i]) + ' ' + POLYGONS[i] + 's '
            self.statusText.set(faceText)

    def change(self, change=None, value=0):
        """
        Change GUI values (checkboxes, zoom, distance) and re-render.
        change: the type of change to make (str)
                'b', 'w', 's', 'r', 'z', 'z+', 'z-', 'd', 'd+', 'd-'
        value: the value to change to (float), default 0
        """
        if change == None:      # When checkboxes are ticked, just re-render
            pass
        elif change == 'b':     # Disable bBrBtn if polyhedron has no snub
            self.bBrBtn.config(state=tk.DISABLED)
        elif change == 'w':     # Disable wireCheck if camera too close
            self.wire.set(1)
            self.wireCheck.config(state=tk.DISABLED)
        elif change == 's':     # Round scale labels to two decimal places
            self.lint.set(round(self.lint.get(), 2))
        elif change == 'li':
            self.lint.set(round(value, 2))
        elif change == 'r':     # Reset to initial states
            try:                # Canvas initializes before zoom
                self.lint.set(1)
                self.zoom.set(ZOOM) # Set initial zoom to ZOOM
                self.unitDist = 20  # Set initial distance to 20 from max
                # unitDist changes by one per button press, between 1 and 100
                # Follows a x^(-3/2) curve; changes more as distance increases
                # Min is ZOOM*RADIUS*RETINA/1000, max is ZOOM*RADIUS*RETINA
                self.dist.set(int(ZOOM*RADIUS*RETINA/self.unitDist**(3/2)))
                self.bBrBtn.config(state=tk.NORMAL)     # Reset button states
                self.wireCheck.config(state=tk.NORMAL)
            except:
                return

        # All ZOOM values are explained with the constants
        elif change == 'z':     # Set zoom to the given value or the max zoom
            self.zoom.set(min(value, ZOOM*RADIUS*RETINA/2))
        elif change == 'z+':    # Change zoom by 5 per button press
            self.zoom.set(min(self.zoom.get() + 5, ZOOM*RADIUS*RETINA/2))
        elif change == 'z-':
            self.zoom.set(max(self.zoom.get() - 5, 0))

        # Decreasing distance increases unitDist
        elif change == 'd':     # Set distance to given value or max distance
            self.dist.set(min(value, ZOOM*RADIUS*RETINA))
            self.unitDist = math.ceil((ZOOM*RADIUS*RETINA/value)**(2/3))
            if self.unitDist >= 100:    # unitDist is an integer within bounds
                self.unitDist = 100     # math.ceil guarantees unitDist >= 1
            if self.unitDist**(3/2) > ZOOM*RETINA:  # If distance < RADIUS
                self.change('w')                    # Camera is too close
                return  # Call change again, so no need to re-render
        elif change == 'd-':
            self.unitDist += 1
            if self.unitDist >= 100:
                self.unitDist = 100
            self.dist.set(int(ZOOM*RADIUS*RETINA/self.unitDist**(3/2)))
            if self.unitDist**(3/2) > ZOOM*RETINA:
                self.change('w')
                return
        elif change == 'd+':
            self.unitDist -= 1
            if self.unitDist < 1:
                self.unitDist = 1
            self.dist.set(int(ZOOM*RADIUS*RETINA/self.unitDist**(3/2)))
            if (self.unitDist**(3/2) < ZOOM*RETINA      # Camera is far enough
                and self.canvas.get_data('star') == 0):
                self.wireCheck.config(state=tk.NORMAL)

        self.canvas.render()

    def close(self):
        """Close the program."""
        self.parent.destroy()



class Canvas(tk.Canvas):

    """
    Display class that manages polytope creation, edits, and display.

    Public methods:
    set_light           Change properties of the lighting and re-render.
    set_colours         Change various colour settings and re-render.
    set_rotax           Change the rotation axis-plane and re-render.
    set_bar             Change the generating point and re-render.
    set_view            Change the current viewing axis and re-render.
    rotate              Rotate polytope on button press and re-render.
    get_data            Return data about the current polytope.
    take_input          Take text input from input box.
    render              Clear the canvas and display the objects.

    Public variables:
    parent              Parent of class (Main)
    rotAxis             The rotation plane's basis vectors (list)

    Private methods:
    __init__            Construct Canvas class.
    _translate          Translate text input to return a Polytope object.
    _schlafli2D         Create a polygon using a 2D Schläfli symbol.
    _schlafli3D         Create a polyhedron using a 3D Schläfli symbol.
    _wythoff            Create a polyhedron using a Wythoff symbol.
    _wythoff_snub       Find the generating point of a snub polyhedron.
    _schwarz            Reflect the generating point everywhere.
    _view               Project 4D points on the viewing plane.
    _reset              Clear the canvas and reset all variables.

    Private variables:
    _hasPolytope        To keep track of if the polytope exists (bool)
    _currPolytope       Instance of Polytope class (Polytope)
    _sphere             Instance of Sphere class (Sphere)
    _currWythoff        To keep track of the current Wythoff numbers (list)
    _noSnub             To keep track of if the snub does not exist (bool)
    _lightAxis          The current light axis (list)
    _lightColour        The current light colour (list)
    _vertexColours      The colour of vertices in wire mode (list)
    _edgeColours        The colour of edges in wire mode (list)
    _baseColours        The colour of polygonal faces (dict)
    _sphereColours      The colours of the sphere overlay (list)
    _menuColours        The colours of menus and the GUI (list)
    """

    def __init__(self, parent):
        """
        Construct Canvas class.
        parent = the parent of canvas (Main)
        """
        self.parent = parent
        tk.Canvas.__init__(self, parent, relief=tk.GROOVE,
                           background=COLOURS[4][1],
                           borderwidth=5, width=300, height=200)
        self._hasPolytope = False
        self._currPolytope = Polytope([])   # Blank polytope is empty list
        self._currWythoff = ['2','2','2']
        self._noSnub = 0
        self._reset()

    def set_light(self, laxis=None, lcol=None):
        """
        Change properties of the lighting and re-render.

        laxis: the light axis in spherical coordinates (list, len=4)
        lcol: the light colour in RGB integers between 0 and 255 (list, len=3)
        """
        if laxis != None:
            self._lightAxis = satisfy_axis_restrictions(laxis)
            if self._hasPolytope:
                self.parent.set_status('laxis')
        if lcol != None:
            self._lightColour = lcol
            if self._hasPolytope:
                self.parent.set_status('lcol')
        self.render()

    def set_colours(self,vcol=None,ecol=None,bcol=None,scol=None,mcol=None):
        """
        Change various colour settings and re-render.

        vcol: the colour of vertices in wireframe mode (list, len=3)
        ecol: the colour of edges in wireframe mode (list, len=6)
        bcol: the colour of different types of polygonal faces (dict, 3:22)
        scol: the colours of the sphere overlay (list, len=4)
        mcol: the colours of menus and the GUI (list, len=3)
        All defaults are None, colours are in RGB integers between 0 and 255.
        """
        if vcol:
            self._vertexColours = vcol
        if ecol:
            self._edgeColours = ecol
        if bcol:
            self._baseColours = bcol
        if scol:
            self._sphereColours = scol
        if mcol:
            self._menuColours = mcol
        if self._hasPolytope:
            self.render()

    def set_rotax(self, rotAxis):
        """
        Change the current rotation axis-plane and re-render.
        rotAxis: the rotation axis-plane as a list of two axes (list, len=2)
                 all elements are in spherical coordinates (list, len=4)
        """
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
            self.rotAxis = rotAxis  # Manual input, not button press
        self._currPolytope.set_rotaxis(self.rotAxis)
        self._sphere.set_rotaxis(self.rotAxis)
        self.render()
        if self._hasPolytope:
            self.parent.set_status('rot')

    def set_bar(self, bar):
        """Change the Wythoff generating point and re-render."""
        self._currPolytope = Polytope(self._wythoff(selection=bar))
        self._hasPolytope = True
        self._reset()   # Treat it as a new polytope
        self.render()

    def set_view(self, viewAxis):
        """
        Change the current viewing axis and re-render.
        viewAxis: the viewing axis in spherical coordinates (list, len=4)
        """
        self._viewAxis = satisfy_axis_restrictions(viewAxis)
        self.render()
        # Since _reset resets all changes, only update status if has polytope
        if self._hasPolytope:
            self.parent.set_status('view')

    def rotate(self, direction, rotAngle=ROTANGLE):
        """
        Rotate polytope on button press and re-render.
        direction: left is 0, right is 1 (int)
        rotAngle: number of radians to rotate (float), default ROTANGLE
        """
        if direction == 0:
            self._currPolytope.rotate(rotAngle)
            self._sphere.rotate(rotAngle)
        elif direction == 1:    # Opposite direction is backwards rotation
            self._currPolytope.rotate(-rotAngle)
            self._sphere.rotate(-rotAngle)
        self.render()

    def get_data(self, event):
        """
        Return data about the current polytope.
        event: the type of data to return (str)
               'view', 'laxis', 'lcol', 'rot', 'faces', 'star'
        return: some data to put on the status bar (str)
        """
        if event == 'view':
            return ', '.join([str(round(self._viewAxis[i], 2))
                              for i in range(3)])
        if event == 'laxis':
            return ', '.join([str(round(self._lightAxis[i],2))
                              for i in range(3)])
        if event == 'lcol':
            return ', '.join([str(self._lightColour[i]) for i in range(3)])
        if event == 'rot':
            u = ', '.join([str(round(self.rotAxis[0][i],2))
                           for i in range(4)])
            v = ', '.join([str(round(self.rotAxis[1][i],2))
                           for i in range(4)])
            return u + ' and ' + v
        if event == 'faces':
            return self._currPolytope.get_face_sides()
        if event == 'star':
            return self._currPolytope.star


    def take_input(self, event):
        """Take text input from input box."""
        translatedInput = self._translate(self.parent.inputText.get())
        if translatedInput == ValueError:   # Lots of them in _translate
            self.parent.set_status('badinput')
        elif translatedInput:
            self._currPolytope = translatedInput
            self._reset()   # Create new polytope using input and reset
        self.parent.inputText.set('')   # Clear the input box

    def _translate(self, entry):

        # Translate text input to return a Polytope object.
        # entry: the input (str), 0 is float, 1 is int, f is frac or int
        #        general: '', 'clear', 'reset', 'quit', 'exit', 'close'
        #        zoom/dist/view: 'z0', 'd0', 'v0,0', 'v0,0,0'
        #        light: 'la0,0', 'la0,0,0', 'lc1,1,1', 'li0'
        #        rotaxis: 'r0,0,0', 'r0,0,0,0/0,0,0,0'
        #        schlafli: '{f}', '{f,f}', '{3,3,3}', '{4,3,3}', '{3,3,4}'
        #        wythoff: '(f f f)', '(| f f f)', '(f | f f)', etc.
        # return: the polytope represented by entry (Polytope)

        if entry == ('' or 'clear' or 'reset'): # Clear canvas
            self.parent.set_status('clear')
            self._hasPolytope = False
            return Polytope([])

        elif entry == ('quit' or 'exit' or 'close'):    # Close the program
            self.parent.close()


        elif entry.startswith('z'):             # Set zoom
            try:
                zoom = int(entry[1:])
                if zoom < 1:            # Zoom must be positive
                    return ValueError
                self.parent.change('z', zoom)
                return
            except:
                return ValueError

        elif entry.startswith('d'):             # Set distance
            try:
                distance = int(entry[1:])
                if distance < 1:
                    return ValueError
                self.parent.change('d', distance)
                return
            except:
                return ValueError

        elif entry.startswith('v'):             # Set viewing axis
            try:
                viewAxis = [float(num) for num in entry[1:].split(',')]
                if len(viewAxis) < 3:   # Add omega if axis specified in 3D
                    viewAxis.append(pi/2)
                if len(viewAxis) != 3:  # After adding omega, length must be 3
                    return ValueError
                self.set_view(viewAxis)
                return
            except:
                return ValueError


        elif entry.startswith('la'):            # Set light axis
            try:
                lightAxis = [float(num) for num in entry[2:].split(',')]
                if len(lightAxis) < 3:
                    lightAxis.append(pi/2)
                if len(lightAxis) != 3:
                    return ValueError
                self.set_light(laxis=lightAxis)
                return
            except:
                return ValueError

        elif entry.startswith('lc'):            # Set light colour
            try:
                lightColour = [int(num) for num in entry[2:].split(',')]
                if len(lightColour) != 3:
                    return ValueError
                self.set_light(lcol=lightColour)
                return
            except:
                return ValueError

        elif entry.startswith('li'):            # Set light intensity
            try:
                lint = float(entry[2:])
                if lint < 0 or lint > 2:
                    return ValueError
                self.parent.change('li', lint)
                return
            except:
                return ValueError


        elif entry.startswith('r'):             # Set rotation axis
            try:
                rotAxis = entry[1:].split('/')
                if len(rotAxis) == 2:       # 3D rotation plane, two vectors
                    u = list(map(float, rotAxis[0].split(',')))
                    v = list(map(float, rotAxis[1].split(',')))
                    if (len(u) != 4 or len(v) != 4):
                        return ValueError
                    self.set_rotax((u, v))
                elif len(rotAxis) == 1:     # 2D rotation axis, one vector
                    u = list(map(float, rotAxis[0].split(',')))
                    if len(u) == 3:
                        u.append(0)         # Cartesian coordinates, add 0
                    if len(u) != 4:
                        return ValueError
                    v = [0,0,0,1]           # Create 3D rotation plane
                else:
                    return ValueError
                self.set_rotax((u, v))
                return
            except:
                return ValueError


        elif entry == '{3,3,3}':            # Pentachoron, side-length 4r
            r = 2*RADIUS
            self._hasPolytope = True
            return Polytope((
                [[r/math.sqrt(10),r/math.sqrt(6),r/math.sqrt(3),r],
                 [r/math.sqrt(10),r/math.sqrt(6),r/math.sqrt(3),-r],
                 [r/math.sqrt(10),r/math.sqrt(6),-2*r/math.sqrt(3),0],
                 [r/math.sqrt(10),-r*math.sqrt(3/2),0,0],
                 [-2*r*math.sqrt(2/5),0,0,0]],
                [(k, 0) for k in range(5)],
                ((0,1),(0,2),(0,3),(0,4),(1,2),
                 (1,3),(1,4),(2,3),(2,4),(3,4))))

        elif entry == '{4,3,3}':            # Tesseract, side-length 2r
            r = RADIUS
            self._hasPolytope = True
            return Polytope((
                 [[r,r,r,r],[r,r,r,-r],[r,r,-r,r],[r,r,-r,-r],
                  [r,-r,r,r],[r,-r,r,-r],[r,-r,-r,r],[r,-r,-r,-r],
                  [-r,r,r,r],[-r,r,r,-r],[-r,r,-r,r],[-r,r,-r,-r],
                  [-r,-r,r,r],[-r,-r,r,-r],[-r,-r,-r,r],[-r,-r,-r,-r]],
                 [(k, 0) for k in range(16)],
                 ((0,1),(1,3),(3,2),(2,0),(12,13),(13,15),(15,14),(14,12),
                  (4,5),(5,7),(7,6),(6,4),(8,9),(9,11),(11,10),(10,8),
                  (0,4),(1,5),(2,6),(3,7),(8,12),(9,13),(10,14),(11,15),
                  (0,8),(1,9),(2,10),(3,11),(4,12),(5,13),(6,14),(7,15))))

        elif entry == '{3,3,4}':            # Hexadecachoron, side-length 4r
            r = 2*RADIUS
            self._hasPolytope = True
            return Polytope((
                [[r,0,0,0],[-r,0,0,0],[0,r,0,0],[0,-r,0,0],
                 [0,0,r,0],[0,0,-r,0],[0,0,0,r],[0,0,0,-r]],
                [(k, 0) for k in range(8)],
                ((0,2),(0,3),(0,4),(0,5),(0,6),(0,7),
                 (1,2),(1,3),(1,4),(1,5),(1,6),(1,7),
                 (2,4),(2,5),(2,6),(2,7),(3,4),(3,5),
                 (3,6),(3,7),(4,6),(4,7),(5,6),(5,7))))


        # Schlafli symbol: {p/d} or {p,q}
        elif entry.startswith('{') and entry.endswith('}'):
            try:
                if ',' in entry:
                    self._hasPolytope = True
                    return Polytope(self._schlafli3D(entry[1:-1]))
                else:
                    self._hasPolytope = True
                    return Polytope(self._schlafli2D(entry[1:-1]))
            except:
                return ValueError

        # Wythoff symbol: (p q s)
        elif entry.startswith('(') and entry.endswith(')'):
            try:
                if entry[1] == '|':
                    while True: # Las Vegas algorithm, repeat until success
                        polytope = Polytope(self._wythoff(entry[1:-1]))
                        if polytope.get_points():
                            self._hasPolytope = True
                            return polytope
                else:
                    self._hasPolytope = True
                    return Polytope(self._wythoff(entry[1:-1]))
            except ValueError:
                return ValueError

        else:
            return ValueError

    def _schlafli2D(self, entry):
        # Create a polygon using a 2D Schläfli symbol.
        # entry: the 2D Schläfli symbol (str)
        #        {p} or {p/d}, where p and d are ints
        # return: the polygon represented by entry (Polytope)
        num = entry.split('/')
        p = int(num[0])
        if len(num) == 1:
            d = 1               # d = 1 if entry is a convex polygon
        elif len(num) == 2:
            d = int(num[1])
        # Add thetas in equal intervals around the circle
        thetas = [(2*k*d*pi/p) for k in range(p)]
        rs = [RADIUS]*p         # radius, phi, and omega are all the same
        phis = [pi/2]*p
        omegas = [pi/2]*p
        points = [convert((rs[n], thetas[n], phis[n], omegas[n]), True)
                  for n in range(len(thetas))]
        colours = [(k,0) for k in range(p)]
        edges = [(k,(k+1)%p) for k in range(p)] # Connect points to next ones
        return points, colours, edges

    def _schlafli3D(self, entry):

        # Create a polyhedron using a 3D Schläfli symbol.
        # entry: the 3D Schläfli symbol (str)
        #        {p,q}, where p and q are ints (no support for star polyhedra)
        # return: the polyhedron represented by entry (Polytope)

        num = entry.split(',')
        p = int(num[0])
        q = int(num[1])
        r = RADIUS
        a = (p-2)*pi/p      # Vertices on the equatorial plane are offset
        b = 2*pi/q          # by a and b from being evenly spaced around it

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

        if firstPhi < pi/2 + EPSILON:       # If not tetrahedron
            if firstPhi < pi/2 - EPSILON:   # If not octahedron
                # Coordinates of the last ring
                thetas += [(k+1/2)*b for k in range(q)]
                phis += [pi-firstPhi]*q

            # Coordinates of the south pole
            thetas += [0]
            phis += [pi]

            # Edges of the last ring
            n = len(thetas)
            edges += [(n-1,n-q+k) for k in range(-1,q-1)]

            if p == 3:      # Edges of the deltahedra
                edges += [(n-q+k-1,n-q+k) for k in range(0,q-1)]
                edges += [(n-2,q+1)]
                if q == 5:  # Edges of the icosahedron
                    edges += [(k,q+k) for k in range(1,q+1)]
                    edges += [(k+1,q+k) for k in range(1,q)]
                    edges += [(1,2*q)]

            elif p == 4:    # Edges of the cube
                edges += [(k,q+k) for k in range(1,q+1)]
                edges += [(k+1,q+k) for k in range(1,q)]
                edges += [(1,2*q)]

            elif p == 5:    # Rings and edges of the dodecahedron, hard-coded
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

        rs = [RADIUS]*len(thetas)   # radius and omega are all the same
        omegas = [pi/2]*len(thetas)
        points = [convert((rs[n], thetas[n], phis[n], omegas[n]), True)
                  for n in range(len(thetas))]
        colours = [(k, 0) for k in range(len(thetas))]
        return points, colours, edges

    def _wythoff(self, entry=None, selection='a'):

        # Create a polyhedron using a Wythoff symbol.
        # entry: the Wythoff symbol (str), default is None
        #        p/d | q/c s/b, where p, q, s are ints; d, c, b are optional;
        #        | can be placed anywhere; but all are separated by spaces
        # selection: the location to place | (str), default is a
        #             a = p q s      b = | p q s    c = p q s |
        #             p = p | q s    q = q | s p    s = s | p q
        #            pq = p q | s   qs = q s | p   qp = s p | q
        # return: the polyhedron represented by entry (Polytope)

        r = RADIUS
        edges = []
        colours = []

        # Store entry as list of numbers (symbol)
        if not entry:        # entry is None when called by set_bar
            symbol = self._currWythoff
        else:                # Otherwise, find where the bar is and remove it
            symbol = entry.split()
            if len(symbol) == 4:
                if symbol.index('|') == 0:
                    selection = 'b'
                elif symbol.index('|') == 1:
                    selection = 'p'
                elif symbol.index('|') == 2:
                    selection = 'pq'
                elif symbol.index('|') == 3:
                    selection = 'c'
                symbol.remove('|')

        # Extract from symbol each Wythoff number (p,q,s)
        pqs = []
        for i in range(3):
            if '/' in symbol[i]:    # Convert all fractions into decimals
                numer, denom = map(int(symbol[i].split('/')))
                pqs.append(numer/denom)
            else:
                pqs.append(int(symbol[i]))
        p,q,s = pqs
        if p == 1 or q == 1 or s == 1:  # Cannot have pi angle
            raise ValueError

        # Check Wythoff symbol validity, then save current Wythoff polyhedron
        lpq = math.acos((math.cos(pi/s) + math.cos(pi/p)*math.cos(pi/q))/
                        (math.sin(pi/p)*math.sin(pi/q)))
        lqs = math.acos((math.cos(pi/p) + math.cos(pi/q)*math.cos(pi/s))/
                        (math.sin(pi/q)*math.sin(pi/s)))
        lsp = math.acos((math.cos(pi/q) + math.cos(pi/s)*math.cos(pi/p))/
                        (math.sin(pi/s)*math.sin(pi/p)))
        self._currWythoff = symbol

        # Check if the snub version exists, and disable its button if not
        if sorted(self._currWythoff) in SNUBABLE:
            self._noSnub = 0
        else:
            if selection == 'b':
                raise ValueError
            else:
                self._noSnub = 1

        # Find fundamental Schwarz triangle
        triangles = [[[0.0 if abs(x) < EPSILON else x for x in
                       convert(point, True)] for point in
                      [(r,0,0,pi/2), (r,0,lpq,pi/2), (r,pi/p,lsp,pi/2)]]]
        op = triangles[0][0]
        oq = triangles[0][1]
        os = triangles[0][2]
        pq = cross3D(op, oq)
        qs = cross3D(oq, os)
        sp = cross3D(os, op)

        # Find the generating point within that triangle
        if selection == 'a':
            n = [0.0,0.0,0.0,0.0]   # No generating point needed
        elif selection == 'c':
            # Find the angle bisectors on two sides
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
            n = cross3D(mq, ns, [r]) + [0.0]    # Centre of the triangle
        elif selection == 'p':
            n = triangles[0][0]                 # p vertex of the triangle
            colour = 0
        elif selection == 'q':
            n = triangles[0][1]                 # q vertex of the triangle
            colour = 1
        elif selection == 's':
            n = triangles[0][2]                 # s vertex of the triangle
            colour = 2
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
                 for t in range(3)] + [0.0]     # Midpoint of pq side
        elif selection == 'qs':
            qn = math.atan2(math.sin(lpq), (
                math.cos(lpq)*math.cos(pi/q)+
                math.sin(pi/q)*math.cos(pi/p/2)/math.sin(pi/p/2)))
            oq = normalize(triangles[0][1], [r])
            os = triangles[0][2]
            qs = cross3D(oq, os)
            ot = cross3D(qs, oq, [r])
            n = [oq[t]*math.cos(qn) + ot[t]*math.sin(qn)
                 for t in range(3)] + [0.0]     # Midpoint of qs side
        elif selection == 'sp':
            sn = math.atan2(math.sin(lqs), (
                math.cos(lqs)*math.cos(pi/s)+
                math.sin(pi/s)*math.cos(pi/q/2)/math.sin(pi/q/2)))
            os = normalize(triangles[0][2], [r])
            op = triangles[0][0]
            sp = cross3D(os, op)
            ot = cross3D(sp, os, [r])
            n = [os[t]*math.cos(sn) + ot[t]*math.sin(sn)
                 for t in range(3)] + [0.0]     # Midpoint of sp side

        # Find actual points, given fundamental triangle and generating point
        if selection == 'b':    # Find generating point of snub polyhedron
            n = self._wythoff_snub(p, q, s)
        points, side = self._schwarz(selection, triangles, n)

        # Connect all points to neighbours if Catalan solid
        if selection == 'a':
            points.remove([0.0,0.0,0.0,0.0])    # Remove fake generating point
            n = 2
            while n < len(points):
                colours += [(n-2, 0), (n-1, 1), (n, 2)]
                edges += [(n-2,n-1), (n-2,n), (n-1,n)]
                n += 3

        # Connect all points to points side away if uniform polyhedron
        else:
            colours = [(k, 0) for k in range(len(points))]
            for n in range(len(points)):
                for k in range(n+1, len(points)):
                    if abs(distance(points[n], points[k]) - side) < 2:
                        edges.append((n,k))
        return points, colours, edges

    def _wythoff_snub(self, p, q, s):

        # Find the generating point of a snub Wythoff polyhedron.
        # p, q, s: the Wythoff numbers of the polyhedron (floats)
        # return: the generating point in Cartesian coordinates (list, len=4)

        # Hard-coded constants
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
                # Convert to Cartesian coordinates and check if it works
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
        return n

    def _schwarz(self, selection, triangles, n):

        # Reflect the generating point everywhere.
        # selection: the lype of reflection (str)
        #            a = reflect every triangle vertex
        #            b = take every other reflected point
        #            otherwise = take every reflected generating point
        # triangles: the initial fundamental triangle (list, len=1)
        #            all elements are lists of vertices (list, len=3)
        #            all vertices are in Cartesian coordinates (list, len=4)
        # n: the generating point in Cartesian coordinates (list, len=4)
        # return: the points and side length of the polyhedron (list, len=2)
        #         the points are in a list of verticel (list)
        #         all vertices are in Cartesian coordinates (list, len=4)

        depth = 16  # Depth to reflect until
        side = 0    # Length of the sides

        triangles[0].append(n)
        points = [n]    # Points in the final polyhedron
        if selection == 'b':
            points = [] # Generating point of snub polyhedron not included

        # Identification system without negative zeros to test membership
        numa = '{:=+04.0f}{:=+04.0f}{:=+04.0f}'.format(*triangles[0][0])
        numb = '{:=+04.0f}{:=+04.0f}{:=+04.0f}'.format(*triangles[0][1])
        numc = '{:=+04.0f}{:=+04.0f}{:=+04.0f}'.format(*triangles[0][2])
        numn = '{:=+04.0f}{:=+04.0f}{:=+04.0f}'.format(*triangles[0][3])
        tricoords = [''.join(sorted([numa, numb, numc]))+numn]
        pointcoords = [numn]

        # Reflect each unreflected triangle once in each side
        while depth > 0:
            for triangle in reversed(triangles):    # Reversed makes a queue
                if selection == 'a':    # Add all points of all triangles
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

    def _view(self, points):

        # Project 4D points on the plane normal to the viewing axis.
        # points: a list of points in 4D (list)
        #         all elements are in spherical coordinates (list, len=4)
        # return: a list of points on the viewing plane (list)
        #         all elements are in Cartesian coordinates (list, len=2)

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
        d = self.parent.dist.get()
        f = d + RETINA

        result = []
        for x,y,z,w in points:
            t = (f-x*u[0]-y*u[1]-z*u[2]-w*u[3])/ \
                (d-x*u[0]-y*u[1]-z*u[2]-w*u[3])
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
            result.append((m*self.parent.zoom.get(),n*self.parent.zoom.get()))
        return result

    def render(self):

        """
        Clear the canvas, center the frame, and display the objects.
        """

        self.delete(tk.ALL)         # Clear the canvas
        w = self.winfo_width()//2   # Center the frame
        h = self.winfo_height()//2

        # Eraw the sphere overlay
        if w != 0 and h != 0 and self.parent.sphere.get() == 1:
            # Draw the lines of longitude and latitude
            # _view flipped the x-coordinates upside down for some reason
            # w and h map the viewing plane origin to the centre of the screen
            points = [(-point[0]+w, point[1]+h) for point in
                      self._view(self._sphere.get_points())]
            edges = self._sphere.get_edges()
            for edge in edges:
                self.create_line(points[edge[0]], points[edge[1]],
                                 fill='#000', width=3)
            # Draw the three coordinate axes
            axes = [(-point[0]+w, point[1]+h) for point in
                    self._view(self._sphere.get_axes())]
            self.create_line(axes[0],axes[1], fill=COLOURS[3][1], width=5)
            self.create_line(axes[2],axes[3], fill=COLOURS[3][2], width=5)
            self.create_line(axes[4],axes[5], fill=COLOURS[3][3], width=5)

        if not self._hasPolytope:
            return      # Do nothing if there's nothing to do

        # Draw the actual polytope, since we know it exists
        self.parent.set_status('faces') # Show what faces it has
        points = [(-point[0]+w, point[1]+h) for point in
                  self._view(self._currPolytope.get_points())]
        # As the camera moves away, the light source moves the same distance
        camera = convert([self.parent.dist.get()] + self._viewAxis,True)
        laxis = convert([self.parent.dist.get()] + self._lightAxis,True)
        lint = self.parent.lint.get()
        lcol = self._lightColour

        # Display by drawing polygons in normal mode
        if self.parent.wire.get() == 0:
            faces = self._currPolytope.get_faces()
            shades = self._currPolytope.get_shades(laxis)
            centres = self._currPolytope.get_face_centres()
            sideTypes = self._currPolytope.get_faces_by_side()
            distances = {}

            # If the polytope is a single polygon, both sides should be shaded
            if len(faces) == 1:
                hexcol = COLOURS[2][sideTypes[0]]   # Get polygon base colour
                colour = []
                for i in range(3):
                    deccol = int(hexcol[1+i], 16)   # Convert hex to dec
                    # Multiply deccol (0-15) by 16, since lcol is (0-255)
                    # Average base colour and light colour times intensity
                    # Then multiply result by shade and intensity again
                    col = (deccol*16 + lcol[i] * lint)/2 * shades * lint
                    # Use min and abs so that result is positive and under 255
                    color = min(255, abs(col))
                    colour.append(format(int(color), '02x'))
                rgb = '#' + ''.join(colour)
                edges = [points[side] for side in faces[0]]
                self.create_polygon(edges,outline=COLOURS[1][5],
                                    width=3,fill=rgb)
                return

            # Otherwise, sort faces by distance to the camera and draw them
            for face in faces:
                distances[face] = distance(centres[face], camera)
            order = sorted(distances, key=distances.get, reverse=True)
            for face in order:              # Colour the faces
                hexcol = COLOURS[2][sideTypes[face]]
                colour = []
                for i in range(3):
                    deccol = int(hexcol[1+i], 16)
                    col = (deccol*16 + lcol[i] * lint)/2 * shades[face] * lint
                    color = max(0, min(255, col))   # Result between 0 and 255
                    colour.append(format(int(color), '02x'))
                rgb = '#' + ''.join(colour)
                edges = [points[side] for side in faces[face]]
                self.create_polygon(edges,outline=COLOURS[1][5],
                                    width=3,fill=rgb)
            return

        # Display by drawing lines in wireframe mode
        elif self.parent.wire.get() == 1:
            edges = self._currPolytope.get_edges()
            centres = self._currPolytope.get_edge_centres()
            colours = self._currPolytope.get_point_colours()
            for colour in colours:
                self.create_oval([p-5 for p in points[colour[0]]],
                                 [p+5 for p in points[colour[0]]],
                                 fill=COLOURS[0][colour[1]])
            distances = {}
            for i in range(len(edges)):
                distances[i] = distance(centres[i], camera)
            order = sorted(distances, key=distances.get, reverse=True)
            quintile = 0            # Group edges into distance quintiles
            fifth = len(order)/5
            count = 0
            for e in order:
                if count >= quintile*fifth:
                    quintile += 1
                count += 1
                self.create_line(points[edges[e][0]], points[edges[e][1]],
                                 fill=COLOURS[1][quintile], width=quintile)
            return


    def _reset(self):
        # Clear the canvas and reset all variables to default state.
        self.delete(tk.ALL)
        self._sphere = Sphere(SPHERENUM, RADIUS)    # Create the sphere
        # Default settings
        self.set_rotax('xw')
        self.set_view([0, 0, pi/2])
        self.set_light([0, 0, pi/2],[255,255,255])
        self.parent.change('r')
        if self.get_data('star') == 1:
            self.parent.change('w')
        if self._noSnub == 1:
            self.parent.change('b')



class Polytope():

    """
    Drawing class that stores vertex coordinates and manages rotations.

    Public methods:
    get_points          Return a list of points of the polytope.
    get_point_colours   Return a list of colours of the points.
    get_edges           Return a list of edges of the polytope.
    get_faces           Return a dict of faces of the polytope.
    get_face_sides      Return a dict of the number of each polygon.
    get_faces_by_side   Return a dict of the polygon type of each face.
    get_edge_centres    Return a list of edge midpoints of the polytope.
    get_face_centres    Return a dict of face centres of the polytope.
    get_shades          Calculate the amount of shading needed for each face.
    set_rotaxis         Set the rotation axis-plane of the polytope.
    rotate              Rotate the current polytope.

    Public variables:
    star                To keep track of if there are star faces. (bool)

    Private methods:
    __init__            Construct Polytope class.
    _set_faces          Create the face dictionaries using the edge list.
    _bfs                Breadth-first search.
    _has_star           Check to see if a polygon is a star.
    _orientation        Find the orientation of two connected line segments.
    _set_edge_centres   Create a list of edge midpoints.
    _set_face_centres   Create a list of face centres.
    _remove_faces       Remove faces. Lots of them.
    _remove_non_faces   Remove types of faces that do not exist.
    _remove_odd_faces   Remove types of faces that there are an odd number of.
    _remove_small_faces Remove types of faces that there're a small number of.
    _remove_close_faces Remove faces that are too close to the centre.

    Private variables:
    _points             The points of the polytope (list)
                            elements are in Cartesian coordinates (list)
    _pointColours       The point colours of the polytope (list)
                            elements are integers from 0 to 2
    _edges              The edges of the polytope (list)
                            elements are lists of point indices (list)
    _faces              The faces of the polytope (dict)
                            keys are face indices (int)
                            values are lists of point indices (list)
    _faceSides          The number of types of each polygon face (dict)
                            keys are the number of sides of the polygon (int)
                            values are the number of those polygons (int)
    _faceTypes          The polygon type of the faces of the polytope (dict)
                            keys are face indices (int)
                            values are the number of sides of the face (int)
    _edgeCentres        The midpoints of the edges of the polytope (list)
                            elements are in Cartesian coordinates (list)
    _faceCentres        The centres of the faces of the polytope (list)
                            elements are in Cartesian coordinates (list)
    _graph              To better represent edges as point neighbours (dict)
    _visited            To keep track of already visited points (set)
    _triangles          To keep track of already added triangles (set)
    _axis_i             A basis vector of the rotation axis-plane (list)
    _axis_j             A basis vector, both in Cartesian coordinates (list)
    """

    def __init__(self, data):
        """
        Construct Polytope class.
        data: the initialization data for the polytope (list)
              if no polytopes are to be created, data = []
              otherwise, data = [points, edges, pointColours]
        """
        if data:
            self._points = data[0]
            self._pointColours = data[1]
            self._edges = data[2]
            self._set_faces()
            self._set_edge_centres()
            self._set_face_centres()
            # If there's not enough faces, then canvas._wythoff_snub failed
            # Unless there's only one face, which means it's a polygon
            if len(self._faces)/len(self._points) < 1/3 \
                and len(self._faces) != 1:
                self.star = False
                self._points = []
                # canvas expects int values, but _faceSides has list values
                self._faceSides = {i:0 for i in range(3,21)}
            else:
                self._remove_faces()
        else:   # Initialize everything as empty lists if data is empty list
            self.star = False
            self._points = []
            self._pointColours = []
            self._edges = []
            self._faces = []
            self._faceSides = []
            self._faceTypes = []
            self._edgeCentres = []
            self._faceCentres = []

    def _set_faces(self):

        # Create a dictionary of faces, a dictionary of face sides,
        # and a dictionary of faces by side, using only a list of edges.

        # Initialize variables
        self._graph = {}
        for edge in self._edges:    # setdefault ensures that the key exists
            self._graph.setdefault(edge[0], list()).append(edge[1])
            self._graph.setdefault(edge[1], list()).append(edge[0])
        self._faces = {}
        self._faceSides = {i:[] for i in range(3,21)}
        self._faceTypes = {}

        # Breadth-first search
        self._visited = set()
        self._triangles = set()
        i = 3           # Iterate across all polygon side numbers
        while i < 11:
            j = 0       # Iterate across all vertices in graph
            while j < len(self._points):
                for start in self._graph[j]:
                    faces = self._bfs(j, start, i)  # Find cycles of length i
                    if faces:       # Two faces can both go from start to j
                        for face in faces:
                            n = len(self._faces)    # Find current face number
                            if self._has_star(face) == True:
                                self._faceSides[i+10].append(n)
                                self._faceTypes[n] = i+10
                            else:
                                self._faceSides[i].append(n)
                                self._faceTypes[n] = i
                            self._faces[n] = face
                j += 1
            i += 1

    def _bfs(self, end, start, length):

        # Breadth-first search to find the only path between start and end.
        # end: the ending vertex (int)
        # start: the starting vertex (int)
        # length: the length of the path between start and end (int)
        # return: the path between start and end (list, len=length)
        #         all elements are vertices (int)

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
            u = [self._points[start][i] - self._points[end][i]
                 for i in range(3)]
            v = [self._points[vertex][i] - self._points[start][i]
                 for i in range(3)]
            normals.append(cross3D(u,v))  # Faces must be coplanar

        # Don't have to worry about the frontier when only finding triangles
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
            pathEnd = path[-3:] # Two consecutive edges belong to unique face
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
                            length = len(path)
                            for i in range(length):
                                three = [path[(i+j)%length] for j in range(3)]
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
        # Check for star polygons by seeing if a polygon's sides intersect.
        # vertices: a list of points (list)
        #           all elements are numbers of the points (int)
        # return: whether the polygon's sides intersect (bool)
        sides = [(vertices[i], vertices[(i+1)%len(vertices)])
                 for i in range(len(vertices))]
        a = self._points[sides[0][0]]
        b = self._points[sides[0][1]]
        ab = [b[i] - a[i] for i in range(3)]
        for side in sides:
            c = self._points[side[0]]
            d = self._points[side[1]]
            if a == c or b == c or a == d or b == d:
                continue    # Cannot intersect if any of the points are equal
            bc = [c[i] - b[i] for i in range(3)]
            bd = [d[i] - b[i] for i in range(3)]
            # Will intersect if orientation of lines is different
            if self._orientation(ab,bc) != self._orientation(ab,bd):
                ac = [c[i] - a[i] for i in range(3)]
                cd = [d[i] - c[i] for i in range(3)]
                if self._orientation(ac,cd) != self._orientation(bc,cd):
                    return True
        return False

    def _orientation(self, ab, bc):
        # Find the orientation of two line segments defined by three points.
        # ab, bc: the line segments (lists)
        #         all elements are in Cartesian coordinates (list, len=4)
        # return: orientation (int), where 0 is parallel, 1 and -1 are curved
        """Return the relative orientation of three points a, b, and c."""
        orientation = sum([cross3D(ab,bc)[i] for i in range(3)])
        if orientation < EPSILON:
            return 0
        return math.copysign(1, orientation)

    def _set_edge_centres(self):
        # Create a list of edge midpoints using a list of edges and vertices.
        self._edgeCentres = [[0,0,0,0] for i in range(len(self._edges))]
        for i in range(len(self._edges)):
            for j in range(4):
                self._edgeCentres[i][j] = (
                    self._points[self._edges[i][0]][j] +
                    self._points[self._edges[i][1]][j])/2

    def _set_face_centres(self):
        # Create a dict of face centres using a list of faces and vertices.
        self._faceCentres = {face:[0, 0, 0, 0] for face in self._faces}
        for face in self._faces:
            for point in self._faces[face]:
                for i in range(4):
                    self._faceCentres[face][i] += self._points[point][i]
            for i in range(4):
                self._faceCentres[face][i] /= len(self._faces[face])

    def _remove_faces(self):
        # Remove faces, change _faceSides to a count, set polytope as star
        number = sum([len(self._faceSides[i]) for i in range(3,21)])
        if number > 1:          # Not a polygon, remove lots of faces
            self._remove_non_faces()
            self._remove_odd_faces()
            if number > 12:     # Lots of faces, remove uncommon faces
                self._remove_small_faces()
        for i in range(3,21):   # Replace reference to faces with a count
            self._faceSides[i] = len(self._faceSides[i])
        for i in range(11,21):  # Contains star faces, is a star polytope
            if self._faceSides[i] > 0:
                self.star = True
                break
        else:                   # Not a star, remove inside faces
            self.star = False
            self._remove_close_faces()

    def _remove_non_faces(self):
        # Remove types of faces that do not exist.
        nope = [9,13,14,19]     # No polyhedra contains these polygons
        for i in nope:
            for j in self._faceSides[i]:
                self._faces.pop(j)
                self._faceCentres.pop(j)
                self._faceTypes.pop(j)
            self._faceSides[i] = []

    def _remove_odd_faces(self):
        # Remove types of faces that there are an odd number of.
        for i in self._faceSides:
            if len(self._faceSides[i])%2 == 1:
                for j in self._faceSides[i]:
                    self._faces.pop(j)
                    self._faceCentres.pop(j)
                    self._faceTypes.pop(j)
                self._faceSides[i] = []

    def _remove_small_faces(self):
        # Remove types of faces that there are a small number of.
        for i in self._faceSides:
            if len(self._faceSides[i]) < 5:
                for j in self._faceSides[i]:
                    self._faces.pop(j)
                    self._faceCentres.pop(j)
                    self._faceTypes.pop(j)
                self._faceSides[i] = []

    def _remove_close_faces(self):
        # Remove faces that are too close to the centre.
        if len(self._faces) <32 and self._faceSides[3]/len(self._faces) <0.6:
            depth = 5000    # Larger depth to keep outside faces, hard-coded
        else:
            depth = 3000    # Smaller depth to remove inside faces
        surface = distance(self._faceCentres[0]) - depth    # Minimum distance
        iterDict = dict(self._faces)    # Keeps dictionary from changing size
        for i in iterDict:
            if distance(self._faceCentres[i]) < surface:
                self._faceSides[len(self._faces[i])] -= 1
                self._faces.pop(i)
                self._faceCentres.pop(i)
                self._faceTypes.pop(i)

    def get_points(self):
        """
        Return a list of points of the polytope.
        return: a list of points of the polytope (list)
                all elements are in Cartesian coordinates (list, len=4)
        """
        return self._points

    def get_point_colours(self):
        """
        Return a list of colours of the points of the polytope.
        return: a list of colours of the points of the polytope (list)
                all elements are in integers (int)
        """
        return self._pointColours

    def get_edges(self):
        """
        Return a list of edges of the polytope.
        return: a list of edges of the polytope (list)
                all elements are lists of edge endpoints (list, len=2)
        """
        return self._edges

    def get_faces(self):
        """
        Return a dictionary of faces of the polytope.
        return: a dictionary of faces of the polytope (dict)
                all keys are face numbers (int)
                all values are lists of the numbers of the points (list)
        """
        return self._faces

    def get_face_sides(self):
        """
        Return a dictionary of the number of faces of each type of polygon.
        return: a dictionary of the number of each polygon type (dict, 3:22)
                all keys are the number of sides of the polygon (int)
                all values are the number of those polygons (int)
        """
        return self._faceSides

    def get_faces_by_side(self):
        """
        Return a dictionary of faces matched with their polygon type.
        return: a dictionary of faces matched with their polygon type (dict)
                all keys are face numbers (int)
                all values are the number of sides of the face (int)
        """
        return self._faceTypes

    def get_edge_centres(self):
        """
        Return a list of edge midpoints of the polytope.
        return: a list of edge midpoints of the polytope (list)
                all elements are in Cartesian coordinates (list, len=4)
        """
        return self._edgeCentres

    def get_face_centres(self):
        """
        Return a dictionary of face centres of the polytope.
        return: a dictionary of face centres of the polytope (list)
                all elements are in Cartesian coordinates (list, len=4)
        """
        return self._faceCentres

    def get_shades(self, laxis):

        """
        Calculate the amount of shading needed according to the angle.
        laxis: the light position in spherical coordinates (list, len=4)
        return: the fraction of incident light that is reflected back
                (int) between 0 and 1 if len(self._faces) == 1,
                (dict) otherwise, all keys are face numbers (int)
                all values are shades between 0 and 1 (int)
        """
        # If polygon, only need one number, always positive
        if len(self._faces) == 1:
            light = [laxis[i] - self._faceCentres[0][i] for i in range(3)]
            a = self._points[self._faces[0][0]]
            b = self._points[self._faces[0][1]]
            c = self._points[self._faces[0][2]]
            u = [a[i] - b[i] for i in range(3)]
            v = [b[i] - c[i] for i in range(3)]
            normal = cross3D(u, v)  # Can't use self._centres[0] = [0,0,0,0]
            denom = math.sqrt(abs(distance(normal) * distance(light)))
            shade = sum([light[i]*normal[i]/denom for i in range(3)])
            return shade

        # Otherwise, find shades for every face in the polyhedron
        else:
            shades = []
            for f in self._faces:
                light = [laxis[i]-self._faceCentres[f][i] for i in range(3)]
                normal = self._faceCentres[f]    # Normal passes origin
                dnm = math.sqrt(abs(distance(normal) * distance(light)))
                shades.append(sum([light[i]*normal[i]/dnm for i in range(3)]))
            return shades

    def set_rotaxis(self, axes):
        """
        Set the perpendicular unit axes of rotation of the polytope.
        axes: the perpendicular unit axes of rotation (list, len=2)
              all elements are in Cartesian coordinates (list, len=4)
        """
        self._axis_i = normalize(axes[0])
        self._axis_j = normalize(axes[1])

    def rotate(self, rotAngle):
        """
        Rotate the current polytope and reset edge midpoints and face centres.
        rotAngle: the angle to rotate the current polytope by (float)
        """
        i = self._axis_i
        j = self._axis_j
        cos = math.cos(rotAngle)
        sin = math.sin(rotAngle)
        for n in range(len(self._points)):
            p = self._points[n]
            r = sum([p[t]*i[t] for t in range(4)])
            s = sum([p[t]*j[t] for t in range(4)])
            I = [i[t]*r+j[t]*s for t in range(4)]
            ip = [p[t]-I[t] for t in range(4)]
            if ip != [0,0,0,0]:     # If I = P, then there is no rotation
                iq = cross4D(ip, i, j, ip)
                self._points[n] = [ip[t]*cos+iq[t]*sin + I[t]
                                   for t in range(4)]
        self._set_edge_centres()
        self._set_face_centres()


class Sphere():

    """
    Drawing class that stores latitude and longitude and manages rotations.

    Public methods:
    get_points          Return a list of points of the sphere.
    get_edges           Return a list of edges of the sphere.
    get_axes            Return a list of Cartesian coordinate axes.
    set_rotaxis         Set the rotation axis-plane of the sphere.
    rotate              Rotate the current sphere.

    Private methods:
    __init__            Construct Sphere class.

    Private variables:
    _points             The points of the sphere (list)
                            elements are in Cartesian coordinates (list)
    _edges              The edges of the sphere (list)
                            elements are lists of point indices (list)
    _axes               The Cartesian coordinate axes (list)
                            elements are in Cartesian coordinates (list)
    _axis_i             A basis vector of the rotation axis-plane (list)
    _axis_j             A basis vector, both in Cartesian coordinates (list)
    """

    def __init__(self, number, radius):

        """
        Construct Sphere class.
        number: the number of longitude and latitude circles to draw (int)
        radius: the radius of the sphere (float)
        """

        n = number
        r = radius
        thetas = [2*k*pi/n for k in range(n)]   # Lists of all possible
        phis = [k*pi/n for k in range(1,n)]     # thetas and phis

        # Start with only the north and south poles
        self._points = [(0,0,r,0),(0,0,-r,0)]
        self._edges = [(0, k*(n-1)+2) for k in range(n)]
        self._edges.extend([(1, (k+1)*(n-1)+1) for k in range(n)])
        for t in range(n-1):    # Add all thetas and phis as points and edges
            self._points.extend([convert((r, thetas[t], phis[k], pi/2), True)
                                 for k in range(n-1)])
            self._edges.extend([(t*(n-1)+k+2, t*(n-1)+k+3)
                                for k in range(n-2)])
            self._edges.extend([(k*(n-1)+t+2, ((k+1)*(n-1)%((n-1)*n)+t+2))
                                for k in range(n)])
        # End by adding in the last points and connecting their edges
        self._points.extend([convert((r, thetas[n-1], phis[k], pi/2), True)
                             for k in range(n-1)])
        self._edges.extend([((n-1)*(n-1)+k+2, (n-1)*(n-1)+k+3)
                            for k in range(n-2)])

        # Create three orthogonal basis axes
        self._axes = [(2*r,0,0,0), (-2*r,0,0,0),
                      (0,2*r,0,0), (0,-2*r,0,0),
                      (0,0,2*r,0), (0,0,-2*r,0)]

    def get_points(self):
        """
        Return a list of points of the sphere.
        return: a list of points of the sphere (list)
                all elements are in Cartesian coordinates (list, len=4)
        """
        return self._points

    def get_edges(self):
        """
        Return a list of edges of the sphere.
        return: a list of edges of the sphere (list)
                all elements are lists of edge endpoints (list, len=2)
                all elements are point indices (int)
        """
        return self._edges

    def get_axes(self):
        """
        Return a list of Cartesian coordinate axes.
        return: a list of points of the Cartesian axes (list)
                all elements are in Cartesian coordinates (list, len=4)
        """
        return self._axes

    def set_rotaxis(self, axes):
        """
        Set the perpendicular unit axes of rotation of the sphere.
        axes: the perpendicular unit axes of rotation (list, len=2)
              all elements are in Cartesian coordinates (list, len=4)
        """
        self._axis_i = normalize(axes[0])
        self._axis_j = normalize(axes[1])

    def rotate(self, rotAngle):
        """
        Rotate the current sphere.
        rotAngle: the angle to rotate the current sphere by (float)
        """
        i = self._axis_i
        j = self._axis_j
        cos = math.cos(rotAngle)
        sin = math.sin(rotAngle)
        for n in range(len(self._points)):
            p = self._points[n]
            r = sum([p[t]*i[t] for t in range(4)])
            s = sum([p[t]*j[t] for t in range(4)])
            I = [i[t]*r+j[t]*s for t in range(4)]
            ip = [p[t]-I[t] for t in range(4)]
            if ip != [0,0,0,0]:
                iq = cross4D(ip, i, j, ip)
                self._points[n] = [ip[t]*cos+iq[t]*sin + I[t]
                                   for t in range(4)]
        for n in range(len(self._axes)):
            p = self._axes[n]
            r = sum([p[t]*i[t] for t in range(4)])
            s = sum([p[t]*j[t] for t in range(4)])
            I = [i[t]*r+j[t]*s for t in range(4)]
            ip = [p[t]-I[t] for t in range(4)]
            if ip != [0,0,0,0]:
                iq = cross4D(ip, i, j, ip)
                self._axes[n] = [ip[t]*cos + iq[t]*sin + I[t]
                                 for t in range(4)]



root = tk.Tk()
main = Main(root)
root.mainloop()
