"use strict";

var MenuItem = function (game, name, state) {
    Phaser.Sprite.call(this, game, 0, 0, 'menu-'+name+'-off')
    this.visible = true
    this.anchor.set(0.5, 0.5)

    this.bgd_sprite = game.add.sprite(0, 0, 'menu-bgd')
    this.bgd_sprite.visible = false
    this.bgd_sprite.anchor.set(0.5, 0.5)

    this.on_sprite = game.add.sprite(0, 0, 'menu-'+name+'-on')
    this.on_sprite.visible = false
    this.on_sprite.anchor.set(0.5, 0.5)

    this.state = state
    this.glow = 0.0
    this.active = false
}
MenuItem.prototype = Object.create(Phaser.Sprite.prototype)
MenuItem.prototype.constructor = Mass

MenuItem.prototype.init = function(x, y) {
    this.x = x
    this.y = y
    this.bgd_sprite.x = x
    this.bgd_sprite.y = y
    this.on_sprite.x = x
    this.on_sprite.y = y
}

MenuItem.prototype.on = function(x, y) {
    this.visible = false
    this.active = true
    this.bgd_sprite.visible = true
    this.on_sprite.visible = true
}

MenuItem.prototype.off = function(x, y) {
    this.visible = true
    this.active = false
    this.bgd_sprite.visible = false
    this.on_sprite.visible = false
}

MenuItem.prototype.update = function() {
    if (this.bgd_sprite.visible) {
        this.glow += 0.1
        this.bgd_sprite.alpha = Math.abs(Math.sin(this.glow))
    }
}

var GameMenu = function(game) {
    this.current = 0
}

GameMenu.prototype.init = function () {
}

GameMenu.prototype.create = function () {
    var self = this,
        game = this.game

    // Add and start the menu soundtrack
    if (!game.music.menu.isPlaying) {
        game.music.menu.play()
    }

    //'menu-bgd'

    // Define star group
    game.groups = {stars:      starGroup(game),
                   background: game.add.group(),
                   menu:       game.add.group()}

    // "Spacewar" Logo
    this.logo = game.groups.background.create(100, 25, 'logo')

    // Large ship image
    this.ship = game.groups.background.create(450, 250, 'ship-big')
    this.ship.tint = 0x808080

    // Rotating box image/animation
    this.bigboxes = game.groups.background.create(580,  80, 'bigboxes')
    this.bigboxes.animations.add('anim', [0,1,2,3,4,5,6,7,8,9,
                                          10,11,12,13,14], 30, true)
    this.bigboxes.animations.play('anim')
    this.bigboxes.tint = 0xe0e0e0

    this.info = game.add.text(20, 570,
            'Spacewar Version ' + VERSION,
            {font: "Arial Black",
             fontSize: 10,
             fill: rgba(200, 120, 100)},
            game.groups.menu)
    this.info.setShadow(2, 2, 'rbga(128,128,128,0.7)', 2)

    this.version = game.add.text(100, 460,
            'with ' + vars.player_cnt() + ' players',
            {font: "Arial Black",
             fontSize: 11,
             fill: rgba(200, 175, 120)},
            game.groups.menu)
    this.version.setShadow(2, 2, 'rbga(128,128,128,0.7)', 2)

    // Menu items
    this.menu = [new MenuItem(game, 'start', 'Play'),
                 new MenuItem(game, 'setup', 'Setup'),
                 new MenuItem(game, 'news',  'News'),
                 new MenuItem(game, 'creds', 'Creds')]

    var posX = 140, posY = 400
    for (var i in this.menu) {
        var m = this.menu[i]
        game.groups.menu.add(m)
        m.init(posX, posY)
        posX += 180
        if (i % 2) {
            posY -= 30
        } else {
            posY += 30
        }
    }

    // Activate starting menu item
    this.menu[this.current].on()

    //
    // Menu interactions
    //
    function move(dx, x) {
        var len = self.menu.length
        self.menu[self.current].off()
        if (typeof x === 'number') {
            self.current = x
        } else {
            self.current = (self.current + len + dx) % len
        }
        self.menu[self.current].on()
        game.sounds.menu_move.play()
    }
    function choose() {
        if (self.current === 0) {
            game.music.menu.stop()
        }
        game.sounds.menu_choose.play()
        self.state.start(self.menu[self.current].state);
    }

    // Add keyboard interaction
    var k = game.input.keyboard
    k.addKey(Phaser.Keyboard.LEFT ).onDown.add(function() { move(-1) })
    k.addKey(Phaser.Keyboard.RIGHT).onDown.add(function() { move(+1) })
    k.addKey(Phaser.Keyboard.ENTER   ).onDown.add(choose)
    k.addKey(Phaser.Keyboard.SPACEBAR).onDown.add(choose)
    game.input.onDown.add(choose)

    // Add mouse interaction
    game.input.addMoveCallback(function(pointer, absX, absY) {
        var x = absX/game.scaleVal, y = absY/game.scaleVal
        for (var i in self.menu) {
            var menu = self.menu[i]
            if (menu.active) { continue }
            if (Phaser.Rectangle.contains(menu.getBounds(), x, y)) {
                move(null, parseInt(i))
            }
        }
    }, this)
}

GameMenu.prototype.update = function () {
}

GameMenu.prototype.render = function () {
    var game = this.game
    //game.debug.soundInfo(game.music.menu, 20, 460)
}
