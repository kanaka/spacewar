"use strict";

var GameCreds = function(game) {}

GameCreds.prototype.init = function () {
}

GameCreds.prototype.create = function () {
    var self = this,
        game = this.game

    game.groups = {stars:   starLayerGroup(game),
                   scroll:  game.add.group(),
                   main:    game.add.group()}

    game.groups.main.create(20, 20, 'menu-creds-on')

    this.startX = game.world.centerX
    this.startY = game.world.height + 40
    this.creds = game.add.text(this.startX, this.startY,
                               creds.join('\n'),
                               {font: "Arial Black",
                                fontSize: 20,
                                fill: rgba(200, 200, 200)},
                               game.groups.scroll)
    this.creds.anchor.set(0.5, 0)
    //this.creds.context.setTransform()

    // Add keyboard interaction
    var k = game.input.keyboard
    function finish() {
        game.sounds.menu_choose.play()
        saveStarLayers(game.groups.stars)
        game.state.start('Menu')
    }
    k.addKey(Phaser.Keyboard.ENTER   ).onDown.add(finish)
    k.addKey(Phaser.Keyboard.ESC     ).onDown.add(finish)
    k.addKey(Phaser.Keyboard.SPACEBAR).onDown.add(finish)
    game.input.onDown.add(finish)
}

GameCreds.prototype.update = function () {
    var game = this.game

    this.creds.y -= 1
    if (this.creds.y + this.creds.height < -40) {
        this.creds.y = this.startY
    }
}
