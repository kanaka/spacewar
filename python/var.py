"""
var module
global game state, variables, constants, and settings
"""

import os
from pygame.rect import Rect

version = "0.6"

#various data constants
arena = Rect(0, 0, 700, 600)
ai_train = 0

speedmult = 0

musictime = 1000 * 120 #two minutes
text_length = 80  #frames text is displayed in-game
site_url = 'http://joelandrebecca.martintribe.org/spacewar'
news_url = 'http://joelandrebecca.martintribe.org/spacewar/thenews.html'

#number of insults must match num of complements, be careful
Complements = (
    'Nice',
    'Smooth',
    'Deck',
    'Last Starfighter',
    'Oh yeah',

    'Rocket Scientist',
    'King of the Well',
    'Bring the smack',
    'Own a PDP-1?',
    'Boom!',

    'There is no spoon',
    'Ship parts for sale',
    'Walk in the park',
    'Easy as pie',
    'Candy from a baby',

    'Eat that!',
    'One down...',
    'Yes!',
    'I brake for no one',
)
Insults = (
    'Ouch',
    'Sloppy',
    'What was that?',
    'This is your ship on drugs',
    'Flying by braile',

    'Flying blind',
    'Look ma, no ha...',
    'Get the clue stick',
    'Thrusters on, nobody home',
    'Watch the event horizon',
    
    'Mayday, mayday',
    'Eject!',
    'That\'s no moon!',
    'Not that button!',
    'Holy hand-grenade, Batman!',

    'Bring out your dead!',
    'Orange ... no, Blue!',
    'Luke, pull up!',
    'Run, the sky\'s falling!',
)


#clock info
clock = None
clockticks = 1

#current gamehandler class instance
#this should be set by function creating new handler
handler = None
thread = None  #any background thread
stopthread = 0 #request thread terminate

# frame rate constant
frames_per_sec = 40

# Timing constants, proportional to frames_per_sec
fire_delay_frames = frames_per_sec / 2
compass_dirs = frames_per_sec
fire_life = frames_per_sec * 4

# Game physics constants
reverse_power = -0.08
thrust_power = 0.12
fire_speed = 5.0
explosion_damage = 3
sbobble_power = 50.0
bbobble_charge = frames_per_sec * 20
smoke_speed = 5.0
start_clearance = 30  # distance ships start from other objects

# AI constants
deaths_per_generation = 50
population_size = 10
regen_rate = 10
mutate_rate = 10

################################################################
# These are the defaults for settings in Setup (gamepref.py)
################################################################
music = 2
volume = 2
display = 1
game_mode = 1 # 1 = normal, 2 = tutorial
player_1 = 1  # 0 = off, 1 = human, 2 = computer
player_2 = 1
player_3 = 0
player_4 = 0
win_score = 10
scoring = 0
graphics = 2 
    # 0 = No stars or smoke trails
    # 1 = Smoke trails
    # 2 = Stars
fire_damage = 80
spike_rate = 30
shield_powerup_rate = 20  # Lower is more frequent
bullet_powerup_rate = 40
sun = 1
gravity_const = 20
heal_rate = 3
death_time = 5

################################################################
# Here is the table of values and labels for Setup (gamepref.py)
################################################################
# Values must be integers
Prefs = {
0: ("game_mode", (("Normal", 1), ("1 Player Tutorial", 2))),
1: ("player_1", (("Human", 1), ("Computer", 2))),
2: ("player_2", (("Human", 1), ("Computer", 2), ("Off", 0))),
3: ("player_3", (("Human", 1), ("Computer", 2), ("Off", 0))),
4: ("player_4", (("Human", 1), ("Computer", 2), ("Off", 0))),
5: ("win_score", (("1", 1), ("5", 5), ("7", 7), ("10", 10), ("21", 21))),
6: ("scoring", (("Death Subtract", 0), ("Never Subtract", 1))),
7: ("sun", (("None", 0), ("Tethered", 1), ("Floating", 2), ("Black Hole", 3))),
8: ("fire_damage", (("Low", 20), ("Medium", 50), ("Normal", 80), ("Super", 120))),
9: ("gravity_const", (("Weak", 10), ("Normal", 20), ("Strong", 40))),
10: ("spike_rate", (("Infrequent", 60), ("Normal", 30), ("Frequent", 10))),
11: ("shield_powerup_rate", (("Infrequent", 40), ("Normal", 20), ("Frequent", 12))),
12: ("bullet_powerup_rate", (("Infrequent", 70), ("Normal", 40), ("Frequent", 20))),
13: ("heal_rate", (("Slow", 1), ("Normal", 3), ("Fast", 10))),
14: ("death_time", (("Quick", 3), ("Normal", 5), ("Slow", 10))),
15: ("graphics", (("Minimal", 0), ("Smoke", 1), ("Smoke and Stars", 2))),
16: ("display", (("Window", 0), ("Fullscreen", 1))),
17: ("music", (("Off", 0), ("Low", 1), ("Normal", 2))),
18: ("volume", (("Off", 0), ("Low", 1), ("Normal", 2))),
}
################################################################


# Utility functions
def player_cnt():
    if game_mode == 2:
        return 1
    cnt = 0
    for player in (player_1, player_2, player_3, player_4):
        if player: cnt += 1
    return cnt


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
