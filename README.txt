Spacewar - http://joelandrebecca.martintribe.org/spacewar
    version 0.1

by Joel Martin

Graphics and some code borrowed from:
    SolarWolf - http://pygame.org/shredwheat/solarwolf
        by Pete "ShredWheat" Shinners"

Spacewar is an action/arcade game written entirely in Python.
It is free and open source, released under the LGPL license.

Spacewar is a two player game. Each person controls a ship on
a looping "toroid" plane. Each ship can rotate and has a thruster that
accelerates the ship in the direction it is facing. Each ship also has
a blaster that fires bullets at a limited rate, and each bullet exists
for a limited amount of time.  There is also an object in the center
of the screen that constantly accelerates the ships towards itself
(gravity). Ships are destroyed if they collide with a bullet, the
center object, or another ship. The game is timed and players score
a point when they kill the other player. Accidentally death results in
a score deduction.

Controls:
    Player 1: 
        Rotate  -> Left and Right arrows
        Thrust  -> Up arrow
        Blaster -> Down arrow
    
    Player 2: 
        Rotate  -> 'A' and 'D'
        Thrust  -> 'W'
        Blaster -> 'S'

Spacewar should be relatively cross-platform. I have only tested it on
Linux.

Pygame Powered
