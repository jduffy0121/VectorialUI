#Driver program to create a UI to read in vectorial model data for comet analysis
#and create multiple results graphs using MatPlotLib.
#Uses PyQt5 as the interface to create the UI.
#This work is based on a pvvectorial repository created by sjoset.
#
#This version is formatted for MacOS
#
#Author: Jacob Duffy
#Version: 8/25/2022

import FileCreator
import FileRunner
import sys
import os
from dataclasses import dataclass
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QListWidget, QTabWidget
from PyQt5.QtWidgets import QLineEdit, QMessageBox, QLabel, QCheckBox, QFileDialog, QVBoxLayout, QRadioButton
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

#Creates a data class to manage the UI data throughout all programs in the interface.
@dataclass
class UIInputData:
    BaseQ: float
    TimeVariationType: float
    SinAmp: float
    SinPer: float
    SinDelta: float
    GausAmp: float
    GausSTD: float
    GausT_Max: float
    SquareAmp: float
    SquareDur: float
    SquareT_Start: float
    ParentName: float
    VOutflow: float
    TauD: float
    Sigma: float
    TtoDRatio: float
    FragmentName: float
    VPhoto: float
    TauT: float
    CometName: float
    Rh: float
    CometDelta: float
    TransformMethod: float
    ApplyTransforMethod: bool
    AngularPoints: int
    RadialPoints: int
    RadialSubsteps: int
    PyvComaPickle: str
    ApertureChecks: str
    YamlFile: str
    PickleInputs: bool

#Creates a global UI data manager to be modified by the UI window and passed to all the programs in the interface.
CurrentUIRun = UIInputData(BaseQ = None, TimeVariationType = None, SinAmp = None, SinPer = None, SinDelta = None,
                        GausAmp = None, GausSTD = None, GausT_Max = None, SquareAmp = None, SquareDur = None,
                        SquareT_Start = None, ParentName = None, VOutflow = None, TauD = None, Sigma = None,
                        TtoDRatio = None, FragmentName = None, VPhoto = None, TauT = None, CometName = None, Rh = None,
                        CometDelta = None, TransformMethod = None, ApplyTransforMethod = False, AngularPoints = None, RadialPoints = None,
                        RadialSubsteps = None, PyvComaPickle = None, ApertureChecks = None, YamlFile = None, PickleInputs = False)

#Plot the graphs
#Creates a MatPlotLib graph widget for ResultsWindow() based on the graphType input.
class PlotGraphs(FigureCanvasQTAgg):
    #Intial UI Config
    def __init__(self, vmc, vmr, graphType, parent=None, width=10, height=10, dpi=100):
        plot = Figure(figsize=(width, height), dpi=dpi) #Creates the figure
        self.axes = plot.add_subplot(111) #Creates the initial (x,y) axis
        FigureCanvasQTAgg.__init__(self, plot)
        self.vmc = vmc
        self.vmr = vmr
        self.graphType = graphType
        self.setParent(parent)
        self.graph()

    #Updates the graph figure that is created in __init__ to the correct graph based on graphType.
    def graph(self):
        if(self.graphType == "frag sput"):
            self.figure = FileRunner.getFragSputter(self.vmc, self.vmr)
        if(self.graphType == "radial"):
            self.figure = FileRunner.getRadialPlots(self.vmc, self.vmr)
        if(self.graphType == "column dens"):
            self.figure = FileRunner.getColumnDensity(self.vmc, self.vmr)
        if(self.graphType == "3d column dens"):
            self.figure = FileRunner.get3DColumnDensity(self.vmc, self.vmr)
        if(self.graphType == "3d column dens cent"):
            self.figure = FileRunner.get3DColumnDensityCentered(self.vmc, self.vmr)
        self.draw() #Draws the figure

#Extra results
#Creates a QWidget for radial/column densities and agreement/aperture checks for ResultsWindow()
class ExtraResults(QWidget):
    #Intial UI Config
    def __init__(self, vmr, parent=None):
        super().__init__(parent)
        self.vmr = vmr
        self.initUI()
    
    #Defines the UI Interface
    def initUI(self):
        global CurrentUIRun
        self.radDensityBox = QListWidget(self)
        self.radDensityBox.addItem(FileRunner.getPrintRadialDensity(self.vmr))
        self.radDensityBox.setGeometry(2000,400,400,2000)
        self.radDensityBox.move(10,10)
        self.columnDesityBox = QListWidget(self)
        self.columnDesityBox.addItem(FileRunner.getPrintColumnDensity(self.vmr))
        self.columnDesityBox.setGeometry(2000,400,400,2000)
        self.columnDesityBox.move(425,10)

        #Test to see if pickle input was used to only add the agreement to the output
        if (CurrentUIRun.PickleInputs):
            self.agreementCheckBox = QListWidget(self)
            self.agreementCheckBox.addItem(FileRunner.getAgreementCheck(self.vmr))
            self.agreementCheckBox.setGeometry(110,600,600,110)
            self.agreementCheckBox.move(850,10)
        else:
            self.agreementCheckBox = QListWidget(self)
            self.agreementCheckBox.addItem(FileRunner.getAgreementCheck(self.vmr))
            self.agreementCheckBox.addItem(CurrentUIRun.ApertureChecks)
            self.agreementCheckBox.setGeometry(200,600,600,200)
            self.agreementCheckBox.move(850,10)
        

