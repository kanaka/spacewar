"use strict";

var starLayerCache = []

//
// Star object
//
function StarLayer(game, layer, x, y, vx, vy, cnt, bitmap) {
    //var color = [layer*45+65, layer*50+60, layer*35+110],
    var color = [layer*35+115, layer*50+70, layer*45+85],
        bm
    if (typeof bitmap === 'undefined') {
        bm = game.add.bitmapData(800,800)
        for (var i = 0; i < cnt; i++) {
            var px = parseInt(Math.random()*800),
                py = parseInt(Math.random()*800)
            bm.rect(px, py, 1, 1, rgba.apply(null, color))
        }
    } else {
        bm = bitmap
    }

    Phaser.TileSprite.call(this, game, 0, 0, 800, 800, bm)

    this.layer = layer
    this.tilePosition.x = x
    this.tilePosition.y = y
    this.vx = vx
    this.vy = vy
    this.bitmap = bm

    starLayerCache.push(this)
}
StarLayer.prototype = Object.create(Phaser.TileSprite.prototype)
StarLayer.prototype.constructor = StarLayer

StarLayer.prototype.update = function() {
    this.tilePosition.x += this.vx
    this.tilePosition.y += this.vy
}

function saveStarLayers(grp) {
    for (var sl of starLayerCache) {
        grp.remove(sl, false)
    }
}

// create/recreate star sprite batch
function starLayerGroup(game) {
    var grp = game.add.group()

    grp.visible = true

    // Reuse star layers to maintain location and velocity
    if (starLayerCache.length === 0) {
        // Restore stars layers from cache
        for (var layer = 0; layer < CONST_STAR_LAYERS; layer++) {
            var vx = -0.1 + -0.25 * layer, vy = 0.09 + 0.15 * layer
            grp.add(new StarLayer(game, layer,
                                  0, 0, vx, vy,
                                  vars.num_stars / CONST_STAR_LAYERS))
        }
    } else if (vars.graphics >= 2) {
        // Create new stars layers
        for (var sl of starLayerCache) {
            grp.add(sl)
        }
    }
    return grp
}
