# ASTEROIDE MULTIPLAYER v2.0
# This file coordinates world state, spawning, collisions, scoring, and progression for 2 players.

import math
from random import uniform

import pygame as pg

import config as C
from sprites import (
    Asteroid, BossBullet, PowerAsteroid, Ship, UFO, BlackHole, ClockItem, LifeItem
)
from utils import Vec, rand_edge_pos, rand_unit_vec


class World:
    def __init__(self):
        # Initialize ships based on multiplayer setting
        if C.MULTIPLAYER_ENABLED:
            self.ship1 = Ship(Vec(C.WIDTH / 3, C.HEIGHT / 2), player_id=1)
            self.ship2 = Ship(Vec(2 * C.WIDTH / 3, C.HEIGHT / 2), player_id=2)
            self.ships = [self.ship1, self.ship2]
            self.ship = self.ship1  # Default for compatibility
        else:
            self.ship1 = Ship(Vec(C.WIDTH / 2, C.HEIGHT / 2), player_id=1)
            self.ship = self.ship1
            self.ships = [self.ship1]
            self.ship2 = None
        
        self.bullets = pg.sprite.Group()
        self.ufo_bullets = pg.sprite.Group()
        self.asteroids = pg.sprite.Group()
        self.ufos = pg.sprite.Group()
        self.black_hole = None
        self.bh_timer = uniform(C.BH_TIMER_MIN, C.BH_TIMER_MAX)
        self.bh_duration = 0
        self.all_sprites = pg.sprite.Group(*self.ships)
        self.score = 0
        self.lives = C.START_LIVES
        self.wave = 0
        self.wave_cool = C.WAVE_DELAY
        self.safe = C.SAFE_SPAWN_TIME
        self.safe2 = C.SAFE_SPAWN_TIME  # For player 2
        self.ufo_timer = C.UFO_SPAWN_EVERY
        self.game_over = False  
        self.boss_defeated_timer = 0.0
        self.power_asteroids = pg.sprite.Group()
        self.spread_boss_timer = C.SPREAD_BOSS_INTERVAL
        self.clock_items = pg.sprite.Group()
        self.life_items = pg.sprite.Group()
        self.freeze_timer = 0.0

    def start_wave(self):
        self.wave += 1
        count = 3 + self.wave
        for _ in range(count):
            pos = rand_edge_pos()
            # Avoid spawning near any ship
            for ship in self.ships:
                while (pos - ship.pos).length() < 150:
                    pos = rand_edge_pos()
            ang = uniform(0, math.tau)
            speed = uniform(C.AST_VEL_MIN, C.AST_VEL_MAX)
            vel = Vec(math.cos(ang), math.sin(ang)) * speed
            self.spawn_asteroid(pos, vel, "L")

        if uniform(0, 1) < C.SPREAD_ASTEROID_CHANCE:
            self.spawn_power_asteroid()

    def spawn_asteroid(self, pos: Vec, vel: Vec, size: str):
        a = Asteroid(pos, vel, size)
        a.frozen = self.freeze_timer > 0
        self.asteroids.add(a)
        self.all_sprites.add(a)

    def spawn_power_asteroid(self):
        pos = rand_edge_pos()
        for ship in self.ships:
            while (pos - ship.pos).length() < 150:
                pos = rand_edge_pos()
        ang = uniform(0, math.tau)
        speed = uniform(C.AST_VEL_MIN, C.AST_VEL_MAX)
        vel = Vec(math.cos(ang), math.sin(ang)) * speed
        pa = PowerAsteroid(pos, vel)
        pa.frozen = self.freeze_timer > 0
        self.power_asteroids.add(pa)
        self.asteroids.add(pa)
        self.all_sprites.add(pa)

    def spawn_ufo(self):
        if self.ufos:
            return
        small = uniform(0, 1) < 0.5
        y = uniform(0, C.HEIGHT)
        x = 0 if uniform(0, 1) < 0.5 else C.WIDTH
        ufo = UFO(Vec(x, y), small)
        ufo.dir.xy = (1, 0) if x == 0 else (-1, 0)
        self.ufos.add(ufo)
        self.all_sprites.add(ufo)

    def ufo_try_fire(self):
        for ufo in self.ufos:
            # Fire at closest ship
            target = self.ships[0] if self.ship2 is None else \
                     (self.ship1 if (self.ship1.pos - ufo.pos).length() < (self.ship2.pos - ufo.pos).length() else self.ship2)
            bullet = ufo.fire_at(target.pos)
            if bullet:
                self.ufo_bullets.add(bullet)
                self.all_sprites.add(bullet)

    def spawn_black_hole(self):
        pos = Vec(uniform(0, C.WIDTH), uniform(0, C.HEIGHT))
        for ship in self.ships:
            while (pos - ship.pos).length() < 200:
                pos = Vec(uniform(0, C.WIDTH), uniform(0, C.HEIGHT))
        bh = BlackHole(pos)
        self.black_hole = bh
        self.all_sprites.add(bh)
        self.bh_duration = uniform(C.BH_DURATION_MIN, C.BH_DURATION_MAX)

    def try_fire(self):
        if len(self.bullets) >= C.MAX_BULLETS:
            return
        b = self.ship1.fire()
        if b:
            self.bullets.add(b)
            self.all_sprites.add(b)

    def try_spread(self):
        result = self.ship1.spread_fire()
        if result is None:
            return
        for b in result:
            self.bullets.add(b)
            self.all_sprites.add(b)

    def hyperspace(self):
        self.ship1.hyperspace()
        self.score = max(0, self.score - C.HYPERSPACE_COST)

    def try_shield(self):
        self.ship1.activate_shield()

    def try_fire_p2(self):
        if self.ship2 is None:
            return
        if len(self.bullets) >= C.MAX_BULLETS:
            return
        b = self.ship2.fire()
        if b:
            self.bullets.add(b)
            self.all_sprites.add(b)

    def try_spread_p2(self):
        if self.ship2 is None:
            return
        result = self.ship2.spread_fire()
        if result is None:
            return
        for b in result:
            self.bullets.add(b)
            self.all_sprites.add(b)

    def hyperspace_p2(self):
        if self.ship2 is None:
            return
        self.ship2.hyperspace()
        self.score = max(0, self.score - C.HYPERSPACE_COST)

    def try_shield_p2(self):
        if self.ship2 is None:
            return
        self.ship2.activate_shield()

    def update(self, dt: float, keys=None, joystick=None, keys_p2=None, joystick2=None):
        # Update the world simulation, timers, enemy behavior, and progression.
        if self.freeze_timer > 0:
            self.freeze_timer -= dt
            if self.freeze_timer <= 0:
                self.freeze_timer = 0
                for a in self.asteroids:
                    a.frozen = False

        # Control both ships
        self.ship1.control(keys, dt, joystick if joystick else None)
        if self.ship2:
            self._control_p2(keys_p2, dt, joystick2 if joystick2 else None)
        
        self.all_sprites.update(dt)

        # Black hole update
        if self.black_hole:
            self.bh_duration -= dt
            if self.bh_duration <= 0:
                self.black_hole.kill()
                self.black_hole = None
                self.bh_timer = uniform(10, 20)
        else:
            self.bh_timer -= dt
            if self.bh_timer <= 0:
                self.spawn_black_hole()

        # Black hole gravity on both ships
        if self.black_hole:
            for ship in self.ships:
                dir_vec = self.black_hole.pos - ship.pos
                dist = dir_vec.length()
                if dist > 0:
                    dir_vec = dir_vec.normalize()
                    force = self.black_hole.strength / (dist + 1)
                    ship.vel += dir_vec * force * dt * 50

        # Safe spawn timers
        if self.safe > 0:
            self.safe -= dt
            self.ship1.invuln = 0.5
        if self.ship2 and self.safe2 > 0:
            self.safe2 -= dt
            self.ship2.invuln = 0.5

        # UFO spawning and firing
        if self.ufos:
            self.ufo_try_fire()
        else:
            self.ufo_timer -= dt
        if not self.ufos and self.ufo_timer <= 0:
            self.spawn_ufo()
            self.ufo_timer = C.UFO_SPAWN_EVERY

        self.handle_collisions()

        if self.boss_defeated_timer > 0:
            self.boss_defeated_timer -= dt
            if self.boss_defeated_timer <= 0:
                self.start_wave()
            return

        if self.freeze_timer <= 0:
            if not self.asteroids and self.wave_cool <= 0:
                self.start_wave()
                self.wave_cool = C.WAVE_DELAY
            elif not self.asteroids:
                self.wave_cool -= dt

    def _control_p2(self, keys=None, dt: float = 0.0, joystick=None):
        """Control player 2 ship with WASD + special keys"""
        left = False
        right = False
        up = False

        if keys is not None:
            left = keys[C.P2_LEFT]
            right = keys[C.P2_RIGHT]
            up = keys[C.P2_UP]
        
        if joystick:
            axis_x = joystick.get_axis(C.JOYSTICK_LEFT_RIGHT)
            if axis_x < -(C.JOYSTICK_ANALOG_DRIFT):
                left = True
            if axis_x > C.JOYSTICK_ANALOG_DRIFT:
                right = True
            if joystick.get_button(C.JOYSTICK_UP):
                up = True
        
        # Apply movement
        if left:
            self.ship2.angle -= C.SHIP_TURN_SPEED * dt
        if right:
            self.ship2.angle += C.SHIP_TURN_SPEED * dt
        if up:
            self.ship2.vel += Vec(math.cos(math.radians(self.ship2.angle)), 
                                   math.sin(math.radians(self.ship2.angle))) * C.SHIP_THRUST * dt
        self.ship2.vel *= C.SHIP_FRICTION

    def handle_collisions(self):
        # Asteroids hit by bullets
        hits = pg.sprite.groupcollide(
            self.asteroids,
            self.bullets,
            False,
            True,
            collided=lambda a, b: (a.pos - b.pos).length() < a.r,
        )
        for ast, _ in hits.items():
            if isinstance(ast, PowerAsteroid):
                self.score += C.AST_SIZES[ast.size]["score"]
                life = LifeItem(Vec(ast.pos))
                self.life_items.add(life)
                self.all_sprites.add(life)
                ast.kill()
            else:
                self.split_asteroid(ast)

        # Asteroids hit by UFO bullets
        ufo_hits = pg.sprite.groupcollide(
            self.asteroids,
            self.ufo_bullets,
            False,
            True,
            collided=lambda a, b: (a.pos - b.pos).length() < a.r,
        )
        for ast, _ in ufo_hits.items():
            self.split_asteroid(ast)

        # Clock items (freeze)
        for item in list(self.clock_items):
            for ship in self.ships:
                if (item.pos - ship.pos).length() < (item.r + ship.r):
                    item.kill()
                    self.freeze_timer = C.FREEZE_DURATION
                    for a in self.asteroids:
                        a.frozen = True
                    break

        # Life items
        for item in list(self.life_items):
            for ship in self.ships:
                if (item.pos - ship.pos).length() < (item.r + ship.r):
                    item.kill()
                    self.lives += 1
                    break

        # Ship collisions with asteroids and UFOs
        for ship in self.ships:
            safe_timer = self.safe if ship == self.ship1 else self.safe2
            if ship.invuln <= 0 and safe_timer <= 0 and not ship.shield_active:
                # Check asteroid collision
                for ast in self.asteroids:
                    if (ast.pos - ship.pos).length() < (ast.r + ship.r):
                        self.ship_die(ship)
                        break
                
                # Check UFO collision
                for ufo in self.ufos:
                    if (ufo.pos - ship.pos).length() < (ufo.r + ship.r):
                        self.ship_die(ship)
                        break
                
                # Check UFO bullet collision
                for bullet in self.ufo_bullets:
                    if (bullet.pos - ship.pos).length() < (bullet.r + ship.r):
                        bullet.kill()
                        self.ship_die(ship)
                        break

        # UFO vs bullets
        for ufo in list(self.ufos):
            for b in list(self.bullets):
                if (ufo.pos - b.pos).length() < (ufo.r + b.r):
                    score = (C.UFO_SMALL["score"] if ufo.small else C.UFO_BIG["score"])
                    self.score += score
                    ufo.kill()
                    b.kill()

        # Black hole collision
        if self.black_hole:
            for ship in self.ships:
                dist = (self.black_hole.pos - ship.pos).length()
                if dist < self.black_hole.r + ship.r:
                    self.lives = 0
                    self.game_over = True
                    return

    def split_asteroid(self, ast: Asteroid):
        self.score += C.AST_SIZES[ast.size]["score"]
        split = C.AST_SIZES[ast.size]["split"]
        pos = Vec(ast.pos)

        if not isinstance(ast, PowerAsteroid) and uniform(0, 1) < C.FREEZE_ITEM_CHANCE:
            item = ClockItem(pos)
            self.clock_items.add(item)
            self.all_sprites.add(item)

        ast.kill()
        for s in split:
            dirv = rand_unit_vec()
            speed = uniform(C.AST_VEL_MIN, C.AST_VEL_MAX) * 1.2
            self.spawn_asteroid(pos, dirv * speed, s)

    def ship_die(self, ship: Ship = None):
        if ship is None:
            ship = self.ship1
        
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
            return
        
        # Reset the dead ship
        ship.pos.xy = (C.WIDTH / 3 if ship == self.ship1 else 2 * C.WIDTH / 3, C.HEIGHT / 2)
        ship.vel.xy = (0, 0)
        ship.angle = -90
        ship.invuln = C.SAFE_SPAWN_TIME
        
        # Update safe timer
        if ship == self.ship1:
            self.safe = C.SAFE_SPAWN_TIME
        else:
            self.safe2 = C.SAFE_SPAWN_TIME

    def draw(self, surf: pg.Surface, font: pg.font.Font):
        for spr in self.all_sprites:
            spr.draw(surf)

        pg.draw.line(surf, (60, 60, 60), (0, 50), (C.WIDTH, 50), width=1)
        
        # Shared score and lives
        txt = f"SCORE {self.score:06d}   LIVES {self.lives}   WAVE {self.wave}"
        label = font.render(txt, True, C.WHITE)
        surf.blit(label, (10, 10))

        # Player 1 status
        if self.ship1.spread_cool > 0:
            sl = font.render(f"P1 SPREAD {self.ship1.spread_cool:.1f}s", True, C.GRAY)
        else:
            sl = font.render("P1 SPREAD OK", True, C.SPREAD_COLOR)
        surf.blit(sl, (C.WIDTH - 230, 10))

        if self.ship1.shield_active:
            sh = font.render(f"P1 SHIELD {self.ship1.shield_timer:.1f}s", True, C.SHIELD_COLOR)
            surf.blit(sh, (C.WIDTH - 230, 30))
        elif self.ship1.shield_cooldown > 0:
            sh = font.render(f"P1 SHIELD CD {self.ship1.shield_cooldown:.0f}s", True, C.GRAY)
            surf.blit(sh, (C.WIDTH - 260, 30))
        else:
            sh = font.render("P1 SHIELD OK", True, C.SHIELD_COLOR)
            surf.blit(sh, (C.WIDTH - 230, 30))

        # Player 2 status
        if self.ship2:
            if self.ship2.spread_cool > 0:
                sl2 = font.render(f"P2 SPREAD {self.ship2.spread_cool:.1f}s", True, C.GRAY)
            else:
                sl2 = font.render("P2 SPREAD OK", True, C.SPREAD_COLOR)
            surf.blit(sl2, (10, 30))

            if self.ship2.shield_active:
                sh2 = font.render(f"P2 SHIELD {self.ship2.shield_timer:.1f}s", True, C.SHIELD_COLOR)
                surf.blit(sh2, (10, 50))
            elif self.ship2.shield_cooldown > 0:
                sh2 = font.render(f"P2 SHIELD CD {self.ship2.shield_cooldown:.0f}s", True, C.GRAY)
                surf.blit(sh2, (10, 50))
            else:
                sh2 = font.render("P2 SHIELD OK", True, C.SHIELD_COLOR)
                surf.blit(sh2, (10, 50))

        if self.freeze_timer > 0:
            fl = font.render(f"FREEZE: {self.freeze_timer:.1f}s", True, C.ICY_BLUE)
            surf.blit(fl, (C.WIDTH // 2 - fl.get_width() // 2, 10))
