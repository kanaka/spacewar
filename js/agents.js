"use strict";

function Agent(game, playernum, ship) {
    this.game = game
    this.playernum = playernum
    this.ship = ship
    this.ship.player = this
    this.score = 0
    this.deaths = 0

    this.compliment = false
    this.insult = false
}

function HumanAgent(game, playernum, ship) {
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

HumanAgent.prototype.do_action = function (keyset) {
    if (typeof keyset === 'undefined') {
        keyset = this.ship.shipnum
    }

    if (this.ship.dead || this.ship.pending_frames || this.ship.appear_frames) {
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

function DNAAgent(game, playernum, ship, dna, groups) {
    Agent.call(this, game, playernum, ship)
    this.dna = dna
    this.groups = groups

    this.start()
}
DNAAgent.prototype = Object.create(Agent.prototype)
DNAAgent.prototype.constructor = Agent

DNAAgent.prototype.start = function () {
    this.cur_gene = null
    this.cur_action = 0
}

DNAAgent.prototype.choose_gene = function () {
    var objs = this.groups.low.children.concat(this.groups.high.children)
    for (var gene of this.dna) {
        for (var obj of objs) {
            if (obj !== this.ship && test_gene(gene, this.ship, obj)) {
                return gene
            }
        }
    }
    //console.log("could not find a matching gene")
    return null_gene
}

DNAAgent.prototype.do_action = function () {
    if (this.ship.dead || this.ship.pending_frames || this.ship.appear_frames) {
        this.ship.cmd_turn_off()
        this.ship.cmd_thrust_off()
        return
    }

    if (this.cur_gene === null) {
        this.cur_gene = this.choose_gene()
        this.cur_action = 0
    }
    var gene = this.cur_gene
    //console.log("gene:", JSON.stringify(gene))
    if (gene.actions[this.cur_action] === "left") {
        this.ship.cmd_left()
    } else if (gene.actions[this.cur_action] === "right") {
        this.ship.cmd_right()
    } else {
        this.ship.cmd_turn_off()
    }

    if (gene.actions[this.cur_action] === "thrust") {
        this.ship.cmd_thrust()
    } else if (gene.actions[this.cur_action] === "rthrust") {
        this.ship.cmd_reverse()
    } else {
        this.ship.cmd_thrust_off()
    }

    if (gene.actions[this.cur_action] === "fire") {
        this.ship.cmd_fire()
    }
    var actions = gene.actions.length
    this.cur_action = (this.cur_action + 1) % actions
    if (this.cur_action === 0) {
        this.cur_gene = null
    }
}
