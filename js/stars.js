"use strict";

//
// Star object
//
var Star = function(game, x, y, vx, vy, bitmap) {
    Mass.call(this, game, bitmap, x, y, vx, vy, 0.0, 0)
    this.bitmap = bitmap
}
Star.prototype = Object.create(Mass.prototype)
Star.prototype.constructor = Star

Star.prototype.update = function() {
    // Skip Mass.update
    if (this.x > this.game.world.width) { this.x = 0 }
    if (this.x < 0) { this.x = this.game.world.width }
    if (this.y > this.game.world.height) { this.y = 0 }
    if (this.y < 0) { this.y = this.game.world.height }
}

var starCache = []

// create/recreate star sprite batch
function starGroup(game) {
    var grp = new Phaser.SpriteBatch(game, null)
    grp.destroy = function() {
        // Save the positions of the stars to keep them consistent
        // when moving between game states
        for (var s of this.children) {
            starCache.push({x: s.x,
                            y: s.y,
                            vx: s.body.velocity.x,
                            vy: s.body.velocity.y,
                            bitmap: s.bitmap})
        }
        Phaser.SpriteBatch.prototype.destroy.call(this) 
    }
    grp.visible = true

    // TODO: dynamically adjust number of stars based on target FPS
    if (starCache.length > 0) {
        // Recreate star sprites maintaining location and velocity
        while (starCache.length > 0) {
            var s = starCache.pop()
            grp.add(new Star(game, s.x, s.y, s.vx, s.vy, s.bitmap))
        }
    }

    updateStars(game, grp)
    return grp
}

function updateStars(game, grp) {
    if (vars.graphics >= 2 && grp.children.length < vars.num_stars) {
        // Add new stars
        for (var i = grp.children.length; i < vars.num_stars; i++) {
            var x = parseInt(Math.random() * game.arena.right),
                y = parseInt(Math.random() * game.arena.bottom),
                layer = parseInt(Math.random() * 4),
                vx = - layer * 10,
                vy = layer * 10,
                bm = game.starBitmap[layer]
            grp.add(new Star(game, x, y, vx, vy, bm))
        }
    }

}
