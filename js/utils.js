"use strict";

function capitalize(txt) {
        return txt.replace(/(?:^|\s)\S/g, function(a) { return a.toUpperCase() })
}

function label(txt) {
    return capitalize(txt.replace(/_/g, " "))
}

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

function borderRect(bmd, x1, y1, w, h, stroke, lineWidth, pattern, offset) {
    bmd.ctx.beginPath()
    bmd.ctx.lineWidth = lineWidth
    bmd.ctx.strokeStyle = stroke
    if (typeof pattern !== 'undefined') {
        bmd.ctx.setLineDash(pattern)
    }
    if (typeof offset !== 'undefined') {
        bmd.ctx.lineDashOffset = offset
    }
    bmd.ctx.rect(x1+lineWidth/2, y1+lineWidth/2,
               w-lineWidth, h-lineWidth)
    bmd.ctx.stroke()
    bmd.ctx.closePath()
    return bmd
}

