"use strict";

var GamePlay = function(game) {}

GamePlay.prototype.init = function() {
    //this.game.physics.startSystem(Phaser.Physics.ARCADE);
}

GamePlay.prototype.create = function () {
    var self = this,
        game = this.game,
        arena = this.game.arena

    // Start the in-game soundtrack
    game.music.play_index = parseInt(Math.random()*game.music.play.length)
    game.music.play[game.music.play_index].play()

    // Define groups/layers
    game.groups = {stars:   starLayerGroup(game),
                   powerup: game.add.group(),
                   vapors:  game.add.group(),
                   low:     game.add.group(),
                   high:    game.add.group(),
                   virtual: game.add.group(),
                   pend:    new Phaser.Group(game, null)}

    // Add Sun
    if (vars.sun > 0) {
        var sun = new Sun(game)
        sun.start()
        game.groups.low.add(sun)
        if (vars.sun === 3) {
            // Invisible black-hole
            sun.visible = false
        }
    }

    // Add the ships/players
    this.players = []
    var all_dna = game.cache.getJSON('dna_main'),
        pdata = [[0, vars.player_1, arena.right-50, arena.bottom-50],
                 [1, vars.player_2, arena.left +50, arena.top   +50],
                 [2, vars.player_3, arena.right-50, arena.top   +50],
                 [3, vars.player_4, arena.left +50, arena.bottom-50]]
    for (var d of pdata) {
        var ship, agent
        if (d[1] === CONST_PLAYER_OFF) { continue }
        // TODO: only for game_mode === 2
        if (d[1] === CONST_PLAYER_HUMAN) {
            ship = new Ship(game, d[0])
            agent = new HumanAgent(game, d[0], ship)
        } else if (d[1] === CONST_PLAYER_COMPUTER) {
            var ship = new Ship(game, d[0], d[2], d[3]),
                idx = parseInt(Math.random() * all_dna.length),
                dna = all_dna[idx]
            console.log("using DNA index:", idx)
            agent = new DNAAgent(game, d[0], ship, dna, game.groups)
        }
        ship.start(d[2], d[3])
        game.groups.low.add(ship)
        this.players.push(agent)
    }

    // Add HUD image
    game.groups.virtual.add(new HUD(game, this.players))

    // Disable default input behaviors
    game.input.touch.preventDefault = false
    game.input.keyboard.addKeyCapture([
        Phaser.Keyboard.LEFT,
        Phaser.Keyboard.RIGHT,
        Phaser.Keyboard.UP,
        Phaser.Keyboard.DOWN,
        Phaser.Keyboard.TAB,
        Phaser.Keyboard.CONTROL,
        Phaser.Keyboard.SPACE])

    game.input.keyboard.addKey(Phaser.Keyboard.ESC).onDown.add(function() {
        self.gameover()
    })
}

GamePlay.prototype.update = function () {
    var music = this.game.music

    // Switch soundtracks
    if (music.play[music.play_index].currentTime >
        music.play[music.play_index].durationMS - 1000) {
        var new_index = (music.play_index + 1) % music.play.length
        if (!music.play[new_index].isPlaying) {
            console.log("switching soundtrack from", music.play_index, "to", new_index)
            music.play[music.play_index].fadeTo(1000, 0)
            music.play_index = new_index
            music.play[music.play_index].restart('', 0, 0)
            music.play[music.play_index].fadeTo(1000, vars.music)
        }
    }

    // Handler player input
    for (var player of this.players) {
        player.do_action()
    }


    // Perform object behavior and interactions
    runobjects(this.game)
}

GamePlay.prototype.render = function () {
    var game = this.game

    //game.debug.soundInfo(game.music.play[1], 20, 440)
    game.debug.text("fps(" + rendererName(game) + "): " +
                    (game.time.fps || '--'), 20, 560, "#00ff00")
}

GamePlay.prototype.gameover = function () {
    var self = this,
        game = this.game
    for (var player of this.players) {
        player.ship.explode(true)
        player.ship.pending_frames = 3600 // No re-appear
    }
    setTimeout(function () {
        for (var m of game.music.play) { m.stop() }
        saveStarLayers(game.groups.stars)
        self.state.start('Menu');
    }, 1000)
}