#Results window
#Class to give a pop up window with the results from FileRunner.py using PlotGraphs().
class ResultsWindow(QWidget):
    #Intial UI Config
    def __init__(self, vmc, vmr, parent=None):
        super().__init__(parent)
        self.title = 'Results'
        self.left = 10
        self.top = 10
        self.width = 2500
        self.height = 1400
        self.vmc = vmc
        self.vmr = vmr
        self.initUI()

    #Defines the UI Interface
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        #Defines a special style format for Results() (for aesthetic purposes only)
        self.setStyleSheet("""
        QWidget{
            background: None
        }
        QLabel {
            color: #000000;
            background: None;
        }
        """)

        self.layout = QVBoxLayout() #Defines the full window layout
        self.tabs = QTabWidget() #Creates a widget containing the tabs

        #Creates a bunch of empty widgets used in each tab
        self.fragSput = QWidget() 
        self.radial = QWidget()
        self.columD = QWidget()
        self.columD3 = QWidget()
        self.columD3C = QWidget()

        #Plots and displays the fragment sputter graph
        self.tabs.addTab(self.fragSput, "Fragment Sputter") #Creates the tab named "Fragment Sputter"
        self.fragSput.layout = QVBoxLayout(self) #Defines the tab layout as "QVBoxLayout"
        self.fragSputGraph = PlotGraphs(self.vmc, self.vmr, "frag sput", width=5, height=4, dpi=100) #Creates the graph
        self.fragSputToolbar = NavigationToolbar2QT(self.fragSputGraph, self) #Creates the toolbar for the graph
        self.fragSput.layout.addWidget(self.fragSputGraph) #Adds the graph to the QVBoxLayout
        self.fragSput.layout.addWidget(self.fragSputToolbar) #Adds the toolbar to the QVBoxLayout
        self.fragSput.setLayout(self.fragSput.layout) #Finalizes the tab layout
        
        #Plots and displays the radial plot graph
        self.tabs.addTab(self.radial, "Radial")
        self.radial.layout = QVBoxLayout(self)
        self.radialGraph = PlotGraphs(self.vmc, self.vmr, "radial", width=5, height=4, dpi=100)
        self.radialToolbar = NavigationToolbar2QT(self.radialGraph, self)
        self.radial.layout.addWidget(self.radialGraph)
        self.radial.layout.addWidget(self.radialToolbar)
        self.radial.setLayout(self.radial.layout)
        
        #Plots and displays the column density graph
        self.tabs.addTab(self.columD, "Column Density")
        self.columD.layout = QVBoxLayout(self)
        self.columDGraph = PlotGraphs(self.vmc, self.vmr, "column dens", width=5, height=4, dpi=100)
        self.columDToolbar = NavigationToolbar2QT(self.columDGraph, self)
        self.columD.layout.addWidget(self.columDGraph)
        self.columD.layout.addWidget(self.columDToolbar)
        self.columD.setLayout(self.columD.layout)
        
        #Plots and displays the column density graph (off centered)
        self.tabs.addTab(self.columD3, "Column Density (3D Off Centered)")
        self.columD3.layout = QVBoxLayout(self)
        self.columD3Graph = PlotGraphs(self.vmc, self.vmr, "3d column dens", width=5, height=4, dpi=100)
        self.columD3Toolbar = NavigationToolbar2QT(self.columD3Graph, self)
        self.columD3.layout.addWidget(self.columD3Graph)
        self.columD3.layout.addWidget(self.columD3Toolbar)
        self.columD3.setLayout(self.columD3.layout)
        
        #Plots and displays the column density graph (centered)
        self.tabs.addTab(self.columD3C, "Column Density (3D Centered)")
        self.columD3C.layout = QVBoxLayout(self)
        self.columD3CGraph = PlotGraphs(self.vmc, self.vmr, "3d column dens cent", width=5, height=4, dpi=100)
        self.columD3CToolbar = NavigationToolbar2QT(self.columD3CGraph, self)
        self.columD3C.layout.addWidget(self.columD3CGraph)
        self.columD3C.layout.addWidget(self.columD3CToolbar)
        self.columD3C.setLayout(self.columD3C.layout)
    
        self.tabs.addTab(ExtraResults(self.vmr), "Extra") #Creates the extra tab by referencing ExtraResults()
        self.layout.addWidget(self.tabs) #Adds all tabs to the Results window
        self.setLayout(self.layout) #Finalizes the whole window layout
        
