"use strict";

// AI data structure constants
var types = ['none', 'significant', 'hard', 'damage', 'ship', 'sun',
         'fire', 'spike', 'asteroid', 'shield', 'bullet', 'powerup']

var actions = ['none', 'fire', 'thrust', 'rthrust', 'left', 'right']

var comparisons = [
        'none',
        'rand_num',   // <rand> operator value
        'dist_dist',  // <dist * future1> operator <dist * future2 + value>
        'dist_num',   // <dist * future1> operator value
        'dir_dir',    // <dir * future1> operator <dir * future2 + value>
        'dir_num']    // <dir * future1> operator value

// future is index into futures array to get frames into the
// future for distance and direction
var futures = [  0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                10,11,12,13,14,15,16,17,18,19,
                20,22,24,26,28,30,32,34,36,38,
                40,45,50,55,60,65,70,75,80,85]

// Meaning of value is either raw or index into distances
// or directions array depending on setting of comparisons
var distances = [   0,  10,  12,  14,  16,
                   18,  20,  22,  24,  26,
                   28,  30,  35,  40,  45,
                   50,  55,  60,  65,  70,
                   75,  80,  90, 100, 110,
                  120, 140, 160, 180, 200,
                  220, 250, 300, 350, 400,
                  450, 500, 600, 700, 800]

var directions = []
for (var i = 0; i < 31; i++) { directions.push(i) }
for (var i = -29; i < 0; i++) { directions.push(i) }
//for (var i = 0; i < 21; i++) { directions.push(i) }
//for (var i = -19; i < 0; i++) { directions.push(i) }

// for distance, == means between previous and next
var operators = ['==', '>', '<']

/*
// Very approximate
function gauss(mean, stddev) {
    var u1, u2, w
    do {
        u1 = 2.0 * Math.random() - 1.0
        u2 = 2.0 * Math.random() - 1.0
        w  = u1 * u1 + u2 * u2
    } while (w >= 1.0)
    z0 = Math.sqrt((-2.0 * Math.log(w))/w)

    return (u1 * w) * stddev + mean
}


// Upper half of gauss distribution
function half_gauss(start, end) {
    var found = false,
        num = 0
    while (!found) {
        num = gauss(start, (end-start)/3.0)
        if (num >= start && num <= end) {
            found = true
        }
    }
    return num
}
*/

function _relativeDirection(obj1, obj2) {
    var rad = angleBetween(obj1, obj2) - obj1.rotation
    // Adjust for Phaser 0 radians being due east
    rad = rad + Math.PI/2
    if (rad > Math.PI) {
        return rad - Math.PI*2
    } else if (rad < -Math.PI) {
        return rad + Math.PI*2
    } else {
// -1.18
        return rad
    }
}

