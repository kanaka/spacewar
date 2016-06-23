"use strict";

var GamePlay = function(game) {}

GamePlay.prototype.init = function() {
    this.game.time.advancedTiming = true;
    this.game.physics.startSystem(Phaser.Physics.ARCADE);
}

GamePlay.prototype.create = function () {
    var self = this,
        game = this.game,
        arena = this.game.arena

    // Start the in-game soundtrack
    game.music.play_index = parseInt(Math.random()*game.music.play.length)
    game.music.play[game.music.play_index].play()

    // Define groups/layers
    game.groups = {stars:   starGroup(game),
                   powerup: game.add.group(),
                   vapors:  game.add.group(),
                   low:     game.add.group(),
                   high:    game.add.group(),
                   virtual: game.add.group(),
                   pend:    new Phaser.Group(game, null)}

    // Add Sun
    if (vars.sun > 0) {
        var sun = new Sun(game)
        game.groups.low.add(sun)
        if (vars.sun === 3) {
            // Invisible black-hole
            sun.visible = false
        }
    }

    // Add the ships/players
    this.players = []
    var pdata = [[0, vars.player_1, arena.right-50, arena.bottom-50],
                 [1, vars.player_2, arena.left +50, arena.top   +50],
                 [2, vars.player_3, arena.right-50, arena.top   +50],
                 [3, vars.player_4, arena.left +50, arena.bottom-50]]
    for (var d of pdata) {
        if (d[1] === CONST_PLAYER_HUMAN) {
            var ship = new Ship(game, d[0], d[2], d[3])
            this.players.push(new HumanAgent(game, d[0], ship))
            game.groups.low.add(ship)
        }
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
        for (var m of game.music.play) { m.stop() }
        self.state.start('Menu');
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
    game.debug.text("fps: " + (game.time.fps || '--'), 20, 440, "#00ff00")
    game.debug.soundInfo(game.music.play[1], 20, 460)
}
