import socket
import serial
import thread
import time
import re

class dronIo:
    def getRotate(self):
        return self._data['rotate']
    def getPitch(self):
        return self._data['pitch']
    def getRoll(self):
        return self._data['roll']
    def getLPS(self):
        return self._data['lps']
    def getMotor(self,no=False):
        if no:
            return self._data['motor'][no]
        return self._data['motor']
    def getMotor0(self):
        return self._data['motor'][0]/180.0
    def getMotor1(self):
        return self._data['motor'][1]/180.0
    def getMotor2(self):
        return self._data['motor'][2]/180.0
    def getMotor3(self):
        return self._data['motor'][3]/180.0
    def getBattery(self):
        return self._data['battery']
    def getHeight(self):
        return self._data['height']
    def getOther(self):
        return self._data['other']
    def __init__(self):
        # Inputs
        self._throtleInput = None
        self._pitchInput = None
        self._rottInput = None
        self._rollInput = None
        self._gimbalPitchInput = None
        self._gimbalRollInput = None
        # Vars
        self._con = None
        self.write = None
        self.read = None
        self._writeLoop = False
        self._readLoop = False
        self._dataQueue = []
        # From drone
        self._data = {
            'pitch': 0.0,
            'roll': 0.0,
            'lps': 0.0,
            'motor': [0.0,0.0,0.0,0.0],
            'rotate': 0.0,
            'battery': 0.0,
            'height': 0.0,
            'other': 0.0
        }
        self._lastMessageTime = 0.0
        self._log = False
    def log(self,text):
        if self._log:
            self._log(text)
    def setLogCallback(self,logCallbackFunction):
        self._log = logCallbackFunction

    def isOnline(self):
        return (time.time() - self._lastMessageTime) < 0.35

    def _openSerial(self,serialDevice, baudrate=57600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=None):
        tryTime = 20
        while tryTime > 0:
            tryTime -= 1
            try:
                ser = serial.Serial(port=serialDevice,baudrate=baudrate,parity=parity,stopbits=stopbits,bytesize=bytesize,timeout=timeout)
                if ser:
                    break
            except Exception as e:
                if tryTime == 0:
                    raise e
            ser=False
            time.sleep(0.5)
        return ser
    def _openSocket(self,host):
        tryTime = 20
        while tryTime > 0:
            tryTime -= 1
            try:
                soc = socket.socket()
                soc.connect( host )
                if soc:
                    break
            except Exception as e:
                if tryTime == 0:
                    raise e
            soc = False
            time.sleep(0.5)
        return soc
    def close(self):
        try:
            self._writeLoop = False
        except Exception as e:
            self.log(e)
        try:
            self._readLoop = False
        except Exception as e:
            self.log(e)
        try:
            self._con.close()
        except Exception as e:
            self.log(e)
        time.sleep(1)

    def reconnect(self):
        return self.open(
            serialDevice=self._baseSerialDevice,
            host=self._baseHost,
            response_timeout=self._baseResponse_timeout
        )

    def open(self,serialDevice=None,host=None,response_timeout=5):

        self._baseSerialDevice=serialDevice
        self._baseHost=host
        self._baseResponse_timeout=response_timeout
        try:
            if serialDevice!=None:
                connection = self._openSerial(serialDevice)
            if host!=None:
                connection = self._openSocket(host)
        except Exception as e:
            self.log(e)
            return False
        if dir(connection).count('write') == 1:
            self.write = connection.write
        elif dir(connection).count('send') == 1:
            self.write = connection.send
        if dir(connection).count('read') == 1:
            self.read = connection.read
        elif dir(connection).count('recv') == 1:
            self.read = connection.recv
        self._con = connection
        try:
    		thread.start_new_thread( self._droneReaderLoop, () )
    		thread.start_new_thread( self._droneWriterLoop, () )
        except Exception as e:
            self.log(e)
            return False
        return True
    def reset(self):
        if dir(self._con).count('setDTR') == 1:
            try:
                self._con.setDTR(False)
                self._con.setDTR(True)
                return True
            except Exception as e:
                pass
        return False

    def setThrotleInput(self,uInput):
        self._throtleInput = uInput
    def setPitchInput(self,uInput):
        self._pitchInput = uInput
    def setRottInput(self,uInput):
        self._rottInput = uInput
    def setRollInput(self,uInput):
        self._rollInput = uInput
    def setGimbalPitchInput(self,uInput):
        self._gimbalPitchInput = uInput
    def setGimbalRollInput(self,uInput):
        self._gimbalRollInput = uInput
    def sendMessage(self,msg):
        self._dataQueue.append(msg)
    def _droneReaderLoop(self):
        self._readLoop = True
        buff = ''
        pPattern = r"\<"+','.join(['([-+]?\d*\.\d+|\d+)']*14)+"\>"
        try:
            self.log('DronIO: Running reader loop')
            while self._readLoop:
                buff += self.read(1)
                data = re.findall(pPattern, buff)
                if len(data) > 0:
                    self._lastMessageTime = time.time()
                    reads = data[-1]
                    self._data['pitch'] = float(reads[0])
                    self._data['roll'] = float(reads[1])
                    self._data['lps'] = float(reads[2])
                    # motors
                    self._data['motor'][0] = float(reads[3])
                    self._data['motor'][1] = float(reads[4])
                    self._data['motor'][2] = float(reads[5])
                    self._data['motor'][3] = float(reads[6])
                    # rotacja
                    self._data['rotate'] = float(reads[7])
                    # bateria
                    self._data['battery'] = float(reads[8])
                    # wysokosc
                    self._data['height'] = float(reads[9])
                    self._data['other'] = ','.join(reads[10:14])
                    buff = buff[buff.find('>',buff.find('<',))+1:]
        except Exception as e:
            self.log(e)
        self.log('DronIO: Reader loop done')


    def _droneWriterLoop(self,interval=0.1):
        self._writeLoop = True
        try:
            self.log('DronIO: Running writer loop')
            while self._writeLoop:
                self.write("<P%0.4f:%0.4f:%0.4f:%0.4f:%0.4f:%0.4f>"%(
        			self._pitchInput(),
        			self._rollInput(),
        			self._rottInput(),
        			self._throtleInput(),
        			self._gimbalRollInput(),
        			self._gimbalPitchInput()
        		))
                while len(self._dataQueue) > 0:
                    cmd = self._dataQueue.pop(0)
                    self.log("Sending:%s"%cmd)
                    self.write("<%s>"%cmd)
                    time.sleep(0.05)
                time.sleep(interval)
        except Exception as e:
            self.log(e)
        self.log('DronIO: Writer loop done')
