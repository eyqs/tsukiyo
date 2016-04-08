"""
Polytope Player v0.94

This program lets you play with polytopes!
guiRight is now split into two menus, guiLeft and guiRight.
Each menu can be collapsed and expanded individually.
guiBottom is now much tidier too. The entire GUI is!
"""
import tkinter as tk
import tkinter.ttk as ttk
import math
import random

TITLE = 'Polytope Player v0.94'
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
           ('#FD9', '#F00', '#0F0', '#00F', '#F90'), ('#CCC', '#FFF', '#F00')]



def distance2(head, tail=[0,0,0,0]):
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
    norm = math.sqrt(distance2(points))
    if norm == 0:
        return [0 for x in points]
    magnitude = math.sqrt(distance2(unit))
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
    0 <= theta < 2pi, 0 <= phi < pi, 0 <= omega < pi, 0 <= whatever < pi ...

    axis: the spherical coordinates of the axis, excluding r (list, len=>1)
    return: equivalent coordinates that satisfy the restrictions (list, len=>1)
    """
    for angle in axis:
        while angle >= 2*pi:
            angle -= 2*pi
        while angle < 0:
            angle += 2*pi
    for i in range(1,len(axis)):
        if axis[i] > pi:
            axis[i] = 2*pi - axis[i]
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
    set_view            Change the current viewing axis and re-render.
    set_light           Change properties of the lighting and re-render.
    set_rotax           Change the rotation axis-plane and re-render.
    take_input          Take text input from input box.
    close               Close the program.

    Public variables:
    parent              Parent of class (tk.Tk)
    canvas              Instance of Canvas class (Canvas)
    guiLeft             Left collapsible sidebar (ttk.Frame)
    guiRight            Right collapsible sidebar (ttk.Frame)
    statusLabel         To allow statusText to clear itself (ttk.Label)
    statusText          To display the current status (tk.StringVar)
    inputText           To display the current input (tk.StringVar)
    leftText            To display the status of the sidebars (tk.StringVar)
    rightText
    rotBtns             To allow the buttons to be disabled (list)
    barBtns                 all elements are ttk.Buttons
    viewBtns
    viewWidgets         To allow the scales to be disabled (list)
    rotuWidgets             all elements are ttk.Scales
    rotvWidgets
    viewEntries         To allow the entries to be disabled (list)
    rotuEntries             all elements are ttk.Entrys
    rotvEntries
    lint ltheta lphi    To keep track of light properties (tk.DoubleVars)
    lred lgreen lblue   To keep track of light colours (tk.IntVars)
    vtheta vphi vomega  To keep track of camera location (tk.DoubleVars)
    rutheta ruphi       To keep track of rotation axis-plane location
    ruomega rvtheta         (tk.DoubleVars)
    rvphi rvomega
    sphere              To keep track of sphere check (tk.BooleanVar)
    axes                To keep track of axes check (tk.BooleanVar)
    wire                To keep track of wire check (tk.BooleanVar)
    wireCheck           To allow the check to be disabled (ttk.Checkbutton)
    only3D              To know if only 3D mode is on (tk.BooleanVar)
    zoom                To keep track of the current zoom (tk.IntVar)
    dist                To keep track of the current distance (tk.IntVar)
    unitDist            To change dist depending on the distance (int)

    Private methods:
    __init__            Construct Main class.
    _make_menus         Initialize dropdown menus.
    _make_popups        Create the actual pop-up windows.
    _initUI             Initialize GUI placement and bind buttons.
    _collapse           Collapse the right sidebar.
    _valid              Ensure that scale entry inputs are valid.
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
        # On left: title on top, canvas on middle, guiBottom on bottom
        # All that on left, self.guiLeft on right, self.guiRight even righter

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        titleLabel = ttk.Label(self, text=TITLE)
        titleLabel.grid(row=0, column=0, pady=10)
        self.canvas = Canvas(self)
        self.canvas.grid(row=1, column=0, padx=10,
                         sticky=tk.N+tk.E+tk.S+tk.W)
        # 20px padding on bottom but 0px on top since canvas is already padded
        guiBottom = ttk.Frame(self)
        guiBottom.columnconfigure(0, weight=1)
        guiBottom.grid(row=2, column=0, padx=10, pady=(0,20),sticky=tk.E+tk.W)
        self.guiLeft = ttk.Frame(self)
        self.guiLeft.grid(row=0, column=1, rowspan=3, pady=20, sticky=tk.N)
        self.guiRight = ttk.Frame(self)
        self.guiRight.grid(row=0, column=2, rowspan=3, padx=10, sticky=tk.N)

        # Grid guiBottom widgets: 2 rows, 4 columns

        # Grid status label, text box, and link them to statusText, inputText
        self.statusText = tk.StringVar()
        self.statusLabel = ttk.Label(
            guiBottom, textvariable=self.statusText, foreground=COLOURS[4][2])
        self.statusLabel.grid(row=0, column=0, columnspan=4, sticky=tk.W)
        self.inputText = tk.StringVar()
        inputBox = ttk.Entry(guiBottom, textvariable=self.inputText)
        inputBox.bind('<Key-Return>', self.take_input)
        inputBox.grid(row=1, column=0, columnspan=4, sticky=tk.E+tk.W)
        inputBox.focus()    # Put initial keyboard focus on inputBox

        # Grid reset and collapse buttons
        resetBtn = ttk.Button(guiBottom, text='Reset',
                              command=lambda: self.change('r'))
        resetBtn.bind('<Key-Return>', lambda event: self.change('r'))
        resetBtn.grid(row=0, column=1, sticky=tk.E)
        self.leftText = tk.StringVar()
        self.leftText.set('Collapse Left Sidebar >>')
        leftBtn = ttk.Button(guiBottom, textvariable=self.leftText,
                             command=lambda: self._collapse('left'))
        leftBtn.bind('<Key-Return>', lambda event: self._collapse('left'))
        leftBtn.grid(row=0, column=2)
        self.rightText = tk.StringVar()
        self.rightText.set('Collapse Right Sidebar >>')
        rightBtn = ttk.Button(guiBottom, textvariable=self.rightText,
                              command=lambda: self._collapse('right'))
        rightBtn.bind('<Key-Return>', lambda event: self._collapse('right'))
        rightBtn.grid(row=0, column=3)

        # Grid guiLeft widgets: 21 rows, 3 columns

        # Grid rotate label, 2 rotate buttons, and 6 rotation axis buttons
        rotateLabel = ttk.Label(self.guiLeft, text='Rotate:')
        rotateLabel.grid(row=0, column=0, columnspan=3)
        leftRotBtn = ttk.Button(self.guiLeft, image=self._leftBtn,
                                command=lambda: self.canvas.rotate(0))
        leftRotBtn.bind('<Button-1>', lambda event: self._mouse_down('r0'))
        leftRotBtn.bind('<ButtonRelease-1>', self._mouse_up)
        leftRotBtn.bind('<Key-Return>', lambda event: self.canvas.rotate(0))
        leftRotBtn.grid(row=1, column=0, columnspan=2, sticky=tk.W)
        rightRotBtn = ttk.Button(self.guiLeft, image=self._rightBtn,
                                 command=lambda: self.canvas.rotate(1))
        rightRotBtn.bind('<Button-1>', lambda event: self._mouse_down('r1'))
        rightRotBtn.bind('<ButtonRelease-1>', self._mouse_up)
        rightRotBtn.bind('<Key-Return>', lambda event: self.canvas.rotate(1))
        rightRotBtn.grid(row=1, column=1, columnspan=2, sticky=tk.E)

        # Loop through buttons and grid them in 2 rows, 3 columns
        self.rotBtns = ['xw', 'yw', 'zw', 'xy', 'yz', 'xz']
        for i,t in enumerate(self.rotBtns):
            # Use default variable to ensure lambdas have different arguments
            b = ttk.Button(self.guiLeft, text=t, width=5,
                           command=lambda t=t: self.set_rotax(t))
            b.bind('<Key-Return>', lambda event,t=t: self.set_rotax(t))
            b.grid(row=int(2+i/3), column=i%3)
            self.rotBtns[i] = b     # Replace text with actual buttons

        # Grid Wythoff label and 9 Wythoff bar buttons
        wythoffLabel = ttk.Label(self.guiLeft, text='Wythoff:')
        wythoffLabel.grid(row=4, column=0, columnspan=3, pady=(20,0))
        self.barBtns = [('(pqs)', 'a'), ('(|pqs)', 'b'), ('(pqs|)', 'c'),
                        ('(p|qs)', 'p'), ('(q|sp)', 'q'), ('(s|pq)', 's'),
                        ('(pq|s)', 'pq'), ('(qs|p)', 'qs'), ('(sq|q)', 'sp')]
        for i,(t,c) in enumerate(self.barBtns):
            b = ttk.Button(self.guiLeft, text=t, width=5,
                           command=lambda c=c: self.canvas.set_bar(c))
            b.bind('<Key-Return>', lambda event,c=c: self.canvas.set_bar(c))
            b.grid(row=int(5+i/3), column=i%3)
            self.barBtns[i] = b

        # Grid view label and 4 view axis buttons
        viewLabel = ttk.Label(self.guiLeft, text='Views:')
        viewLabel.grid(row=9, column=0, rowspan=2, pady=(20,0))
        self.viewBtns = [('x', [0, pi/2, pi/2]), ('y', [0, pi/2, pi/2]),
                         ('z', [0, 0, pi/2]), ('w', [0, 0, 0])]
        for i,(t,c) in enumerate(self.viewBtns):
            b = ttk.Button(self.guiLeft, text=t, width=5,
                           command=lambda c=c: self.set_view(c))
            b.bind('<Key-Return>', lambda event,c=c: self.set_view(c))
            if i < 2:
                b.grid(row=9, column=1+i%2, pady=(20,0))
            else:
                b.grid(row=10, column=1+i%2)
            self.viewBtns[i] = b

        # Grid light axis and intensity labels, scales, and displays
        lightLabel = ttk.Label(self.guiLeft, text='Light Properties:')
        lightLabel.grid(row=11, column=0, columnspan=3, pady=(20,0))
        self.lint = tk.DoubleVar()
        self.ltheta = tk.DoubleVar()
        self.lphi = tk.DoubleVar()
        lightWidgets = [('cd', self.lint, 2), ('θ', self.ltheta, 6.28),
                        ('φ', self.lphi, 3.14)]     # t = text, v = variable
        for i,(t,v,o) in enumerate(lightWidgets):   # o = maximum value (to)
            l = ttk.Label(self.guiLeft, text=t)
            l.grid(row=12, column=i)
            d = ttk.Entry(self.guiLeft, textvariable=v, width=4,
                          validate='key', validatecommand=(self.register(
                          self._valid), '%P', o, 'float'))
            d.bind('<Key-Return>', lambda event: self.change('s'))
            d.grid(row=13, column=i)
            s = ttk.Scale(self.guiLeft, orient=tk.VERTICAL, from_=0, to=o,
                          variable=v, command=lambda event: self.change('s'))
            s.grid(row=14, column=i)

        # Grid light colours labels, scales, and displays
        colourLabel = ttk.Label(self.guiLeft, text='Light Colours:')
        colourLabel.grid(row=15, column=0, columnspan=3, pady=(20,0))
        self.lred = tk.DoubleVar()
        self.lgreen = tk.DoubleVar()
        self.lblue = tk.DoubleVar()
        colourWidgets = [('Red', self.lred, 255), ('Green', self.lgreen, 255),
                         ('Blue', self.lblue, 255)]
        for i,(t,v,o) in enumerate(colourWidgets):
            l = ttk.Label(self.guiLeft, text=t)
            l.grid(row=16, column=i)
            d = ttk.Entry(self.guiLeft, textvariable=v, width=4,
                          validate='key', validatecommand=(self.register(
                          self._valid), '%P', o, 'int'))
            d.bind('<Key-Return>', lambda event: self.change('s'))
            d.grid(row=17, column=i)
            s = ttk.Scale(self.guiLeft, orient=tk.VERTICAL, from_=0, to=o,
                          variable=v, command=lambda event: self.change('s'))
            s.grid(row=18, column=i)

        # Grid distance label, display, and buttons
        distLabel = ttk.Label(self.guiLeft, text='Camera Distance:')
        distLabel.grid(row=19, column=0, columnspan=3, pady=(20,0))
        self.dist = tk.IntVar()
        dUpBtn = ttk.Button(self.guiLeft, image=self._upBtn,
                            command=lambda: self.change('d+'))
        dUpBtn.bind('<Button-1>', lambda event: self._mouse_down('d+'))
        dUpBtn.bind('<ButtonRelease-1>', self._mouse_up)
        dUpBtn.bind('<Key-Return>', lambda event: self.change('d+'))
        dUpBtn.grid(row=20, column=0)
        distDisplay = ttk.Label(self.guiLeft, textvariable=self.dist)
        distDisplay.grid(row=20, column=1)
        dDownBtn = ttk.Button(self.guiLeft, image=self._downBtn,
                              command=lambda: self.change('d-'))
        dDownBtn.bind('<Button-1>', lambda event: self._mouse_down('d-'))
        dDownBtn.bind('<ButtonRelease-1>', self._mouse_up)
        dDownBtn.bind('<Key-Return>', lambda event: self.change('d-'))
        dDownBtn.grid(row=20, column=2)

        # Grid guiRight widgets: 20 rows, 3 columns

        # Grid options label and 4 checkbuttons for toggling BooleanVars
        optionsLabel = ttk.Label(self.guiRight, text='Options:')
        optionsLabel.grid(row=0, column=0, columnspan=3, pady=(20,0))
        self.sphere = tk.BooleanVar()
        sphereCheck = ttk.Checkbutton(self.guiRight, text='Sphere',
                                      variable=self.sphere,
                                      command=lambda: self.change())
        sphereCheck.grid(row=1, column=0, columnspan=3, sticky=tk.W)
        self.axes = tk.BooleanVar()
        axesCheck = ttk.Checkbutton(self.guiRight, text='Axes',
                                    variable=self.axes,
                                    command=lambda: self.change())
        axesCheck.grid(row=2, column=0, columnspan=3, sticky=tk.W)
        self.wire = tk.BooleanVar()
        self.wireCheck = ttk.Checkbutton(self.guiRight, text='Wireframe',
                                         variable=self.wire,
                                         command=lambda: self.change())
        self.wireCheck.grid(row=3, column=0, columnspan=3, sticky=tk.W)
        self.only3D = tk.BooleanVar()
        only3DCheck = ttk.Checkbutton(self.guiRight, text='Only 3D Mode',
                                      variable=self.only3D,
                                      command=lambda: self.change('3'))
        only3DCheck.grid(row=4, column=0, columnspan=3, sticky=tk.W)

        # Grid view axis labels, scales, and displays
        viewLabel = ttk.Label(self.guiRight, text='Camera Direction:')
        viewLabel.grid(row=5, column=0, columnspan=3, pady=(29,0))
        self.vtheta = tk.DoubleVar()
        self.vphi = tk.DoubleVar()
        self.vomega = tk.DoubleVar()
        self.viewWidgets = [('θ', self.vtheta, 6.28), ('φ', self.vphi, 3.14),
                            ('ω', self.vomega, 3.14)]
        self.viewEntries = []
        for i,(t,v,o) in enumerate(self.viewWidgets):
            l = ttk.Label(self.guiRight, text=t)
            l.grid(row=6, column=i)
            d = ttk.Entry(self.guiRight, textvariable=v, width=4,
                          validate='key', validatecommand=(self.register(
                          self._valid), '%P', o, 'float'))
            d.bind('<Key-Return>', lambda event: self.change('s'))
            d.grid(row=7, column=i)
            s = ttk.Scale(self.guiRight, orient=tk.VERTICAL, from_=0, to=o,
                          variable=v, command=lambda event: self.change('s'))
            s.grid(row=8, column=i)
            self.viewWidgets[i] = s
            self.viewEntries.append(d)

        # Grid rotation axis-plane labels, scales, and displays
        rotLabel = ttk.Label(self.guiRight, text='Rotation Axis-Plane:')
        rotLabel.grid(row=9, column=0, columnspan=3, pady=(20,5))
        rotuLabel = ttk.Label(self.guiRight, text='First Axis Basis:')
        rotuLabel.grid(row=10, column=0, columnspan=3)
        self.rutheta = tk.DoubleVar()
        self.ruphi = tk.DoubleVar()
        self.ruomega = tk.DoubleVar()
        self.rotuWidgets = [('θ', self.rutheta, 6.28), ('φ', self.ruphi, 3.14),
                            ('ω', self.ruomega, 3.14)]
        self.rotuEntries = []
        for i,(t,v,o) in enumerate(self.rotuWidgets):
            l = ttk.Label(self.guiRight, text=t)
            l.grid(row=11, column=i)
            d = ttk.Entry(self.guiRight, textvariable=v, width=4,
                          validate='key', validatecommand=(self.register(
                          self._valid), '%P', o, 'float'))
            d.bind('<Key-Return>', lambda event: self.change('s'))
            d.grid(row=12, column=i)
            s = ttk.Scale(self.guiRight, orient=tk.VERTICAL, from_=0, to=o,
                          variable=v, command=lambda event: self.change('s'))
            s.grid(row=13, column=i)
            self.rotuWidgets[i] = s
            self.rotuEntries.append(d)

        # Grid rotation axis-plane labels, scales, and displays
        rotvLabel = ttk.Label(self.guiRight, text='Second Axis Basis:')
        rotvLabel.grid(row=14, column=0, columnspan=3, pady=(20,0))
        self.rvtheta = tk.DoubleVar()
        self.rvphi = tk.DoubleVar()
        self.rvomega = tk.DoubleVar()
        self.rotvWidgets = [('θ', self.rvtheta, 6.28), ('φ', self.rvphi, 3.14),
                            ('ω', self.rvomega, 3.14)]
        self.rotvEntries = []
        for i,(t,v,o) in enumerate(self.rotvWidgets):
            l = ttk.Label(self.guiRight, text=t)
            l.grid(row=15, column=i)
            d = ttk.Entry(self.guiRight, textvariable=v, width=4,
                          validate='key', validatecommand=(self.register(
                          self._valid), '%P', o, 'float'))
            d.bind('<Key-Return>', lambda event: self.change('s'))
            d.grid(row=16, column=i)
            s = ttk.Scale(self.guiRight, orient=tk.VERTICAL, from_=0, to=o,
                          variable=v, command=lambda event: self.change('s'))
            s.grid(row=17, column=i)
            self.rotvWidgets[i] = s
            self.rotvEntries.append(d)

        # Grid zoom label, display, and buttons
        zoomLabel = ttk.Label(self.guiRight, text='Camera Zoom:')
        zoomLabel.grid(row=18, column=0, columnspan=3, pady=(20,0))
        self.zoom = tk.IntVar()
        zUpBtn = ttk.Button(self.guiRight, image=self._upBtn,
                            command=lambda: self.change('z+'))
        zUpBtn.bind('<Button-1>', lambda event: self._mouse_down('z+'))
        zUpBtn.bind('<ButtonRelease-1>', self._mouse_up)
        zUpBtn.bind('<Key-Return>', lambda event: self.change('z+'))
        zUpBtn.grid(row=19, column=0)
        zoomDisplay = ttk.Label(self.guiRight, textvariable=self.zoom)
        zoomDisplay.grid(row=19, column=1)
        zDownBtn = ttk.Button(self.guiRight, image=self._downBtn,
                              command=lambda: self.change('z-'))
        zDownBtn.bind('<Button-1>', lambda event: self._mouse_down('z-'))
        zDownBtn.bind('<ButtonRelease-1>', self._mouse_up)
        zDownBtn.bind('<Key-Return>', lambda event: self.change('z-'))
        zDownBtn.grid(row=19, column=2)

        self.change('r')    # Initialize all properties with default values

    def _collapse(self, sidebar):
        # Collapse the sidebars.
        # sidebar: which sidebar to collapse, 'left' or 'right' (str)
        if sidebar == 'left':
            if self.leftText.get() == 'Collapse Left Sidebar >>':
                self.leftText.set('Show Left Sidebar <<')
                self.guiLeft.grid_remove()
            elif self.leftText.get() == 'Show Left Sidebar <<':
                self.leftText.set('Collapse Left Sidebar >>')
                self.guiLeft.grid()
        elif sidebar == 'right':
            if self.rightText.get() == 'Collapse Right Sidebar >>':
                self.rightText.set('Show Right Sidebar <<')
                self.guiRight.grid_remove()
            elif self.rightText.get() == 'Show Right Sidebar <<':
                self.rightText.set('Collapse Right Sidebar >>')
                self.guiRight.grid()

    def _valid(self, entry, to, numType):
        # Ensure that scale entry inputs are valid.
        # entry: the value of the entry if the edit is allowed (str)
        # numType: the type of the entry, 'int' or 'float' (str)
        # to: the maximum value of the entry (float)
        # return: whether or not the edit is allowed (bool)
        if entry == '':
            return True         # Always allow empty string, to clear entry
        if len(entry) > 4:
            return False        # Too long to fit, is invalid
        if numType == 'int':
            try:
                value = int(entry)
            except ValueError:
                return False    # Not an int, is invalid
        elif numType == 'float':
            try:
                value = float(entry)
            except ValueError:
                return False    # Not a float, is invalid
        if value < 0 or value > float(to):
            return False        # Out of from_ and to bounds, is invalid
        return True             # Otherwise, is valid

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
               'clear', 'badinput', 'view', 'rot', 'lcol', 'faces'
        """
        if event == '':
            self.statusText.set('')

        elif event == 'faces':  # Keep displaying number and types of faces
            faceText = ''
            faces = self.canvas.get_data('faces')
            for i in range(3,21):
                if faces[i] == 1:   # No -s ending for singular nouns
                    faceText += str(faces[i]) + ' ' + POLYGONS[i] + ' '
                if faces[i] > 1:
                    faceText += str(faces[i]) + ' ' + POLYGONS[i] + 's '
            self.statusText.set(faceText)

        else:
            if event == 'clear':
                self.statusText.set('Canvas cleared.')
            elif event == 'badinput':
                self.statusText.set('Bad input!')   # Keep status on for FADEDELAY

            elif event == 'view':
                self.statusText.set('New view angle: ' + ', '.join(
                    [str(self.vtheta.get()), str(self.vphi.get()),
                     str(self.vomega.get())]))
            elif event == 'lcol':
                self.statusText.set('New light colour: ' + ', '.join(
                    [str(self.lred.get()), str(self.lgreen.get()),
                     str(self.lblue.get())]))
            elif event == 'rot':
                self.statusText.set('New rotation axes: ' + ', '.join(
                    [str(self.rutheta.get()), str(self.ruphi.get()),
                     str(self.ruomega.get())]) + ' and ' + ', '.join(
                    [str(self.rvtheta.get()), str(self.rvphi.get()),
                     str(self.rvomega.get())]))
            self.statusLabel.after(FADEDELAY, self.set_status, '')

    def change(self, change=None, value=0):
        """
        Change GUI values (checkboxes, zoom, distance) and re-render.
        change: the type of change to make (str)
                'b', 'w', '3', 's', 'r', 'z', 'z+', 'z-', 'd', 'd+', 'd-'
        value: the value to change to (float), default 0
        """
        if change == None:      # When checkboxes are ticked, just re-render
            pass
        elif change == 'b':     # Disable 'b' barBtn if polyhedron has no snub
            self.barBtns[1].config(state=tk.DISABLED)
        elif change == 'w':     # Disable wireCheck if camera too close
            self.wire.set(True)
            self.wireCheck.config(state=tk.DISABLED)

        elif change == 'y':
            if value == 0:      # Disable Wythoff buttons if not a Wythoff
                for i in range(9):
                    self.barBtns[i].config(state=tk.DISABLED)
            elif value == 1:    # Enable Wythoff buttons if it is a Wythoff
                for i in range(9):
                    self.barBtns[i].config(state=tk.NORMAL)

        elif change == '3':     # Disable 4D features if only 3D mode is on
            if self.only3D.get() == True:   # Disable 4D view button
                self.viewBtns[3].config(state=tk.DISABLED)
                self.viewWidgets[2].state(['disabled'])
                self.viewEntries[2].state(['disabled'])
                self.vomega.set(1.57)   # Reset omega component of view axis
                for i in range(3,6):    # Disable 4D rotation buttons
                    self.rotBtns[i].config(state=tk.DISABLED)
                for i in range(3):      # Disable second rotation axis scales
                    self.rotvWidgets[i].state(['disabled'])
                    self.rotvEntries[i].state(['disabled'])
                self.ruomega.set(1.57)  # Reset w-component
                self.rvtheta.set('{0:.2f}'.format(0))   # Set second rotaxis
                self.rvphi.set('{0:.2f}'.format(0))     # as w-axis, so all
                self.rvomega.set('{0:.2f}'.format(0))   # rotations are in 3D
                self.wireCheck.config(state=tk.NORMAL)
            else:                       # Enable everything above
                self.viewBtns[3].config(state=tk.NORMAL)
                self.viewWidgets[2].state(['!disabled'])
                self.viewEntries[2].state(['!disabled'])
                for i in range(3,6):
                    self.rotBtns[i].config(state=tk.NORMAL)
                for i in range(3):
                    self.rotvWidgets[i].state(['!disabled'])
                    self.rotvEntries[i].state(['!disabled'])
                self.wire.set(True)     # Force wireframe mode to be true
                self.wireCheck.config(state=tk.DISABLED)

        elif change == 's':     # Round scale labels to two decimal places
            for s in (self.lint, self.ltheta, self.lphi,
                      self.vtheta, self.vphi, self.vomega,
                      self.rutheta, self.ruphi, self.ruomega,
                      self.rvtheta, self.rvphi, self.rvomega):
                try:
                    s.get()
                except tk.TclError:     # Error because tk expects a float
                    s.set(0)            # but the entry may be an empty string
                s.set('{0:.2f}'.format(s.get()))
            # Round RGB colour labels to zero decimal places
            for s in (self.lred, self.lgreen, self.lblue):
                try:
                    s.get()
                except tk.TclError:
                    s.set(0)
                s.set('{0:.0f}'.format(s.get()))
            # Update the current light colour and camera position
            self.set_view([s.get() for s in
                           (self.vtheta, self.vphi, self.vomega)])
            self.set_light([s.get() for s in
                            (self.lred, self.lgreen, self.lblue)])
            self.set_rotax([[s.get() for s in
                             (self.rutheta, self.ruphi, self.ruomega)],
                            [s.get() for s in
                             (self.rvtheta, self.rvphi, self.rvomega)]])
            self.set_status('')     # Don't set any status

        elif change == 'li':
            self.lint.set('{0:.2f}'.format(value))
        elif change == 'la':
            axis = satisfy_axis_restrictions(value)
            self.ltheta.set('{0:.2f}'.format(axis[0]))
            self.lphi.set('{0:.2f}'.format(axis[1]))

        elif change == 'r':     # Reset to initial states
            try:                # Canvas initializes before zoom
                self.canvas.make_polytope(None)
                self.set_view([0, 0, pi/2])
                self.set_light([255,255,255])
                self.set_rotax('xw')
                self.lint.set('{0:.2f}'.format(1))
                self.ltheta.set('{0:.2f}'.format(0))
                self.lphi.set('{0:.2f}'.format(0))
                self.zoom.set(ZOOM) # Set initial zoom to ZOOM
                self.unitDist = 20  # Set initial distance to 20 from max
                # unitDist changes by one per button press, between 1 and 100
                # Follows a x^(-3/2) curve; changes more as distance increases
                # Min is ZOOM*RADIUS*RETINA/1000, max is ZOOM*RADIUS*RETINA
                self.dist.set(int(ZOOM*RADIUS*RETINA/self.unitDist**(3/2)))
                self.sphere.set(False)
                self.axes.set(False)
                self.only3D.set(True)
                self.change('3')    # Set 3D mode to True
                self.change('y', 0) # Not a Wythoff
                self.set_status('clear')
            except:
                return

        # All ZOOM values are explained with the constants
        elif change == 'z':     # Set zoom to the given value or the max zoom
            self.zoom.set(int(min(value, ZOOM*RADIUS*RETINA/2)))
        elif change == 'z+':    # Change zoom by 5 per button press
            self.zoom.set(int(min(self.zoom.get() + 5, ZOOM*RADIUS*RETINA/2)))
        elif change == 'z-':
            self.zoom.set(int(max(self.zoom.get() - 5, 1))) # Minimum 1, not 0

        # Decreasing distance increases unitDist
        elif change == 'd':     # Set distance to given value or max distance
            self.dist.set(int(min(value, ZOOM*RADIUS*RETINA)))
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
                and self.canvas.get_data('star') == False):
                self.wireCheck.config(state=tk.NORMAL)

        self.canvas.render()

    def set_view(self, viewAxis):
        """
        Change the current viewing axis and re-render.
        viewAxis: the viewing axis in spherical coordinates (list, len=3)
        """
        viewAxis = satisfy_axis_restrictions(viewAxis)
        self.vtheta.set('{0:.2f}'.format(viewAxis[0]))
        self.vphi.set('{0:.2f}'.format(viewAxis[1]))
        self.vomega.set('{0:.2f}'.format(viewAxis[2]))
        self.set_status('view')
        self.canvas.render()

    def set_light(self, lcol):
        """
        Change properties of the lighting and re-render.
        lcol: the light colour in RGB integers between 0 and 255 (list, len=3)
        """
        try:
            self.lred.set('{0:.0f}'.format(lcol[0]))
            self.lgreen.set('{0:.0f}'.format(lcol[1]))
            self.lblue.set('{0:.0f}'.format(lcol[2]))
        except:
            pass    # Light colour scales not loaded yet, fix this soon!
        self.set_status('lcol')
        self.canvas.render()

    def set_rotax(self, rotAxis):
        """
        Change the current rotation axis-plane and re-render.
        rotAxis: the rotation axis-plane as a list of two axes (list, len=2)
                 all elements are in spherical coordinates (list, len=3)
        """
        # Button presses have specified rotAxis, manual inputs go through
        if rotAxis == 'xw':
            rotuAxis = (0, pi/2, pi/2)
            rotvAxis = (0, 0, 0)
        elif rotAxis == 'yw':
            rotuAxis = (pi/2, pi/2, pi/2)
            rotvAxis = (0, 0, 0)
        elif rotAxis == 'zw':
            rotuAxis = (0, 0, pi/2)
            rotvAxis = (0, 0, 0)
        elif rotAxis == 'xy':
            rotuAxis = (0, pi/2, pi/2)
            rotvAxis = (pi/2, pi/2, pi/2)
        elif rotAxis == 'yz':
            rotuAxis = (pi/2, pi/2, pi/2)
            rotvAxis = (0, 0, pi/2)
        elif rotAxis == 'xz':
            rotuAxis = (0, pi/2, pi/2)
            rotvAxis = (0, 0, pi/2)
        else:
            rotuAxis = rotAxis[0]
            rotvAxis = rotAxis[1]
        rotuAxis = satisfy_axis_restrictions(rotuAxis)
        rotvAxis = satisfy_axis_restrictions(rotvAxis)
        u = [self.rutheta, self.ruphi, self.ruomega]
        v = [self.rvtheta, self.rvphi, self.rvomega]
        for i in range(3):
            u[i].set('{0:.2f}'.format(rotuAxis[i]))
            v[i].set('{0:.2f}'.format(rotvAxis[i]))
        self.canvas.set_rotaxes((rotuAxis, rotvAxis))
        self.set_status('rot')
        self.canvas.render()

    def take_input(self, event):
        """
        Take text input from input box.
        entry: the input (str), assigned in the function, not a parameter
               general: '', 'clear', 'reset', 'quit', 'exit', 'close'
               zoom/dist/view: 'z0', 'd0', 'v0,0', 'v0,0,0'
               light: 'la0,0', 'la0,0,0', 'lc1,1,1', 'li0'
               rotaxis: 'r0,0,0', 'r0,0,0,0/0,0,0,0'
        """
        hasError = False
        entry = self.inputText.get()

        try:    # If anything fails, catch the error and set hasError to 1
            if entry in ['', 'clear', 'reset']:         # Clear canvas
                self.change('r')
            elif entry in ['quit', 'exit', 'close']:    # Close program
                self.close()

            elif entry.startswith('z'):                 # Set zoom
                zoom = int(entry[1:])
                if zoom < 1:                            # Must be positive
                    hasError = True
                else:
                    self.change('z', zoom)
            elif entry.startswith('d'):                 # Set distance
                distance = int(entry[1:])
                if distance < 1:
                    hasError = True
                else:
                    self.change('d', distance)
            elif entry.startswith('v'):                 # Set viewing axis
                viewAxis = [float(num) for num in entry[1:].split(',')]
                if len(viewAxis) < 3:   # Add omega if axis specified in 3D
                    viewAxis.append(pi/2)
                if len(viewAxis) != 3:  # After adding omega, length must be 3
                    hasError = True
                else:
                    self.set_view(viewAxis)

            elif entry.startswith('li'):                # Set light intensity
                lint = float(entry[2:])
                if lint < 0 or lint > 2:
                    hasError = True
                else:
                    self.change('li', lint)
            elif entry.startswith('la'):                # Set light axis
                laxis = [float(num) for num in entry[2:].split(',')]
                if len(laxis) < 3:
                    laxis.append(pi/2)
                if len(laxis) != 3:
                    hasError = True
                else:
                    self.change('la', laxis)
            elif entry.startswith('lc'):                # Set light colour
                lightColour = [int(num) for num in entry[2:].split(',')]
                if len(lightColour) != 3:
                    hasError = True
                else:
                    self.set_light(lightColour)

            elif entry.startswith('r'):                 # Set rotation axis
                rotAxis = entry[1:].split('/')
                if len(rotAxis) == 2:       # 3D rotation plane, two vectors
                    u = list(map(float, rotAxis[0].split(',')))
                    v = list(map(float, rotAxis[1].split(',')))
                    if (len(u) != 3 or len(v) != 3):
                        hasError = True
                    else:
                        self.set_rotax((u,v))
                elif len(rotAxis) == 1:     # 2D rotation axis, one vector
                    u = list(map(float, rotAxis[0].split(',')))
                    if len(u) == 2:
                        u.append(pi/2)      # Spherical coordinates, w = pi/2
                    if len(u) != 3:
                        hasError = True
                    else:                   # Second vector is w-axis (0,0,0)
                        self.set_rotax((u,(0,0,0)))
                else:
                    hasError = True
            else:
                self.canvas.make_polytope(entry)
                self.set_status('faces')

        except:
            hasError = True

        if hasError == True:
            self.set_status('badinput')
        self.inputText.set('')   # Clear the input box

    def close(self):
        """Close the program."""
        self.parent.destroy()



