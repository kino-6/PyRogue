import pygame

WINDOW_SIZE_H = 720
WINDOW_SIZE_W = 1280

GRID_SIZE = 20  # [px]
GAMEMAP_WIDTH = 48  # [size]
GAMEMAP_HEIGHT = 32  # [size]

GRID_MOVEMENT_SPEED = 1  # [grid]

FONT_DEFAULT = "CourierPrime-Regular.ttf"
FONT_SIZE = 26
LOG_FONT_SIZE = 20  # 20
LOG_WRAP_SIZE = 57

DRAW_LOG_SIZE = 3
DRAW_LOG_MARGIN = 20

# https://www.pygame.org/docs/ref/color_list.html
PYGAME_COLOR_WHITE = (255, 255, 255)
PYGAME_COLOR_BLACK = (0, 0, 0)

PYGAME_FPS = 60
PYGAME_ONE_TURN_WAIT_MS = 30  # [ms]

PLAYER_STATUS = "player.yaml"
BASED_HIT_RATE = 90

a_z_KEY = [
    pygame.K_a,
    pygame.K_b,
    pygame.K_c,
    pygame.K_d,
    pygame.K_e,
    pygame.K_f,
    pygame.K_g,
    pygame.K_h,
    pygame.K_i,
    pygame.K_j,
    pygame.K_k,
    pygame.K_l,
    pygame.K_m,
    pygame.K_n,
    pygame.K_o,
    pygame.K_p,
    pygame.K_q,
    pygame.K_r,
    pygame.K_s,
    pygame.K_t,
    pygame.K_u,
    pygame.K_v,
    pygame.K_w,
    pygame.K_x,
    pygame.K_y,
    pygame.K_z,
]

# game balance
MAXROOMS = 9
MAX_GOLDS = 4
MAXTHINGS = 9
MAXOBJ = 9
MAXPACK = 23
INVENTORY_MAX = 26
MAXTRAPS = 10
AMULETLEVEL = 26
NUMTHINGS = 7  # number of types of things
MAXPASS = 13  # upper limit on number of passages
NUMLINES = 24
NUMCOLS = 80
STATLINE = NUMLINES - 1
BORE_LEVEL = 50

HEALTIME = 30
HUHDURATION = 20
SEEDURATION = 850

# food
EACH_TURN_STARVE = 1
HUNGERTIME = 1300
FOOD_TUNE_VALUE = 200
FOOD_RAND_MAX = 400
STOMACHSIZE = 2000
STARVETIME = 850

MORETIME = 150

RECOVERY_AMOUNT_CONF = 32  # max_hp / this
RECOVERY_INTERVAL = 10
