"use strict";

//
// Game constants
//
var VERSION               = 0.6,
    CONST_PLAYER_OFF      = 0,
    CONST_PLAYER_HUMAN    = 1,
    CONST_PLAYER_COMPUTER = 2,
    CONST_HEALTH_COLORS = [[75, 0, 0], [0, 75, 0], [0, 0, 75], [75, 75, 0]],
    CONST_FPS = 60

//
// Game settings
//
var vars = {
    frames_per_sec: CONST_FPS,  // TODO: depends on Phaser goal
    num_stars: 500,
    fire_life: 4 * CONST_FPS,

    start_clearance: 30, // distance ships start from other objects

    arena: {left:     0,
            top:      0,
            right:  700,
            bottom: 600},


    fire_delay_frames: 30,
    //rotation_step: 0.10,
    rotation_step: Math.PI * 2 / CONST_FPS,

    thrust_power: 4.00,
    reverse_power: -2.70,
    fire_speed: 200.0,
    explosion_damage: 3,
    smoke_speed: 250.0,
    sbobble_power: 50.0,
    bbobble_charge: 120.0, // frames_per_sec * 20

    graphics: 2, // 0 = no stars/smoke, 1 = smoke, 2 = smoke+stars

    //
    // Settings menu configurable items
    //
    player_1:            CONST_PLAYER_HUMAN,
    player_2:            CONST_PLAYER_HUMAN,
    player_3:            CONST_PLAYER_OFF,
    player_4:            CONST_PLAYER_OFF,

    win_score:           10,
    death_score:         -1,
    music:               1,
    sounds:              1,

    sun:                 1,
    fire_damage:         80,
    gravity_const:       480,
    spike_rate:          1.0 / (CONST_FPS * 40),  // once every 30 seconds avg
    asteroid_rate:       1.0 / (CONST_FPS * 90),  // once every 90 seconds avg
    shield_powerup_rate: 1.0 / (CONST_FPS * 20),  // once every 20 seconds avg
    bullet_powerup_rate: 1.0 / (CONST_FPS * 40),  // once every 40 seconds avg
    heal_rate:           3,
    death_time:          5,

}

var prefs = [
    ["player_1", [["Human", CONST_PLAYER_HUMAN],
                  ["Computer", CONST_PLAYER_COMPUTER]]],
    ["player_2", [["Human", CONST_PLAYER_HUMAN],
                  ["Computer", CONST_PLAYER_COMPUTER],
                  ["Off", CONST_PLAYER_OFF]]],
    ["player_3", [["Human", CONST_PLAYER_HUMAN],
                  ["Computer", CONST_PLAYER_COMPUTER],
                  ["Off", CONST_PLAYER_OFF]]],
    ["player_4", [["Human", CONST_PLAYER_HUMAN],
                  ["Computer", CONST_PLAYER_COMPUTER],
                  ["Off", CONST_PLAYER_OFF]]],

//    ["game_mode", [["Normal", 1], ["1 Player Tutorial", 2]]],
//    ["graphics", [["Minimal", 0], ["Smoke", 1], ["Smoke and Stars", 2]]],
//    ["display", [["Window", 0], ["Fullscreen", 1]]],
//    ["win_score", [["3", 3], ["7", 7], ["11", 11], ["21", 21]]],
    ["death_score", [["-2", -2], ["-1", -1], ["0", 0]]],
    ["music", [["Mute", 0], ["Quiet", 0.3], ["Normal", 1]]],
    ["sounds", [["Mute", 0], ["Quiet", 0.3], ["Normal", 1]]],

    ["sun", [["None", 0], ["Tethered", 1], ["Floating", 2], ["Black Hole", 3]]],
    ["fire_damage", [["Low", 20], ["Medium", 50], ["Normal", 80], ["Super", 120]]],
    ["gravity_const", [["Weak", 200], ["Normal", 480], ["Strong", 1500]]],
    ["spike_rate",    [["Infrequent", 1.0 / (CONST_FPS * 90)],
                       ["Normal",     1.0 / (CONST_FPS * 40)],
                       ["Frequent",   1.0 / (CONST_FPS * 20)]]],
    ["asteroid_rate", [["Infrequent", 1.0 / (CONST_FPS * 90)],
                       ["Normal",     1.0 / (CONST_FPS * 40)],
                       ["Frequent",   1.0 / (CONST_FPS * 20)]]],
    ["shield_powerup_rate", [["Infrequent", 40], ["Normal", 20], ["Frequent", 12]]],
    ["bullet_powerup_rate", [["Infrequent", 70], ["Normal", 40], ["Frequent", 20]]],
    ["heal_rate", [["Slow", 1], ["Normal", 3], ["Fast", 10]]],
    ["death_time", [["Quick", 3], ["Normal", 5], ["Slow", 10]]],
]

var creds = ['Spacewar',
             '    Developer: Joel Martin (@bus_kanaka)',
             '',
             'Sound/Graphics from Solar Wolf',
             '    Developer: Pete "ShredWheat" Shinners',
             '    Graphics: Eero Tamminen',
             '    Music: "theGREENzebra"',
             '    Programming Help: Aaron "APS" Schlaegel',
             '    Programming Help: Michael "MU" Urman']


vars.player_cnt = function() {
    var v = vars, cnt = 0
    for (var p of [v.player_1, v.player_2, v.player_3, v.player_4]) {
        if (p > 0) { cnt += 1}
    }
    return cnt
}
