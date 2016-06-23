"use strict";

//
// Mass abstract object
//
var Mass = function (game, key, x, y, vx, vy, mass, rotation) {
    Phaser.Sprite.call(this, game, x, y, key)
    //console.log('Mass: ', game, key, x, y, vx, vy, mass, rotation)
    game.physics.arcade.enable(this)
    this.texture.baseTexture.scaleMode = PIXI.scaleModes.NEAREST
    this.anchor.set(0.5, 0.5)

    this.body.velocity.set(vx, vy)

    this.pending_frames = 0
    this.mass = mass
    this.rotation = rotation
    this.ticks_to_live = -1
    this.dead = false
}
Mass.prototype = Object.create(Phaser.Sprite.prototype)
Mass.prototype.constructor = Mass

Mass.prototype.Radius = 0.0

Mass.prototype.update = function() {
    if (this.x > this.game.arena.right)  { this.x = this.game.arena.left   }
    if (this.x < this.game.arena.left)   { this.x = this.game.arena.right  }
    if (this.y > this.game.arena.bottom) { this.y = this.game.arena.top    }
    if (this.y < this.game.arena.top)    { this.y = this.game.arena.bottom }

    if (this.ticks_to_live > 0) {
        this.ticks_to_live -= 1
        if (!this.dead && this.ticks_to_live === 0) {
            this.dead = true
        }
    }
}


// Adjust velocity for gravitational pull towards another mass
Mass.prototype.gravitate = function(other_mass) {
    var dist = this.game.physics.arcade.distanceBetween(this, other_mass),
        angle = this.game.physics.arcade.angleBetween(this, other_mass),
        force = 0

    dist = dist < 4 ? 4 : dist
    force = other_mass.mass/(dist*dist)

    this.body.velocity.x += Math.cos(angle)*force*vars.gravity_const
    this.body.velocity.y += Math.sin(angle)*force*vars.gravity_const
}

Mass.prototype.clearance = function(other_mass) {
    var dist = this.game.physics.arcade.distanceBetween(this, other_mass)
    return dist - (this.Radius + other_mass.Radius)
}

Mass.prototype.check_spot = function() {
    var low     = this.game.groups.low.children,
        high    = this.game.groups.high.children,
        solids  = low.concat(high)
    for (var o of solids) {
        if (o !== this) {
            if (this.clearance(o) < vars.start_clearance) {
                return false
            }
        }
    }
    return true
}

Mass.prototype.find_spot = function() {
    var arena = this.game.arena
    while (true) {
        this.x = Math.random() * (arena.right - 100) + 50
        this.y = Math.random() * (arena.bottom - 100) + 50
        if (this.check_spot()) { return }
    }
}

Mass.prototype.hit_by = function(other_mass) {
    // no-op
}


//
// Smoke "object"
//
var Smoke = function(game, x, y, vx, vy) {
    Mass.call(this, game, 'smoke', x, y, vx, vy, 0.0, 0)
    this.ticks_to_live = parseInt(Math.random()*8+12)

    // Vary alpha/brightness of smoke trail
    this.alpha = Math.random() * 0.25
}
Smoke.prototype = Object.create(Mass.prototype)
Smoke.prototype.constructor = Smoke

Smoke.prototype.Radius = 5.0

Smoke.prototype.update = function() {
    Mass.prototype.update.call(this)
}


//
// Fire objects
//
var Fire = function(game, x, y, vx, vy, owner, key) {
    if (typeof key === 'undefined') { key = 'fire' }
    Mass.call(this, game, key, x, y, vx, vy, 0.0, 0)

    this.animations.add('anim', [0,1,2,3,4,5,6,7], 10, true)
    this.animations.play('anim')

    this.owner = owner
    this.dead_by_hit = false
    this.ticks_to_live = vars.fire_life
    this.damage = vars.fire_damage
}
Fire.prototype = Object.create(Mass.prototype)
Fire.prototype.constructor = Fire

Fire.prototype.Radius = 8.0

Fire.prototype.hit_by = function(other_mass) {
    if (!this.dead) {
        this.dead = true
        this.dead_by_hit = true
    }
}

