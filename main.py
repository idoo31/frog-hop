import pygame
import random
import sys
import os
import json
from entities import Frog, Platform, Collectible

pygame.init()

# Constants
WIDTH, HEIGHT = 600, 800
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Frog Hopper")
clock = pygame.time.Clock()

# Load Assets
def load_image(name, scale=None):
    try:
        img = pygame.image.load(f"assets/{name}").convert_alpha()
        if scale:
            img = pygame.transform.scale(img, scale)
        return img
    except Exception as e:
        print(f"Error loading {name}: {e}")
        surface = pygame.Surface((40, 40))
        surface.fill((255, 0, 255))
        return surface

frog_idle_img = load_image('frog_idle.png', (48, 48))
frog_jump_img = load_image('frog_jump.png', (48, 48))
frog_red_idle_img = load_image('frog_red_idle.png', (48, 48))
frog_red_jump_img = load_image('frog_red_jump.png', (48, 48))
frog_blue_idle_img = load_image('frog_blue_idle.png', (48, 48))
frog_blue_jump_img = load_image('frog_blue_jump.png', (48, 48))

characters = [
    {"name": "Green Frog", "idle": frog_idle_img, "jump": frog_jump_img},
    {"name": "Red Frog", "idle": frog_red_idle_img, "jump": frog_red_jump_img},
    {"name": "Blue Frog", "idle": frog_blue_idle_img, "jump": frog_blue_jump_img}
]

lily_pad_img = load_image('lily_pad.png', (80, 32))
log_img = load_image('log.png', (120, 40))
fly_img = load_image('fly.png', (32, 32))
heart_img = load_image('heart.png', (32, 32))
try:
    water_bg = pygame.image.load("assets/water_background.png").convert()
except:
    water_bg = pygame.Surface((1, 1))
    water_bg.fill((30, 100, 200))

try:
    menu_bg = pygame.image.load("assets/menu_bg.png").convert()
    menu_bg = pygame.transform.scale(menu_bg, (WIDTH, HEIGHT))
except:
    menu_bg = pygame.Surface((WIDTH, HEIGHT))
    menu_bg.fill((50, 150, 200))

try:
    logo_img = pygame.image.load("assets/logo.png").convert_alpha()
    logo_img = pygame.transform.scale(logo_img, (400, 200))
except:
    logo_img = None

font = pygame.font.SysFont("Arial", 36)
font_small = pygame.font.SysFont("Arial", 24)
font_bold = pygame.font.SysFont("Arial", 28, bold=True)

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

def generate_platform(y_pos, level=1):
    ptype = random.choice(['lily', 'log'])
    img = lily_pad_img if ptype == 'lily' else log_img
    x = random.randint(0, WIDTH - img.get_width())
    speed = random.uniform(1.0 + level * 0.2, 3.0 + level * 0.5)
    direction = random.choice([-1, 1])
    return Platform(x, y_pos, img, speed, direction, WIDTH)

def draw_rounded_rect(surface, color, rect, radius=15):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_button(surface, rect, color, text, font, text_color=(255, 255, 255)):
    draw_rounded_rect(surface, color, rect)
    # Bottom shadow effect
    shadow_rect = pygame.Rect(rect.x, rect.bottom - 5, rect.width, 5)
    shadow_color = (max(0, color[0]-40), max(0, color[1]-40), max(0, color[2]-40))
    pygame.draw.rect(surface, shadow_color, shadow_rect, border_bottom_left_radius=15, border_bottom_right_radius=15)
    
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)

