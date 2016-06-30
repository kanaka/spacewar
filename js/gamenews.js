"use strict";

var GameNews = function(game) {}

GameNews.prototype.init = function () {
}

GameNews.prototype.create = function () {
    var self = this,
        game = this.game

    game.groups = {stars:   starLayerGroup(game),
                   main:    game.add.group()}

    game.groups.main.create(20, 20, 'menu-news-on')

    var news = game.cache.getJSON('news')
    if (!news) {
        // TODO: render error
        console.log("could not retrieve news/CHANGES.json")
    }

    // Add news entries
    var left = 100,
        top = 150
    for (var entry of news) {
        var t
        t = game.add.text(left, top, 'Spacewar ' + entry.version,
                {font: "Arial Black",
                 fontSize: 18,
                 fill: rgba(150, 170, 200)},
                game.groups.main)
        t = game.add.text(left + 150, top + 5, entry.date,
                {font: "Arial Black",
                 fontSize: 11,
                 fill: rgba(125, 140, 170)},
                game.groups.main)

        t = game.add.text(left + 30, top + 22, entry.summary,
                {font: "Arial Black",
                 fontSize: 14,
                 fill: rgba(160, 170, 190)},
                game.groups.main)
        top += 50
    }

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

GameNews.prototype.update = function () {
    var game = this.game
}