var SuperFire = function(game, x, y, vx, vy, owner) {
    Fire.call(this, game, x, y, vx, vy, owner, 'fire2')

    this.ticks_to_live = vars.fire_life * 1.5
    this.damage = parseInt(vars.fire_damage * 1.5)
}
SuperFire.prototype = Object.create(Fire.prototype)
SuperFire.prototype.constructor = SuperFire

//
// Ephemeral objects (pops, explosions)
//

// An object that phases through the animations frames and then dies
var Ephemeral = function(game, key, x, y, vx, vy) {
    Mass.call(this, game, key, x, y, vx, vy, 0.0, 0)

    this.phase = 0.0
}
Ephemeral.prototype = Object.create(Mass.prototype)
Ephemeral.prototype.constructor = Ephemeral

Ephemeral.prototype.Radius = 8.0
Ephemeral.prototype.PhaseRate = 0.0

Ephemeral.prototype.update = function() {
    Mass.prototype.update.call(this)

    var phases = this.animations.frameTotal

    this.phase += this.PhaseRate

    if (!this.dead && this.phase >= phases) {
        this.dead = true
    }

    this.frame = Math.min(parseInt(this.phase), phases-1)
}

Ephemeral.prototype.gravitate = function(other_mass) {
    // No effect from gravity
}


var Pop = function(game, x, y, vx, vy) {
    Ephemeral.call(this, game, 'pop', x, y, vx, vy, 0.0, 0)
}
Pop.prototype = Object.create(Ephemeral.prototype)
Pop.prototype.constructor = Ephemeral

Pop.prototype.Radius = 8.0
Pop.prototype.PhaseRate = 0.2


var Explosion = function(game, x, y, vx, vy) {
    Ephemeral.call(this, game, 'explosion', x, y, vx, vy, 0.0, 0)

    this.game.sounds.explode.play()
}
Explosion.prototype = Object.create(Ephemeral.prototype)
Explosion.prototype.constructor = Ephemeral

Explosion.prototype.Radius = 18.0
Explosion.prototype.PhaseRate = 0.5


//
// Sun object
//
var Sun = function(game, x, y) {
    if (typeof x === 'undefined') { x = game.arena.right / 2 }
    if (typeof y === 'undefined') { y = game.arena.bottom / 2 }

    Mass.call(this, game, 'boxes', x, y, 0, 0, 10.0, 0)

    this.animations.add('spin', [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14], 10, true)
    this.animations.play('spin')
}
Sun.prototype = Object.create(Mass.prototype)
Sun.prototype.constructor = Sun

Sun.prototype.Radius = 10.0

Sun.prototype.gravitate = function(other_mass) {
    // Floating and black holes move around
    if (vars.sun >= 2) {
        Mass.prototype.gravitate.call(this, other_mass)
    }
}


//
// Hard objects
//
var Hard = function(game, key, mass) {
    Mass.call(this, game, key, 0, 0, 0, 0, mass, 0)
}
Hard.prototype = Object.create(Mass.prototype)
Hard.prototype.constructor = Hard

Hard.prototype.update = function() {
    if (this.pending_frames > 0) {
        if (this.pending_frames === vars.frames_per_sec / 2) {
            if (this.snd1) { this.snd1.play() }
        }
        this.pending_frames -= 1
        if (this.pending_frames <= 0) {
            this.dead = 0
            this.find_spot()
            this.body.velocity.x = (Math.random()-0.5) * 40
            this.body.velocity.y = (Math.random()-0.5) * 40
            if (this.snd2) { this.snd2.play() }
        }
        return
    }

    Mass.prototype.update.call(this)
}

Hard.prototype.hit_by = function(other_mass) {
    if (this.dead) { return }
    if (other_mass instanceof Sun ||
        other_mass instanceof Hard) {
        this.dead = true
        var vx = this.body.velocity.x, vy = this.body.velocity.y
        var explosion = new Explosion(this.game, this.x, this.y, vx, vy)
        explosion.mass = this.mass
        this.game.groups.high.add(explosion)
    }
}


// Spikes
var Spike = function(game) {
    Hard.call(this, game, 'spike', 4.0)

    this.animations.add('spin', [0,1,2,3,4,5,6,7,8,9,10,11],
                        10, true)
    this.animations.play('spin')

    this.snd1 = game.sounds.flop
    this.snd2 = game.sounds.klank
}
Spike.prototype = Object.create(Hard.prototype)
Spike.prototype.constructor = Hard