class Creator():

    """
    Mathematical class that manages polytope creation.

    Public methods:
    get_polytope        Get the polytope created during initialization.

    Private methods:
    __init__            Construct Creator class.
    _schlafli2D         Create a polygon using a 2D Schläfli symbol.
    _schlafli3D         Create a polyhedron using a 3D Schläfli symbol.
    _wythoff            Create a polyhedron using a Wythoff symbol.
    _wythoff_snub       Find the generating point of a snub polyhedron.
    _schwarz            Reflect the generating point everywhere.

    Private variables:
    _polytope           The polytope created during initialization (Polytope)
    _currWythoff        To keep track of the current Wythoff numbers (list)
    _noSnub             To keep track of if the snub does not exist (bool)
    """

    def __init__(self, entry):
        """
        Construct Creator class.
        entry: the text input (str): '{d}', '{d/d}', '{d,d}', '(d | d d)' etc.
        """
        self._polytope = None
        self._currWythoff = None
        self._noSnub = False
        if entry.startswith('{') and entry.endswith('}'):
            try:
                if ',' in entry:
                    self._polytope = Polytope(self._schlafli3D(entry[1:-1]))
                else:
                    self._polytope = Polytope(self._schlafli2D(entry[1:-1]))
            except ValueError:
                self._polytope = None

        elif entry.startswith('(') and entry.endswith(')'):
            try:
                if entry[1] == '|':
                    # Las Vegas algorithm, repeat until success
                    while self._polytope == None:
                        points, edges, colours, self._currWythoff, \
                            self._noSnub = self._wythoff(entry[1:-1])
                        self._polytope = Polytope([points, edges, colours])
                else:
                    points, edges, colours, self._currWythoff, \
                        self._noSnub = self._wythoff(entry[1:-1])
                    self._polytope = Polytope([points, edges, colours])
            except ValueError:
                self._polytope = None
        else:
            self._polytope = None

    def get_polytope(self):
        """
        Get the polytope created during initialization.
        return: the polytope created during initialization (Polytope)
        """
        return self._polytope

    def get_wythoff(self):
        """
        Get the Wythoff variables created during initialization.
        return: the fundamental triangle numbers (list, len=3) and
                if the generated polyhedron cannot be snubbed (bool)
        """
        return self._currWythoff, self._noSnub

    def _schlafli2D(self, entry):
        # Create a polygon using a 2D Schläfli symbol.
        # entry: the 2D Schläfli symbol (str)
        #        p or p/d where p and d are ints
        # return: the [points, edges, pointColours] of the polygon
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
        points = [convert((rs[i], thetas[i], phis[i], omegas[i]), True)
                  for i in range(len(thetas))]
        colours = [(k,0) for k in range(p)]
        edges = [(k,(k+1)%p) for k in range(p)] # Connect points to next ones
        return points, edges, colours

    def _schlafli3D(self, entry):
        # Create a polyhedron using a 3D Schläfli symbol.
        # entry: the 3D Schläfli symbol (str)
        #        p,q where p and q are ints (no support for star polyhedra)
        # return: the [points, edges, pointColours] of the polyhedron

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
        points = [convert((rs[i], thetas[i], phis[i], omegas[i]), True)
                  for i in range(len(thetas))]
        colours = [(k, 0) for k in range(len(thetas))]
        return points, edges, colours

    def _wythoff(self, entry):
        # Create a polyhedron using a Wythoff symbol.
        # entry: the Wythoff symbol (str)
        #        p/d | q/c s/b where p, q, s are ints; d, c, b are optional;
        #        | can be placed anywhere; but all are separated by spaces
        # return: points, edges, pointColours, symbol, noSnub (list, len=5)
        #         [points, edges, pointColours] are of the Wythoff polyhedron
        #         symbol has the fundamental triangle numbers (list, len=3)
        #         noSnub is true if the symbol cannot be snubbed (bool)

        r = RADIUS
        edges = []
        colours = []

        # Store entry as list of numbers (symbol)
        # selection: the location to place the bar (str)
        #             a = p q s      b = | p q s    c = p q s |
        #             p = p | q s    q = q | s p    s = s | p q
        #            pq = p q | s   qs = q s | p   qp = s p | q
        symbol = entry.split()
        if len(symbol) == 3:
            selection = 'a'
        elif len(symbol) == 4:
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
            raise ValueError

        # Extract from symbol each Wythoff number (p,q,s)
        pqs = []
        for i in range(3):
            if '/' in symbol[i]:    # Convert all fractions into decimals
                numer, denom = map(int,symbol[i].split('/'))
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

        # Check if the snub version exists, and disable its button if not
        if sorted(symbol) in SNUBABLE:
            noSnub = False
        else:
            if selection == 'b':
                raise ValueError
            noSnub = True

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
            for i in range(len(points)):
                for j in range(i+1, len(points)):
                    if abs(distance2(points[i], points[j]) - side) < 2:
                        edges.append((i,j))
        # Use sorted symbol for consistency with set_bar
        return points, edges, colours, sorted(symbol), noSnub

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
        # return: the points and side length squared (list, len=2)
        #         the points are in a list of vertices (list)
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



