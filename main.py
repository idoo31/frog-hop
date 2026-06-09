from ursina import *
import random
import json
import os
from entities import Frog, Platform, Collectible

app = Ursina(size=(450, 800), title="Frog Hopper Adventure")

# Configure Camera
camera.orthographic = True
camera.fov = 15

# Assets mapping
assets_path = 'assets/'

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

# --- UI Setup ---
menu_parent = Entity(parent=camera.ui)
game_ui_parent = Entity(parent=camera.ui, enabled=False)
char_select_parent = Entity(parent=camera.ui, enabled=False)
game_over_parent = Entity(parent=camera.ui, enabled=False)

# Background for menu
menu_bg = Entity(parent=menu_parent, model='quad', texture=assets_path+'menu_bg.png', scale=(2, 1), z=1)
logo = Entity(parent=menu_parent, model='quad', texture=assets_path+'logo.png', scale=(1, 0.5), y=0.3)

# Menu Buttons
btn_play = Button(parent=menu_parent, text='PLAY', color=color.green, scale=(0.5, 0.08), y=-0.1)
btn_char = Button(parent=menu_parent, text='KARAKTER', color=color.azure, scale=(0.5, 0.08), y=-0.2)
btn_exit = Button(parent=menu_parent, text='EXIT', color=color.red, scale=(0.5, 0.08), y=-0.3)

# Stats Bar
stats_bg = Button(parent=menu_parent, color=color.dark_gray, scale=(0.6, 0.08), y=0.05, highlight_color=color.dark_gray, pressed_color=color.dark_gray)
Text(parent=stats_bg, text=f"Coins: {save_data['coins']}", origin=(-1.5, 0), x=-0.4, color=color.gold)
Text(parent=stats_bg, text=f"BEST: {save_data['best_score']}", origin=(1.5, 0), x=0.4)

# Char Select UI
Text(parent=char_select_parent, text="SELECT CHARACTER", y=0.3, origin=(0,0), scale=2)
char_display = Entity(parent=char_select_parent, model='quad', texture=characters[0]['idle'], scale=(0.3, 0.3), y=0)
char_name_text = Text(parent=char_select_parent, text=characters[0]['name'], y=-0.2, origin=(0,0), scale=1.5)
btn_prev = Button(parent=char_select_parent, text='Prev', scale=(0.15, 0.1), x=-0.3, y=0)
btn_next = Button(parent=char_select_parent, text='Next', scale=(0.15, 0.1), x=0.3, y=0)
btn_back = Button(parent=char_select_parent, text='BACK', color=color.gray, scale=(0.3, 0.08), y=-0.4)

# Game Over UI
go_title = Text(parent=game_over_parent, text="GAME OVER", color=color.red, y=0.2, origin=(0,0), scale=3)
go_score = Text(parent=game_over_parent, text="Score: 0", y=0, origin=(0,0), scale=2)
btn_restart = Button(parent=game_over_parent, text="RESTART", color=color.green, scale=(0.4, 0.08), y=-0.2)
btn_menu = Button(parent=game_over_parent, text="MAIN MENU", color=color.azure, scale=(0.4, 0.08), y=-0.3)

# HUD
hud_score = Text(parent=game_ui_parent, text="Score: 0", position=(-0.45, 0.45), scale=2)
hud_lives = Text(parent=game_ui_parent, text="Lives: 3", position=(0.3, 0.45), scale=2)

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
    go_score.text = f"Final Score: {score}"
    
    if score > save_data.get("best_score", 0):
        save_data["best_score"] = score
        save_game(save_data)

def update_hud():
    hud_score.text = f"Score: {score}"
    hud_lives.text = f"Lives: {lives}"

# Button Callbacks
def on_play(): start_game()
btn_play.on_click = on_play

def on_char():
    menu_parent.enabled = False
    char_select_parent.enabled = True
btn_char.on_click = on_char

def on_exit(): application.quit()
btn_exit.on_click = on_exit

def on_back():
    char_select_parent.enabled = False
    menu_parent.enabled = True
btn_back.on_click = on_back

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
    char_name_text.text = char['name']

def on_restart(): start_game()
btn_restart.on_click = on_restart

def on_menu():
    game_over_parent.enabled = False
    menu_parent.enabled = True
    game_state = "MENU"
    camera.y = 0
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
