import pygame, sys,os, math
import thread
import time

class display:
    def __init__(self):
        self._running = False
        self._widgets = []
        self._log = False
    def log(self,text):
        if self._log:
            self._log(text)
    def setLogCallback(self,logCallbackFunction):
        self._log = logCallbackFunction
    def addWidget(self,widget):
        self._widgets.append(widget)
    def close(self):
        self._running = False
        time.sleep(1)
    def _loop(self):
        self._running = True
        clock= pygame.time.Clock()
        self.log('Display: Running loop')
        while self._running:
            for widget in self._widgets:
                try:
                    widget(self._window)
                except Exception as e:
                    self.log(e)
            pygame.display.update()
            clock.tick(25)
        self.log('Display: Main loop done')

    def open(self, fullscreen=False):
        try:
        	pygame.display.init()
        	found = True
        except pygame.error:
        	for driver in  ['fbcon', 'directfb', 'svgalib','x11']:
        		os.putenv('SDL_VIDEODRIVER', driver)
        		try: pygame.display.init()
        		except pygame.error: continue
        		found = True
        		break
        if not found: raise Exception('No suitable video driver found!')
        self._window = None
        if fullscreen:
        	self._window = pygame.display.set_mode((800, 600),pygame.FULLSCREEN)
        else:
        	self._window = pygame.display.set_mode((800, 600))
        pygame.display.set_caption('Copter controler')
        pygame.font.init()
        try:
    		thread.start_new_thread( self._loop, () )
        except Exception as e:
            return False
        return True
