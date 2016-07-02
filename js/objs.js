"use strict";

// Mass/object pool. Unused objects go back into the pool and get
// re-used later to avoid GC
var massPool = {
    Smoke:        [],
    Fire:         [],
    SuperFire:    [],
    Pop:          [],
    Explosion:    [],
    Debris1:      [],
    Debris2:      [],
    Debris3:      [],
    Debris4:      [],
    DebrisBase:   [],
    DebrisBubble: [],
    DebrisMotor:  [],
    Spike:        [],
    Asteroid:     [],
    ShieldBobble: [],
    BulletBobble: []
}

function mass(game, klass, grp, x, y, vx, vy, props) {
    var o, pool = massPool[klass.name]
    if (pool.length > 0) {
        //console.log("Reusing:", klass.name)
        o = pool.pop()
    } else {
        //console.log("Creating new:", klass.name)
        o = new klass(game)
    }
    o.start(x, y, vx, vy)
    if (typeof props !== 'undefined') {
        for (var k in props) {
            o[k] = props[k]
        }
    }
    game.groups[grp].add(o)
    return o
}

function massCounts() {
    for (var k in massPool) {
        console.log(k,"-", massPool[k].length);
    }
}

//
// Mass abstract object
//
function Mass(game, key) {
    Phaser.Sprite.call(this, game, 20, 20, key)
    this.texture.baseTexture.scaleMode = PIXI.scaleModes.NEAREST
    this.anchor.set(0.5, 0.5)

    this.mass = 0.0
    this.rotation = 0.0
    this.x = this.y = this.vx = this.vy = 0
}
Mass.prototype = Object.create(Phaser.Sprite.prototype)
Mass.prototype.constructor = Mass

Mass.prototype.Radius = 0.0
Mass.prototype.Taxonomy = {}

Mass.prototype.start = function(x, y, vx, vy) {
    this.x = typeof x === 'undefined' ? this.x : x
    this.y = typeof y === 'undefined' ? this.y : y
    this.vx = typeof vx === 'undefined' ? this.vx : vx
    this.vy = typeof vy === 'undefined' ? this.vy : vy


    this.dead = false
    this.pending_frames = 0
    this.ticks_to_live = -1
}

Mass.prototype.update = function() {
    if (this.game.pausePlay) { return }

    this.x += this.vx * this.game.time.physicsElapsed
    this.y += this.vy * this.game.time.physicsElapsed

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
    var dist = distanceBetween(this, other_mass),
        angle = angleBetween(this, other_mass),
        force = 0

    dist = dist < 4 ? 4 : dist
    force = other_mass.mass/(dist*dist)

    this.vx += Math.cos(angle)*force*vars.gravity_const
    this.vy += Math.sin(angle)*force*vars.gravity_const
}