#Time Variation window.
#Class to give the user the option to add time variation in anthor window.
class TimeVarWindow(QWidget):
    #Intial UI Config
    def __init__(self,parent=None):
        super().__init__(parent)
        self.title = 'Time Variation Method'
        self.left = 10
        self.top = 10
        self.width = 850
        self.height = 550
        self.initUI()
    
    #Defines the UI Interface
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        #Defines a special style format for TimeVarWindow() (for aesthetic purposes only)
        self.setStyleSheet("""
        QWidget {
            background: #1F2022;
        }
        QListWidget {
            border: 2px solid #fff;
            padding: 10px;
            border-style: solid;
            border-radius: 10px;
            background: #3D3D3D; 
        }
        QLabel {
            color: #EEEADE;
            background: #3D3D3D;
        }   
        QLineEdit {
            padding: 1px;
            color: #EEEADE;
            border-style: solid;
            border: 1px solid #EEEADE;
            border-radius: 8px;
            background: #616161
        }
        QPushButton {
            padding: 1px;
            color: #EEEADE;
            border-style: solid;
            border: 1px solid #EEEADE;
            border-radius: 8px;
            background: #616161
        }
        QPushButton:hover {
            border: 1px #C6C6C6 solid;
            color: #fff;
            background: #0892D0;
        }  
        QRadioButton {
            background: None
        }  """)

        #Creates a bunch of UI Boxes (for aesthetic purposes only)
        self.uiBox1 = QListWidget(self)
        self.uiBox1.setGeometry(60,70,70,60)
        self.uiBox1.move(140,10)
        self.uiBox2 = QListWidget(self)
        self.uiBox2.setGeometry(150,375,375,150)
        self.uiBox2.move(10,90)
        self.uiBox3 = QListWidget(self)
        self.uiBox3.setGeometry(60,100,100,60)
        self.uiBox3.move(140,290)
        self.uiBox4 = QListWidget(self)
        self.uiBox4.setGeometry(150,375,375,150)
        self.uiBox4.move(10,370)
        self.uiBox5 = QListWidget(self)
        self.uiBox5.setGeometry(60,120,120,60)
        self.uiBox5.move(570,10)
        self.uiBox6 = QListWidget(self)
        self.uiBox6.setGeometry(150,375,375,150)
        self.uiBox6.move(440,90)
        self.uiBox7 = QListWidget(self)
        self.uiBox7.setGeometry(160,375,375,160)
        self.uiBox7.move(440,290)

        #Creates title headers for the UI
        self.headingLabel1 = QLabel("Sine", self)
        self.headingLabel1.setFont((QFont('Arial', 25)))
        self.headingLabel1.move(150,20)
        self.headingLabel2 = QLabel("Gaussian", self)
        self.headingLabel2.setFont((QFont('Arial', 25)))
        self.headingLabel2.move(580,20)
        self.headingLabel3 = QLabel("Square", self)
        self.headingLabel3.setFont((QFont('Arial', 25)))
        self.headingLabel3.move(150,300)

        #Creates UI elements for sine input
        self.sineAmpText = QLabel("Input Amplitude: ", self)
        self.sineAmpText.move(20,100)
        self.sineAmpText.resize(300,40)
        self.sineAmpBox = QLineEdit(self)
        self.sineAmpBox.move(130,110)
        self.sineAmpBox.resize(100,25)
        self.sineAmpUnits = QLabel("molecules/sec", self)
        self.sineAmpUnits.move(240,100)
        self.sineAmpUnits.resize(130,40)
        self.sinePeriodText = QLabel("Input Period: ", self)
        self.sinePeriodText.move(20,140)
        self.sinePeriodText.resize(300,40)
        self.sinePeriodBox = QLineEdit(self)
        self.sinePeriodBox.move(110,150)
        self.sinePeriodBox.resize(100,25)
        self.sinePeriodUnits = QLabel("hours", self)
        self.sinePeriodUnits.move(220,140)
        self.sinePeriodUnits.resize(150,40)
        self.sineDeltaText = QLabel("Input Delta: ", self)
        self.sineDeltaText.move(20,180)
        self.sineDeltaText.resize(300,40)
        self.sineDeltaBox = QLineEdit(self)
        self.sineDeltaBox.move(100,190)
        self.sineDeltaBox.resize(100,25)
        self.sineDeltaUnits = QLabel("angular offset in hours", self)
        self.sineDeltaUnits.move(210,180)
        self.sineDeltaUnits.resize(160,40)

        #Creates UI elements for gaussian input
        self.gausAmpText = QLabel("Input Amplitude: ", self)
        self.gausAmpText.move(450,100)
        self.gausAmpText.resize(300,40)
        self.gausAmpBox = QLineEdit(self)
        self.gausAmpBox.move(560,110)
        self.gausAmpBox.resize(100,25)
        self.gausAmpUnits = QLabel("molecules/sec", self)
        self.gausAmpUnits.move(670,100)
        self.gausAmpUnits.resize(120,40)
        self.gausStdText = QLabel("Input Standard Deviation: ", self)
        self.gausStdText.move(450,140)
        self.gausStdText.resize(350,40)
        self.gausStdBox = QLineEdit(self)
        self.gausStdBox.move(620,150)
        self.gausStdBox.resize(100,25)
        self.gausStdUnits = QLabel("hours", self)
        self.gausStdUnits.move(730,140)
        self.gausStdUnits.resize(80,40)
        self.gausTPText = QLabel("Input Time at Peak: ", self)
        self.gausTPText.move(450,180)
        self.gausTPText.resize(350,40)
        self.gausTPBox = QLineEdit(self)
        self.gausTPBox.move(580,190)
        self.gausTPBox.resize(100,25)
        self.gausTPUnits = QLabel("hours", self)
        self.gausTPUnits.move(690,180)
        self.gausTPUnits.resize(100,40)

        #Creates UI elements for square input
        self.squareAmpText = QLabel("Input Amplitude: ", self)
        self.squareAmpText.move(20,380)
        self.squareAmpText.resize(180,40)
        self.squareAmpBox = QLineEdit(self)
        self.squareAmpBox.move(130,390)
        self.squareAmpBox.resize(100,25)
        self.squareAmpUnits = QLabel("molecules/sec", self)
        self.squareAmpUnits.move(240,380)
        self.squareAmpUnits.resize(130,40)
        self.squareDurText = QLabel("Input Duration: ", self)
        self.squareDurText.move(20,420)
        self.squareDurText.resize(300,40)
        self.squareDurBox = QLineEdit(self)
        self.squareDurBox.move(120,430)
        self.squareDurBox.resize(100,25)
        self.squareDurUnits = QLabel("hours", self)
        self.squareDurUnits.move(230,420)
        self.squareDurUnits.resize(100,40)
        self.squareTSPText = QLabel("Input Start of Pulse: ", self)
        self.squareTSPText.move(20,460)
        self.squareTSPText.resize(300,40)
        self.squareTSPBox = QLineEdit(self)
        self.squareTSPBox.move(150,470)
        self.squareTSPBox.resize(100,25)
        self.squareTSPUnits = QLabel("hours", self)
        self.squareTSPUnits.move(260,460)
        self.squareTSPUnits.resize(100,40)

        #Other UI elements
        self.setButton = QPushButton('Set Time Variation Method', self)
        self.setButton.move(430,480)
        self.setButton.resize(400,30)
        self.setButton.clicked.connect(self.setResults)
        self.sineButton = QRadioButton("", self)
        self.sineButton.move(450,300)
        self.sineButtonText = QLabel("Select for sine time variation", self)
        self.sineButtonText.move(480,300)
        self.gausButton = QRadioButton("", self)
        self.gausButton.move(450,340)
        self.gausButtonText = QLabel("Select for gaussian time variation", self)
        self.gausButtonText.move(480,340)
        self.squareButton = QRadioButton("", self)
        self.squareButton.move(450,380)
        self.gausButtonText = QLabel("Select for square time variation", self)
        self.gausButtonText.move(480,380)
        self.noneButton = QRadioButton("", self)
        self.noneButton.move(450,420)
        self.noneButton.setChecked(True)
        self.noneButtonText = QLabel("Select for no time variation", self)
        self.noneButtonText.move(480,420)
        self.show()
    
    #Creates pop up windows for successfully setting time variation or error throws
    def popUpWin(self, type, message=None):
        self.message = QMessageBox()
        if(type == 'success'):
            self.message.setIcon(QMessageBox.Information)
            self.message.setWindowTitle("Success")
            self.message.setText(f"Time variation successfully set to: \"{message}\".")
        else:
            self.message.setIcon(QMessageBox.Critical)
            self.message.setWindowTitle("Error")
            if(type == 'incorrect data'):
                 self.message.setText(f"Incorrect manual data entry for: \"{message}\". \nPlease try again.")
            else:
                return
        self.message.show()
    
    #Sets the current user input to the global variables
    def setResults(self):
        global CurrentUIRun
        #Clears out any possible time variation type input that occured before
        CurrentUIRun.TimeVariationType = None
        CurrentUIRun.SinAmp = None
        CurrentUIRun.SinDelta = None
        CurrentUIRun.SinPer = None
        CurrentUIRun.GausAmp = None
        CurrentUIRun.GausSTD = None
        CurrentUIRun.GausT_Max = None
        CurrentUIRun.SquareAmp = None
        CurrentUIRun.SquareDur = None
        CurrentUIRun.SquareT_Start = None
       
        #Declarations if sine time variation is selected
        if(self.sineButton.isChecked()):
            CurrentUIRun.TimeVariationType = 'sine wave'
            if(FileRunner.valueTest(self.sineAmpBox.text(), 'float')):
                CurrentUIRun.SinAmp = float(self.sineAmpBox.text())
            else:
                self.popUpWin('incorrect data', 'Amplitude')
                return
            if(FileRunner.valueTest(self.sinePeriodBox.text(), 'float')):
                CurrentUIRun.SinPer = float(self.sinePeriodBox.text())
            else:
                self.popUpWin('incorrect data', 'Period')
                return
            if(FileRunner.valueTest(self.sineDeltaBox.text(), 'float')):
                CurrentUIRun.SinDelta = float(self.sineDeltaBox.text())
            else:
                self.popUpWin('incorrect data', 'Delta')
                return
            self.popUpWin('success', 'Sine')
            return

        #Declarations if gaussian time variation is selected
        elif(self.gausButton.isChecked()):
            CurrentUIRun.TimeVariationType = 'gaussian'
            if(FileRunner.valueTest(self.gausAmpBox.text(), 'float')):
                CurrentUIRun.GausAmp = float(self.gausAmpBox.text())
            else:
                self.popUpWin('incorrect data', 'Amplitude')
                return
            if(FileRunner.valueTest(self.gausStdBox.text(), 'float')):
                CurrentUIRun.GausSTD = float(self.gausStdBox.text())
            else:
                self.popUpWin('incorrect data', 'Standard Deviation')
                return
            if(FileRunner.valueTest(self.gausTPBox.text(), 'float')):
                CurrentUIRun.GausT_Max = float(self.gausTPBox.text())
            else:
                self.popUpWin('incorrect data', 'Time at Peak')
                return
            self.popUpWin('success', 'Gaussian')
            return

        #Declarations if square time variation is selected
        elif(self.squareButton.isChecked()):
            CurrentUIRun.TimeVariationType = 'square pulse'
            if(FileRunner.valueTest(self.squareAmpBox.text(), 'float')):
                CurrentUIRun.SquareAmp = float(self.squareAmpBox.text())
            else:
                self.popUpWin('incorrect data', 'Amplitude')
                return
            if(FileRunner.valueTest(self.squareDurBox.text(), 'float')):
                CurrentUIRun.SquareDur = float(self.squareDurBox.text())
            else:
                self.popUpWin('incorrect data', 'Duration')
                return
            if(FileRunner.valueTest(self.squareTSPBox.text(), 'float')):
                CurrentUIRun.SquareT_Start = float(self.squareTSPBox.text())
            else:
                self.popUpWin('incorrect data', 'Start of Pulse')
                return
            self.popUpWin('success', 'Square')
            return
        
        #Declarations if no time variation is selected
        elif(self.noneButton.isChecked()):
            self.popUpWin('success', 'None')
            return