Spike.prototype.Radius = 10.0
Spike.prototype.PhaseRate = 0.6

// Asteroids
var Asteroid = function(game) {
    Hard.call(this, game, 'asteroid', 4.0)

    this.animations.add('spin', [0,1,2,3,4,5,6,7,8,9,10,11,12,
                                 13,14,15,16,17,18,19,20,21,22,23,24],
                        5, true)
    this.animations.play('spin')

    this.snd1 = null
    this.snd2 = null
}
Asteroid.prototype = Object.create(Hard.prototype)
Asteroid.prototype.constructor = Hard

Asteroid.prototype.Radius = 15.0
Asteroid.prototype.PhaseRate = 0.4

Asteroid.prototype.find_spot = function() {
    var new_rotation = Math.random() * Math.PI * 2 - Math.PI,
        edge = parseInt(Math.random() * 2)
    while (true) {
        if (edge === 0) {
            this.x = 0
            this.y = parseInt(Math.random()*this.game.arena.bottom)
        } else {
            this.y = 0
            this.x = parseInt(Math.random()*this.game.arena.right)
        }
        if (this.check_spot()) { return }
    }
}


//
// Bobble objects
//
var Bobble = function(game) {
    Mass.call(this, game, 'bobble', 0, 0, 0, 0, 0.5, 0)

    this.animations.add('spin', [0,1,2,3,4], 10, true)
    this.animations.play('spin')
}
Bobble.prototype = Object.create(Mass.prototype)
Bobble.prototype.constructor = Bobble

Bobble.prototype.update = function() {
    if (this.pending_frames > 0) {
        this.pending_frames -= 1
        if (this.pending_frames <= 0) {
            this.dead = 0
            this.find_spot()
            this.body.velocity.x = (Math.random()-0.5) * 60
            this.body.velocity.y = (Math.random()-0.5) * 60
            this.game.sounds.chimeout.play()
        }
        return
    }

    Mass.prototype.update.call(this)
}

Bobble.prototype.hit_by = function(other_mass) {
    if (this.dead) { return }
    this.dead = true
    if (other_mass instanceof Ship) {
        // collision with Ship handled in Ship.hit_by
    } else {
        var vx = this.body.velocity.x / 5,
            vy = this.body.velocity.y / 5,
            pop = new Pop(this.game, this.x, this.y, vx, vy)
        this.game.groups.vapors.add(pop)
        this.game.sounds.boxhit.play()
    }
}

var ShieldBobble = function(game) {
    Bobble.call(this, game)
}
ShieldBobble.prototype = Object.create(Bobble.prototype)
ShieldBobble.prototype.constructor = Bobble

ShieldBobble.prototype.Radius = 10.0
ShieldBobble.prototype.PhaseRate = 0.2


var BulletBobble = function(game) {
    Bobble.call(this, game)
}
BulletBobble.prototype = Object.create(Bobble.prototype)
BulletBobble.prototype.constructor = Bobble

BulletBobble.prototype.Radius = 10.0
BulletBobble.prototype.PhaseRate = 0.1


//
// Ship object
//
var Ship = function(game, shipnum, x, y) {
    Mass.call(this, game, 'ship'+shipnum, x, y, 0, 0, 1.0, 0)

    this.shipnum = shipnum
    this.mycolor = CONST_HEALTH_COLORS[shipnum]
    this.max_health = 100.0
    this.max_shield = 100.0
    this.max_bullet = vars.bbobble_charge
    this.max_appear_frames = 45
    this.appear_frames = this.max_appear_frames
    this.visible = false

    // Add sprites for animations
    this.appear_sprite = game.add.sprite(0, 0, 'appear')
    this.appear_sprite.visible = false
    this.appear_sprite.anchor.set(0.5, 0.5)

    this.thrust_sprite = game.add.sprite(0, 0, 'ship'+shipnum+'-thrust')
    this.thrust_sprite.visible = false
    this.thrust_sprite.animations.add('thrust', [0,1,2,3], 20, true)
    this.thrust_sprite.anchor.set(0.5, 0.5)

    this.reverse_sprite = game.add.sprite(0, 0, 'ship'+shipnum+'-reverse')
    this.reverse_sprite.visible = false
    this.reverse_sprite.animations.add('reverse', [0,1,2,3], 15, true)
    this.reverse_sprite.anchor.set(0.5, 0.5)

    this.shield_sprite = new Phaser.Sprite(game, 0, 0, 'shield')
    this.shield_sprite.visible = false
    this.shield_sprite.animations.add('shield', [0,1,2,3,2,1,0], 30, true)
    this.shield_sprite.anchor.set(0.5, 0.5)
    this.shield_sprite.scale.setTo(1.2)
    this.game.groups.powerup.add(this.shield_sprite)

    this.bullet_sprite = new Phaser.Sprite(game, 0, 0, 'bullet')
    this.bullet_sprite.visible = false
    this.bullet_sprite.animations.add('bullet', [0,1,2,3], 20, true)
    this.bullet_sprite.anchor.set(0.5, 0.5)
    this.game.groups.powerup.add(this.bullet_sprite)

}
Ship.prototype = Object.create(Mass.prototype)
Ship.prototype.constructor = Ship

