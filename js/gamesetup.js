"use strict";

function capitalize(txt) {
        return txt.replace(/(?:^|\s)\S/g, function(a) { return a.toUpperCase() })
}

function label(txt) {
    return capitalize(txt.replace(/_/g, " "))
}

var GameSetup = function(game) {
    this.user_vars = {}

    var raw = localStorage.getItem("vars")
    console.log("GameSetup user vars:", raw)
    if (raw) {
        this.user_vars = JSON.parse(raw)
        for (var k in this.user_vars) {
            vars[k] = this.user_vars[k]
        }
    }
}

GameSetup.prototype.init = function () {
    this.linesize = 20
    this.ox = 0
    this.oy = 0

    this.prefs = []
    this.options = []
    var offsetx = 300,
        offsety = 160
    for (var p of prefs) {
        var x = offsetx,
            y = offsety
        this.prefs.push({name:    label(p[0]),
                         x:       120,
                         y:       offsety,
                         color:   [160, 200, 250]})

        var optRow = []
        this.options.push(optRow)
        for (var o of p[1]) {
            optRow.push({key:       p[0],
                         name:      o[0],
                         value:     o[1],
                         x:         x,
                         y:         y,
                         color:     [140, 150, 160],
                         color_on:  [220, 230, 240]})
            x += 100
        }
        offsety += this.linesize
    }
    this.options.push([{key:       null,
                        name:      "Return to Menu",
                        value:     null,
                        x:         offsetx,
                        y:         offsety + 30,
                        color:     [140, 150, 160],
                        color_on:  [220, 230, 240]}])
}

GameSetup.prototype.create = function () {
    var self = this,
        game = this.game

    game.groups = {stars:   starLayerGroup(game),
                   main:    game.add.group()}

    // Menu header
    game.groups.main.create(20,20, 'menu-setup-on')

    // Render the preferences/options
    for (var p of this.prefs.concat.apply(this.prefs, this.options)) {
        if (p.name) {
            var color = p.color
            if ('value' in p && p.key &&
                (p.value.toFixed(8) === vars[p.key].toFixed(8))) {
                color = p.color_on
            }
            p.text = game.add.text(p.x, p.y, p.name,
                    {font: "Arial Black",
                     fontSize: 13,
                     fill: rgba.apply(null, color)},
                    game.groups.main)
            p.text.setShadow(2, 2, 'rbga(128,128,128,0.7)', 2)
        }
    }

    // Add the selector icon
    this.ship = game.groups.main.create(0, 0, 'menu-ship')
    this.ship.anchor.set(1, 0)
    this.ship.scale.set(0.7, 0.7)

    // Add keyboard interaction
    var k = game.input.keyboard
    k.addKey(Phaser.Keyboard.ESC).onDown.add(function () {
        saveStarLayers(game.groups.stars)
        game.state.start('Menu');
    }, this)

    //
    // Pref/option navigation
    //
    function move(dx, dy) {
        var opts = self.options
        self.oy = (self.oy + opts.length + dy) % opts.length
        var orow = self.options[self.oy]
        self.ox = Math.min(self.ox, orow.length-1)
        self.ox = (self.ox + orow.length + dx) % orow.length
        game.sounds.menu_move.play()
    }
    k.addKey(Phaser.Keyboard.UP   ).onDown.add(function () { move( 0, -1) })
    k.addKey(Phaser.Keyboard.DOWN ).onDown.add(function () { move( 0, +1) })
    k.addKey(Phaser.Keyboard.LEFT ).onDown.add(function () { move(-1,  0) })
    k.addKey(Phaser.Keyboard.RIGHT).onDown.add(function () { move(+1,  0) })

    //
    // Pref/option selection
    //
    function select() {
        var opt = self.options[self.oy][self.ox]
        game.sounds.menu_choose.play()
        if (opt.value === null) { 
            saveStarLayers(game.groups.stars)
            game.state.start('Menu');
            return
        }
        for (var o of self.options[self.oy]) {
            if (o === opt) {
                o.text.style.fill = rgba.apply(null, o.color_on)
            } else {
                o.text.style.fill = rgba.apply(null, o.color)
            }
            o.text.setStyle(o.text.style)
        }

        vars[opt.key] = opt.value
        self.user_vars[opt.key] = opt.value
        localStorage.setItem("vars", JSON.stringify(self.user_vars))

        vars.applyVars(game)
    }

    k.addKey(Phaser.Keyboard.ENTER).onDown.add(select, this)
    game.input.onDown.add(function() {
        var x = game.input.x/game.scaleVal,
            y = game.input.y/game.scaleVal
        for (var i in self.options) {
            for (var j in self.options[i]) {
                var t = self.options[i][j].text
                if (Phaser.Rectangle.contains(t.getBounds(), x, y)) {
                    self.oy = parseInt(i)
                    self.ox = parseInt(j)
                    select()
                }
            }
        }
    }, this)
}

GameSetup.prototype.update = function () {
    var game = this.game

    // Update the selector ship icon
    this.ship.x = this.options[this.oy][this.ox].x - 5
    this.ship.y = this.options[this.oy][this.ox].y
}
