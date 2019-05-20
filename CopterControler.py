from userInput import userInput
from dronIo import dronIo
from display import display
from time import sleep
from widgets import *
import csv

class Controller:
    def __init__(self):
        self.inputs = userInput()
        self.display = display()
        self.dron = dronIo()
        self._running = False

    def close(self):
        self.log('Exiting - closing devices...')
        sleep(0.2)
        self.dron.close()
        self.inputs.close()
        self.display.close()
        self.log('All closed! - Exiting in 1 secound')
        sleep(1)
        self._running = False

    def open(self):
        # Connect callbacks
        self.inputs.setExitCallback(self.close)
        self.inputs.setMessageCallback(self.dron.sendMessage)

        # Connect inputs
        self.dron.setThrotleInput(self.inputs.getThrotle)
        self.dron.setRottInput(self.inputs.getRott)
        self.dron.setPitchInput(self.inputs.getPitch)
        self.dron.setRollInput(self.inputs.getRoll)
        self.dron.setGimbalPitchInput(self.inputs.getGimbalPitch)
        self.dron.setGimbalRollInput(self.inputs.getGimbalRoll)


        def pidConstSend():
            self.log("Sending PID")
            try:
                values = []
                for line in csv.reader(open('pid.csv','r')):
                    for value in line:
                        values.append(float(value))
                for (n,v) in enumerate(values):
                    self.dron.sendMessage("EI%d:%04.3f"%(n,v))
                self.dron.sendMessage("MP")
                self.log("Sending PID values - OK")
            except Exception as e:
                self.log(e)
                self.log("Sending PID - ERROR")

        def reconnect():
            self.log("Reconnect")
            try:
                self.dron.close()
            except Exception as e:
                pass
            try:
                self.dron.reconnect()
            except Exception as e:
                pass

        self.inputs.setKeyMapping(8,pidConstSend)
        self.inputs.setKeyMapping(7,reconnect)


        ##### Put stuff in display
        # Background
        bg = background()
        self.display.addWidget(bg.fill)

        ri = rotationIndactor(self.dron.getRotate,(62,349))
        self.display.addWidget(ri.draw)

        # Artificial Horizon
        af = horizon(self.dron.getPitch,self.dron.getRoll,42,70,230,230,printAngles=True)
        self.display.addWidget(af.draw)

        # Status bar
        status = statusBar( (5,580) )
        self.display.addWidget(status.draw)

        # Motors
        m0 = horizontal(self.dron.getMotor0,(495,70),(246,41))
        m1 = horizontal(self.dron.getMotor1,(495,133),(246,41))
        m2 = horizontal(self.dron.getMotor2,(495,196),(246,41))
        m3 = horizontal(self.dron.getMotor3,(495,259),(246,41))
        self.display.addWidget(m0.draw)
        self.display.addWidget(m1.draw)
        self.display.addWidget(m2.draw)
        self.display.addWidget(m3.draw)
        # Throtle
        throtle = vertical(self.inputs.getThrotle,(305,70),(58,230))
        self.display.addWidget(throtle.draw)
        # Battery
        battery = verticalReversedColor(self.dron.getBattery,(308,354),(112,204))
        self.display.addWidget(battery.draw)

        # textLog
        tLog = textLog((448,326))
        self.display.addWidget(tLog.draw)

        # onlineIndactor
        online = onlineIndactor( self.dron.isOnline, (0,0))
        self.display.addWidget(online.show)

        # Text info
        self.status = status.text
        self.log = tLog.log
        self.inputs.setLogCallback(self.log)
        self.display.setLogCallback(self.log)
        self.dron.setLogCallback(self.log)

        ##### Open devices
        # Open devices
        self.log('Opening display...')
        self.display.open(fullscreen=False)

        self.log('Opening inputs...')
        self.inputs.open()

        self.log('Connecting to drone...')
        self.dron.open(serialDevice="/dev/ttyUSB0")
        # self.dron.open(host=('10.10.100.254',8899))

        ########################################################################
        # Run main loop of controller - perhaps only wait for close
        self.log('All opened!')
        self._running = True
        while self._running:
            # Some debug
            self.status("LPS: %f"%self.dron.getLPS())
            sleep(0.5)

dronController = Controller()
dronController.open()
