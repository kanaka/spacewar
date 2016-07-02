"use strict";

//
// Game constants
//
var VERSION               = 0.6,
    CONST_PLAYER_OFF      = 0,
    CONST_PLAYER_HUMAN    = 1,
    CONST_PLAYER_COMPUTER = 2,
    CONST_HEALTH_COLORS   = [[75, 0, 0],
                             [0, 75, 0],
                             [0, 0, 75],
                             [75, 75, 0]],
    CONST_MESSAGE_COLORS  = [[255, 128, 128],
                             [128, 255, 128],
                             [128, 128, 255],
                             [255, 255, 128]],
    CONST_FPS             = 60,
    CONST_STAR_LAYERS     = 4


// number of insultsmust match num of complements, be careful
var COMPLIMENTS = [
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
    'I brake for no one'
]
var INSULTS = [
    'Ouch',
    'Sloppy',
    'What was that?',
    'This is your ship on drugs',
    'Flying by braile',

    'Flying blind',
    'Look ma, no han...',
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
    'Run, the sky\'s falling!'
]


//
// Game settings
//
var vars = {
    frames_per_sec: CONST_FPS,  // TODO: depends on Phaser goal
    num_stars: 1000,
    fire_life: 4 * CONST_FPS,
    message_frames: 2 * CONST_FPS,

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
    debris_damage: 10,
    smoke_speed: 250.0,
    sbobble_power: 50.0,
    bbobble_charge: 120.0, // frames_per_sec * 20

    //
    // Settings menu configurable items
    //
    player_1:            CONST_PLAYER_HUMAN,
    player_2:            CONST_PLAYER_COMPUTER,
    player_3:            CONST_PLAYER_OFF,
    player_4:            CONST_PLAYER_OFF,

    graphics:            2, // 0 = no stars/smoke, 1 = smoke, 2 = smoke+stars

    win_score:           7,
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
    ["graphics", [["Minimal", 0], ["Smoke", 1], ["Smoke and Stars", 2]]],
//    ["display", [["Window", 0], ["Fullscreen", 1]]],
    ["win_score", [["3", 3], ["5", 5], ["7", 7], ["11", 11], ["21", 21]]],
    ["death_score", [["-2", -2], ["-1", -1], ["0", 0]]],
    ["music", [["Mute", 0], ["Quiet", 0.3], ["Normal", 1]]],
    ["sounds", [["Mute", 0], ["Quiet", 0.3], ["Normal", 1]]],

    ["sun", [["None", 0], ["Tethered", 1], ["Floating", 2], ["Black Hole", 3]]],
    ["fire_damage", [["Low", 20], ["Medium", 50], ["Normal", 80], ["Super", 120]]],
    ["gravity_const", [["Weak", 200], ["Normal", 480], ["Strong", 1500]]],
    ["spike_rate",    [["Infrequent", 1.0 / (CONST_FPS * 90)],
                       ["Moderate",   1.0 / (CONST_FPS * 40)],
                       ["Frequent",   1.0 / (CONST_FPS * 20)]]],
    ["asteroid_rate", [["Infrequent", 1.0 / (CONST_FPS * 90)],
                       ["Moderate",   1.0 / (CONST_FPS * 40)],
                       ["Frequent",   1.0 / (CONST_FPS * 20)]]],
    ["shield_powerup_rate", [["Infrequent", 1.0 / (CONST_FPS * 40)],
                             ["Moderate", 1.0 / (CONST_FPS * 20)],
                             ["Frequent", 1.0 / (CONST_FPS * 12)]]],
    ["bullet_powerup_rate", [["Infrequent", 1.0 / (CONST_FPS * 70)],
                             ["Moderate", 1.0 / (CONST_FPS * 40)],
                             ["Frequent", 1.0 / (CONST_FPS * 20)]]],
    ["heal_rate", [["Slow", 1], ["Normal", 3], ["Fast", 10]]],
    ["death_time", [["Quick", 3], ["Normal", 5], ["Slow", 10]]],
]

var creds = ['Spacewar',
             '    Developer: Joel Martin (@bus_kanaka)',
             '',
             'Sound/Graphics from SolarWolf',
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

vars.applyVars = function(game) {
    // Adjust music volume if needed
    if (!game.music.menu.volume !== vars.music) {
        game.music.menu.volume = vars.music
        for (var m of game.music.play) {
            m.volume = vars.music
        }
    }

    // Adjust sound-effects volume if needed
    if (!game.sounds.startlife.volume !== vars.sound) {
        for (var k in game.sounds) {
            var s = game.sounds[k]
            s.volume = vars.sounds
        }
        // Adjust other sounds
        game.sounds.fire.volume = vars.sounds / 2
    }

    // TODO: Enable/disable stars
}

