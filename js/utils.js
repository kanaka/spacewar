"use strict";

function rgba(red, green, blue, alpha) {
    if (typeof alpha === 'undefined') { alpha = 1.0 }
    return "rgba("+red+","+green+","+blue+","+alpha+")"
}

var distanceBetween = Phaser.Physics.Arcade.prototype.distanceBetween
var angleBetween = Phaser.Physics.Arcade.prototype.angleBetween

function rendererName(game) {
    var lookup = {}
    for (var k of ['CANVAS', 'WEBGL', 'HEADLESS']) {
        lookup[Phaser[k]] = k
    }
    return lookup[game.renderType] || 'unknown'
}
