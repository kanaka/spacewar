"use strict";

//
// Message object
//
function Message(game, msg, color, ticks_to_live) {
    Phaser.Group.call(this, game)
    this.game = game
    this.ticks = 0
    color = color || [128, 255, 255]

    if (typeof ticks_to_live === 'undefined') {
        ticks_to_live = vars.message_frames
    }
    this.ticks_to_live = ticks_to_live

    // Create the message sprite
    var y = 40,  // First position
        msgs = game.groups.message.children
    if (msgs.length > 0) {
        y = msgs[msgs.length-1].text.y + 30
    }
    this.text = game.add.text(game.arena.right / 2, y, msg,
                              { font: "Arial Black",
                                fontSize: 16,
                                fill: rgba.apply(null, color)},
                              this)
    this.text.alpha = 0.0  // adjusted by update()
    this.text.anchor.set(0.5, 0.5)
    this.text.setShadow(2, 2, 'rgba(128,128,128,0.7)', 2)

    game.groups.message.add(this)
}
Message.prototype = Object.create(Phaser.Group.prototype)
Message.prototype.constructor = Message

Message.prototype.update = function() {
    if (this.game.pausePlay) { return }

    this.ticks += 1

    var remaining = this.ticks_to_live - this.ticks
    if (this.ticks < 30) {
        // appear
        this.text.alpha = this.ticks / 45
    } else if (remaining < 30) {
        // disappear
        this.text.alpha = remaining / 45
    }

    if (this.ticks >= this.ticks_to_live) {
        this.game.groups.message.remove(this, true)
    }
}

