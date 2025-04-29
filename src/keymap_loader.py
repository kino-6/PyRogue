import yaml
import pygame

# キー名→pygameキーコード変換辞書
KEY_NAME_TO_CODE = {
    ".": pygame.K_PERIOD,
    ">": pygame.K_GREATER,
    "<": pygame.K_LESS,
    "KP_PERIOD": pygame.K_KP_PERIOD,  # テンキーのピリオド
    "e": pygame.K_e,
    "w": pygame.K_w,
    "W": (pygame.K_w, pygame.KMOD_SHIFT),
    "P": (pygame.K_p, pygame.KMOD_SHIFT),
    "i": pygame.K_i,
    "?": pygame.K_QUESTION,
    "h": pygame.K_h,
    "@": pygame.K_AT,
    "KP5": pygame.K_KP5,
    "SHIFT+2": (pygame.K_2, pygame.KMOD_SHIFT),
    "SHIFT+h": (pygame.K_h, pygame.KMOD_SHIFT),
    "F1": pygame.K_F1,
    "F2": pygame.K_F2,
}

def load_keymap(yaml_path):
    with open(yaml_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    keymap = config["keymap"]
    return keymap

def get_action_for_key(key, mod, keymap):
    for action, keys in keymap.items():
        for k in keys:
            code = KEY_NAME_TO_CODE.get(k)
            if code is None:
                continue  # 未定義キーはスキップ
            if isinstance(code, tuple):
                if key == code[0] and mod & code[1]:
                    return action
            else:
                if key == code:
                    return action
    return None

def get_keys_for_action(action, keymap):
    return keymap.get(action, [])
