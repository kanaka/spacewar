"use strict";

//
// HUD object
//
function HUD(game, players) {
    Phaser.Group.call(this, game)
    this.visible = true
    this.max_appear_frames = 20
    this.appear_frames = this.max_appear_frames
    this.max_disappear_frames = 20
    this.disappear_frames = 0
    this.start_x = 800
    this.end_x = 700
    this.x = this.start_x
    this.y = 0
    this.players = players
    this.show_player = 0
    this.stats = []

    // HUD background image
    this.create(0, 0, 'hud')

    // "Spacewar" title
    this.title = game.add.text(50, 20, 'Spacewar',
            { font: "Arial Black",
              fontSize: 16,
              fill: "#96aac8"}, this);
    this.title.anchor.set(0.5, 0.5)
    this.title.setShadow(2, 2, 'rgba(128,128,128,0.7)', 2)

    //
    // Game stats
    //
    var t, gsfont = { font: "Arial Black",
                      fontSize: 12,
                      fill: "#969696"}

    // Time
    t = game.add.text(10, 40, 'Time:', gsfont, this);
    t.setShadow(2, 2, 'rgba(128,128,128,0.7)', 2)

    this.time = game.add.text(90, 40, '0', gsfont, this);
    this.time.setShadow(2, 2, 'rgba(128,128,128,0.7)', 2)
    this.time.anchor.set(1, 0)

    // Deaths
    t = game.add.text(10, 60, 'Deaths:', gsfont, this);
    t.setShadow(2, 2, 'rgba(128,128,128,0.7)', 2)

    this.deaths = game.add.text(90, 60, '0', gsfont, this);
    this.deaths.setShadow(2, 2, 'rgba(128,128,128,0.7)', 2)
    this.deaths.anchor.set(1, 0)

    // Kills
    t = game.add.text(10, 80, 'Kills:', gsfont, this);
    t.setShadow(2, 2, 'rgba(128,128,128,0.7)', 2)

    this.kills = game.add.text(90, 80, '0', gsfont, this);
    this.kills.setShadow(2, 2, 'rgba(128,128,128,0.7)', 2)
    this.kills.anchor.set(1, 0)

    //
    // Per player stats
    //
    var space_each = (600-140)/players.length
    for (var i in players) {
        var ship = players[i].ship,
            stats = new Phaser.Group(game, this)
        this.stats[i] = stats

        stats.visible = false

        // Player icon/ship image
        var p = stats.create(50, 120+(i*space_each), 'ship'+i)
        p.frameName = 'main'
        p.anchor.set(0.5, 0)

        // Player scores
        stats.score = game.add.text(10, 145+(i*space_each), '0',
                { font: "Arial Black",
                  fontSize: 16,
                  //fontWeight: 'bold',
                  fill: "#c8c896"}, stats);

        // Player Health and shield bacground
        var s = stats.create(6, 171+(i*space_each), 'imghealth')
        // Health bar
        var hb = game.add.bitmapData(80, 15)
        hb.ctx.beginPath()
        hb.ctx.rect(0, 0, 80, 15)
        var c = ship.mycolor,
            color = [c[0] + 50, c[1] + 50, c[2] + 50]
        hb.ctx.fillStyle = rgba.apply(null, color)
        hb.ctx.fill()
        stats.health = stats.create(10, 175+(i*space_each), hb)

        // Shield bar
        var sb = game.add.bitmapData(80, 8)
        sb.ctx.beginPath()
        sb.ctx.rect(0, 0, 80, 8)
        sb.ctx.fillStyle = rgba(255, 200, 0)
        sb.ctx.fill()
        stats.shield = stats.create(10, 198+(i*space_each), sb)
    }

    this.ticks = 0
}
HUD.prototype = Object.create(Phaser.Group.prototype)
HUD.prototype.constructor = HUD

HUD.prototype.disappear = function() {
    this.disappear_frames = this.max_disappear_frames
}

HUD.prototype.update = function() {
    if (this.game.pausePlay) { return }

    var total_deaths = 0,
        total_kills = 0
    this.ticks += 1

    if (this.appear_frames > 0) {
        this.appear_frames -= 1
        var ratio = (this.max_appear_frames - this.appear_frames)
                    / this.max_appear_frames,
            shift = (this.end_x - this.start_x) * ratio
        this.x = this.start_x + shift
    } else if (this.disappear_frames > 0) {
        this.disappear_frames -= 1
        var ratio = (this.max_disappear_frames - this.disappear_frames)
                    / this.max_disappear_frames,
            shift = (this.end_x - this.start_x) * ratio
        this.x = this.end_x - shift
    } else if (this.show_player < this.players.length) {
        if (this.ticks > this.max_appear_frames + 30 + this.show_player * 45) {
            this.stats[this.show_player].visible = true
            this.game.sounds.pop.play()
            this.show_player += 1
        }
    }

    // Update per player stats
    for (var i in this.players) {
        var stats = this.stats[i],
            ship = this.players[i].ship,
            healthp = Math.max(0.001, ship.health / ship.max_health),
            shieldp = Math.max(0.001, ship.shield / ship.max_shield)

        total_deaths += this.players[i].deaths
        total_kills += this.players[i].score

        // Update score
        stats.score.setText(this.players[i].score + " / " + vars.win_score)

        // Update health bar
        stats.health.scale.setTo(healthp, 1)

        // Update shield bar
        stats.shield.scale.setTo(shieldp, 1)
    }

    // Update game stats
    this.time.setText(parseInt(this.ticks / vars.frames_per_sec))
    this.deaths.setText(total_deaths)
    this.kills.setText(total_kills)

}

