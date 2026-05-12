# ASTEROIDE SINGLEPLAYER v1.0
# This file manages the application loop, scenes, input handling, and screen drawing.

import random
import sys
from dataclasses import dataclass

import pygame as pg

import config as C
from systems import World
from utils import text


@dataclass
class Scene:
    name: str


class Game:
    # Initialize pygame, shared UI resources, and the initial scene state.
    def __init__(self):
        pg.init()

        # Joysticks: P1 usa o primeiro, P2 usa o segundo (se existir).
        pg.joystick.init()
        self.joystick = None
        self.joystick2 = None
        self.joystick_id = None
        self.joystick2_id = None
        self.joystick_index = None
        self.joystick2_index = None
        self.keyboard_player = 1
        if pg.joystick.get_count() > 0:
            self.joystick = pg.joystick.Joystick(0)
            self.joystick.init()
            self.joystick_id = self.joystick.get_instance_id()
            self.joystick_index = self.joystick.get_id()
            print(f"Controle P1 conectado: {self.joystick.get_name()}")
        if C.MULTIPLAYER_ENABLED and pg.joystick.get_count() > 1:
            self.joystick2 = pg.joystick.Joystick(1)
            self.joystick2.init()
            self.joystick2_id = self.joystick2.get_instance_id()
            self.joystick2_index = self.joystick2.get_id()
            print(f"Controle P2 conectado: {self.joystick2.get_name()}")

        # Modos aceitos no multiplayer:
        # 1) 1 teclado + 1 controle
        # 2) 2 controles
        if C.MULTIPLAYER_ENABLED:
            joy_count = pg.joystick.get_count()
            if joy_count >= 2:
                # Dois controles: desabilita jogador no teclado.
                self.keyboard_player = 0
            elif joy_count == 1:
                # Teclado fica com P1, único controle vai para P2.
                self.keyboard_player = 1
                self.joystick2 = self.joystick
                self.joystick2_id = self.joystick_id
                self.joystick2_index = self.joystick_index
                self.joystick = None
                self.joystick_id = None
                self.joystick_index = None
            else:
                # Sem controle: mantém apenas P1 no teclado.
                self.keyboard_player = 1

        if C.RANDOM_SEED is not None:
            random.seed(C.RANDOM_SEED)
        self.screen = pg.display.set_mode((C.WIDTH, C.HEIGHT))
        pg.display.set_caption("Asteroides")
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont("consolas", 20)
        self.big = pg.font.SysFont("consolas", 48)
        self.scene = Scene("menu")
        self.world = World()
        self.final_score = 0    # Pontuação capturada no momento do game over
        self.go_fade = 0.0      # Temporizador de fade-in da tela de game over

    def run(self):
        
        while True:
            dt = self.clock.tick(C.FPS) / 1000.0
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    pg.quit()
                    sys.exit(0)

                #keyboard controllers
                if e.type == pg.KEYDOWN:
                    # ESC: encerra o jogo nas cenas menu/play; volta ao menu no game over
                    if e.key == pg.K_ESCAPE:
                        if self.scene.name == "game_over":
                            self.scene = Scene("menu")
                        else:
                            pg.quit()
                            sys.exit(0)
                    elif self.scene.name == "menu":
                        self.world = World()
                        self.scene = Scene("play")
                    elif self.scene.name == "game_over":
                        self.world = World()
                        self.go_fade = 0.0
                        self.scene = Scene("play")
                    elif self.scene.name == "play" and self.keyboard_player == 1:
                        # Apenas um jogador no teclado (P1)
                        if e.key == pg.K_SPACE:
                            self.world.try_fire()
                        if e.key == pg.K_LSHIFT:
                            self.world.hyperspace()
                        if e.key == pg.K_s:
                            self.world.try_shield()
                        if e.key == pg.K_RSHIFT:
                            self.world.try_spread()

                #joystick controllers
                if e.type == pg.JOYBUTTONDOWN:
                    if self.scene.name == "play":
                        event_joy = getattr(
                            e,
                            "instance_id",
                            getattr(e, "joy", getattr(e, "device", None)),
                        )
                        if self.joystick_id is not None and event_joy in (self.joystick_id, self.joystick_index):
                            if e.button == C.JOYSTICK_SHIELD:
                                self.world.try_shield()
                            elif e.button == C.JOYSTICK_HYPERSPACE:
                                self.world.hyperspace()
                            elif e.button == C.JOYSTICK_EXIT:
                                pg.quit()
                                sys.exit(0)
                        elif self.joystick2_id is not None and event_joy in (self.joystick2_id, self.joystick2_index):
                            if e.button == C.JOYSTICK_SHIELD:
                                self.world.try_shield_p2()
                            elif e.button == C.JOYSTICK_HYPERSPACE:
                                self.world.hyperspace_p2()

                if e.type == pg.JOYAXISMOTION:
                    if self.scene.name == "play":
                        event_joy = getattr(
                            e,
                            "instance_id",
                            getattr(e, "joy", getattr(e, "device", None)),
                        )
                        if self.joystick_id is not None and event_joy in (self.joystick_id, self.joystick_index):
                            if e.axis == C.JOYSTICK_FIRE and e.value > C.JOYSTICK_ANALOG_DRIFT:
                                self.world.try_fire()
                            elif e.axis == C.JOYSTICK_SPREAD and e.value > C.JOYSTICK_ANALOG_DRIFT:
                                self.world.try_spread()
                        elif self.joystick2_id is not None and event_joy in (self.joystick2_id, self.joystick2_index):
                            if e.axis == C.JOYSTICK_FIRE and e.value > C.JOYSTICK_ANALOG_DRIFT:
                                self.world.try_fire_p2()
                            elif e.axis == C.JOYSTICK_SPREAD and e.value > C.JOYSTICK_ANALOG_DRIFT:
                                self.world.try_spread_p2()
      
      
                    

            keys = pg.key.get_pressed()
            self.screen.fill(C.BLACK)

            if self.scene.name == "menu":
                self.draw_menu()
            elif self.scene.name == "play":
                keys_p1 = keys if self.keyboard_player == 1 else None
                self.world.update(dt, keys_p1, self.joystick, None, self.joystick2)
                self.world.draw(self.screen, self.font)
                # Verifica se o mundo sinalizou fim de jogo
                if self.world.game_over:
                    self.final_score = self.world.score
                    self.go_fade = 0.0
                    self.scene = Scene("game_over")
            elif self.scene.name == "game_over":
                self.go_fade += dt
                self.draw_game_over()

            pg.display.flip()

    def draw_game_over(self):
        # Exibe a tela de game over com fade-in, pontuação final e instruções.
        alpha = min(255, int(255 * self.go_fade / C.GAME_OVER_FADE_DURATION))

        overlay = pg.Surface((C.WIDTH, C.HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        self.screen.blit(overlay, (0, 0))

        if alpha < 60:
            return

        text(self.screen, self.big, "GAME OVER",
             C.WIDTH // 2 - 130, C.HEIGHT // 2 - 100)
        text(self.screen, self.font,
             f"Pontuacao final: {self.final_score:06d}",
             C.WIDTH // 2 - 110, C.HEIGHT // 2 - 20)
        text(self.screen, self.font,
             "Enter / Espaco: jogar novamente",
             C.WIDTH // 2 - 150, C.HEIGHT // 2 + 40)
        text(self.screen, self.font,
             "ESC: menu principal",
             C.WIDTH // 2 - 90, C.HEIGHT // 2 + 80)

    def draw_menu(self):
        text(self.screen, self.big, "ASTEROIDS",
             C.WIDTH // 2 - 150, 120)
        if C.MULTIPLAYER_ENABLED:
            text(self.screen, self.font,
                 "P1 TECLADO: Setas  Space tiro  LShift hiper  S shield  RShift spread",
                 50, 270)
            text(self.screen, self.font,
                 "CONTROLE: Analogico virar  A acelerar  RT tiro  LT spread  B shield  X hiper",
                 50, 310)
            if self.keyboard_player == 0:
                mode_txt = "Modo atual: 2 controles"
            elif self.joystick2 is not None:
                mode_txt = "Modo atual: teclado + 1 controle"
            else:
                mode_txt = "Modo atual: apenas teclado (conecte controle para P2)"
            text(self.screen, self.font,
                 mode_txt,
                 260, 360)
            text(self.screen, self.font,
                 "Pressione qualquer tecla para iniciar", 240, 420)
        else:
            text(self.screen, self.font,
                 "Setas: virar/acelerar  Espaco: tiro  LShift: hiper  S: shield",
                 120, 300)
            text(self.screen, self.font,
                 "RShift: tiro espalhado (15s cooldown)",
                 230, 330)
            text(self.screen, self.font,
                 "Pressione qualquer tecla...", 260, 390)