Ship.prototype.Radius = 11.0

Ship.prototype.start = function(x, y, vx, vy, mass, rotation) {
    if (typeof mass === 'undefined') { mass = 1.0 }
    if (typeof rotation === 'undefined') { rotation = 0.0 }
    if (typeof vx === 'undefined') { vx = 0 }
    if (typeof vy === 'undefined') { vy = 0 }
    if (typeof x === 'undefined') { x = this.x }
    if (typeof y === 'undefined') { y = this.y }

    this.x = x
    this.y = y
    this.body.velocity.set(vx, vy)
    this.mass = mass
    this.rotation = rotation

    this.visible = true
    this.dead = false

    this.health = 100.0
    this.shield = 0.0
    this.bullet = 0.0
    this.thrust = 0
    this.turn = 0
    this.fire_delay = 0
    this.smoke_rate = 2.0
    this.pending_frames = 0
}

Ship.prototype.update = function() {
    if (this.appear_frames > 0) {
        this.appear_sprite.x = this.x
        this.appear_sprite.y = this.y
        if (this.appear_frames > 0 && this.appear_sprite.visible === false) {
            this.appear_sprite.visible = true
            this.game.sounds.startlife.play()
        }
        var frameCnt = this.appear_sprite.animations.frameTotal,
            ratio = 1 - this.appear_frames / this.max_appear_frames
        this.appear_sprite.frame = parseInt(frameCnt * ratio)
        this.appear_frames -= 1
        if (this.appear_frames <= 0) {
            this.start()
            this.appear_sprite.visible = false
        } else {
            return
        }
    }

    if (this.pending_frames > 0) {
        if (this.pending_frames === vars.frames_per_sec / 2) {
            this.game.sounds.startlife.play()
        }
        this.pending_frames -= 1
        this.health = (this.max_health *
                (vars.death_time * vars.frames_per_sec - this.pending_frames) /
                (vars.death_time * vars.frames_per_sec))
        if (this.pending_frames <= 0) {
            this.start()
            this.find_spot()
            this.rotation = Math.random() * Math.PI * 2 - Math.PI
        } else {
            return
        }
    }

    if (this.thrust) {
        this.body.velocity.x += Math.sin(this.rotation)*this.thrust
        this.body.velocity.y -= Math.cos(this.rotation)*this.thrust
        // Smoke trails, don't overload frame rate
        // TODO: disable if AI training
        if (vars.graphics > 0) {
            // TODO: adjust smoke_rate based on current FPS and target FPS
            var rads = this.rotation
            if (this.thrust > 0) {
                rads = (rads + Math.PI)
            }
            for (var i = 0; i < this.smoke_rate; i++) {
                var x = (this.x +
                         Math.sin(rads)*(this.Radius+10) +
                         Math.random()*14 - 7),
                    y = (this.y -
                         Math.cos(rads)*(this.Radius+10) +
                         Math.random()*14 - 7),
                    vx = (this.body.velocity.x +
                          Math.sin(rads)*vars.smoke_speed +
                          Math.random()/3),
                    vy = (this.body.velocity.y -
                          Math.cos(rads)*vars.smoke_speed +
                          Math.random()/3),
                    smoke = new Smoke(this.game, x, y, vx, vy)
                this.game.groups.vapors.add(smoke)
            }
        }
    }

    if (this.turn) {
        this.rotation += this.turn*vars.rotation_step
    }

    Mass.prototype.update.call(this)

    // Keep other sprites in sync with the main one
    this.thrust_sprite.x = this.x
    this.thrust_sprite.y = this.y
    this.thrust_sprite.rotation = this.rotation
    this.reverse_sprite.x = this.x
    this.reverse_sprite.y = this.y
    this.reverse_sprite.rotation = this.rotation
    this.shield_sprite.x = this.x
    this.shield_sprite.y = this.y
    this.bullet_sprite.x = this.x
    this.bullet_sprite.y = this.y

    // Health, Shield, and Bullet housekeeping
    if (this.health < this.max_health) {
        this.health = Math.min(this.max_health,
                               this.health + vars.heal_rate/100.0)
        // HUD object will update visual represenation
    }

    if (this.shield > 0) {
        this.shield_sprite.alpha = (this.shield / this.max_shield) * 0.75
        if (!this.shield_sprite.visible) {
            this.shield_sprite.visible = true
            this.shield_sprite.animations.play('shield')
        }
    } else if (this.shield_sprite.visible) {
        this.shield_sprite.visible = false
        this.shield_sprite.animations.stop()
    }

    if (this.bullet > 0) {
        this.bullet -= 0.1
        this.bullet_sprite.alpha = Math.min(1.0, this.bullet * 4 /
                                                 this.max_bullet)
        if (this.bullet > 0 && !this.bullet_sprite.visible) {
            this.bullet_sprite.visible = true
            this.bullet_sprite.animations.play('bullet')
        }
    } else if (this.bullet_sprite.visible) {
        this.bullet_sprite.visible = false
        this.bullet_sprite.animations.stop()
    }

    // Slow down firing rate. No re-fire until delay finished
    if (this.fire_delay > 0) {
        this.fire_delay -= 1
    }

}

