from ursina import *
import random
import json
import os
from entities import Frog, Platform, Collectible

app = Ursina(size=(540, 960), title="Frog Hopper Adventure")

# Configure Camera
camera.orthographic = True
camera.fov = 15

# Assets mapping
assets_path = 'assets/'

def _to_unix_path(p):
    """Konversi Windows path ke Unix-style yang diterima Panda3D/Ursina."""
    p = p.replace('\\', '/')
    if len(p) >= 2 and p[1] == ':':          # misal "C:/..." → "/c/..."
        p = '/' + p[0].lower() + p[2:]
    return p

_font_bundled = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'fonts', 'comicbd.ttf')
_font_system  = 'C:/Windows/Fonts/comicbd.ttf'
if os.path.exists(_font_bundled):
    CUTE_FONT = _to_unix_path(_font_bundled)   # font dari assets/ (portable)
elif os.path.exists(_font_system):
    CUTE_FONT = _to_unix_path(_font_system)    # fallback: font sistem Windows
else:
    CUTE_FONT = 'default'

# Save file setup
SAVE_FILE = "save.json"
def load_save():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as f:
            return json.load(f)
    return {"best_score": 0, "coins": 1250}

def save_game(data):
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f)

save_data = load_save()

# Global Game State
game_state = "MENU"
score = 0
lives = 3
max_height = 0
platforms = []
collectibles = []
selected_char_idx = 0

characters = [
    {"name": "Green Frog", "idle": assets_path+"frog_idle.png", "jump": assets_path+"frog_jump.png"},
    {"name": "Red Frog", "idle": assets_path+"frog_red_idle.png", "jump": assets_path+"frog_red_jump.png"},
    {"name": "Blue Frog", "idle": assets_path+"frog_blue_idle.png", "jump": assets_path+"frog_blue_jump.png"}
]

def create_button_3d(parent, text, color_top, color_bottom, scale=(0.38, 0.07), y=0):
    btn = Button(
        parent=parent,
        text=f"<b>{text}</b>",
        color=color_top,
        highlight_color=color.tint(color_top, 0.1),
        pressed_color=color.tint(color_top, -0.1),
        scale=scale,
        y=y
    )
    btn.text_color = color.white
    if CUTE_FONT != 'default':
        btn.text_entity.font = CUTE_FONT
    btn.text_entity.shadow = True
    btn.text_entity.scale *= 1.45  # Make text larger and thicker
    
    # 3D Base Shadow
    btn.base = Entity(
        parent=btn,
        model='quad',
        texture='button_tint',
        color=color_bottom,
        scale=(1.0, 1.0),
        y=-0.12,  # Relative offset downwards
        z=0.01   # Behind the button
    )
    return btn

# --- UI Setup ---
menu_parent = Entity(parent=camera.ui)
game_ui_parent = Entity(parent=camera.ui, enabled=False)
char_select_parent = Entity(parent=camera.ui, enabled=False)
game_over_parent = Entity(parent=camera.ui, enabled=False)
help_parent = Entity(parent=camera.ui, enabled=False)

# Background for menu
menu_bg = Entity(parent=menu_parent, model='quad', texture=assets_path+'bg_menu.png', scale=(2, 2), z=1)
logo = Entity(parent=menu_parent, model='quad', texture=assets_path+'logo.png', scale=(0.32, 0.32), y=0.30)

# Menu Buttons
btn_play = create_button_3d(
    parent=menu_parent, 
    text='MULAI', 
    color_top=color.Color(0.26, 0.84, 0.48, 1.0), 
    color_bottom=color.Color(0.17, 0.65, 0.35, 1.0), 
    scale=(0.38, 0.07), 
    y=-0.02
)
btn_char = create_button_3d(
    parent=menu_parent, 
    text='KARAKTER', 
    color_top=color.Color(0.24, 0.65, 1.0, 1.0), 
    color_bottom=color.Color(0.11, 0.46, 0.80, 1.0), 
    scale=(0.38, 0.07), 
    y=-0.10
)
btn_help = create_button_3d(
    parent=menu_parent, 
    text='CARA BERMAIN', 
    color_top=color.Color(1.0, 0.67, 0.17, 1.0), 
    color_bottom=color.Color(0.80, 0.48, 0.08, 1.0), 
    scale=(0.38, 0.07), 
    y=-0.18
)
btn_exit = create_button_3d(
    parent=menu_parent, 
    text='KELUAR', 
    color_top=color.Color(1.0, 0.32, 0.32, 1.0), 
    color_bottom=color.Color(0.80, 0.20, 0.20, 1.0), 
    scale=(0.38, 0.07), 
    y=-0.26
)

# Stats Bar (Glassmorphic Transparent Design)
stats_bg = Entity(
    parent=menu_parent,
    model='quad',
    color=color.Color(0, 0, 0, 0.35),
    scale=(0.44, 0.070),
    y=0.08,
    z=0.01
)
# Satu teks terpusat agar otomatis pas di tengah stats bar
def get_stats_text():
    return f"<b>Coins: {save_data['coins']}   |   Best: {save_data['best_score']}</b>"