#Class to give a new pop up window to the user more info about proper usage of the Main UI.
class MoreWindow(QWidget):
    #Intial UI Config
    def __init__(self,parent=None):
        super().__init__(parent)
        self.title = 'More Information'
        self.left = 10
        self.top = 10
        self.width = 1050
        self.height = 650
        self.initUI()

    #Defines the UI Interface
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        #Defines a special style format for More() (for aesthetic purposes only)
        self.setStyleSheet("""
        QWidget {
            background: #1F2022;
        }
        QListWidget {
            border: 2px solid #fff;
            padding: 10px;
            border-style: solid;
            border-radius: 10px;
            background: #3D3D3D; 
        }
        QLabel {
            color: #EEEADE;
            background: #3D3D3D;
        } """)

        #Creates a bunch of UI Boxes (for aesthetic purposes only)
        self.uiBox1 = QListWidget(self)
        self.uiBox1.setGeometry(60,100,100,60)
        self.uiBox1.move(485,10)
        self.uiBox2 = QListWidget(self)
        self.uiBox2.setGeometry(270,1000,1000,270)
        self.uiBox2.move(25,100)
        self.uiBox3 = QListWidget(self)
        self.uiBox3.setGeometry(60,115,115,60)
        self.uiBox3.move(485,415)
        self.uiBox4 = QListWidget(self)
        self.uiBox4.setGeometry(125,1000,1000,125)
        self.uiBox4.move(25,505)

        #Creates title headers for the UI
        self.headingLabel1 = QLabel("Inputs", self)
        self.headingLabel1.setFont((QFont('Arial', 25)))
        self.headingLabel1.move(500,20)
        self.headingLabel2 = QLabel("Outputs", self)
        self.headingLabel2.setFont((QFont('Arial', 25)))
        self.headingLabel2.move(500,425)

        #Input text
        self.inputText1 = QLabel("---All name inputs (parent, fragment, and comet) are optional inputs.", self)
        self.inputText1.move(40,120)
        self.inputText2 = QLabel("---Delta under \"comet variables\" is optional as it does not influence the results.", self)
        self.inputText2.move(40,155)
        self.inputText2 = QLabel("---In using a manual input, a .yaml file is created, \"keeping the .yaml file\" will save to your current directory named \"pyvectorial.yaml\".", self)
        self.inputText2.move(40,190)
        self.inputText3 = QLabel("---\"Transformation method\" and \"time variation type\" can only have 1 applied max.", self)
        self.inputText3.move(40,225)
        self.inputText4 = QLabel("---All other manual inputs can only be floats (grid variables must be int).", self)
        self.inputText4.move(40,260)
        self.inputText5 = QLabel("---A .yaml file will only be understood if it is formatted the proper way (look at a manually created .yaml file for this format).", self)
        self.inputText5.move(40,295)
        self.inputText6 = QLabel("---The \"Pvy coma pickle\" is a special file that will not create a vmc when running the program as it already holds all important info from the vmc.", self)
        self.inputText6.move(40,330)

        #Output text
        self.outputText1 = QLabel ("---When finished the program will give the user:", self)
        self.outputText1.move(40,525)
        self.outputText2 = QLabel ("Fragment Sputter Graph", self)
        self.outputText2.move(150,550)
        self.outputText3 = QLabel ("Radial Density Graph", self)
        self.outputText3.move(400,550)
        self.outputText4 = QLabel ("Column Density Graphs (2D, 3D centered, 3D off centered)", self)
        self.outputText4.move(650,550)
        self.outputText5 = QLabel ("Radius vs. Fragment Densitiy Table", self)
        self.outputText5.move(150,570)
        self.outputText6 = QLabel ("Radius vs. Column Densitiy Table", self)
        self.outputText6.move(400,570)
        self.outputText7 = QLabel ("Fragment Agreement Check", self)
        self.outputText7.move(650,570)
        self.outputText8 = QLabel ("Fragment Aperture Check (not given for pickle file input)", self)
        self.outputText8.move(400,590)
        self.show()