function test_base(base, ship, obj) {
    var right = vars.arena.right,
        bottom = vars.arena.bottom,
        sx = ship.x,
        sy = ship.y,
        svx = ship.vx / CONST_FPS,
        svy = ship.vy / CONST_FPS,
        ox = obj.x,
        oy = obj.y,
        ovx = obj.vx / CONST_FPS,
        ovy = obj.vy / CONST_FPS,
        f1 = futures[base.future1],
        f2 = futures[base.future2],
        t1 = {x: 0, y: 0, rotation: 0},
        t2 = {x: 0, y: 0, rotation: 0},
        dir1, dir2, dirIdx, dist1, dist2, distIdx
    
    switch (base.comparison) {
    case 'none':
        return true
    case 'rand_num':
        var rand = parseInt(Math.random() * CONST_FPS)
        if (((base.operator === "<")  && (rand < base.value)) ||
            ((base.operator === ">")  && (rand > base.value)) ||
            ((base.operator === "==") && (rand === base.value))) {
            return true
        }
        return false
    case 'dist_dist':
        t1.x = (sx + svx * f1) % right
        t1.y = (sy + svy * f1) % bottom
        t2.x = (ox + ovx * f1) % right
        t2.y = (oy + ovy * f1) % bottom
        dist1 = distanceBetween(t1, t2)
        t1.x = (sx + svx * f2) % right
        t1.y = (sy + svy * f2) % bottom
        t2.x = (ox + ovx * f2) % right
        t2.y = (oy + ovy * f2) % bottom
        distIdx = base.value
        if (base.value < 0) { distIdx += distances.length }
        dist2 = distanceBetween(t1, t2) + distances[distIdx]
        if ((base.operator === "<") && (dist1 < dist2)) { return true }
        if ((base.operator === ">") && (dist1 > dist2)) { return true }
        if (base.operator === "==") {
            if (Math.abs((dist1 - dist2)/((dist1+dist2)/2)) < 0.2) {
                return true
            }
        }
        return false
    case 'dist_num':
        t1.x = (sx + svx * f1) % right
        t1.y = (sy + svy * f1) % bottom
        t2.x = (ox + ovx * f1) % right
        t2.y = (oy + ovy * f1) % bottom
        dist1 = distanceBetween(t1, t2)
        distIdx = base.value
        if (base.value < 0) { distIdx += distances.length }
        dist2 = distances[distIdx]
        if ((base.operator === "<") && (dist1 < dist2)) { return true }
        if ((base.operator === ">") && (dist1 > dist2)) { return true }
        if (base.operator === "==") {
            if (Math.abs((dist1 - dist2)/((dist1+dist2)/2)) < 0.2) {
                return true
            }
        }
        return false
    case 'dir_dir':
        t1.x = (sx + svx * f1) % right
        t1.y = (sy + svy * f1) % bottom
        t1.rotation = ship.rotation
        t2.x = (ox + ovx * f1) % right
        t2.y = (oy + ovy * f1) % bottom
        // Flip sign to match python version
        dir1 = - _relativeDirection(t1, t2)
        t1.x = (sx + svx * f2) % right
        t1.y = (sy + svy * f2) % bottom
        t1.rotation = ship.rotation
        t2.x = (ox + ovx * f2) % right
        t2.y = (oy + ovy * f2) % bottom
        // Flip sign to match python version
        dir2 = - _relativeDirection(t1, t2)
        dirIdx = base.value
        if (base.value < 0) { dirIdx += directions.length }
        dir2 = dir2 + directions[dirIdx] * (Math.PI / (CONST_FPS / 2))
        if (dir2 > Math.PI) {
            dir2 -= 2*Math.PI
        } else if (dir2 < -Math.PI) {
            dir2 += 2*Math.PI
        }
        if ((base.operator === "<") && (dir1 < dir2)) { return true }
        if ((base.operator === ">") && (dir1 > dir2)) { return true }
        if (base.operator === "==") {
            if (Math.abs(dir1 - dir2) < Math.PI / (CONST_FPS / 2)) {
                return true
            }
        }
        return false
    case 'dir_num':
        t1.x = (sx + svx * f1) % right
        t1.y = (sy + svy * f1) % bottom
        t1.rotation = ship.rotation
        t2.x = (ox + ovx * f1) % right
        t2.y = (oy + ovy * f1) % bottom
        // Flip sign to match python version
        dir1 = - _relativeDirection(t1, t2)
        dirIdx = base.value
        if (dirIdx < 0) { dirIdx += directions.length }
        dir2 = directions[dirIdx] * (Math.PI / (CONST_FPS / 2))
        if ((base.operator === "<") && (dir1 < dir2)) { return true }
        if ((base.operator === ">") && (dir1 > dir2)) { return true }
        if (base.operator === "==") {
            if (Math.abs(dir1 - dir2) < Math.PI / (CONST_FPS/2)) {
                return true
            }
        }
        return false
    default:
        return false
    }
}

function test_gene(gene, ship, obj) {
    var match = false
    if (gene.type in obj.Taxonomy) {
        match = true
        for (var base of gene.bases) {
            if (!test_base(base, ship, obj)) {
                match = false
                break
            }
        }
    }
    return match
}

var null_gene = {type: 'significant',
                 bases: [{comparison: 'none',
                          future1:    0,
                          future2:    0,
                          value:      0,
                          operator:   "=="}],
                 actions: ['none']}
