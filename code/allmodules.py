#this is simply to ensure init type functions
#will work, because all needed game modules will
#be imported. groove on

#we'll just parse this string out and import everything in it
modules_string = """
gameplay, gamemenu, gamehelp, gamepause, gamepref,
var, gfx, snd, txt, hud, main, input, objs, objtext, stars
"""

def modules_import():
    mods = modules_string.split(',')
    for m in mods:
        m = m.strip()
        __import__(m)

modules_import()

