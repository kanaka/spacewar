"use strict";

var HelpText = {
    welcome:
    {title: "Welcome to Spacewar",
     w: 420, h: 480, size: 15, font: "Arial",
     text:
     "The objective of Spacwar is to pilot a ship and score points " +
     "by killing your opponents. Your ship is equipped with a blaster " +
     "and forward and reverse thrusters." +
     "\n\n" +
     "Shield and blaster powerups will appear every now and then. If " +
     "you run into these with your ship, you will receive a charge to " +
     "shields or blasters. Asteroids and spiked balls also appear " +
     "periodically and collisions with them are fatal. " +
     "\n\n" +
     "The vital stats for each player's ship appear on the heads up " +
     "display to the right. Below the ship image is the player's " +
     "score. Below the score is the health of the ship and below that " +
     "is the shield strength if the ship has gotten a shield powerup. " +
     "\n\n" +
     "Press F1 during the game to show the keys that control each " +
     "player."},
    keys:
    {title: "Player Control Keys",
     w: 480, h: 350, size: 13, font: "Monospace",
     text:
     "Player 1:                        Player 2:\n" +
     "....Left:     Left Arrow         ....Left:     a\n" +
     "....Right:    Right Arrow        ....Right:    d\n" +
     "....Thrust:   Up Arrow           ....Thrust:   w\n" +
     "....R-Thrust: Down Arrow         ....R-Thrust: s\n" +
     "....Fire:     Right-Ctrl         ....Fire:     Tab\n" +
     "\n" +
     "Player 3:                        Player 4:\n" +
     "....Left:     j                  ....Left:     Numpad 2\n" +
     "....Right:    l                  ....Right:    Numpad 8\n" +
     "....Thrust:   i                  ....Thrust:   Numpad 4\n" +
     "....R-Thrust: k                  ....R-Thrust: Numpad 5\n" +
     "....Fire:     Space              ....Fire:     Numpad 0 \n"
    }}


//
// Help object
//
function Help(game, item) {
    Phaser.Group.call(this, game)
    this.visible = true
    this.ticks = 0

    var data = HelpText[item]
    this.x = (game.arena.right - data.w) / 2
    this.y = (game.arena.bottom - data.h) / 2

    // Background rectangle
    var bg = game.add.bitmapData(data.w, data.h)
    bg.rect(0, 0, data.w, data.h, rgba(50, 100, 50, 0.75))
    console.log(data.w, data.h)
    //bg.rect(0, 0, 200, 200, rgba(50, 100, 50))
    this.create(0, 0, bg)

    // "Help" title
    this.title = game.add.text(data.w / 2, 10, data.title,
            { font: "Arial Black",
              fontSize: 18,
              fill: rgba(255, 240, 200)},
            this);
    this.title.anchor.set(0.5, 0)
    this.title.setShadow(2, 2, 'rgba(128,128,128,0.7)', 2)

    // "Help" text
    this.text = game.add.text(20, 50, data.text,
            { font: data.font,
              fontSize: data.size,
              fill: rgba(255, 240, 200),
              align: 'left',
              wordWrap: true,
              wordWrapWidth: data.w-40},
            this);
    this.text.anchor.set(0, 0)
    this.text.setShadow(2, 2, 'rgba(128,128,128,0.7)', 2)

    // Outline
    this.create(0, 0, borderRect(game.add.bitmapData(0, 0),
                                 0, 0, data.w, data.h,
                                 rgba(40, 80, 40), 2))

    // Dotted line animation
    var frameCnt = 20,
        sheet = game.add.bitmapData(frameCnt * data.w, data.h)
    for (var i=0; i < frameCnt; i++) {
        var amplitude = Math.cos(Math.PI * 2 * i/frameCnt),
            color = rgba(255,
                         parseInt(220 + amplitude * 30),
                         parseInt(180 + amplitude * 65))
        borderRect(sheet,
                   i * data.w, 0, data.w, data.h,
                   color, 2, [frameCnt/2, frameCnt/2], i)
    }
    game.cache.addSpriteSheet(item, '', sheet.canvas,
                              data.w, data.h, frameCnt, 0, 0)
    this.border = this.create(0, 0, item)
    this.border.animations.add('anim', null, 30, true)
    this.border.animations.play('anim')
}
Help.prototype = Object.create(Phaser.Group.prototype)
Help.prototype.constructor = Help