Ship.prototype.cmd_left = function() {
    this.turn = -1
}

Ship.prototype.cmd_right = function() {
    this.turn = 1
}

Ship.prototype.cmd_turn_off = function() {
    this.turn = 0
}

Ship.prototype.cmd_thrust = function() {
    if (!this.thrust) {
        this.thrust = vars.thrust_power
        // switch sprite
        this.visible = false
        this.thrust_sprite.visible = true
        this.thrust_sprite.animations.play('thrust')
        this.reverse_sprite.visible = false
    }
}

Ship.prototype.cmd_reverse = function() {
    if (!this.thrust) {
        this.thrust = vars.reverse_power
        // switch sprite
        this.visible = false
        this.thrust_sprite.visible = false
        this.reverse_sprite.visible = true
        this.reverse_sprite.animations.play('reverse')
    }
}

Ship.prototype.cmd_thrust_off = function() {
    if (this.thrust) {
        this.thrust = 0
        // switch sprite
        this.visible = true
        this.thrust_sprite.visible = false
        this.thrust_sprite.animations.stop()
        this.reverse_sprite.visible = false
        this.reverse_sprite.animations.stop()
    }
}

Ship.prototype.cmd_fire = function() {
    if (!this.fire_delay && !this.pending_frames) {
        var rads = this.rotation,
            vx = this.body.velocity.x + Math.sin(rads)*vars.fire_speed,
            vy = this.body.velocity.y - Math.cos(rads)*vars.fire_speed,
            x = this.x + Math.sin(rads)*(this.Radius+Fire.prototype.Radius+5),
            y = this.y - Math.cos(rads)*(this.Radius+Fire.prototype.Radius+5)
        if (this.bullet > 0) {
            this.fire_delay = parseInt(vars.fire_delay_frames * 0.75)
            vx *= 1.2
            vy *= 1.2
            var fire = new SuperFire(this.game, x, y, vx, vy, this)
        } else {
            this.fire_delay = vars.fire_delay_frames
            var fire = new Fire(this.game, x, y, vx, vy, this)
        }
        this.game.groups.high.add(fire)
        this.game.sounds.fire.play()
    }
}