Mass.prototype.clearance = function(other_mass) {
    var dist = distanceBetween(this, other_mass)
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
function Smoke(game) {
    Mass.call(this, game, 'smoke')

    this.alpha = Math.random() * 0.25
    this.animations.add('anim', [0,1,2,3], 5, true)
    this.animations.play('anim')
}
Smoke.prototype = Object.create(Mass.prototype)
Smoke.prototype.constructor = Smoke

Smoke.prototype.Radius = 5.0

Smoke.prototype.start = function(x, y, vx, vy) {
    Mass.prototype.start.call(this, x, y, vx, vy)
    this.ticks_to_live = parseInt(Math.random()*8+12)
}


//
// Fire objects
//
function Fire(game, key) {
    Mass.call(this, game, key || 'fire')

    this.animations.add('anim', [0,1,2,3], 10, true)

    this.damage = vars.fire_damage
    this.owner = null
}
Fire.prototype = Object.create(Mass.prototype)
Fire.prototype.constructor = Fire

Fire.prototype.Radius = 8.0
Fire.prototype.Taxonomy = {fire: true,
                           damage: true,
                           significant: true}


Fire.prototype.start = function(x, y, vx, vy) {
    Mass.prototype.start.call(this, x, y, vx, vy)
    this.owner = null
    this.dead_by_hit = false
    this.ticks_to_live = vars.fire_life
    this.animations.stop('fire')
    this.animations.stop('superfire')
    this.animations.play(this.mode)
}

Fire.prototype.hit_by = function(other_mass) {
    if (!this.dead) {
        this.dead = true
        this.dead_by_hit = true
    }
}

function SuperFire(game) {
    Fire.call(this, game, 'superfire')

    this.damage = parseInt(vars.fire_damage * 1.5)
}
SuperFire.prototype = Object.create(Fire.prototype)
SuperFire.prototype.constructor = SuperFire

SuperFire.prototype.start = function(x, y, vx, vy) {
    this.mode = 'superfire'
    Fire.prototype.start.call(this, x, y, vx, vy)
    this.ticks_to_live = vars.fire_life * 1.5
}

//
// Ephemeral objects (pops, explosions, Debris)
//

// An object that phases through the animations frames and then dies
function Ephemeral(game, key) {
    Mass.call(this, game, key)
    this.phases = []
}
Ephemeral.prototype = Object.create(Mass.prototype)
Ephemeral.prototype.constructor = Ephemeral

Ephemeral.prototype.Radius = 8.0
Ephemeral.prototype.PhaseRate = 0.0

Ephemeral.prototype.start = function(x, y, vx, vy) {
    Mass.prototype.start.call(this, x, y, vx, vy)
    this.phase = 0.0
}

Ephemeral.prototype.update = function() {
    if (this.game.pausePlay) { return }

    Mass.prototype.update.call(this)

    this.phase += this.PhaseRate

    if (!this.dead && this.phase >= this.phases.length) {
        this.dead = true
    }

    this.frame = Math.min(parseInt(this.phase), this.phases.length-1)
}

Ephemeral.prototype.gravitate = function(other_mass) {
    // No effect from gravity
}


function Pop(game) {
    Ephemeral.call(this, game, 'pop')
    this.phases = [0,1,2,3]
}
Pop.prototype = Object.create(Ephemeral.prototype)
Pop.prototype.constructor = Pop

Pop.prototype.Radius = 8.0
Pop.prototype.PhaseRate = 0.2


function Explosion(game) {
    Ephemeral.call(this, game, 'explosion')
    this.phases = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
}
Explosion.prototype = Object.create(Ephemeral.prototype)
Explosion.prototype.constructor = Explosion

Explosion.prototype.Radius = 18.0
Explosion.prototype.PhaseRate = 0.5
Explosion.prototype.Taxonomy = {explosion: true,
                                damage: true,
                                significant: true}

function Debris(game, key) {
    Ephemeral.call(this, game, key)
}
Debris.prototype = Object.create(Ephemeral.prototype)
Debris.prototype.constructor = Debris
Debris.prototype.Taxonomy = {debris: true, damage: true, significant: true}

Debris.prototype.PhaseRate = 0.2

Debris.prototype.start = function(x, y, vx, vy) {
    vx = parseInt(vx + Math.random()*100-50)
    vy = parseInt(vy + Math.random()*100-50)
    Ephemeral.prototype.start.call(this, x, y, vx, vy)
    this.dead_by_hit = false
}

Debris.prototype.hit_by = function(other_mass) {
    if (!this.dead && !other_mass.dead) {
        if (other_mass instanceof Ephemeral) {
            return
        }
        if (other_mass instanceof Sun || this.phase < this.phases / 2) {
            // Allow debris to pass through on initial collision with
            // Sun
            return
        }
        this.dead = true
        this.dead_by_hit = true
    }
}


function Debris1(game) {
    Debris.call(this, game, 'debris1')
    this.phases = [0,1,2,3,4,5,6,7]
}
Debris1.prototype = Object.create(Debris.prototype)
Debris1.prototype.constructor = Debris1
Debris1.prototype.Radius = 6.0

function Debris2(game) {
    Debris.call(this, game, 'debris2')
    this.phases = [0,1,2,3,4,5,6,7]
}
Debris2.prototype = Object.create(Debris.prototype)
Debris2.prototype.constructor = Debris2
Debris2.prototype.Radius = 6.0

function Debris3(game) {
    Debris.call(this, game, 'debris3')
    this.phases = [0,1,2,3,4,5,6,7]
}
Debris3.prototype = Object.create(Debris.prototype)
Debris3.prototype.constructor = Debris3
Debris3.prototype.Radius = 6.0

function Debris4(game) {
    Debris.call(this, game, 'debris4')
    this.phases = [0,1,2,3,4,5,6,7]
}
Debris4.prototype = Object.create(Debris.prototype)
Debris4.prototype.constructor = Debris4
Debris4.prototype.Radius = 6.0

function DebrisBase(game) {
    Debris.call(this, game, 'debris-base')
    this.phases = [0,1,2,3,4,5,6,7]
}
DebrisBase.prototype = Object.create(Debris.prototype)
DebrisBase.prototype.constructor = DebrisBase
DebrisBase.prototype.Radius = 18.0
DebrisBase.prototype.PhaseRate = 0.07

function DebrisBubble(game) {
    Debris.call(this, game, 'debris-bubble')
    this.phases = [0,1,2,3,4,5,6,7]
}
DebrisBubble.prototype = Object.create(Debris.prototype)
DebrisBubble.prototype.constructor = DebrisBubble
DebrisBubble.prototype.Radius = 8.0
DebrisBubble.prototype.PhaseRate = 0.1

function DebrisMotor(game) {
    Debris.call(this, game, 'debris-motor')
    this.phases = [0,1,2,3,4,5,6,7]
}
DebrisMotor.prototype = Object.create(Debris.prototype)
DebrisMotor.prototype.constructor = DebrisMotor
DebrisMotor.prototype.Radius = 6.0
DebrisMotor.prototype.PhaseRate = 0.1



//
// Sun object
//
function Sun(game) {
    Mass.call(this, game, 'boxes')
    this.mass = 10.0

    this.animations.add('spin',
            [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14],
            10, true)
    this.animations.play('spin')

    this.x = game.arena.right / 2
    this.y = game.arena.bottom / 2
}
Sun.prototype = Object.create(Mass.prototype)
Sun.prototype.constructor = Sun

Sun.prototype.Radius = 10.0
Sun.prototype.Taxonomy = {sun: true,
                          hard: true,
                          significant: true}

Sun.prototype.gravitate = function(other_mass) {
    // Floating and black holes move around
    if (vars.sun >= 2) {
        Mass.prototype.gravitate.call(this, other_mass)
    }
}


//
// Hard objects
//
function Hard(game, key) {
    Mass.call(this, game, key)
}
Hard.prototype = Object.create(Mass.prototype)
Hard.prototype.constructor = Hard

Hard.prototype.update = function() {
    if (this.game.pausePlay) { return }

    if (this.pending_frames > 0) {
        if (this.pending_frames === vars.frames_per_sec / 2) {
            if (this.snd1) { this.snd1.play() }
        }
        this.pending_frames -= 1
        if (this.pending_frames <= 0) {
            this.dead = 0
            this.find_spot()
            this.vx = (Math.random()-0.5) * 40
            this.vy = (Math.random()-0.5) * 40
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
        var vx = this.vx, vy = this.vy
        this.game.sounds.explode.play()
        //var explosion = new Explosion(this.game, this.x, this.y, vx, vy)
        mass(this.game, Explosion, 'high',
             this.x, this.y, vx, vy, {mass: this.mass})
    }
}


// Spikes
function Spike(game) {
    Hard.call(this, game, 'spike')
    this.mass = 4.0

    this.animations.add('spin', [0,1,2,3,4,5,6,7,8,9,10,11], 10, true)
    this.animations.play('spin')

    this.snd1 = game.sounds.flop
    this.snd2 = game.sounds.klank
}
Spike.prototype = Object.create(Hard.prototype)
Spike.prototype.constructor = Spike

Spike.prototype.Radius = 10.0
Spike.prototype.PhaseRate = 0.6
Spike.prototype.Taxonomy = {spike: true,
                            hard: true,
                            significant: true}

// Asteroids
function Asteroid(game) {
    Hard.call(this, game, 'asteroid')
    this.mass = 4.0

    this.animations.add('spin',
            [0,1,2,3,4,5,6,7,8,9,10,11,12,13,
             14,15,16,17,18,19,20,21,22,23], 5, true)
    this.animations.play('spin')

    this.snd1 = null
    this.snd2 = null
}
Asteroid.prototype = Object.create(Hard.prototype)
Asteroid.prototype.constructor = Asteroid

Asteroid.prototype.Radius = 15.0
Asteroid.prototype.PhaseRate = 0.4
Asteroid.prototype.Taxonomy = {asteroid: true,
                               hard: true,
                               significant: true}

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
function Bobble(game, key) {
    Mass.call(this, game, key)
    this.mass = 0.5

    this.animations.add('spin', [0,1,2,3,4], 10, true)
    this.animations.play('spin')
}
Bobble.prototype = Object.create(Mass.prototype)
Bobble.prototype.constructor = Bobble

Bobble.prototype.update = function() {
    if (this.game.pausePlay) { return }

    if (this.pending_frames > 0) {
        this.pending_frames -= 1
        if (this.pending_frames <= 0) {
            this.dead = 0
            this.find_spot()
            this.vx = (Math.random()-0.5) * 60
            this.vy = (Math.random()-0.5) * 60
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
        mass(this.game, Pop, 'vapors',
             this.x, this.y, this.vx / 5, this.vy / 5)
        this.game.sounds.boxhit.play()
    }
}

function ShieldBobble(game) {
    Bobble.call(this, game, 'bobble')
}
ShieldBobble.prototype = Object.create(Bobble.prototype)
ShieldBobble.prototype.constructor = ShieldBobble

ShieldBobble.prototype.Radius = 10.0
ShieldBobble.prototype.PhaseRate = 0.2
ShieldBobble.prototype.Taxonomy = {shield: true,
                                   powerup: true,
                                   significant: true}


function BulletBobble(game) {
    Bobble.call(this, game, 'bobble')
}
BulletBobble.prototype = Object.create(Bobble.prototype)
BulletBobble.prototype.constructor = BulletBobble

BulletBobble.prototype.Radius = 10.0
BulletBobble.prototype.PhaseRate = 0.1
BulletBobble.prototype.Taxonomy = {bullet: true,
                                   powerup: true,
                                   significant: true}


//
// Ship object
//
function Ship(game, shipnum) {
    Mass.call(this, game, 'ship'+shipnum)
    this.mass = 1.0

    this.shipnum = shipnum
    this.mycolor = CONST_HEALTH_COLORS[shipnum]
    this.max_health = 100.0
    this.max_shield = 100.0
    this.max_bullet = vars.bbobble_charge
    this.max_appear_frames = 45
    this.appear_frames = this.max_appear_frames
    this.max_warp_frames = 60
    this.warp_frames = 0
    this.visible = true

    this.frameName = 'main'
    this.animations.add('thrust',
            Phaser.Animation.generateFrameNames('thrust', 0, 3),
            20, true)

    this.animations.add('reverse',
            Phaser.Animation.generateFrameNames('reverse', 0, 3),
            15, true)

    this.appearPhases = Phaser.Animation.generateFrameNames('teleport', 0, 23)
    this.warpPhases = Phaser.Animation.generateFrameNames('warp', 0, 11)

    // Add sprites for powerups

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

    // Play initial appearing sound
    this.game.sounds.startlife.play()
}
Ship.prototype = Object.create(Mass.prototype)
Ship.prototype.constructor = Ship

Ship.prototype.Radius = 11.0
Ship.prototype.Taxonomy = {ship: true,
                           damage: true,
                           significant: true}

Ship.prototype.activate = function(x, y, vx, vy, mass, rotation) {
    if (typeof mass === 'undefined') { mass = 1.0 }
    if (typeof rotation === 'undefined') { rotation = 0.0 }
    if (typeof vx === 'undefined') { vx = 0 }
    if (typeof vy === 'undefined') { vy = 0 }
    if (typeof x === 'undefined') { x = this.x }
    if (typeof y === 'undefined') { y = this.y }

    this.x = x
    this.y = y
    this.vx = vx
    this.vy = vy
    this.mass = mass
    this.rotation = rotation

    this.visible = true
    this.dead = false
    this.frameName = 'main'

    this.health = 100.0
    this.shield = 0.0
    this.bullet = 0.0
    this.thrust = 0
    this.turn = 0
    this.fire_delay = 0
    this.smoke_rate = 2.0
    this.pending_frames = 0
}

Ship.prototype.deactivate = function() {
    if (this.dead) { return }
    this.dead = true
    this.health = 0.0
    this.shield = 0.0
    this.bullet = 0.0

    this.visible = false
    this.shield_sprite.visible = false
    this.shield_sprite.animations.stop()
    this.bullet_sprite.visible = false
    this.bullet_sprite.animations.stop()
}

Ship.prototype.update = function() {
    if (this.game.pausePlay) { return }

    // Handle special modes
    if (this.appear_frames > 0) {
        var frameCnt = this.appearPhases.length,
            ratio = 1 - this.appear_frames / this.max_appear_frames
        this.frameName = this.appearPhases[parseInt(frameCnt * ratio)]
        this.appear_frames -= 1
        if (this.appear_frames <= 0) {
            this.activate()
        } else {
            return
        }
    } else if (this.warp_frames > 0) {
        var frameCnt = this.warpPhases.length,
            ratio = 1 - this.warp_frames / this.max_warp_frames
        this.frameName = this.warpPhases[parseInt(frameCnt * ratio)]
        this.warp_frames -= 1
        if (this.warp_frames <= 0) {
            this.pending_frames = 3600 // No re-appear
            this.deactivate()
        } else {
            return
        }
    } else if (this.pending_frames > 0) {
        if (this.pending_frames === vars.frames_per_sec / 2) {
            this.game.sounds.startlife.play()
        }
        this.pending_frames -= 1
        this.health = (this.max_health *
                (vars.death_time * vars.frames_per_sec - this.pending_frames) /
                (vars.death_time * vars.frames_per_sec))
        if (this.pending_frames <= 0) {
            this.activate()
            this.find_spot()
            this.rotation = Math.random() * Math.PI * 2 - Math.PI
        } else {
            return
        }
    }

    if (this.thrust) {
        this.vx += Math.sin(this.rotation)*this.thrust
        this.vy -= Math.cos(this.rotation)*this.thrust
        // Smoke trails, don't overload frame rate
        // TODO: disable if AI training
        if (vars.graphics > 0) {
            // TODO: adjust smoke_rate based on current FPS and target FPS
            var rads = this.rotation
            if (this.thrust > 0) {
                rads = (rads + Math.PI)
            }
            for (var i = 0; i < this.smoke_rate; i++) {
                var x = (this.x + Math.sin(rads)*(this.Radius+10) +
                         Math.random()*14 - 7),
                    y = (this.y - Math.cos(rads)*(this.Radius+10) +
                         Math.random()*14 - 7),
                    vx = (this.vx + Math.sin(rads)*vars.smoke_speed +
                          Math.random()/3),
                    vy = (this.vy - Math.cos(rads)*vars.smoke_speed +
                          Math.random()/3)
                mass(this.game, Smoke, 'vapors', x, y, vx, vy)
            }
        }
    }

    if (this.turn) {
        this.rotation += this.turn*vars.rotation_step
    }

    Mass.prototype.update.call(this)

    // Keep other sprites in sync with the main one
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
        // switch animation
        this.animations.play('thrust')
    }
}

Ship.prototype.cmd_reverse = function() {
    if (!this.thrust) {
        this.thrust = vars.reverse_power
        // switch animation
        this.animations.play('reverse')
    }
}

Ship.prototype.cmd_thrust_off = function() {
    if (this.thrust) {
        this.thrust = 0
        // switch back to normal ship
        this.animations.stop()
        this.frameName = 'main'
    }
}

Ship.prototype.cmd_fire = function() {
    if (!this.fire_delay && !this.pending_frames) {
        var rads = this.rotation,
            dx = Math.sin(rads),
            dy = -Math.cos(rads),
            separation = this.Radius+Fire.prototype.Radius+5,
            vx = this.vx + dx*vars.fire_speed,
            vy = this.vy + dy*vars.fire_speed,
            x = this.x + dx*separation,
            y = this.y + dy*separation
        if (this.bullet > 0) {
            this.fire_delay = parseInt(vars.fire_delay_frames * 0.75)
            mass(this.game, SuperFire, 'high', x, y, vx * 1.2, vy * 1.2,
                     {owner: this})
        } else {
            this.fire_delay = vars.fire_delay_frames
            mass(this.game, Fire, 'high', x, y, vx, vy, {owner: this})
        }
        this.game.sounds.fire.play()
    }
}

Ship.prototype.explode = function(without_fire) {
    if (this.dead) { return }
    this.deactivate()

    this.game.sounds.explode.play()
    if (vars.graphics > 0) {
        // debris
        for (var D of [Debris1, Debris2, Debris3, Debris4,
                       DebrisBase, DebrisBubble, DebrisMotor]) {
            mass(this.game, D, 'low', this.x, this.y, this.vx, this.vy,
                 {mass: this.mass / 14})
        }
    }
    if (typeof without_fire === 'undefined' || !without_fire) {
        // explosion
        mass(this.game, Explosion, 'high', this.x, this.y, this.vx, this.vy,
             {mass: this.mass / 2})
    }
}

Ship.prototype.warp = function() {
    this.shield_sprite.visible = false
    this.shield_sprite.animations.stop()
    this.bullet_sprite.visible = false
    this.bullet_sprite.animations.stop()
    this.game.sounds.gameover.play()
    this.warp_frames = this.max_warp_frames
    this.animations.stop()
}

Ship.prototype.damage = function(damage) {
    this.shield -= damage
    if (this.shield < 0.0) {
        this.health += this.shield
        this.shield = 0.0
    }
    if (this.health <= 0.0) {
        this.player.deaths += 1
        this.pending_frames = vars.death_time * vars.frames_per_sec

        this.explode()
        return true // dead
    } else {
        return false // still alive
    }
}

Ship.prototype.hit_by = function(other_mass) {
    var dead = false, other_dead = false
    if (this.dead) { return }
    if (other_mass instanceof Fire) {
        var damage = ((other_mass.damage-10) *
                      other_mass.ticks_to_live/vars.fire_life + 10)
        dead = this.damage(other_mass.damage)
        if (dead && other_mass.owner !== this) {
            other_mass.owner.player.score += 1
            other_mass.owner.player.compliment = true
        }
    } else if (other_mass instanceof Debris) {
        this.damage(vars.debris_damage)
    } else if (other_mass instanceof Explosion) {
        if (!this.shield) {
            this.damage(vars.explosion_damage)
        }
    } else if (other_mass instanceof Ship) {
        var my_damage = other_mass.health + other_mass.shield,
            other_damage = this.health + this.shield
        dead = this.damage(my_damage)
        other_dead = other_mass.damage(other_damage)
        other_mass.player.insult = other_dead
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
        }
    }
    // Insult/compliment depending on outcome
    if (dead && !(other_mass instanceof Fire)) {
        this.player.insult = true
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
        pend    = groups.pend.children,
        solids  = low.concat(high),
        real    = vapors.concat(solids)

    // Make objects (Spikes, Asteroids, Bobble/powerups) appear
    for (var d of [[Spike,        vars.spike_rate],
                   [Asteroid,     vars.asteroid_rate],
                   [ShieldBobble, vars.shield_powerup_rate],
                   [BulletBobble, vars.bullet_powerup_rate]]) {

        if (Math.random() < d[1]) {
            mass(game, d[0], 'pend', 0, 0, 0, 0,
                 {dead: true, pending_frames: vars.frames_per_sec})
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
    for (var grp of [groups.vapors, groups.low, groups.high]) {
        for (var o of grp.children) {
            if (o.dead) {
                if (o instanceof Ship) {
                    grp.remove(o, false)
                    groups.pend.add(o)
                    continue
                }
                if (o instanceof Fire) {
                    if (o.dead_by_hit) {
                        game.sounds.pop.play()
                        mass(game, Pop, 'vapors', o.x, o.y, o.vx/5, o.vy/5)
                    } else {
                        mass(game, Pop, 'vapors', o.x, o.y, o.vx, o.vy)
                    }
                } else if (o instanceof Debris) {
                    if (o.dead_by_hit) {
                        game.sounds.pop.play()
                        mass(game, Pop, 'vapors', o.x, o.y, o.vx/5, o.vy/5)
                    }
                }
                // Recycle
                massPool[o.constructor.name].push(o)
                grp.remove(o, false)
            }
        }
    }
}