class Canvas(tk.Canvas):

    """
    Display class that manages object rotation and display.

    Public methods:
    make_polytope       Make new polytope and re-render.
    set_rotaxes         Change the rotation axis-plane of all objects.
    set_bar             Change the generating point and make new polyhedron.
    rotate              Rotate objects on button press and re-render.
    get_data            Return data about the current polytope.
    render              Clear the canvas and display the objects.

    Public variables:
    parent              Parent of class (Main)
    rotAxis             The rotation plane's basis vectors (list)

    Private methods:
    _view               Project 4D points on the viewing plane.

    Private variables:
    _currPolytope       Instance of Polytope class (Polytope)
    _sphere             Instance of Sphere class (Sphere)
    _axes               Instance of Axes class (Axes)
    _currWythoff        To keep track of the current Wythoff numbers (list)
    _noSnub             To keep track of if the snub does not exist (bool)
    """

    def __init__(self, parent):
        """
        Construct Canvas class.
        parent: the parent of canvas (Main)
        """
        self.parent = parent
        tk.Canvas.__init__(self, parent, relief=tk.GROOVE,
                           background=COLOURS[4][1],
                           borderwidth=5, width=300, height=200)
        self._currPolytope = Polytope([])
        self._sphere = Sphere(SPHERENUM, RADIUS)
        self._axes = Axes()
        self._noSnub = False

    def make_polytope(self, entry):
        """
        Create a new polytope object and re-render.
        entry: the text input that represents the object (str)
        """
        if not entry:   # Make blank polytope`
            self._currPolytope = Polytope([])
        else:
            creator = Creator(entry)
            polytope = creator.get_polytope()
            if polytope:
                self._currPolytope = polytope
                if creator.get_wythoff()[0]:
                    self._currWythoff, self._noSnub = creator.get_wythoff()
                    self.parent.change('y', 1)  # Yes, this is a Wythoff
                    if self._noSnub == True:
                        self.parent.change('b')
                    if self._currPolytope.star == True:
                        self.parent.change('w')
                else:
                    self.parent.change('y', 0)  # No, this is not a Wythoff
                self.set_rotaxes(None)
                self.render()

    def set_rotaxes(self, rotAxis):
        """
        Change the current rotation axis-plane of all objects.
        rotAxis: the rotation axis-plane as a list of two axes (list, len=2)
                 default is the previous one, when only _currPolytope changes
                 all elements are in spherical coordinates (list, len=3)
        """
        if rotAxis:
            self._currPolytope.set_rotaxis(rotAxis)
            self._sphere.set_rotaxis(rotAxis)
            self._axes.set_rotaxis(rotAxis)
        else:
            rotAxis = [(self.parent.rutheta.get(), self.parent.ruphi.get(),
                        self.parent.ruomega.get()),
                       (self.parent.rvtheta.get(), self.parent.rvphi.get(),
                        self.parent.rvomega.get())]
            self._currPolytope.set_rotaxis(rotAxis)

    def set_bar(self, bar):
        """
        Change the Wythoff generating point and make new uniform polyhedron.
        bar: the type of generating point (str)
        """
        p = str(self._currWythoff[0])
        q = str(self._currWythoff[1])
        s = str(self._currWythoff[2])
        if bar == 'a':
            symbol = ' '.join(['(',p,q,s,')'])
        elif bar == 'b':
            symbol = ' '.join(['(','|',p,q,s,')'])
        elif bar == 'c':
            symbol = ' '.join(['(',p,q,s,'|',')'])
        elif bar == 'p':
            symbol = ' '.join(['(',p,'|',q,s,')'])
        elif bar == 'q':
            symbol = ' '.join(['(',q,'|',s,p,')'])
        elif bar == 's':
            symbol = ' '.join(['(',s,'|',p,q,')'])
        elif bar == 'pq':
            symbol = ' '.join(['(',p,q,'|',s,')'])
        elif bar == 'qs':
            symbol = ' '.join(['(',q,s,'|',p,')'])
        elif bar == 'sp':
            symbol = ' '.join(['(',s,p,'|',q,')'])
        self.make_polytope(symbol)
        self.parent.set_status('faces')

    def rotate(self, direction, rotAngle=ROTANGLE):
        """
        Rotate objects on button press and re-render.
        direction: left is 0, right is 1 (int)
        rotAngle: number of radians to rotate (float), default ROTANGLE
        """
        if direction == 0:
            if self._currPolytope.get_points():
                self._currPolytope.rotate(rotAngle)
            self._sphere.rotate(rotAngle)
            self._axes.rotate(rotAngle)
        elif direction == 1:    # Opposite direction is backwards rotation
            if self._currPolytope.get_points():
                self._currPolytope.rotate(-rotAngle)
            self._sphere.rotate(-rotAngle)
            self._axes.rotate(-rotAngle)
        self.render()

    def get_data(self, event):
        """
        Return data about the current polytope.
        event: the type of data to return (str)
        return: some data to put on the status bar (str)
        """
        if event == 'faces':
            return self._currPolytope.get_face_sides()
        if event == 'star':
            return self._currPolytope.star

    def _view(self, points, viewAxis):
        # Project 4D points on the plane normal to the viewing axis.
        # points: a list of points in 4D (list)
        #         all elements are in spherical coordinates (list, len=4)
        # viewAxis: the viewing axis in spherical coordinates (list, len=3)
        # return: a list of points on the viewing plane (list)
        #         all elements are in Cartesian coordinates (list, len=2)

        so = math.sin(viewAxis[2])
        co = math.cos(viewAxis[2])
        sp = math.sin(viewAxis[1])
        cp = math.cos(viewAxis[1])
        st = math.sin(viewAxis[0])
        ct = math.cos(viewAxis[0])

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
            if abs(viewAxis[2]) < EPSILON:
                if abs(viewAxis[1] - pi/2) < EPSILON:
                    m = (1-t)*-z*sp
                    if (abs(viewAxis[0]) < EPSILON or
                        abs(viewAxis[0] - pi) < EPSILON):
                        n = (1-t)*y*ct
                        p = (1-t)*(-x*co*sp*ct)
                    else:
                        n = (1-t)*(x-y*ct/st)*-st
                        p = ((1-t)*y-n*ct)/(-co*sp*st)
                else:
                    if (abs(viewAxis[0]) < EPSILON or
                        abs(viewAxis[0] - pi) < EPSILON):
                        n = (1-t)*y*ct
                        m = (1-t)*(x-z*sp/cp*ct)*cp/ct
                    else:
                        n = (1-t)*(x-y*ct/st)*(st/(ct*ct-st*st))
                        m = ((1-t)*(y-z*sp/cp*st)+n*ct)*cp/st
                    p = ((1-t)*z+m*sp)/(-co*cp)
            else:
                p = ((1-t)*w+(d*t-f)*co)/so
                if abs(viewAxis[1]) < EPSILON:
                    if (abs(viewAxis[0]) < EPSILON or
                        abs(viewAxis[0] - pi) < EPSILON):
                        n = (1-t)*y*ct
                        m = (1-t)*x*cp*ct
                    else:
                        n = (1-t)*(x-y*ct/st)*-st
                        m = ((1-t)*y-n*ct)/(cp*st)
                else:
                    m = -((1-t)*z+(d*t-f)*so*sp+p*co*cp)/sp
                    if (abs(viewAxis[0]) < EPSILON or
                        abs(viewAxis[0] - pi) < EPSILON):
                        n = (1-t)*y*ct
                    else:
                        n = -((1-t)*x+(d*t-f)*so*sp*ct-m*cp*ct+p*co*sp*ct)/st
            result.append((m*self.parent.zoom.get(),n*self.parent.zoom.get()))
        return result

    def render(self):
        """Clear the canvas, center the frame, and display the objects."""

        self.delete(tk.ALL)         # Clear the canvas
        w = self.winfo_width()//2   # Center the frame
        h = self.winfo_height()//2

        # Get viewAxis and lightAxis data from parent
        viewAxis = [self.parent.vtheta.get(), self.parent.vphi.get(),
                    self.parent.vomega.get()]
        # Light axis only has theta and phi, omega will always be 1.57
        lightAxis = [self.parent.ltheta.get(), self.parent.lphi.get(), pi/2]
        laxis = convert([self.parent.dist.get()] + lightAxis,True)
        lint = self.parent.lint.get()
        lcol = [self.parent.lred.get(), self.parent.lgreen.get(),
                self.parent.lblue.get()]

        # Draw the sphere overlay
        if w != 0 and h != 0 and self.parent.sphere.get() == True:
            # Draw the lines of longitude and latitude
            # _view flipped the x-coordinates upside down for some reason
            # w and h map the viewing plane origin to the centre of the screen
            points = [(-point[0]+w, point[1]+h) for point in
                      self._view(self._sphere.get_points(), viewAxis)]
            edges = self._sphere.get_edges()
            for edge in edges:
                self.create_line(points[edge[0]], points[edge[1]],
                                 fill=COLOURS[1][3], width=3)

        # Draw the coordinate axes
        if w != 0 and h != 0 and self.parent.axes.get() == True:
            # Half-length of the axis, hard-coded, ZeroDivisionError somewhere
            l = 0.3 * RADIUS * self.parent.dist.get() / self.parent.zoom.get()
            axes = [normalize(axis, [l]) for axis in self._axes.get_points()]
            points = [(-point[0]+w, point[1]+h) for point in
                      self._view(axes, viewAxis)]
            edges = self._axes.get_edges()
            for i,edge in enumerate(edges):
                self.create_line(points[edge[0]], points[edge[1]],
                                 fill=COLOURS[3][i+1], width=5)

        if not self._currPolytope.get_points():
            return      # Do nothing if the polytope is empty

        # Draw the actual polytope, since we know it exists
        points = [(-point[0]+w, point[1]+h) for point in
                  self._view(self._currPolytope.get_points(), viewAxis)]
        # As the camera moves away, the light source moves the same distance
        camera = convert([self.parent.dist.get()] + viewAxis,True)

        # Display by drawing polygons in normal mode
        if self.parent.wire.get() == False:
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
                    colour.append(int(min(255, abs(col))))
                rgb = '#{0:02x}{1:02x}{2:02x}'.format(*colour)
                edges = [points[side] for side in faces[0]]
                self.create_polygon(edges,outline=COLOURS[1][5],
                                    width=3,fill=rgb)
                return

            # Otherwise, sort faces by distance to the camera and draw them
            for face in faces:
                distances[face] = distance2(centres[face], camera)
            order = sorted(distances, key=distances.get, reverse=True)
            for face in order:              # Colour the faces
                hexcol = COLOURS[2][sideTypes[face]]
                colour = []
                for i in range(3):
                    deccol = int(hexcol[1+i], 16)
                    col = (deccol*16 + lcol[i] * lint)/2 * shades[face] * lint
                    colour.append(int(max(0, min(255, col))))
                rgb = '#{0:02x}{1:02x}{2:02x}'.format(*colour)
                edges = [points[side] for side in faces[face]]
                self.create_polygon(edges,outline=COLOURS[1][5],
                                    width=3,fill=rgb)
            return

        # Display by drawing lines in wireframe mode
        elif self.parent.wire.get() == True:
            edges = self._currPolytope.get_edges()
            centres = self._currPolytope.get_edge_centres()
            colours = self._currPolytope.get_point_colours()
            for colour in colours:
                self.create_oval([p-5 for p in points[colour[0]]],
                                 [p+5 for p in points[colour[0]]],
                                 fill=COLOURS[0][colour[1]])
            # Create list of doubles of edge distance and edge number
            distances = []
            for i in range(len(edges)):
                distances.append((math.sqrt(distance2(centres[i],camera)), i))
            order = sorted(distances, reverse=True)
            closest = self.parent.dist.get() - RADIUS
            for d,e in order:
                # Colour of closest line is 0, colour of furthest line is 240
                col = max(0, min(255, int(120 * (d - closest) / RADIUS)))
                rgb = '#' + '{0:02x}{0:02x}{0:02x}'.format(col)
                # Width of closest line is 5, width of furthest line is 1
                width = int(5 - 2 * (d - closest) / RADIUS)
                self.create_line(points[edges[e][0]], points[edges[e][1]],
                                 fill=rgb, width=width)
            return



