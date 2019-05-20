import pygame, sys,os, math
import thread
import time

class userInput:
    def __init__(self,pad=True,keyboard=True):
        # Varibles
        self._device = None
        self._gimbalRoll = 0.0
        self._gimbalPitch = 0.0
        self._throtle = 0.0
        self._running = False
        # Callbacks
        self._messageCallback = None
        self._resetCallback = None
        self._exitCallback = None
        self._buttonCallback = None
        # Settings
        self._keyMapping = {
            9:self._doExit
        }
        self._keyToMessageMapping = {
			0 : 'MI', # Idle - Mode
			1 : 'MG', # Gimbal test - Mode
			2 : 'MT', # Motor test - Mode
			3 : 'MF'  # Fly - Mode
		}
        self._axisMapping = {'roll':0,'pitch':3,'rott':2}
        self._axisThrotle = 1
        self._axisThrotleAmp = -0.01
        self._gimbalSpeed = 0.02
        self._axisSpeed = 0.25
        # Data
        self._axis = {'roll':0.0,'pitch':0.0,'rott':0.0,'throtle':0.0}

        self._kb = keyboard
        self._pad = pad
        if pad:
            try:
                pygame.joystick.init()
            except Exception as e:
                self._pad = False
        self._log = False
    def log(self,text):
        if self._log:
            self._log(text)
    def setLogCallback(self,logCallbackFunction):
        self._log = logCallbackFunction

    def setKeyMapping(self,button,callbackFunction):
        self._keyMapping[button] = callbackFunction

    def _doExit(self):
        if self._exitCallback != None:
            self._exitCallback()

    def _limit(self,value,vMin=-1.0,vMax=1.0):
        if value >= vMax: return vMax
        elif value <= vMin: return vMin
        return value

    def _loop(self):
        self._running = True
        try:
            maxTimeWait = 200
            while pygame.display.get_init()==0:
                time.sleep(0.1)
                maxTimeWait -= 1
                if maxTimeWait == 0:
                    raise Exception('Video not inited - timeout!')
            # Main loop
            keyDown = []
            usedKeys = self._keyMapping.keys() + self._keyToMessageMapping.keys()
            self.log('Inputs: Running loop!')
            while self._running:
                for event in pygame.event.get():
                    if (event.type == pygame.KEYDOWN) and self._kb:
                        if event.type == pygame.KEYDOWN:
                            buttonNo = event.key - pygame.K_0
                            if buttonNo in usedKeys:
                                if self._keyMapping.has_key(buttonNo):
                                    self._keyMapping[buttonNo]()
                                elif self._keyToMessageMapping.has_key(buttonNo):
                                    self._messageCallback(self._keyToMessageMapping[buttonNo])
                            if event.key == pygame.K_UP:
                                self._axis['throtle'] = self._limit(self._axis['throtle'] - self._axisThrotleAmp,0.0)
                            if event.key == pygame.K_DOWN:
                                self._axis['throtle'] = self._limit(self._axis['throtle'] + self._axisThrotleAmp,0.0)
                if self._pad:
                    for (axisName,axisNo) in self._axisMapping.iteritems():
                        self._axis[axisName] = self._device.get_axis(axisNo)
                    self._axis['throtle'] = self._limit(self._axis['throtle'] + (self._device.get_axis(self._axisThrotle) * self._axisThrotleAmp),0.0)
                    (gr,gp) = self._device.get_hat(0)
                    self._gimbalRoll  = self._limit(self._gimbalRoll  + gr*self._gimbalSpeed)
                    self._gimbalPitch = self._limit(self._gimbalPitch + gp*self._gimbalSpeed)
                    for buttonNo in usedKeys:
                        if self._device.get_button(buttonNo):
                            if not(buttonNo in keyDown):
                                keyDown.append(buttonNo)
                                if self._keyMapping.has_key(buttonNo):
                                    self._keyMapping[buttonNo]()
                                elif self._keyToMessageMapping.has_key(buttonNo):
                                    self._messageCallback(self._keyToMessageMapping[buttonNo])
                        else:
                            if buttonNo in keyDown:
                                keyDown.remove(buttonNo)

                time.sleep(0.05)
            # /Main loop
            self.log('Inputs: Main loop done')
        except Exception, e:
            print e
        self._running = False

    def close(self):
        self._running = False
        time.sleep(1)

    def open(self,padNo=0):
        if self._running:
            return True
        try:
            if self._pad:
                try:
                    self._device = pygame.joystick.Joystick(padNo)
                    self._device.init()
                except Exception as e:
                    self._pad = False
                    self.log(e)
            thread.start_new_thread(self._loop,())
            return True
        except Exception, e:
            self.log(e)
        return False
    def setMessageCallback(self,callbackFunction):
        self._messageCallback = callbackFunction
    def setResetCallback(self,callbackFunction):
        self._resetCallback = callbackFunction
    def setExitCallback(self,callbackFunction):
        self._exitCallback = callbackFunction
    def setButtonCallback(self,callbackFunction):
        self._buttonCallback = callbackFunction

    def getGimbalRoll(self):
        return self._gimbalRoll
    def getGimbalPitch(self):
        return self._gimbalPitch
    def getRoll(self):
        return self._axis['roll']*self._axisSpeed
    def getRott(self):
        return self._axis['rott']
    def getPitch(self):
        return self._axis['pitch']*self._axisSpeed
    def getThrotle(self):
        return self._axis['throtle']