Ship.prototype.damage = function(damage) {
    this.shield -= damage
    if (this.shield < 0.0) {
        this.health += this.shield
        this.shield = 0.0
    }
    if (this.health <= 0.0) {
        this.health = 0.0
        this.dead = true
        this.visible = false
        this.player.deaths += 1
        this.pending_frames = vars.death_time * vars.frames_per_sec

        this.shield_sprite.visible = false
        this.shield_sprite.animations.stop()
        this.bullet_sprite.visible = false
        this.bullet_sprite.animations.stop()
        var vx = this.body.velocity.x,
            vy = this.body.velocity.y
        var explosion = new Explosion(this.game, this.x, this.y, vx, vy)
        explosion.mass = this.mass
        this.game.groups.high.add(explosion)
        return true // dead
    } else {
        return false // still alive
    }
}

Ship.prototype.hit_by = function(other_mass) {
    var dead = false
    if (this.dead) { return }
    if (other_mass instanceof Fire) {
        var damage = ((other_mass.damage-10) *
                      other_mass.ticks_to_live/vars.fire_life + 10)
        dead = this.damage(other_mass.damage)
        if (dead && other_mass.owner !== this) {
            other_mass.owner.player.score += 1
            other_mass.owner.player.complement = 1
        }
    } else if (other_mass instanceof Explosion) {
        if (!this.shield) {
            this.damage(vars.explosion_damage)
        }
    } else if (other_mass instanceof Ship) {
        var my_damage = other_mass.health + other_mass.shield,
            other_damage = this.health + this.shield
        this.damage(my_damage)
        other_mass.damage(other_damage)
    } else if (other_mass instanceof ShieldBobble) {
        this.shield = Math.min(this.max_shield,
                               this.shield + vars.sbobble_power)
        this.game.sounds.chimein.play()
    } else if (other_mass instanceof BulletBobble) {
        this.bullet = Math.min(this.max_bullet,
                               this.bullet + vars.bbobble_charge)
        this.game.sounds.chimein.play()
    } else {
        dead = this.damage(1000)
        if (dead && this.player.score > 0) {
            this.player.score += vars.death_score
            this.player.insult = 1
        }
    }
}


//
// Object interactions/physics
//
function runobjects(game) {
    var groups  = game.groups,
        vapors  = groups.vapors.children,
        low     = groups.low.children,
        high    = groups.high.children,
        virtual = groups.virtual.children,
        pend    = groups.pend.children,
        solids  = low.concat(high),
        real    = vapors.concat(solids),
        all     = real.concat(virtual)

    // Make objects (Spikes, Asteroids, Bobble/powerups) appear
    for (var d of [[Spike,        vars.spike_rate],
                   [Asteroid,     vars.asteroid_rate],
                   [ShieldBobble, vars.shield_powerup_rate],
                   [BulletBobble, vars.bullet_powerup_rate]]) {

        if (Math.random() < d[1]) {
            var obj = new d[0](game)
            obj.dead = true
            obj.pending_frames = vars.frames_per_sec
            groups.pend.add(obj)
        }
    }

    // Gravitate
    for (var o1 of real) {
        for (var o2 of solids) {
            if (o1 !== o2) {
                o1.gravitate(o2)
            }
        }
    }

    // Update pending objects (they are not visible so Phaser is not
    // automatically calling update for us)
    for (var o of pend) {
        o.update()
        if (!o.dead && (o instanceof Ship ||
                        o instanceof Hard ||
                        o instanceof Bobble)) {
            groups.pend.remove(o, false)
            groups.low.add(o)
        }
    }

    // Check for collisions
    for (var o1 of solids) {
        for (var o2 of solids) {
            if (o1 !== o2 && !o1.dead) {
                if (o1.clearance(o2) < 0) {
                    o1.hit_by(o2)
                }
            }
        }
    }

    // Check all objects for death
    for (var grp of [groups.vapors,
                     groups.low,
                     groups.high,
                     groups.virtual]) {
        for (var o of grp.children) {
            if (o.dead) {
                if (o instanceof Ship) {
                    grp.remove(o, false)
                    groups.pend.add(o)
                } else if (o instanceof Fire) {
                    var x = o.x, y = o.y,
                        vx = o.body.velocity.x,
                        vy = o.body.velocity.y
                    if (o.dead_by_hit) {
                        vx = vx / 5
                        vy = vy / 5
                        game.sounds.pop.play()
                    }
                    grp.remove(o, true)
                    groups.vapors.add(new Pop(game, x, y, vx, vy))
                } else {
                    grp.remove(o, true)
                }
            }
        }
    }
}
