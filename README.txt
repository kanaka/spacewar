Spacewar - http://joelandrebecca.martintribe.org/spacewar

Largely based on:
    SolarWolf - http://pygame.org/shredwheat/solarwolf
    by Pete "ShredWheat" Shinners" - pete@shinners.org

Spacewar is an action/arcade game written entirely in Python.
It is free and open source, released under the LGPL license.

Spacewar is a two player game. Each person controls a ship on a looping
"toroid" plane. Each ship can rotate and has a thruster that accelerates the
ship forward or backward. Each ship also has a blaster that fires bullets at a
limited rate, and each bullet exists for a limited amount of time.  There is
also a sun in the center of the screen. Each objects exerts gravity on all
other objects (gravity). The sun is much more massive than other objects.
Ships are destroyed if they collide with a bullet, the sun, or another ship.
The game is timed and players score a point when they kill another player. If
a player dies "accidentally", they lose a point.

The controls for each player are as follows:

Player 1:
    Left:     Left Arrow 
    Right:    Right Arrow 
    Thrust:   Up Arrow
    R-Thrust: Down Arrow
    Fire:     Right-Ctrl

Player 2:
    Left:     a
    Right:    d
    Thrust:   w
    R-Thrust: s
    Fire:     Tab

Player 3:
    Left:     j
    Right:    l
    Thrust:   i
    R-Thrust: k
    Fire:     Space

Player 4:
    Left:     Numpad 2
    Right:    Numpad 8
    Thrust:   Numpad 4
    R-Thrust: Numpad 5
    Fire:     Numpad 0

Someday the keys will be configurable.

Spacewar runs on nearly every platform. Windows, Mac OSX, Linux,
BeOS, and a large variety of Unix platforms.

Pygame Powered