#Main UI Window, Driver Class. 
#Used to create/format the UI, read/test in all user data
#reference other child UI windows, run the program and create a new window with the results.
class App(QMainWindow): 
    #Intial UI Config
    def __init__(self,parent=None):
        super().__init__(parent)
        self.title = 'Vectorial Model Input UI' #Titles the UI window
        self.left = 10
        self.top = 10
        self.width = 1250 #Defines the size of the UI window
        self.height = 780 #Defines the size of the UI window
        self.initUI()
    
    #Defines the UI Interface
    def initUI(self):

        #UI Element creator
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        #Creates a bunch of UI Boxes (for aesthetic purposes only)
        self.uiBox1 = QListWidget(self) #Creates a QListWidget() object
        self.uiBox1.setGeometry(665,720,720,665) #Defines the dimensions of the box
        self.uiBox1.move(15,95) #Moves the box to (x,y)
        self.uiBox2 = QListWidget(self)
        self.uiBox2.setGeometry(260,430,430,260)
        self.uiBox2.move(800,95)
        self.uiBox3 = QListWidget(self)
        self.uiBox3.setGeometry(65,175,175,65)
        self.uiBox3.move(250,7)
        self.uiBox4 = QListWidget(self)
        self.uiBox4.setGeometry(65,150,150,65)
        self.uiBox4.move(935,7)
        self.uiBox5 = QListWidget(self)
        self.uiBox5.setGeometry(270,430,430,270)
        self.uiBox5.move(800,385)
        self.uiBox6 = QListWidget(self)
        self.uiBox6.setGeometry(160,325,325,160)
        self.uiBox6.move(850,440)
        #Defines a special style format for uiBox6
        self.uiBox6.setStyleSheet("border: 1px solid #fff; padding: 10px; border-style: solid; color: #EEEADE; border-radius: 10px; background: #616161;") 

        #Creates title headers for the UI
        self.headingLabel1 = QLabel("Manual Input", self) #Creates a text box with the input string
        self.headingLabel1.move(260,10)
        self.headingLabel1.setFont((QFont('Arial', 25))) #Sets font to the input string and font size
        self.headingLabel1.resize(150,60) #Resize the text to fill up to the (x,y)
        self.headingLabel2 = QLabel("File Inputs", self)
        self.headingLabel2.move(950,10)
        self.headingLabel2.setFont((QFont('Arial', 25)))
        self.headingLabel2.resize(130,60)
        
        #Creates manual input UI elements for the Production section
        self.textPro = QLabel("Production Variables", self)
        self.textPro.setFont((QFont('Arial', 20)))
        self.textPro.move(80,110)
        self.textPro.resize(400,40)
        self.baseQText = QLabel("Input Base Q: ", self)
        self.baseQText.move(30,160)
        self.baseQText.resize(180,40)
        self.baseQBox = QLineEdit(self) #Creates a textbox for user to input data in
        self.baseQBox.move(120,170)
        self.baseQBox.resize(100,25)
        self.baseQUnits = QLabel("prod/sec", self)
        self.baseQUnits.move(230,160)
        self.baseQUnits.resize(180,40)
        self.timeVarBox = QPushButton("*Select Time Variation Method", self)
        self.timeVarBox.move(30,210)
        self.timeVarBox.resize(200,25)
        self.timeVarBox.clicked.connect(self.timeVarWin) #Defines the method call when the button is clicked

        #Creates manual input UI elements for the Parent section
        self.textPar = QLabel("Parent Variables", self)
        self.textPar.setFont((QFont('Arial', 20)))
        self.textPar.move(80,270)
        self.textPar.resize(400,40)
        self.parNameText = QLabel("*Input Parent Name: ", self)
        self.parNameText.move(30,320)
        self.parNameText.resize(300,40)
        self.parNameBox = QLineEdit(self)
        self.parNameBox.move(165,330)
        self.parNameBox.resize(100,25)
        self.outVText = QLabel("Input Outflow Velocity: ", self)
        self.outVText.move(30,360)
        self.outVText.resize(300,40)
        self.outVBox = QLineEdit(self)
        self.outVBox.move(175,370)
        self.outVBox.resize(100,25)
        self.outVUnits = QLabel("km/sec", self)
        self.outVUnits.move(285,360)
        self.outVUnits.resize(300,40)
        self.tauDText = QLabel("Input Tau_D: ", self)
        self.tauDText.move(30,400)
        self.tauDText.resize(300,40)
        self.tauDBox = QLineEdit(self)
        self.tauDBox.move(120,410)
        self.tauDBox.resize(100,25)
        self.tauDUnits = QLabel("sec", self)
        self.tauDUnits.move(230,400)
        self.tauDUnits.resize(300,40)
        self.sigmaText = QLabel("Input Sigma: ", self)
        self.sigmaText.move(30,440)
        self.sigmaText.resize(300,40)
        self.sigmaBox = QLineEdit(self)
        self.sigmaBox.move(120,450)
        self.sigmaBox.resize(100,25)
        self.sigmaUnits = QLabel("cm^2", self)
        self.sigmaUnits.move(230,440)
        self.sigmaUnits.resize(300,40)
        self.t_DText = QLabel("Input T to D Ratio: ", self)
        self.t_DText.move(30,480)
        self.t_DText.resize(160,40)
        self.t_DBox = QLineEdit(self)
        self.t_DBox.move(150,490)
        self.t_DBox.resize(100,25)

        #Creates manual input UI elements for the Fragment section  
        self.textFrag = QLabel("Fragment Variables", self)
        self.textFrag.setFont((QFont('Arial', 20)))
        self.textFrag.move(80,580)
        self.textFrag.resize(400,40) 
        self.fragNameText = QLabel("*Input Fragment Name: ", self)
        self.fragNameText.move(30,630)
        self.fragNameText.resize(300,40)
        self.fragNameBox = QLineEdit(self)
        self.fragNameBox.move(185,640)
        self.fragNameBox.resize(100,25) 
        self.vPhotoText = QLabel("Input VPhoto: ", self)
        self.vPhotoText.move(30,670)
        self.vPhotoText.resize(180,40)
        self.vPhotoBox = QLineEdit(self)
        self.vPhotoBox.move(130,680)
        self.vPhotoBox.resize(100,25)
        self.vPhotoUnits = QLabel("km/sec", self)
        self.vPhotoUnits.move(240,670)
        self.vPhotoUnits.resize(300,40)
        self.tauTFragText = QLabel("Input Tau_T: ", self)
        self.tauTFragText.move(30,710)
        self.tauTFragText.resize(300,40)
        self.tauTFragBox = QLineEdit(self)
        self.tauTFragBox.move(120,720)
        self.tauTFragBox.resize(100,25)   
        self.tauTFragUnits = QLabel("sec", self)
        self.tauTFragUnits.move(230,710)
        self.tauTFragUnits.resize(300,40)

        #Creates manual input UI elements for the Comet section
        self.textPar = QLabel("Comet Variables", self)
        self.textPar.setFont((QFont('Arial', 20)))
        self.textPar.move(500,110)
        self.textPar.resize(200,40)
        self.cometNameText = QLabel("*Input Comet Name: ", self)
        self.cometNameText.move(450,160)
        self.cometNameText.resize(200,40)
        self.cometNameBox = QLineEdit(self)
        self.cometNameBox.move(590,170)
        self.cometNameBox.resize(100,25) 
        self.rHText = QLabel("Input Rh: ", self)
        self.rHText.move(450,200)
        self.rHText.resize(100,40)
        self.rHBox = QLineEdit(self)
        self.rHBox.move(520,210)
        self.rHBox.resize(100,25)
        self.rHUnits = QLabel("AU", self)
        self.rHUnits.move(630,200)
        self.rHUnits.resize(80,40)
        self.deltaComText = QLabel("*Input Delta: ", self)
        self.deltaComText.move(450,240)
        self.deltaComText.resize(150,40)
        self.deltaComBox = QLineEdit(self)
        self.deltaComBox.move(540,250)
        self.deltaComBox.resize(100,25)
        self.tFMethText = QLabel("*Transformation Method: ", self)
        self.tFMethText.move(450,330)
        self.tFMethText.resize(150,40)
        self.tFApplied1 = QCheckBox("", self) #Set checkable box
        self.tFApplied1.setChecked(False) #Set checked box to be unchecked when the window is created
        self.tFApplied1.move(620,290)
        self.tFApplied1.resize(50,40)
        self.tFApplied1Text = QLabel("Cochran", self)
        self.tFApplied1Text.resize(65,40)
        self.tFApplied1Text.move(648,290)
        self.tFApplied2 = QCheckBox("", self)
        self.tFApplied2.setChecked(False)
        self.tFApplied2.move(620,330)
        self.tFApplied2.resize(50,40)
        self.tFApplied2Text = QLabel("Fortran", self)
        self.tFApplied2Text.resize(65,40)
        self.tFApplied2Text.move(648,330)
        self.tFApplied3 = QCheckBox("", self)
        self.tFApplied3.move(620,370)
        self.tFApplied3.resize(50,40)   
        self.tFApplied3Text = QLabel("None", self)
        self.tFApplied3Text.resize(65,40)
        self.tFApplied3Text.move(648,370)     

        #Creates manual input UI elements for the Grid section
        self.textGrid = QLabel("Grid Variables", self)
        self.textGrid.setFont((QFont('Arial', 20)))
        self.textGrid.move(500,430)
        self.textGrid.resize(200,40)
        self.aPointsText = QLabel("Input Angular Points: ", self)
        self.aPointsText.move(450,480)
        self.aPointsText.resize(200,40)
        self.aPointsBox = QLineEdit(self)
        self.aPointsBox.move(590,490)
        self.aPointsBox.resize(100,25)
        self.radPointsText = QLabel("Input Radial Points: ", self)
        self.radPointsText.move(450,530)
        self.radPointsText.resize(200,40)
        self.radPointsBox = QLineEdit(self)
        self.radPointsBox.move(580,540)
        self.radPointsBox.resize(100,25)
        self.radSubText = QLabel("Input Radial Substeps: ", self)
        self.radSubText.move(450,580)
        self.radSubText.resize(200,40)
        self.radSubBox = QLineEdit(self)
        self.radSubBox.move(600,590)
        self.radSubBox.resize(100,25)

        #Creates other UI elements such as certain check boxes/text and other UI stuff
        self.keepFile = QCheckBox("", self)
        self.keepFile.setChecked(False)
        self.keepFile.move(450,680)
        self.keepFile.resize(400,40)
        self.keepFileBox = QLabel("*Keep Created .yaml File", self)
        self.keepFileBox.move(478,680)
        self.keepFileBox.resize(150,40)
        self.runProgramButton = QPushButton('Run Program', self)
        self.runProgramButton.move(815,730)
        self.runProgramButton.resize(400,30)
        self.runProgramButton.clicked.connect(self.runProg)
        self.file = QPushButton('*.yaml File Upload', self)
        self.file.move(815,110)
        self.file.resize(400,30)
        self.file.clicked.connect(self.fileInp)
        self.more = QPushButton('*More Information', self)
        self.more.move(815,680)
        self.more.resize(400,30)
        self.more.clicked.connect(self.moreInfo)
        self.fileOut = QListWidget(self) #Creates a widget to display the download path for yaml upload
        self.fileOut.setGeometry(50,400,400,50)
        self.fileOut.setStyleSheet("border: 1px solid #fff; padding: 10px; border-style: solid; color: #EEEADE; border-radius: 10px; background: #616161;")
        self.fileOut.move(815,160)
        self.pickleBox = QPushButton("*Pyv Coma Pickle File Upload", self)
        self.pickleBox.move(815,240)
        self.pickleBox.resize(400,30)
        self.pickleBox.clicked.connect(self.pickleInp)
        self.pickleOut = QListWidget(self)
        self.pickleOut.setGeometry(50,400,400,50)
        self.pickleOut.move(815,290)
        self.pickleOut.setStyleSheet("border: 1px solid #fff; padding: 10px; border-style: solid; color: #EEEADE; border-radius: 10px; background: #616161;")
        self.typeProgram = QLabel('Type of Program Input', self)
        self.typeProgram.setFont((QFont('Arial', 25)))
        self.typeProgram.move(880,395)
        self.typeProgram.resize(250,40)
        self.manProgramButton = QRadioButton('', self)
        self.manProgramButton.move(865,455)
        self.manProgramButton.resize(400,40)
        self.manProgramButtonText = QLabel('Manual Input', self)
        self.manProgramButtonText.move(900,455)
        self.manProgramButtonText.resize(200,40)
        self.manProgramButtonText.setFont((QFont('Arial', 18)))
        self.manProgramButtonText.setStyleSheet("color: #EEEADE; background: #616161")
        self.yamlProgramButton = QRadioButton('', self)
        self.yamlProgramButton.move(865,505)
        self.yamlProgramButton.resize(400,40)
        self.yamlProgramButtonText = QLabel('File Input (.yaml)', self)
        self.yamlProgramButtonText.move(900,505)
        self.yamlProgramButtonText.resize(250,40)
        self.yamlProgramButtonText.setFont((QFont('Arial', 18)))
        self.yamlProgramButtonText.setStyleSheet("color: #EEEADE; background: #616161")
        self.pickleProgramButton = QRadioButton('', self)
        self.pickleProgramButton.move(865,555)
        self.pickleProgramButton.resize(400,40)
        self.pickleProgramButtonText = QLabel('File Input (Pickle)', self)
        self.pickleProgramButtonText.resize(250,40)
        self.pickleProgramButtonText.move(900,555)
        self.pickleProgramButtonText.setFont((QFont('Arial', 18)))
        self.pickleProgramButtonText.setStyleSheet("color: #EEEADE; background: #616161")

        self.show() #Shows the window

    #Creates pop up windows for successful run or error throws
    def popUpWin(self, type, message=None):
        self.message = QMessageBox() #Creates the QMessageBox() object
        if(type == 'success'): #Successful run pop up
            self.message.setIcon(QMessageBox.Information) #Sets icon for the window
            self.message.setWindowTitle("Success")
            self.message.setText("Program run successful!")
        else:
            self.message.setIcon(QMessageBox.Critical)
            self.message.setWindowTitle("Error")
            if(type == 'incorrect yaml'): #Yaml file has an incorrect data type, almost always string to float/int
                self.message.setText(f"The .yaml file is either missing or has an incorrect data type assigned to: \"{message}\". \nPlease try again.")
            elif(type == 'incorrect pickle'): #Pickle file can not be understood by pyvectorial
                self.message.setText("The pickle file could not be understood. \nPlease try again.")
            elif(type == 'no file'): #User selected yaml or pickle file input but never gave a file
                self.message.setText("A file has not been selected. \nPlease try again.")
            elif(type == 'incorrect data'): #User input an incorrect data type, almost always string to float/int
                 self.message.setText(f"Incorrect manual data entry for: \"{message}\". \nPlease try again.")
            elif(type == 'too many boxes'): #User selected too many boxes for an input that only accepts 1 selected
                self.message.setText(f"Too many input boxes selected for: \"{message}\". \nPlease try again.")
            elif(type == 'no boxes'): #User selected no boxes for an input that only accepts 1 selected
                self.message.setText(f"No input boxes selected for: \"{message}\". \nPlease try again.")
            elif(type == 'no input'): #User does not select an input type.
                self.message.setText("No input type was selected. \nPlease try again.")
            elif(type == 'incorrect file run'): #User's manual/file input was unable to be calculated properly
                self.message.setText("The data in the input was unable to converted to results. \nPlease try again.")
            else:
                return
        self.message.show() #Shows the pop up window

    #File Path References

    #Gets the name/file path of the pickle file.
    def pickleInp(self):
        global CurrentUIRun
        self.pickleOut.clear() #Clears the output of the pickleOut widget that displays the path for the user
        CurrentUIRun.PyvComaPickle = None #Clears any previous file path
        file = QFileDialog.getOpenFileNames(self, 'Open file')[0] #Gets the file path
        i = 0
        while i < len(file):
            self.pickleOut.addItem(file[i]) #Adds the path of the pickle file to the pickleOut widget
            CurrentUIRun.PyvComaPickle = file[i] #Stores the file path
            i += 1
        return
    
    #Gets the name/file path of the yaml file.
    def fileInp(self):
        global CurrentUIRun
        self.fileOut.clear()
        CurrentUIRun.YamlFile = None
        file = QFileDialog.getOpenFileNames(self, 'Open file', '', 'Yaml files (*.yaml)')[0] #Gets the file path, only allowing .yaml files to be selected
        i = 0
        while i < len(file):
            self.fileOut.addItem(file[i])
            CurrentUIRun.YamlFile = file[i]
            i += 1
        return

    #References the MoreWindow() above when the more infomation button is pressed.
    def moreInfo(self, checked):
        self.Win = MoreWindow()
        self.Win.show()
    
    #Refences the TineVarWindow() above when the time variation button is pressed.
    def timeVarWin(self, checked):
        self.Win = TimeVarWindow()
        self.Win.show()
        
    #Run Program button
    def runProg(self):
        global CurrentUIRun
        CurrentUIRun.PickleInputs = False

        #Manual input runner
        #Test proper user input and assigns the results to global variables
        #Throws errors if user input is not correct
        if(self.manProgramButton.isChecked()):

            #Param Declarations
            if(FileRunner.valueTest(self.baseQBox.text(), 'float')): #Test to see if the manual input is a correct type for all data required
                CurrentUIRun.BaseQ = float(self.baseQBox.text())
            else:
                self.popUpWin('incorrect data', 'Base Q') #Throws an error if any data is an incorrect type and exits the program
                return

            #Parent Declarations
            CurrentUIRun.ParentName = self.parNameBox.text()
            if(FileRunner.valueTest(self.outVBox.text(), 'float')):
                CurrentUIRun.VOutflow = float(self.outVBox.text())
            else:
                self.popUpWin('incorrect data', 'Outflow Velocity')
                return
            if(FileRunner.valueTest(self.tauDBox.text(), 'float')):
                CurrentUIRun.TauD = float(self.tauDBox.text())
            else:
                self.popUpWin('incorrect data', 'Tau_D')
                return
            if(FileRunner.valueTest(self.sigmaBox.text(), 'float')):
                CurrentUIRun.Sigma = float(self.sigmaBox.text())
            else:
                self.popUpWin('incorrect data', 'Sigma')
                return
            if(FileRunner.valueTest(self.t_DBox.text(), 'float')):
                CurrentUIRun.TtoDRatio = float(self.t_DBox.text())
            else:
                self.popUpWin('incorrect data', 'T to D Ratio')
                return

            #Fragment Declarations
            CurrentUIRun.FragmentName = self.fragNameBox.text()
            if(FileRunner.valueTest(self.vPhotoBox.text(), 'float')):
                CurrentUIRun.VPhoto = float(self.vPhotoBox.text())
            else:
                self.popUpWin('incorrect data', 'VPhoto')
                return
            if(FileRunner.valueTest(self.tauTFragBox.text(), 'float')):
                CurrentUIRun.TauT = float(self.tauTFragBox.text())
            else:
                self.popUpWin('incorrect data', 'Tau_T')
                return

            #Comet Declarations
            CurrentUIRun.CometName = self.cometNameBox.text()
            if(FileRunner.valueTest(self.rHBox.text(), 'float')):
                CurrentUIRun.Rh = float(self.rHBox.text())
            else:
                self.popUpWin('incorrect data', 'Rh')
                return
            CurrentUIRun.CometDelta = self.deltaComBox.text()
            if((self.tFApplied1.isChecked() == False)
                and (self.tFApplied2.isChecked() == False)
                and (self.tFApplied3.isChecked() == False)):
                self.popUpWin('no boxes', 'Transformation Method') #Throws an error if there is no TFApplied box selected
                return
            elif((self.tFApplied1.isChecked() == True) #Checks all 3 tFApplied boxes to make sure only
                and (self.tFApplied2.isChecked() == False) #1 was selected and assigns it to the correct value
                and (self.tFApplied3.isChecked() == False)):
                CurrentUIRun.TransformMethod = "cochran_schleicher_93"
                CurrentUIRun.ApplyTransforMethod = True
            elif((self.tFApplied1.isChecked() == False)
                and (self.tFApplied2.isChecked() == True)
                and (self.tFApplied3.isChecked() == False)):
                CurrentUIRun.TransformMethod = "festou_fortran"
                CurrentUIRun.ApplyTransforMethod = True
            elif((self.tFApplied1.isChecked() == False)
                and (self.tFApplied2.isChecked() == False)
                and (self.tFApplied3.isChecked() == True)):
                CurrentUIRun.TransformMethod = None
                CurrentUIRun.ApplyTransforMethod = False
            else:
                self.popUpWin('too many boxes', 'Transformation Method') #Throws an error if there are more than 1 TFApplied box selected
                return

            #Grid Declarations
            if(FileRunner.valueTest(self.aPointsBox.text(), 'int')):
                CurrentUIRun.AngularPoints = int(self.aPointsBox.text())
            else:
                self.popUpWin('incorrect data', 'Angular Points')
                return
            if(FileRunner.valueTest(self.radPointsBox.text(), 'int')):
                CurrentUIRun.RadialPoints = int(self.radPointsBox.text())
            else:
                self.popUpWin('incorrect data', 'Radial Points')
                return
            if(FileRunner.valueTest(self.radSubBox.text(), 'int')):
                CurrentUIRun.RadialSubsteps = int(self.radSubBox.text())
            else:
                self.popUpWin('incorrect data', 'Radial Substeps')
                return
            
            #Runs the program
            vmc, vmr = FileRunner.runManualProgram(CurrentUIRun) #Runs the manuel program, creating a yaml file, vmc and vmr in FileCreator.py and FileRunner.py
            if(self.keepFile.isChecked() == False): #Removes the file if the keepFile == False
                FileCreator.removeFile('pyvectorial.yaml')
            if(vmc == False): #Test to see if the program was able to run properly
                self.popUpWin('incorrect file run')
                return
            self.popUpWin('success') #Opens the successful run pop up window
            self.Win = ResultsWindow(vmc, vmr) #Creates the results with the vmc and vmr
            self.Win.show() #Shows the results window
            return
        
        #Yaml input runner
        #Test to see if the file is properly formatted and will compute the results if so.
        #Throws an error if the test fails.
        elif(self.yamlProgramButton.isChecked()):
            if (os.path.isfile(f"{CurrentUIRun.YamlFile}") == False): #Test to see if the user uploaded a file
                self.popUpWin('no file')
                return
            testResult, message = FileRunner.fileTest(CurrentUIRun.YamlFile, CurrentUIRun) #Gets the bool test result and a message if testResult = False
            if (testResult): #Reads the file to see if it is formatted properly  
                #Runs the program
                vmc, vmr = FileRunner.runFileYamlProgram(CurrentUIRun.YamlFile, CurrentUIRun) #Runs the yaml file, creating a vmc and vmr in FileRunner.py
                if(vmc == False):
                    self.popUpWin('incorrect file run')
                    return
                self.popUpWin('success')
                self.Win = ResultsWindow(vmc, vmr)
                self.Win.show()
            else:
                self.popUpWin('incorrect yaml', message) #Throws an error meaning that the user's file dict was missing important info
            return
        
        #Pickle input runner
        #Test to see if the pickle file can be understood and runs the results from that.
        #Throws an error if the test fails.
        elif(self.pickleProgramButton.isChecked()):
            CurrentUIRun.PickleInputs = True
            if (os.path.exists(f"{CurrentUIRun.PyvComaPickle}") == False): #Test to see if the user uploaded a file
                self.popUpWin('no file')
                return
            if(FileRunner.pickleTest(CurrentUIRun.PyvComaPickle) == False): #Test to see if pyvectorial can read the pickle in FileRunner.py
                self.popUpWin('incorrect pickle')
                return
            #Runs the program
            vmc, vmr = FileRunner.runFilePickleProgram(CurrentUIRun.PyvComaPickle) #Runs the pickle file, creating a default vmc and proper vmr in FileRunner.py
            self.popUpWin('success')
            self.Win = ResultsWindow(vmc, vmr) 
            self.Win.show() 
            return
        else:
            self.popUpWin('no input')
            return