class Object():

    """
    Generic parent class of canvas objects that manages rotations.

    Public methods:
    get_points          Return a list of points of the canvas object.
    get_edges           Return a list of edges of the canvas object.
    set_rotaxis         Set the rotation axis-plane of the canvas object.
    rotate              Rotate the canvas object.

    Private methods:
    __init__            Construct Object class.

    Private variables:
    _points             The points of the canvas object (list)
                            elements are in Cartesian coordinates (list)
    _edges              The edges of the canvas object (list)
                            elements are lists of point indices (list)
    _axis_i             A basis vector of the rotation axis-plane (list)
    _axis_j             A basis vector, both in Cartesian coordinates (list)
    """

    def __init__(self, points, edges):
        """
        Construct Object class.
        points: the initial points of the canvas object (list)
            elements are in Cartesian coordinates (list, len=4)
        edges: the edges of the canvas object (list)
            elements are lists of edge endpoints (list, len=2)
        """
        self._points = points
        self._edges = edges

    def get_points(self):
        """
        Return a list of points of the canvas object.
        return: a list of points of the canvas object (list)
                all elements are in Cartesian coordinates (list, len=4)
        """
        return self._points

    def get_edges(self):
        """
        Return a list of edges of the polytope.
        return: a list of edges of the polytope (list)
                all elements are lists of edge endpoints (list, len=2)
        """
        return self._edges

    def set_rotaxis(self, axes):
        """
        Set the perpendicular unit axes of rotation of the canvas object.
        axes: the perpendicular unit axes of rotation (list, len=2)
              all elements are in spherical coordinates (list, len=3)
        """
        # Remember to add in the value for the radius when converting
        self._axis_i = normalize(convert([1] + list(axes[0]), True))
        self._axis_j = normalize(convert([1] + list(axes[1]), True))

    def rotate(self, rotAngle):
        """
        Rotate the canvas object.
        rotAngle: the angle to rotate the canvas object by (float)
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



class Polytope(Object):

    """
    Drawing class that stores vertex coordinates.

    Inherited methods:
    __init__            Construct Polytope class.
    get_points          Return a list of points of the polytope.
    get_edges           Return a list of edges of the polytope.
    set_rotaxis         Set the rotation axis-plane of the polytope.
    rotate              Rotate the polytope and reset midpoints and centres.

    Inherited variables:
    _points             The points of the polytope (list)
                            elements are in Cartesian coordinates (list)
    _edges              The edges of the polytope (list)
                            elements are lists of point indices (list)
    _axis_i             A basis vector of the rotation axis-plane (list)
    _axis_j             A basis vector, both in Cartesian coordinates (list)

    Public methods:
    get_point_colours   Return a list of colours of the points.
    get_faces           Return a dict of faces of the polytope.
    get_face_sides      Return a dict of the number of each polygon.
    get_faces_by_side   Return a dict of the polygon type of each face.
    get_edge_centres    Return a list of edge midpoints of the polytope.
    get_face_centres    Return a dict of face centres of the polytope.
    get_shades          Calculate the amount of shading needed for each face.

    Public variables:
    star                To keep track of if there are star faces. (bool)

    Private methods:
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
    _pointColours       The point colours of the polytope (list)
                            elements are integers from 0 to 2
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
    """

    def __init__(self, data):
        """
        Construct Polytope class.
        data: the initialization data for the polytope (list)
              each element is a list, data = [points, edges, pointColours]
        """
        if data:
            super().__init__(data[0], data[1])
            self._pointColours = data[2]
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
        else:
            super().__init__([], [])    # Empty polytope, only rotates
            self.star = False

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

            # First compare new edge to previous edges for coplanarity
            if two not in self._visited and two[0] != two[2]:
                a = self._points[pathEnd[0]]
                b = self._points[pathEnd[1]]
                c = self._points[pathEnd[2]]
                u = [b[i]-a[i] for i in range(3)]
                v = [c[i]-b[i] for i in range(3)]
                new = cross3D(u,v)
                coplanar = True
                for i in range(3):
                    if (new[i] - normal[i]) > EPSILON:
                        coplanar = False

                # Only continue if new edge is coplanar
                if coplanar and depth == length:
                    # Side number reached, try to find the end somewhere
                    for neighbour in self._graph[vertex]:
                        if neighbour == end:
                            path.append(end)
                            sides = []
                            length = len(path)
                            for i in range(length):
                                # Find all sequences of two adjacent sides
                                three = [path[(i+j)%length] for j in range(3)]
                                # Find the lexicographically smallest order
                                two = tuple(sorted([three, three[::-1]])[0])
                                sides.append(two)
                                # Don't add if those two adjacent sides are in
                                if two in self._visited:
                                    break
                            else:
                                self._visited.update(sides)
                                faces.append(tuple(path))

                # Side number not reached, continue the breadth-first search
                elif coplanar:
                    frontier = [neighbour for neighbour
                                in self._graph[vertex]] + frontier
                    paths = [path + [neighbour] for neighbour
                             in self._graph[vertex]] + paths
                    normals = [normal for neighbour
                               in self._graph[vertex]] + normals

            # Decrease the number of vertices left in the queue
            depthTime -= 1
            if depthTime == 0:
                # No vertices left in current depth, increase depth by one
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
        surface = distance2(self._faceCentres[0]) - depth   # Minimum distance
        iterDict = dict(self._faces)    # Keeps dictionary from changing size
        for i in iterDict:
            if distance2(self._faceCentres[i]) < surface:
                self._faceSides[len(self._faces[i])] -= 1
                self._faces.pop(i)
                self._faceCentres.pop(i)
                self._faceTypes.pop(i)

    def get_point_colours(self):
        """
        Return a list of colours of the points of the polytope.
        return: a list of colours of the points of the polytope (list)
                all elements are in integers (int)
        """
        return self._pointColours

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
            denom = math.sqrt(abs(distance2(normal) * distance2(light)))
            shade = sum([light[i]*normal[i]/denom for i in range(3)])
            return shade

        # Otherwise, find shades for every face in the polyhedron
        else:
            shades = []
            for f in self._faces:
                light = [laxis[i]-self._faceCentres[f][i] for i in range(3)]
                normal = self._faceCentres[f]    # Normal passes origin
                dnm = math.sqrt(abs(distance2(normal) * distance2(light)))
                shades.append(sum([light[i]*normal[i]/dnm for i in range(3)]))
            return shades

    def rotate(self, rotAngle):
        """
        Rotate the current polytope and reset edge midpoints and face centres.
        rotAngle: the angle to rotate the current polytope by (float)
        """
        super().rotate(rotAngle)
        self._set_edge_centres()
        self._set_face_centres()



class Sphere(Object):

    """
    Drawing class that stores latitude and longitude.

    Inherited methods:
    __init__            Construct Sphere class.
    get_points          Return a list of points of the sphere.
    get_edges           Return a list of edges of the sphere.
    set_rotaxis         Set the rotation axis-plane of the sphere.
    rotate              Rotate the sphere.

    Inherited variables:
    _points             The points of the sphere (list)
                            elements are in Cartesian coordinates (list)
    _edges              The edges of the sphere (list)
                            elements are lists of point indices (list)
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
        points = [(0,0,r,0),(0,0,-r,0)]
        edges = [(0, k*(n-1)+2) for k in range(n)]
        edges.extend([(1, (k+1)*(n-1)+1) for k in range(n)])

        for t in range(n-1):    # Add all thetas and phis as points and edges
            points.extend([convert((r, thetas[t], phis[k], pi/2), True)
                           for k in range(n-1)])
            edges.extend([(t*(n-1)+k+2, t*(n-1)+k+3) for k in range(n-2)])
            edges.extend([(k*(n-1)+t+2, ((k+1)*(n-1) % ((n-1)*n)+t+2))
                          for k in range(n)])

        # End by adding in the last points and connecting their edges
        points.extend([convert((r, thetas[n-1], phis[k], pi/2), True)
                       for k in range(n-1)])
        edges.extend([((n-1)*(n-1)+k+2, (n-1)*(n-1)+k+3) for k in range(n-2)])

        super().__init__(points, edges)



