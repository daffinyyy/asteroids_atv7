
# MULTIPLAYER CONFIGURATION
MULTIPLAYER_ENABLED = True
PLAYER1_COLOR = (0, 255, 100)      # Verde
PLAYER2_COLOR = (255, 100, 200)    # Rosa/Magenta

# Player 1 Keyboard Controls (Setas)
# P1_UP, P1_DOWN, P1_LEFT, P1_RIGHT já são as setas
# P1_FIRE = SPACE, P1_SHIELD = S, P1_HYPERSPACE = LSHIFT, P1_SPREAD = RSHIFT (já configurado)

# Player 2 Keyboard Controls (WASD)
P2_UP = 119          # W
P2_DOWN = 115        # S
P2_LEFT = 97         # A
P2_RIGHT = 100       # D
P2_FIRE = 120        # X
P2_SHIELD = 99       # C
P2_HYPERSPACE = 122  # Z
P2_SPREAD = 118      # V

# Joystick Configuration
JOYSTICK_PLAYER1 = 0  # First joystick for P1
JOYSTICK_PLAYER2 = 1  # Second joystick for P2
# ASTEROIDE SINGLEPLAYER v1.0
# This file stores the gameplay, rendering, and balancing constants.

WIDTH = 960
HEIGHT = 720
FPS = 60

START_LIVES = 3
SAFE_SPAWN_TIME = 2.0
WAVE_DELAY = 2.0

SHIP_RADIUS = 15
SHIP_TURN_SPEED = 220.0
SHIP_THRUST = 220.0
SHIP_FRICTION = 0.995
SHIP_FIRE_RATE = 0.2
SHIP_BULLET_SPEED = 420.0
HYPERSPACE_COST = 250

# habilidade de tiro espalhado (shift direito)
SPREAD_COOLDOWN = 15.0


AST_VEL_MIN = 30.0
AST_VEL_MAX = 90.0
AST_SIZES = {
    "L": {"r": 46, "score": 20, "split": ["M", "M"]},
    "M": {"r": 24, "score": 50, "split": ["S", "S"]},
    "S": {"r": 12, "score": 100, "split": []},
}

BULLET_RADIUS = 2
BULLET_TTL = 1.0
MAX_BULLETS = 4

UFO_SPAWN_EVERY = 15.0
UFO_SPEED = 80.0
UFO_FIRE_EVERY = 1.2
UFO_BULLET_SPEED = 260.0
UFO_BULLET_TTL = 1.8
UFO_BIG = {"r": 18, "score": 200, "aim": 0.2}
UFO_SMALL = {"r": 12, "score": 1000, "aim": 0.6}

#implementação do parasita
PARASITE_SCORE = 75
PARASITE_SPEED = 50
PARASITE_RADIUS = 10
PARASITE_TIMER_MIN = 8
PARASITE_TIMER_MAX = 15

BLACK_HOLE_RADIUS = 18
BLACK_HOLE_VISUAL_RADIUS = 28
BLACK_HOLE_STRENGTH = 450
BH_TIMER_MIN = 15
BH_TIMER_MAX = 20
BH_DURATION_MIN = 5
BH_DURATION_MAX = 10

WHITE = (240, 240, 240)
GRAY = (120, 120, 120)
BLACK = (0, 0, 0)
PURPLE = (40, 0, 80)
VIOLET = (120, 120, 255)
GREEN = (0, 255, 100)
DARKER_GREEN = (0, 200, 100)

RANDOM_SEED = None

# Duração do fade-in da tela de game over (segundos)
GAME_OVER_FADE_DURATION = 1.5


BOSS_BULLET_RADIUS = 5
BOSS_BULLET_TTL = 7


BOSS_BULLET_COLOR = (255, 60, 60)

SPREAD_BULLET_COUNT = 8
SPREAD_ASTEROID_CHANCE = 0.15
SPREAD_COLOR = (255, 200, 50)
SPREAD_GLOW = (255, 160, 0)
SPREAD_BOSS_INTERVAL = 20.0

# power-up de vida extra (drop do asteroide especial)
LIFE_ITEM_RADIUS = 12
LIFE_ITEM_TTL = 15.0
LIFE_COLOR = (255, 80, 120)

FREEZE_DURATION = 10.0

#Configs do Shield 
SHIELD_DURATION = 2.5
SHIELD_COOLDOWN = 40.0
SHIELD_COLOR = (80, 160, 255)
SHIELD_RADIUS_OFFSET = 10  
FREEZE_ITEM_CHANCE = 0.08
CLOCK_COLOR = (100, 200, 255)
CLOCK_RADIUS = 10
ICY_BLUE = (150, 220, 255)

#controle joystick
JOYSTICK_UP = 0 #botao A
JOYSTICK_LEFT_RIGHT = 0 #left analog
JOYSTICK_ANALOG_DRIFT = 0.3
JOYSTICK_FIRE = 5 #RT
JOYSTICK_SHIELD = 1 #botao B
JOYSTICK_HYPERSPACE = 2 #botao X
JOYSTICK_SPREAD = 4 #LT
JOYSTICK_EXIT = 7 #+

# Power-up de tiro rápido
RAPID_FIRE_DURATION = 7.0
RAPID_FIRE_COOLDOWN = 0.06        # Fire rate durante o power-up (era 0.2)
RAPID_FIRE_ITEM_RADIUS = 10
RAPID_FIRE_ITEM_TTL = 12.0
RAPID_FIRE_COLOR = (255, 220, 50)  # Amarelo dourado
RAPID_FIRE_CHANCE = 0.12           # Chance de dropar ao quebrar asteroide