#Defines the UI when initially running the program
if __name__ == '__main__':
    app = QApplication(sys.argv)
    #Defines the style format for the whole app/main window (for aesthetic purposes only)
    #Other windows or Q objects can override this style by declaring a new setStyleSheet()
    app.setStyleSheet("""
    QMainWindow{ 
        background-color: #1F2022; 
    }
    QListWidget {
        border: 2px solid #fff;
        padding: 10px;
        border-style: solid;
        border-radius: 10px;
        background: #3D3D3D; 
    }
    QLabel {
        color: #EEEADE;
        background: #3D3D3D;
    }
    QLineEdit {
        padding: 1px;
        color: #EEEADE;
        border-style: solid;
        border: 1px solid #EEEADE;
        border-radius: 8px;
        background: #616161
    }
    QPushButton {
        padding: 1px;
        color: #EEEADE;
        border-style: solid;
        border: 1px solid #EEEADE;
        border-radius: 8px;
        background: #616161
    }
    QPushButton:hover {
        border: 1px #C6C6C6 solid;
        color: #fff;
        background: #0892D0;
    }
    QFileDialog {
        background: #616161;
        color: #3D3D3D;
    }
    QMessageBox {
        background: #3D3D3D
    }    """)
    Win = App() #Only shows App() on start up
    Win.show()
    sys.exit(app.exec_()) #Exits the program when all windows are closed