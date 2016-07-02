"use strict";

function Start(game) { }

Start.prototype = {
    preload: function () {
        this.load.image('logo', 'data/logo.png')
        this.load.image('preload', 'data/preload.png')
    },

    create: function () {
        this.input.maxPointers = 1
        this.state.start('Preload')
    }
}

function Preload(game) {
    this.logo = null
    this.preloadBar = null
    this.ready = false

}

Preload.prototype = {
    init: function () {
        this.game.time.advancedTiming = true;
        this.add.sprite(100, 25, 'logo')

        // Set default graphics mode based on device type
        // Unfortunately, this can't go in GameSetup because during
        // the constructor this value isn't initialized yet, but we
        // need it for the preload screen for star rendering.
        //if (this.game.device.desktop) {
        //    vars.graphics = 2
        //} else {
        //    vars.graphics = 0
        //}
    },

    preload: function () {
        // Loading bar/text
        this.preloadBar = this.add.sprite(50, 450, 'preload')
        this.load.setPreloadSprite(this.preloadBar)
        this.loadingText = this.game.add.text(55, 460, 'Loading resources...',
                {font: "Arial Black",
                 fontSize: 12,
                 fill: rgba(250, 230, 180)})

        // Music
        //  Firefox doesn't support mp3 files, so use ogg
        this.load.audio('soundtrack-menu', ['data/music/aster2_sw.ogg'])
        this.load.audio('soundtrack-play1', ['data/music/arg.ogg'])
        this.load.audio('soundtrack-play2', ['data/music/h2.ogg'])

        // Sound effects
        this.load.audio('startlife',    'data/audio/startlife.wav')
        this.load.audio('explode',      'data/audio/explode.wav')
        this.load.audio('fire',         'data/audio/select_choose.wav')
        this.load.audio('pop',          'data/audio/shoot.wav')
        this.load.audio('flop',         'data/audio/flop.wav')
        this.load.audio('klank',        'data/audio/klank2.wav')
        this.load.audio('chimein',      'data/audio/chimein.wav')
        this.load.audio('chimeout',     'data/audio/chimeout.wav')
        this.load.audio('boxhit',       'data/audio/boxhit.wav')
        this.load.audio('gameover',     'data/audio/gameover.wav')
        this.load.audio('menu-move',    'data/audio/select_move.wav')
        this.load.audio('menu-choose',  'data/audio/select_choose.wav')

        // Menu sprties
        this.load.spritesheet('bigboxes',  'data/bigboxes.png', 200, 200)
        this.load.image('ship-big',        'data/ship-big.png')
        this.load.image('menu-bgd',        'data/menu_on_bgd.png')
        this.load.image('menu-start-off',  'data/menu_start_off.png')
        this.load.image('menu-start-on',   'data/menu_start_on.png')
        this.load.image('menu-news-off',   'data/menu_news_off.png')
        this.load.image('menu-news-on',    'data/menu_news_on.png')
        this.load.image('menu-creds-off',  'data/menu_creds_off.png')
        this.load.image('menu-creds-on',   'data/menu_creds_on.png')
        this.load.image('menu-setup-off',  'data/menu_setup_off.png')
        this.load.image('menu-setup-on',   'data/menu_setup_on.png')
        this.load.image('menu-ship',       'data/menu_ship.png')

        // Game object sprites/sheets
        for (var s of ['ship0', 'ship1', 'ship2', 'ship3']) {
            this.load.atlas(s, 'data/sheet-'+s+'.png',
                               'data/sheet-'+s+'.json',
                               Phaser.Loader.TEXTURE_ATLAS_JSON_ARRAY)
        }

        this.load.image(      'hud',       'data/hud.png')
        this.load.image(      'imghealth', 'data/health_back.png')
        this.load.spritesheet('smoke',     'data/smoke.png', 16, 16)
        this.load.spritesheet('fire',      'data/fire.png', 24, 24)
        this.load.spritesheet('superfire', 'data/fire2.png', 24, 24)
        this.load.spritesheet('pop',       'data/popshot.png', 18, 22)
        this.load.spritesheet('explosion', 'data/explosion.png', 48, 48)

        this.load.spritesheet('debris1',    'data/debris1.png', 10, 10)
        this.load.spritesheet('debris2',    'data/debris2.png', 10, 10)
        this.load.spritesheet('debris3',    'data/debris3.png', 10, 10)
        this.load.spritesheet('debris4',    'data/debris4.png', 10, 10)
        this.load.spritesheet('debris-base',   'data/debris-base.png', 28, 28)
        this.load.spritesheet('debris-bubble', 'data/debris-bubble.png', 12, 12)
        this.load.spritesheet('debris-motor',  'data/debris-motor.png', 10, 10)

        this.load.spritesheet('boxes',     'data/boxes.png', 26, 26)
        this.load.spritesheet('spike',     'data/spikeball.png', 24, 24)
        this.load.spritesheet('asteroid',  'data/asteroid.png', 40, 40)
        this.load.spritesheet('bobble',    'data/powerup.png', 25, 25)
        this.load.spritesheet('shield',    'data/bonus-shield.png', 32, 32)
        this.load.spritesheet('bullet',    'data/bonus-bullet.png', 32, 32)

        // Load news/CHANGES.json file
        this.load.json('news', 'CHANGES.json')

        // Load the AI DNA
        //this.load.json('dna_dumb',       'data/ai/dumb.json')
        //this.load.json('dna_generation', 'data/ai/generation.json')
        this.load.json('dna_main', 'data/ai/main.json')

    },

    create: function () {
        var game = this.game
        var arena = game.arena = vars.arena

        // Set background color for all states
        game.stage.backgroundColor = '#000000'

        // Add music
        game.music = {
            menu: this.add.audio('soundtrack-menu'),
            play: [this.add.audio('soundtrack-play1'),
                   this.add.audio('soundtrack-play2')],
        }
        game.music.menu.loop = true

        // Add audio effects
        game.sounds = {
            startlife:    this.add.audio('startlife'),
            explode:      this.add.audio('explode'),
            fire:         this.add.audio('fire'),
            pop:          this.add.audio('pop'),
            flop:         this.add.audio('flop'),
            klank:        this.add.audio('klank'),
            chimein:      this.add.audio('chimein'),
            chimeout:     this.add.audio('chimeout'),
            boxhit:       this.add.audio('boxhit'),
            gameover:     this.add.audio('gameover'),
            menu_move:    this.add.audio('menu-move'),
            menu_choose:  this.add.audio('menu-choose'),
        }

        // Allow multiple instances of same sound to be playing
        // simultaneously
        //game.sounds.explode.allowMultiple = true
        //game.sounds.fire.allowMultiple = true
        //game.sounds.pop.allowMultiple = true
        //game.sounds.flop.allowMultiple = true
        //game.sounds.chimein.allowMultiple = true
        //game.sounds.chimeout.allowMultiple = true
        //game.sounds.boxhit.allowMultiple = true

        // Create parallax star layers
//        game.groups = {stars:      starLayerGroup(game)}

        // Change state to match vars settings
        vars.applyVars(game)
    },

    update: function () {
        //  Make sure music decoded before continuing
        if (!this.ready) {
            if (this.cache.isSoundDecoded('soundtrack-play1') &&
                this.cache.isSoundDecoded('soundtrack-play2') &&
                this.cache.isSoundDecoded('soundtrack-menu')) {
                this.ready = true
                // Play the initial start sound
                this.game.sounds.explode.play('', 0,
                        this.game.sounds.explode.volume / 4)
                // Switch to the menu
                this.state.start('Menu')
            }
        }
    }
}


