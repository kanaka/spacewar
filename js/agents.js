"use strict";

var Agent = function(game, playernum, ship) {
    this.game = game
    this.playernum = playernum
    this.ship = ship
    this.ship.player = this
    this.score = 0
    this.deaths = 0

    this.complement = 0
    this.insult = 0
}

var HumanAgent = function(game, playernum, ship) {
    Agent.call(this, game, playernum, ship)
}
HumanAgent.prototype = Object.create(Agent.prototype)
HumanAgent.prototype.constructor = Agent

HumanAgent.PK_LEFT    = [Phaser.Keyboard.LEFT,
                         Phaser.Keyboard.A,
                         Phaser.Keyboard.J,
                         Phaser.Keyboard.NUMPAD_2]
HumanAgent.PK_RIGHT   = [Phaser.Keyboard.RIGHT,
                         Phaser.Keyboard.D,
                         Phaser.Keyboard.L,
                         Phaser.Keyboard.NUMPAD_8]
HumanAgent.PK_REVERSE = [Phaser.Keyboard.DOWN,
                         Phaser.Keyboard.S,
                         Phaser.Keyboard.K,
                         Phaser.Keyboard.NUMPAD_5]
HumanAgent.PK_THRUST  = [Phaser.Keyboard.UP,
                         Phaser.Keyboard.W,
                         Phaser.Keyboard.I,
                         Phaser.Keyboard.NUMPAD_4]
HumanAgent.PK_FIRE    = [Phaser.Keyboard.CONTROL,
                         Phaser.Keyboard.TAB,
                         Phaser.Keyboard.SPACEBAR,
                         Phaser.Keyboard.NUMPAD_0]

HumanAgent.prototype.do_action = function (self, keyset) {
    if (typeof keyset === 'undefined') {
        keyset = this.ship.shipnum
    }

    if (this.ship.dead) {
        this.ship.cmd_turn_off()
        this.ship.cmd_thrust_off()
        return
    }

    var kbd = this.game.input.keyboard
    if (kbd.isDown(HumanAgent.PK_LEFT[keyset])) {
        this.ship.cmd_left()
    } else if (kbd.isDown(HumanAgent.PK_RIGHT[keyset])) {
        this.ship.cmd_right()
    } else {
        this.ship.cmd_turn_off()
    }

    if (kbd.isDown(HumanAgent.PK_REVERSE[keyset])) {
        this.ship.cmd_reverse()
    } else if (kbd.isDown(HumanAgent.PK_THRUST[keyset])) {
        this.ship.cmd_thrust()
    } else {
        this.ship.cmd_thrust_off()
    }

    if (kbd.isDown(HumanAgent.PK_FIRE[keyset])) {
        this.ship.cmd_fire()
    }
}