t_stats = Text(
    parent=menu_parent,
    text=get_stats_text(),
    x=0, y=0.08,
    origin=(0, 0),
    color=color.gold,
    scale=1.2,
    shadow=True
)
if CUTE_FONT != 'default':
    t_stats.font = CUTE_FONT

# Char Select UI
t_select = Text(parent=char_select_parent, text="<b>SELECT CHARACTER</b>", y=0.3, origin=(0,0), scale=2, shadow=True)
char_display = Entity(parent=char_select_parent, model='quad', texture=characters[0]['idle'], scale=(0.3, 0.3), y=0)
char_name_text = Text(parent=char_select_parent, text=f"<b>{characters[0]['name']}</b>", y=-0.2, origin=(0,0), scale=1.5, shadow=True)
if CUTE_FONT != 'default':
    t_select.font = CUTE_FONT
    char_name_text.font = CUTE_FONT

btn_prev = create_button_3d(parent=char_select_parent, text='PREV', color_top=color.Color(0.70, 0.75, 0.76, 1.0), color_bottom=color.Color(0.39, 0.43, 0.45, 1.0), scale=(0.15, 0.08), y=0)
btn_prev.x = -0.3
btn_next = create_button_3d(parent=char_select_parent, text='NEXT', color_top=color.Color(0.70, 0.75, 0.76, 1.0), color_bottom=color.Color(0.39, 0.43, 0.45, 1.0), scale=(0.15, 0.08), y=0)
btn_next.x = 0.3

btn_back = create_button_3d(
    parent=char_select_parent, 
    text='KEMBALI', 
    color_top=color.Color(0.70, 0.75, 0.76, 1.0), 
    color_bottom=color.Color(0.39, 0.43, 0.45, 1.0), 
    scale=(0.3, 0.08), 
    y=-0.4
)

# Help UI
t_help_title = Text(parent=help_parent, text="<b>CARA BERMAIN</b>", y=0.3, origin=(0,0), scale=2, color=color.orange, shadow=True)
t_help_info = Text(parent=help_parent, text="<b>Ketuk layar atau klik untuk melompat!\nHindari jatuh ke bawah.\nKumpulkan lalat dan hati untuk skor & nyawa.</b>", y=0, origin=(0,0), scale=1.1, shadow=True)
if CUTE_FONT != 'default':
    t_help_title.font = CUTE_FONT
    t_help_info.font = CUTE_FONT

btn_help_back = create_button_3d(
    parent=help_parent, 
    text='KEMBALI', 
    color_top=color.Color(0.70, 0.75, 0.76, 1.0), 
    color_bottom=color.Color(0.39, 0.43, 0.45, 1.0), 
    scale=(0.3, 0.08), 
    y=-0.3
)

# Game Over UI
go_title = Text(parent=game_over_parent, text="<b>GAME OVER</b>", color=color.red, y=0.2, origin=(0,0), scale=3, shadow=True)
go_score = Text(parent=game_over_parent, text="<b>Score: 0</b>", y=0, origin=(0,0), scale=2, shadow=True)
if CUTE_FONT != 'default':
    go_title.font = CUTE_FONT
    go_score.font = CUTE_FONT

btn_restart = create_button_3d(
    parent=game_over_parent, 
    text="RESTART", 
    color_top=color.Color(0.26, 0.84, 0.48, 1.0), 
    color_bottom=color.Color(0.17, 0.65, 0.35, 1.0), 
    scale=(0.4, 0.08), 
    y=-0.2
)
btn_menu = create_button_3d(
    parent=game_over_parent, 
    text="MAIN MENU", 
    color_top=color.Color(0.24, 0.65, 1.0, 1.0), 
    color_bottom=color.Color(0.11, 0.46, 0.80, 1.0), 
    scale=(0.4, 0.08), 
    y=-0.3
)

# HUD
hud_score = Text(parent=game_ui_parent, text="<b>Score: 0</b>", position=(-0.45, 0.45), scale=2, shadow=True)
hud_lives = Text(parent=game_ui_parent, text="<b>Lives: 3</b>", position=(0.3, 0.45), scale=2, shadow=True)
if CUTE_FONT != 'default':
    hud_score.font = CUTE_FONT
    hud_lives.font = CUTE_FONT

# --- Gameplay ---
frog = None
bg_entities = []

def generate_platform(y_pos, level):
    ptype = random.choice(['lily', 'log'])
    tex = assets_path + ('lily_pad.png' if ptype == 'lily' else 'log.png')
    x_pos = random.uniform(-3, 3)
    speed = random.uniform(2.0 + level * 0.5, 4.0 + level * 1.0)
    direction = random.choice([-1, 1])
    plat = Platform(tex=tex, speed=speed, direction=direction, x=x_pos, y=y_pos)
    platforms.append(plat)
    
    # 10% chance for collectible
    if random.random() < 0.1:
        ctype = 'heart' if random.random() < 0.2 else 'fly'
        ctex = assets_path + ('heart.png' if ctype == 'heart' else 'fly.png')
        coll = Collectible(tex=ctex, type_name=ctype, x=plat.x, y=plat.y + 1)
        collectibles.append(coll)

