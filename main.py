import pygame
import sys
import math
import asyncio
import random

# Initialisation de Pygame
pygame.init()

# Configuration de l'ecran
WIDTH, HEIGHT = 448, 512
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PAC-ELLO")
clock = pygame.time.Clock()

# Couleurs retro Pac-Man
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)

# Labyrinthe (1 = Mur, 0 = Pastille a manger, 2 = Vide)
GRID = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,1,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,0,1,0,1,0,1,1,0,1],
    [1,0,0,0,0,1,0,0,0,1,0,0,0,0,1],
    [1,1,1,0,1,1,1,2,1,1,1,0,1,1,1],
    [1,0,0,0,0,0,0,2,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,1,1,1,1,0,1,1,0,1],
    [1,0,0,1,0,0,0,0,0,0,0,1,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

TILE_SIZE = 30
OFFSET_X = (WIDTH - (len(GRID[0]) * TILE_SIZE)) // 2
OFFSET_Y = 150

# Chargement securise de toutes les images
try:
    player_img = pygame.image.load("player_head.png")
    player_img = pygame.transform.scale(player_img, (24, 24))
    
    clap_img = pygame.image.load("clapperboard.png")
    clap_img = pygame.transform.scale(clap_img, (30, 30))
    
    ellox_img = pygame.image.load("ellox.png")
    ellox_img = pygame.transform.scale(ellox_img, (80, 80))
    
    menu_bg = pygame.image.load("menu_bg.png")
    menu_bg = pygame.transform.scale(menu_bg, (WIDTH, HEIGHT))
except Exception as e:
    player_img = None
    clap_img = None
    ellox_img = None
    menu_bg = None
    print("Note : Images manquantes -", e)

# Variables pour le Swipe tactile
touch_start_x = 0
touch_start_y = 0
is_touching = False
SWIPE_THRESHOLD = 25

# Variables de jeu
def reset_game():
    global player_x, player_y, player_dx, player_dy, claps, score, game_state, dots_left, current_grid, funny_message
    player_x = OFFSET_X + TILE_SIZE + 3
    player_y = OFFSET_Y + TILE_SIZE + 3
    player_dx = 0
    player_dy = 0
    score = 0
    game_state = "START"
    
    current_grid = [row[:] for row in GRID]
    dots_left = sum(row.count(0) for row in current_grid)

    claps = [
        {"x": OFFSET_X + 7*TILE_SIZE, "y": OFFSET_Y + 5*TILE_SIZE, "dx": 2, "dy": 0, "open": True},
        {"x": OFFSET_X + 2*TILE_SIZE, "y": OFFSET_Y + 7*TILE_SIZE, "dx": -2, "dy": 0, "open": True},
        {"x": OFFSET_X + 12*TILE_SIZE, "y": OFFSET_Y + 1*TILE_SIZE, "dx": 0, "dy": 2, "open": True}
    ]
    
    messages = [
        "Wasted! The clap cut your scene!",
        "Bro got crunched by cinematography!",
        "Directly to the bloopers reel!",
        "You're not the main character anymore!",
        "Mission failed, next time stay in script!"
    ]
    funny_message = random.choice(messages)

reset_game()
player_speed = 2
animation_counter = 0

def draw_text(text, font_size, color, x, y):
    font = pygame.font.SysFont("Impact" if font_size > 30 else "Arial", font_size, bold=True)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def can_move(nx, ny, size=24):
    corners = [(nx, ny), (nx + size - 1, ny), (nx, ny + size - 1), (nx + size - 1, ny + size - 1)]
    for cx, cy in corners:
        grid_x = (cx - OFFSET_X) // TILE_SIZE
        grid_y = (cy - OFFSET_Y) // TILE_SIZE
        if grid_y < 0 or grid_y >= len(current_grid) or grid_x < 0 or grid_x >= len(current_grid[0]):
            return False
        if current_grid[grid_y][grid_x] == 1:
            return False
    return True

async def main():
    global game_state, player_x, player_y, player_dx, player_dy, score, animation_counter, dots_left, funny_message
    global touch_start_x, touch_start_y, is_touching
    
    while True:
        screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()
        animation_counter += 1
        
        # Zone calibrated pour l'image Canva (Bouton PLAY)
        play_button = pygame.Rect(WIDTH//2 - 60, 135, 120, 45)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == "START":
                    if play_button.collidepoint(mouse_pos):
                        game_state = "PLAYING"
                elif game_state in ["GAME_OVER", "VICTORY"]:
                    if retry_button.collidepoint(mouse_pos):
                        reset_game()
                        game_state = "PLAYING"
                
                elif game_state == "PLAYING":
                    touch_start_x, touch_start_y = event.pos
                    is_touching = True
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if game_state == "PLAYING" and is_touching:
                    is_touching = False
                    end_x, end_y = event.pos
                    
                    delta_x = end_x - touch_start_x
                    delta_y = end_y - touch_start_y
                    
                    if max(abs(delta_x), abs(delta_y)) > SWIPE_THRESHOLD:
                        if abs(delta_x) > abs(delta_y):
                            if delta_x > 0: player_dx, player_dy = player_speed, 0
                            else: player_dx, player_dy = -player_speed, 0
                        else:
                            if delta_y > 0: player_dx, player_dy = 0, player_speed
                            else: player_dx, player_dy = 0, -player_speed

        # Commandes Clavier (PC)
        keys = pygame.key.get_pressed()
        if game_state == "PLAYING":
            if keys[pygame.K_LEFT]: player_dx, player_dy = -player_speed, 0
            elif keys[pygame.K_RIGHT]: player_dx, player_dy = player_speed, 0
            elif keys[pygame.K_UP]: player_dx, player_dy = 0, -player_speed
            elif keys[pygame.K_DOWN]: player_dx, player_dy = 0, player_speed

            if can_move(player_x + player_dx, player_y + player_dy, size=24):
                player_x += player_dx
                player_y += player_dy

            center_x = (player_x + 12 - OFFSET_X) // TILE_SIZE
            center_y = (player_y + 12 - OFFSET_Y) // TILE_SIZE

            if 0 <= center_x < len(current_grid[0]) and 0 <= center_y < len(current_grid):
                if current_grid[center_y][center_x] == 0:
                    current_grid[center_y][center_x] = 2
                    score += 10
                    dots_left -= 1
                    if dots_left <= 0:
                        game_state = "VICTORY"

        # --- ECRAN START ---
        if game_state == "START":
            if menu_bg:
                screen.blit(menu_bg, (0, 0))
            else:
                draw_text("PAC-ELLO", 60, YELLOW, WIDTH//2, 100)
                pygame.draw.rect(screen, RED, play_button, border_radius=8)
                draw_text("PLAY", 22, WHITE, WIDTH//2, 155)
            
        # --- PHASE DE JEU ACTIVE ---
        elif game_state == "PLAYING":
            for r_idx, row in enumerate(current_grid):
                for c_idx, val in enumerate(row):
                    x = OFFSET_X + c_idx * TILE_SIZE
                    y = OFFSET_Y + r_idx * TILE_SIZE
                    if val == 1:
                        pygame.draw.rect(screen, BLUE, (x, y, TILE_SIZE, TILE_SIZE), 2)
                    elif val == 0:
                        pygame.draw.circle(screen, WHITE, (x + TILE_SIZE//2, y + TILE_SIZE//2), 4)

            if player_img:
                screen.blit(player_img, (player_x, player_y))
            else:
                pygame.draw.circle(screen, YELLOW, (player_x + 12, player_y + 12), 12)

            for c in claps:
                if (c["x"] - OFFSET_X) % TILE_SIZE == 0 and (c["y"] - OFFSET_Y) % TILE_SIZE == 0:
                    valid_moves = []
                    for ndx, ndy in [(2, 0), (-2, 0), (0, 2), (0, -2)]:
                        if ndx == -c["dx"] and ndy == -c["dy"]: continue
                        if can_move(c["x"] + ndx, c["y"] + ndy, size=30):
                            valid_moves.append((ndx, ndy))
                    
                    if valid_moves:
                        if random.random() < 0.3 or not can_move(c["x"] + c["dx"], c["y"] + c["dy"], size=30):
                            c["dx"], c["dy"] = random.choice(valid_moves)
                    elif not can_move(c["x"] + c["dx"], c["y"] + c["dy"], size=30):
                        c["dx"], c["dy"] = -c["dx"], -c["dy"]

                c["x"] += c["dx"]
                c["y"] += c["dy"]
                
                if animation_counter % 12 == 0:
                    c["open"] = not c["open"]
                
                if clap_img:
                    if c["open"]:
                        rotated_clap = pygame.transform.rotate(clap_img, 12)
                        screen.blit(rotated_clap, (c["x"], c["y"] - 4))
                    else:
                        screen.blit(clap_img, (c["x"], c["y"]))
                else:
                    pygame.draw.rect(screen, RED, (c["x"], c["y"], 30, 30))

                player_rect = pygame.Rect(player_x, player_y, 24, 24)
                clap_rect = pygame.Rect(c["x"], c["y"], 30, 30)
                if player_rect.colliderect(clap_rect):
                    game_state = "GAME_OVER"

            draw_text(f"SCORE: {score}", 25, WHITE, WIDTH//2, 50)
            draw_text(f"RESTANTS: {dots_left}", 16, YELLOW, WIDTH//2, 90)

        # --- ECRAN GAME OVER ---
        elif game_state == "GAME_OVER":
            draw_text("GAME OVER", 50, RED, WIDTH//2, HEIGHT//2 - 120)
            if ellox_img:
                screen.blit(ellox_img, (WIDTH//2 - 40, HEIGHT//2 - 75))
            draw_text(funny_message, 18, WHITE, WIDTH//2, HEIGHT//2 + 35)
            
            retry_button = pygame.Rect(WIDTH//2 - 85, HEIGHT//2 + 85, 170, 45)
            pygame.draw.rect(screen, RED, retry_button, border_radius=8)
            draw_text("TRY AGAIN", 20, WHITE, WIDTH//2, HEIGHT//2 + 107)

        # --- ECRAN VICTOIRE ---
        elif game_state == "VICTORY":
            draw_text("VICTORY !", 50, GREEN, WIDTH//2, HEIGHT//2 - 60)
            draw_text(f"Final Score: {score} Pts", 22, WHITE, WIDTH//2, HEIGHT//2 - 10)
            
            retry_button = pygame.Rect(WIDTH//2 - 80, HEIGHT//2 + 50, 160, 45)
            pygame.draw.rect(screen, GREEN, retry_button, border_radius=8)
            draw_text("PLAY AGAIN", 20, WHITE, WHITE, WIDTH//2, HEIGHT//2 + 72)

        pygame.display.flip()
        clock.tick(30)
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())