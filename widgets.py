import pygame, sys,os, math

class background:
    def __init__(self):
        self._bg = pygame.image.load('bg.png')
    def fill(self, window):
        window.blit(self._bg,(0,0))

class onlineIndactor:
    def __init__(self,uInput,position):
        self._pos = position
        self._offline = pygame.image.load('offline.png')
        self._input = uInput
    def show(self, window):
        if not self._input():
            window.blit(self._offline,self._pos)

class rotationIndactor:
    def __init__(self,uInput,position):
        self._image = pygame.image.load('rott.png')
        self._pos = (position[0] + 0.5*self._image.get_width(),position[1] + 0.5*self._image.get_height())
        self._input = uInput
        self._rott = 0.0
    def draw(self, window):
        self._rott += self._input() / 25
    	image = pygame.transform.rotozoom(self._image, self._rott * -1.0, 1)
    	window.blit(image, (self._pos[0]-(image.get_width()/2), self._pos[1]-(image.get_height()/2)))

class statusBar:
    def __init__(self,position,color=(192,192,0),font='arial',size=12):
        pygame.font.init()
        self._font = pygame.font.SysFont(font,size)
        self._pos = position
        self._col = color
        self._text = ''
    def text(self,newText):
        self._text = newText
    def draw(self, window):
        txt = self._font.render(self._text, 1, self._col)
        window.blit(txt, self._pos)


class textLog:
    def __init__(self,position):
        pygame.font.init()
        self._linesNo = 14
        self._font = pygame.font.SysFont('arial',15)
        self._pos = [(position[0],position[1]+i*17 ) for i in range(self._linesNo)]
        self._lines = ['']*self._linesNo
    def log(self,newText):
        lines = str(newText).splitlines()
        lines.reverse()
        for newText in lines:
            self._lines.pop()
            self._lines.insert(0,newText)
            sys.stderr.write(newText+'\n')

    def draw(self, window):
        for lineNo in xrange(self._linesNo):
            window.blit(self._font.render(self._lines[lineNo], 1, (0,0,0)), self._pos[lineNo])


class horizontal:
    def __init__(self,uInput,position,size):
        self._input = uInput
        self._max = size[0]
        self._v = [position[0],position[1],size[0],size[1]]
    def draw(self, window):
    	value = self._input()
        if value>0.5:
    		r = 255
    		g = int(255*(1.0-value)/0.5)
    	else:
    		g = 255
    		r = int(512*value)
    	if r > 255: r = 255
        elif r < 0: r= 0
    	if g > 255: g = 255
        elif g < 0: g= 0
        self._v[2] = self._max * value
    	pygame.draw.rect(window,(r,g,0),self._v,0)


class vertical:
    def __init__(self,uInput,position,size):
        self._input = uInput
        self._y = (position[1]+size[1], size[1])
        self._v = [position[0],position[1],size[0],size[1]]
    def draw(self, window):
        value = self._input()
        if value>0.5:
            r = 255
            g = int(255*(1.0-value)/0.5)
        else:
            g = 255
            r = int(512*value)
        if r > 255: r = 255
        elif r < 0: r= 0
        if g > 255: g = 255
        elif g < 0: g= 0
        self._v[3] = self._y[1] * value
        self._v[1] = self._y[0] - self._v[3]
        pygame.draw.rect(window,(r,g,0),self._v,0)


class verticalReversedColor:
    def __init__(self,uInput,position,size):
        self._input = uInput
        self._y = (position[1]+size[1], size[1])
        self._v = [position[0],position[1],size[0],size[1]]
    def draw(self, window):
        value = self._input()
        if value>0.5:
            g = 255
            r = int(255*(1.0-value)/0.5)
        else:
            r = 255
            g = int(512*value)
        if r > 255: r = 255
        elif r < 0: r= 0
        if g > 255: g = 255
        elif g < 0: g= 0
        self._v[3] = self._y[1] * value
        self._v[1] = self._y[0] - self._v[3]
        pygame.draw.rect(window,(r,g,0),self._v,0)

class horizon:
    def __init__(self,pitchInput,rollInput,pos_x,pos_y,size_x=200,size_y=200,pixelPerRad=314,printAngles=False):
        self._pitchInput = pitchInput
        self._rollInput = rollInput
        self._pos_x = pos_x
        self._pos_y = pos_y
        self._size_x = size_x
        self._size_y = size_y
        self._font = False
        if printAngles:
            pygame.font.init()
            self._font = pygame.font.SysFont('arial',12)
            self._font_color = (192,192,32)
        self._pixelPerRad = pixelPerRad
        self._dronImgData = pygame.image.load('ah_dron.png')
        s = self._dronImgData.get_size()

        self._dronImgPos = (pos_x+(size_x/2)-(s[0]/2),9+pos_y+(size_y/2)-(s[1]/2))
        self._x_limit = self._size_x/2
        self._y_limit = self._size_y/2
        self._sky_color = (64,128,255)
        self._soil_color = (0,179,0)

    def draw(self, window):
        a=self._rollInput()
        b=self._pitchInput()

        if self._font:
            textUnder = self._font.render("%0.3f"%a,1,(self._font_color))
            textSide = self._font.render("%0.3f"%b,1,(self._font_color))
            textSide = pygame.transform.rotozoom(textSide,90,1)
            window.blit(textUnder,(self._pos_x + (self._size_x/2)-(textUnder.get_width()/2), 5 + self._pos_y+self._size_y))
            window.blit(textSide,(self._pos_x - 5 - textSide.get_width(), self._pos_y+(self._size_y/2)-(textSide.get_height()/2)))

        c_a = math.tan(a*math.pi)
        c_b = b*self._pixelPerRad
        c_o = self._pos_y + self._y_limit

        def getHorizonOffset(x):
            y0 = -(c_a*x + c_b) + c_o
            if y0 < self._pos_y:
                y0 = self._pos_y
            elif y0 > self._pos_y+self._size_y:
                y0 = self._pos_y+self._size_y
            return y0

        pygame.draw.rect(window, self._sky_color , [self._pos_x,self._pos_y, self._size_x, self._size_y] )
        pygame.draw.polygon(window, self._soil_color , (
            (self._pos_x,self._pos_y + self._size_y),
            (self._pos_x+self._size_x,self._pos_y + self._size_y),
            (self._pos_x+self._size_x,getHorizonOffset(self._x_limit)),
            (self._pos_x,getHorizonOffset(-self._x_limit)),
        ))
        window.blit(self._dronImgData,self._dronImgPos)
