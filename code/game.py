"""game module, place for global game state"""

import os
from pygame.rect import Rect
from cStringIO import StringIO

version = "0.3"

#various data constants
arena = Rect(0, 0, 700, 600)

speedmult = 0

musictime = 1000 * 120 #two minutes

text_length = 80  #frames text is displayed in-game

site_url = 'http://joelandrebecca.martintribe.org/spacewar'
news_url = 'http://joelandrebecca.martintribe.org/spacewar/thenews.html'


#number of insults must match num of complements, be careful
Complements = (
    'Hotshot',
    'Smooth Moves',
)
Insults = (
    'Ouch',
    'Sloppy',
)


player = None
name_maxlength = 10     #longest name
max_players = 5         #most player accounts available

#clock info
clock = None
clockticks = 1


#current gamehandler class instance
#this should be set by function creating new handler
handler = None
thread = None  #any background thread
stopthread = 0 #request thread terminate



#these are the defualt 'setup' controlled by Preferences
music = 2
volume = 2
display = 1
help = 0
thruster = 0
comments = 1
players = 0

player_cnt = 2

def get_resource(filename):
    fullname = os.path.join('data', filename)
    return fullname


def make_dataname(filename):
    if os.name == 'posix':
        home = os.environ['HOME']
        fullhome = os.path.join(home, '.spacewar')
        if not os.path.isdir(fullhome):
            try: os.mkdir(fullhome, 0755)
            except OSError: fullhome = home
        filename = os.path.join(fullhome, filename)
    else:
        filename = get_resource(filename)
    filename = os.path.abspath(filename)
    filename = os.path.normpath(filename)
    return filename

DEBUG = 0
