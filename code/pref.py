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


################################################################
# These are the defualts for settings in Setup (gamepref.py)
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


# Currently unused
help = 0
comments = 1

# Utility functions
def player_cnt():
    if game_mode == 2:
        return 1
    cnt = 0
    for player in (player_1, player_2, player_3, player_4):
        if player: cnt += 1
    return cnt
