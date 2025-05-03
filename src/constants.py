import pygame

WINDOW_SIZE_H = 720
WINDOW_SIZE_W = 1280

GRID_SIZE = 20  # [px]
GAMEMAP_WIDTH = 48  # [size]
GAMEMAP_HEIGHT = 28  # [size]

GRID_MOVEMENT_SPEED = 1  # [grid]

FONT_DEFAULT = "CourierPrime-Regular.ttf"
FONT_SIZE = 26
LOG_FONT_SIZE = 20  # 20
LOG_WRAP_SIZE = 57

DRAW_LOG_SIZE = 7
DRAW_LOG_MARGIN = 20

# https://www.pygame.org/docs/ref/color_list.html
PYGAME_COLOR_WHITE = (255, 255, 255)
PYGAME_COLOR_BLACK = (0, 0, 0)
PYGAME_COLOR_RED = (255, 0, 0)

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

INITIAL_SPAWN_ENEMY_NUM = 8
RESPAWN_TURN = 4
RESPAWN_DICE_MIN, RESPAWN_DICE_MAX = 1, 6

BASE_EXP = 10
LEVEL_FACTOR = 1.2

HEALING_AMOUNT = 8
HEALING_REGENE = 2

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

# effects
POISON_DURATION = 15  # 毒の持続ターン数
POISON_DAMAGE_DIVISOR = 16  # 最大HPを割る数（1/16のダメージ）
SLEEP_DURATION = 5  # 睡眠の持続ターン数
STRENGTH_DURATION = 20  # 力の持続ターン数
INVISIBILITY_DURATION = 20  # 透明化の持続ターン数
REGENERATION_DURATION = 15  # 再生の持続ターン数
REGENERATION_HEAL_AMOUNT = 2  # 再生の回復量

# Border color thresholds
BORDER_HP_CRITICAL_THRESHOLD = 1/8  # HPが1/8以下の場合に赤枠
BORDER_HP_WARNING_THRESHOLD = 1/2    # HPが半分以下の場合に黄枠

# Border colors
BORDER_COLOR_NORMAL = PYGAME_COLOR_WHITE
BORDER_COLOR_WARNING = (255, 255, 0)  # 黄色
BORDER_COLOR_CRITICAL = PYGAME_COLOR_RED