class Axes(Object):

    """
    Drawing class that stores the four orthogonal unit coordinate axes.

    Inherited methods:
    __init__            Construct Axes class.
    get_points          Return a list of points of the axes.
    get_edges           Return a list of edges of the axes.
    set_rotaxis         Set the rotation axis-plane of the axes.
    rotate              Rotate the axes.

    Inherited variables:
    _points             The points of the axes (list)
                            elements are in Cartesian coordinates (list)
    _edges              The edges of the axes (list)
                            elements are lists of point indices (list)
    _axis_i             A basis vector of the rotation axis-plane (list)
    _axis_j             A basis vector, both in Cartesian coordinates (list)
    """

    def __init__(self):
        """Construct Axes class."""
        points = [(1,0,0,0), (-1,0,0,0), (0,1,0,0), (0,-1,0,0),
                  (0,0,1,0), (0,0,-1,0), (0,0,0,1), (0,0,0,-1)]
        edges = [(0,1), (2,3), (4,5), (6,7)]
        super().__init__(points, edges)



root = tk.Tk()
main = Main(root)
root.bind('<Up>', lambda event: main.change('d-'))
root.bind('<Down>', lambda event: main.change('d+'))
root.bind('<Left>', lambda event: main.canvas.rotate(0))
root.bind('<Right>', lambda event: main.canvas.rotate(1))
root.mainloop()