def start_game():
    global game_state, frog, score, lives, max_height, platforms, collectibles, bg_entities
    
    # Clear old entities
    if frog: destroy(frog)
    for p in platforms: destroy(p)
    for c in collectibles: destroy(c)
    for b in bg_entities: destroy(b)
    platforms.clear()
    collectibles.clear()
    bg_entities.clear()
    
    # Reset states
    score = 0
    lives = 3
    max_height = 0
    camera.y = 0
    
    # Setup Backgrounds
    for i in range(3):
        bg = Entity(model='quad', texture=assets_path+'water_background.png', scale=(15, 15), z=2, y=i*15)
        bg_entities.append(bg)
        
    # Initial platforms
    safe_plat = Platform(tex=assets_path+'lily_pad.png', speed=0, direction=1, x=0, y=-5)
    platforms.append(safe_plat)
    
    for i in range(1, 10):
        generate_platform(safe_plat.y + i * 3, 1)
        
    # Setup Frog
    char = characters[selected_char_idx]
    frog = Frog(idle_tex=char['idle'], jump_tex=char['jump'], x=0, y=-4)
    frog.on_platform = safe_plat
    
    menu_parent.enabled = False
    game_over_parent.enabled = False
    game_ui_parent.enabled = True
    game_state = "PLAYING"
    update_hud()

def game_over():
    global game_state
    game_state = "GAME_OVER"
    game_ui_parent.enabled = False
    game_over_parent.enabled = True
    go_score.text = f"<b>Final Score: {score}</b>"
    
    if score > save_data.get("best_score", 0):
        save_data["best_score"] = score
        save_game(save_data)

def update_hud():
    hud_score.text = f"<b>Score: {score}</b>"
    hud_lives.text = f"<b>Lives: {lives}</b>"

# Button Callbacks
def on_play(): start_game()
btn_play.on_click = on_play

def on_char():
    menu_parent.enabled = False
    char_select_parent.enabled = True
btn_char.on_click = on_char

def on_help():
    menu_parent.enabled = False
    help_parent.enabled = True
btn_help.on_click = on_help

def on_exit(): application.quit()
btn_exit.on_click = on_exit

def on_back():
    char_select_parent.enabled = False
    menu_parent.enabled = True
btn_back.on_click = on_back

def on_help_back():
    help_parent.enabled = False
    menu_parent.enabled = True
btn_help_back.on_click = on_help_back

def on_prev():
    global selected_char_idx
    selected_char_idx = (selected_char_idx - 1) % len(characters)
    update_char_display()
btn_prev.on_click = on_prev

def on_next():
    global selected_char_idx
    selected_char_idx = (selected_char_idx + 1) % len(characters)
    update_char_display()
btn_next.on_click = on_next

def update_char_display():
    char = characters[selected_char_idx]
    char_display.texture = char['idle']
    char_name_text.text = f"<b>{char['name']}</b>"

def on_restart(): start_game()
btn_restart.on_click = on_restart

def on_menu():
    game_over_parent.enabled = False
    menu_parent.enabled = True
    game_state = "MENU"
    camera.y = 0
    t_stats.text = get_stats_text()  # Refresh stats (best score mungkin sudah berubah)
btn_menu.on_click = on_menu

# Main Update Loop
def update():
    global score, lives, max_height
    
    if game_state == "PLAYING" and frog:
        # Camera logic
        if frog.y > camera.y:
            camera.y = frog.y
            
            # Score logic
            if camera.y > max_height:
                max_height = camera.y
                score = int(max_height * 10)
                update_hud()
                
        # Background logic (infinite scroll)
        for bg in bg_entities:
            if camera.y - bg.y > 15:
                bg.y += 15 * len(bg_entities)
                
        # Platform generation
        highest_plat = max(platforms, key=lambda p: p.y)
        if highest_plat.y < camera.y + 10:
            level = 1 + int(max_height / 30)
            generate_platform(highest_plat.y + random.uniform(2.5, 4.0), level)
            
        # Collectible collisions
        to_remove = []
        for coll in collectibles:
            # Sync position with platform if it's on top of one
            # Not strictly necessary if it floats, but let's just leave it static or move it down
            if frog.intersects(coll).hit:
                if coll.type_name == 'fly':
                    score += 500
                elif coll.type_name == 'heart':
                    lives += 1
                update_hud()
                to_remove.append(coll)
                
        for c in to_remove:
            if c in collectibles:
                collectibles.remove(c)
                destroy(c)
                
        # Death check
        if frog.y < camera.y - 8:
            lives -= 1
            update_hud()
            if lives > 0:
                # Respawn on lowest visible platform
                safe = min([p for p in platforms if p.y > camera.y - 5], key=lambda p: p.y, default=None)
                if safe:
                    frog.y = safe.y + 1
                    frog.x = safe.x
                    frog.vel_y = 0
                    frog.is_jumping = False
                    frog.on_platform = safe
                else:
                    game_over()
            else:
                game_over()

app.run()