//var thegame = new Phaser.Game(800, 600, Phaser.CANVAS, 'spacewar')
var thegame = new Phaser.Game(800, 600, Phaser.AUTO, 'spacewar')

// Setup game modes
thegame.state.add('Start',   Start)
thegame.state.add('Preload', Preload)
thegame.state.add('Menu',    GameMenu)
thegame.state.add('Play',    GamePlay)
thegame.state.add('Setup',   GameSetup)
thegame.state.add('News',    GameNews)
thegame.state.add('Creds',   GameCreds)
thegame.state.start('Start')

// Scaling to Window
// Based on:
//   http://www.html5rocks.com/en/tutorials/casestudies/gopherwoord-studios-resizing-html5-games/
function scaleGame() {
    var canvas = thegame.canvas,
        gameAspect = 800 / 600,
        scale = 1.0

    if (window.innerWidth / window.innerHeight > gameAspect) {
        scale = window.innerHeight * gameAspect / canvas.width
    } else {
        scale = window.innerWidth / gameAspect / canvas.height
    }

    canvas.style.webkitTransform = "scale("+scale+","+scale+")";
    canvas.style.webkitTransformOrigin = "0 0";
    canvas.style.transform       = "scale("+scale+","+scale+")";
    canvas.style.transformOrigin = "0 0";

    console.log('scaling to:', scale)
    thegame.scaleVal = scale
}

window.onload = function() {
    window.addEventListener('resize', scaleGame, false)
    window.addEventListener('orientationchange', scaleGame, false)
    scaleGame()
}