def main_menu():
    selected_idx = 0
    state = "HOME"
    save_data = load_save()
    
    # Define button rects
    btn_width, btn_height = 400, 60
    btn_x = WIDTH//2 - btn_width//2
    play_rect = pygame.Rect(btn_x, 500, btn_width, btn_height)
    karakter_rect = pygame.Rect(btn_x, 575, btn_width, btn_height)
    how_to_rect = pygame.Rect(btn_x, 650, btn_width, btn_height)
    exit_rect = pygame.Rect(btn_x, 725, btn_width, btn_height)
    back_rect = pygame.Rect(20, 20, 100, 40)
    
    while True:
        screen.blit(menu_bg, (0, 0))
        mouse_pos = pygame.mouse.get_pos()
        
        if state == "HOME":
            if logo_img:
                screen.blit(logo_img, (WIDTH//2 - logo_img.get_width()//2, 50))
            else:
                title = font_bold.render("FROG HOPPER", True, WHITE)
                screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
            
            # Center frog
            char = characters[selected_idx]
            char_img = pygame.transform.scale(char["idle"], (120, 120))
            screen.blit(char_img, (WIDTH//2 - 60, 280))
            # Lily pads
            pad_scaled = pygame.transform.scale(lily_pad_img, (160, 64))
            screen.blit(pad_scaled, (WIDTH//2 - 80, 360))
            
            # Stats bar
            stats_rect = pygame.Rect(WIDTH//2 - 200, 420, 400, 50)
            draw_rounded_rect(screen, (20, 40, 80), stats_rect, radius=25)
            
            coins_text = font_small.render(f"{save_data['coins']}", True, (255, 215, 0))
            screen.blit(coins_text, (stats_rect.left + 50, stats_rect.centery - coins_text.get_height()//2))
            
            best_text = font_small.render(f"BEST {save_data['best_score']}", True, WHITE)
            screen.blit(best_text, (stats_rect.right - best_text.get_width() - 20, stats_rect.centery - best_text.get_height()//2))
            
            # Buttons
            draw_button(screen, play_rect, (34, 177, 76), "PLAY", font_bold)
            draw_button(screen, karakter_rect, (0, 102, 204), "KARAKTER", font_bold)
            draw_button(screen, how_to_rect, (255, 128, 0), "HOW TO PLAY", font_bold)
            draw_button(screen, exit_rect, (204, 0, 0), "EXIT", font_bold)
            
        elif state == "KARAKTER":
            title = font_bold.render("SELECT CHARACTER", True, WHITE)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
            
            char = characters[selected_idx]
            char_img = pygame.transform.scale(char["idle"], (120, 120))
            screen.blit(char_img, (WIDTH//2 - 60, HEIGHT//2 - 60))
            
            char_name = font_bold.render(char["name"], True, WHITE)
            screen.blit(char_name, (WIDTH//2 - char_name.get_width()//2, HEIGHT//2 + 80))
            
            nav_prompt = font_small.render("Use LEFT/RIGHT Arrow Keys", True, (220, 220, 220))
            screen.blit(nav_prompt, (WIDTH//2 - nav_prompt.get_width()//2, HEIGHT - 150))
            
            left_arrow = font_bold.render("<", True, WHITE)
            right_arrow = font_bold.render(">", True, WHITE)
            screen.blit(left_arrow, (WIDTH//2 - 120, HEIGHT//2 - 20))
            screen.blit(right_arrow, (WIDTH//2 + 100, HEIGHT//2 - 20))
            
            draw_button(screen, back_rect, (100, 100, 100), "BACK", font_small)
            
        elif state == "HOW_TO_PLAY":
            title = font_bold.render("HOW TO PLAY", True, WHITE)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
            
            instructions = [
                "Use LEFT / RIGHT arrows to move",
                "Press SPACE to jump upwards",
                "Land on platforms to survive",
                "Collect Flies for +50 points",
                "Collect Hearts for Extra Lives",
                "Don't fall off the screen!"
            ]
            
            y_offset = 200
            for line in instructions:
                text_surf = font_small.render(line, True, WHITE)
                screen.blit(text_surf, (WIDTH//2 - text_surf.get_width()//2, y_offset))
                y_offset += 40
                
            draw_button(screen, back_rect, (100, 100, 100), "BACK", font_small)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    if state == "HOME":
                        if play_rect.collidepoint(mouse_pos):
                            return characters[selected_idx]
                        elif karakter_rect.collidepoint(mouse_pos):
                            state = "KARAKTER"
                        elif how_to_rect.collidepoint(mouse_pos):
                            state = "HOW_TO_PLAY"
                        elif exit_rect.collidepoint(mouse_pos):
                            pygame.quit()
                            sys.exit()
                    elif state in ["KARAKTER", "HOW_TO_PLAY"]:
                        if back_rect.collidepoint(mouse_pos):
                            state = "HOME"
                            
            if event.type == pygame.KEYDOWN:
                if state == "KARAKTER":
                    if event.key == pygame.K_LEFT:
                        selected_idx = (selected_idx - 1) % len(characters)
                    elif event.key == pygame.K_RIGHT:
                        selected_idx = (selected_idx + 1) % len(characters)
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                        state = "HOME"
                elif state == "HOME" and event.key == pygame.K_SPACE:
                    return characters[selected_idx]

def game_loop(char):
    platforms = []
    collectibles = []
    
    start_y = HEIGHT - 50
    for i in range(10):
        platforms.append(generate_platform(start_y - i * 120, 1))
    
    safe_plat = Platform(WIDTH//2 - 40, HEIGHT - 50, lily_pad_img, 0, 1, WIDTH)
    platforms[0] = safe_plat
    
    frog = Frog(WIDTH//2, HEIGHT - 50, char["idle"], char["jump"])
    frog.on_platform = safe_plat
    
    score = 0
    lives = 3
    level = 1
    max_height = 0
    scroll_threshold = HEIGHT // 2

    bg_y = 0

    running = True
    while running:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        frog.update(keys, WIDTH, HEIGHT, platforms)
        
        for plat in platforms:
            plat.update()
            
        scroll_y = 0
        if frog.rect.top < scroll_threshold:
            scroll_y = scroll_threshold - frog.rect.top
            frog.rect.top = scroll_threshold
            
            max_height += scroll_y
            score = max_height // 10
            level = 1 + (max_height // 1000)

        for plat in platforms:
            plat.rect.y += scroll_y
            
        for coll in collectibles:
            coll.update(scroll_y)

        platforms = [p for p in platforms if p.rect.top < HEIGHT]
        while len(platforms) < 10:
            highest_y = min(p.rect.y for p in platforms)
            new_y = highest_y - random.randint(100, 140)
            platforms.append(generate_platform(new_y, level))
            
            if random.random() < 0.1:
                ctype = 'heart' if random.random() < 0.2 else 'fly'
                img = heart_img if ctype == 'heart' else fly_img
                cx, cy = platforms[-1].rect.centerx, platforms[-1].rect.top - 20
                collectibles.append(Collectible(cx, cy, img, ctype))

        to_remove_coll = []
        for coll in collectibles:
            if frog.rect.colliderect(coll.rect):
                if coll.type_name == 'fly':
                    score += 50
                elif coll.type_name == 'heart':
                    lives += 1
                to_remove_coll.append(coll)
            elif coll.rect.top > HEIGHT:
                to_remove_coll.append(coll)
        
        for c in to_remove_coll:
            if c in collectibles:
                collectibles.remove(c)

        if frog.rect.top > HEIGHT:
            lives -= 1
            if lives > 0:
                safe = min(platforms, key=lambda p: abs(p.rect.y - (HEIGHT - 150)))
                frog.rect.midbottom = (safe.rect.centerx, safe.rect.top)
                frog.vel_y = 0
                frog.on_platform = safe
            else:
                running = False

        if water_bg.get_width() > 1:
            bg_y = (bg_y + scroll_y * 0.5) % water_bg.get_height()
            for x in range(0, WIDTH, water_bg.get_width()):
                for y in range(-water_bg.get_height(), HEIGHT, water_bg.get_height()):
                    screen.blit(water_bg, (x, y + bg_y))
        else:
            screen.fill((30, 100, 200))

        for plat in platforms:
            plat.draw(screen)
            
        for coll in collectibles:
            coll.draw(screen)
            
        frog.draw(screen)
        
        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (WIDTH - lives_text.get_width() - 10, 10))
        
        pygame.display.flip()

    return score

def game_over_screen(score):
    while True:
        screen.fill(BLACK)
        go_text = font.render("GAME OVER", True, (255, 0, 0))
        score_text = font.render(f"Final Score: {score}", True, WHITE)
        prompt = font.render("Press SPACE to Restart, ESC to Quit", True, WHITE)
        
        screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//3))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2 + 50))
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

if __name__ == "__main__":
    while True:
        selected_char = main_menu()
        final_score = game_loop(selected_char)
        
        save_data = load_save()
        if final_score > save_data.get("best_score", 0):
            save_data["best_score"] = final_score
        save_game(save_data)
        
        game_over_screen(final_score)
