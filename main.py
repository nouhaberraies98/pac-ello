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

# Couleurs retro
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Labyrinthe (1 = Mur, 0 = Pastille, 2 = Vide)
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

# Chargement des images
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

# Configuration Swipe mobile
touch_start_x = 0
touch_start_y = 0
is_touching = False
SWIPE_THRESHOLD = 15  # Plus sensible pour un glissement parfait sur telephone

# Variables de jeu
score = 0
current_level = 1
lives = 3
game_state = "START"

player_speed = 2
player_dx, player_dy = 0, 0
next_dx, next_dy = 0, 0

def reset_player_position():
    global player_x, player_y, player_dx, player_dy, next_dx, next_dy
    player_x = OFFSET_X + TILE_SIZE + 3
    player_y = OFFSET_Y + TILE_SIZE + 3
    player_dx, player_dy = 0, 0
    next_dx, next_dy = 0, 0

def init_level():
    """Génère strictement le nombre de claps selon le niveau, sans blocage."""
    global claps, dots_left, current_grid
    
    current_grid = [row[:] for row in GRID]
    dots_left = sum(row.count(0) for row in current_grid)
    reset_player_position()
    
    # Utilisation d'une vitesse fixe stable (2) pour eviter les bugs de virgules
    speed = 2
    
    # Positions de depart distinctes pour chaque clap
    potential_claps = [
        {"x": OFFSET_X + 7*TILE_SIZE, "y": OFFSET_Y + 5*TILE_SIZE, "dx": speed, "dy": 0, "open": True},
        {"x": OFFSET_X + 2*TILE_SIZE, "y": OFFSET_Y + 7*TILE_SIZE, "dx": -speed, "dy": 0, "open": True},
        {"x": OFFSET_X + 12*TILE_SIZE, "y": OFFSET_Y + 1*TILE_SIZE, "dx": 0, "dy": speed, "open": True}
    ]
    
    # Niveau 1 = 1 clap | Niveau 2 = 2 claps | Niveau 3 = 3 claps
    num_claps = min(current_level, 3)
    claps = potential_claps[:num_claps]

def reset_full_game():
    global score, current_level, lives, game_state, funny_message
    score = 0
    current_level = 1
    lives = 3
    game_state = "START"
    init_level()
    funny_message = "Wasted! Le clap a coupe ta scene !"

reset_full_game()
animation_counter = 0

def draw_text(text, font_size, color, x, y):
    font = pygame.font.SysFont("Impact" if font_size > 30 else "Arial", font_size, bold=True)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def can_move(nx, ny, size=24):
    corners = [(nx, ny), (nx + size - 1, ny), (nx, ny + size - 1), (nx + size - 1, ny + size - 1)]
    for cx, cy in corners:
        grid_x = int((cx - OFFSET_X) // TILE_SIZE)
        grid_y = int((cy - OFFSET_Y) // TILE_SIZE)
        if grid_y < 0 or grid_y >= len(current_grid) or grid_x < 0 or grid_x >= len(current_grid[0]):
            return False
        if current_grid[grid_y][grid_x] == 1:
            return False
    return True

async def main():
    global game_state, player_x, player_y, player_dx, player_dy, score, animation_counter, dots_left, funny_message
    global touch_start_x, touch_start_y, is_touching, lives, current_level, next_dx, next_dy
    
    while True:
        screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()
        animation_counter += 1
        
        play_button = pygame.Rect(WIDTH//2 - 60, 140, 120, 45)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == "START" and play_button.collidepoint(mouse_pos):
                    game_state = "PLAYING"
                elif game_state in ["GAME_OVER", "VICTORY"] and retry_button.collidepoint(mouse_pos):
                    reset_full_game()
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
                            if delta_x > 0: next_dx, next_dy = player_speed, 0
                            else: next_dx, next_dy = -player_speed, 0
                        else:
                            if delta_y > 0: next_dx, next_dy = 0, player_speed
                            else: next_dx, next_dy = 0, -player_speed

        # Touches Clavier PC (Super fluide)
        keys = pygame.key.get_pressed()
        if game_state == "PLAYING":
            if keys[pygame.K_LEFT]: next_dx, next_dy = -player_speed, 0
            elif keys[pygame.K_RIGHT]: next_dx, next_dy = player_speed, 0
            elif keys[pygame.K_UP]: next_dx, next_dy = 0, -player_speed
            elif keys[pygame.K_DOWN]: next_dx, next_dy = 0, player_speed

            # Le tampon applique le mouvement au prochain croisement libre
            if (next_dx, next_dy) != (0, 0) and can_move(player_x + next_dx, player_y + next_dy, size=24):
                player_dx, player_dy = next_dx, next_dy
            
            if can_move(player_x + player_dx, player_y + player_dy, size=24):
                player_x += player_dx
                player_y += player_dy

            # Manger les points
            cx = int((player_x + 12 - OFFSET_X) // TILE_SIZE)
            cy = int((player_y + 12 - OFFSET_Y) // TILE_SIZE)
            if 0 <= cx < len(current_grid[0]) and 0 <= cy < len(current_grid):
                if current_grid[cy][cx] == 0:
                    current_grid[cy][cx] = 2
                    score += 10
                    dots_left -= 1
                    
                    if dots_left <= 0:
                        if current_level < 3:
                            current_level += 1
                            init_level()
                        else:
                            game_state = "VICTORY"

        # --- DESSIN DES ÉCRANS ---
        if game_state == "START":
            if menu_bg: screen.blit(menu_bg, (0, 0))
            else:
                draw_text("PAC-ELLO", 60, YELLOW, WIDTH//2, 100)
                pygame.draw.rect(screen, RED, play_button, border_radius=8)
                draw_text("PLAY", 22, WHITE, WIDTH//2, 155)
            
        elif game_state == "PLAYING":
            for r, row in enumerate(current_grid):
                for c, val in enumerate(row):
                    x = OFFSET_X + c * TILE_SIZE
                    y = OFFSET_Y + r * TILE_SIZE
                    if val == 1: pygame.draw.rect(screen, BLUE, (x, y, TILE_SIZE, TILE_SIZE), 2)
                    elif val == 0: pygame.draw.circle(screen, WHITE, (x + TILE_SIZE//2, y + TILE_SIZE//2), 4)

            if player_img: screen.blit(player_img, (player_x, player_y))
            else: pygame.draw.circle(screen, YELLOW, (player_x + 12, player_y + 12), 12)

            # Mouvement et Animation continue des Claps
            for clap in claps:
                # Aligner parfaitement sur la grille aux intersections
                if (clap["x"] - OFFSET_X) % TILE_SIZE == 0 and (clap["y"] - OFFSET_Y) % TILE_SIZE == 0:
                    moves = []
                    for ndx, ndy in [(2, 0), (-2, 0), (0, 2), (0, -2)]:
                        if ndx == -clap["dx"] and ndy == -clap["dy"]: continue # Ne fait pas demi-tour directement
                        if can_move(clap["x"] + ndx, clap["y"] + ndy, size=30):
                            moves.append((ndx, ndy))
                    
                    if moves:
                        if random.random() < 0.2 or not can_move(clap["x"] + clap["dx"], clap["y"] + clap["dy"], size=30):
                            clap["dx"], clap["dy"] = random.choice(moves)
                    else:
                        clap["dx"], clap["dy"] = -clap["dx"], -clap["dy"]

                clap["x"] += clap["dx"]
                clap["y"] += clap["dy"]
                
                # Fait claquer l'image en permanence toutes les 8 frames
                if animation_counter % 8 == 0: 
                    clap["open"] = not clap["open"]
                
                if clap_img:
                    if clap["open"]: screen.blit(pygame.transform.rotate(clap_img, 12), (clap["x"], clap["y"] - 4))
                    else: screen.blit(clap_img, (clap["x"], clap["y"]))
                else: pygame.draw.rect(screen, RED, (clap["x"], clap["y"], 30, 30))

                # Collisions
                if pygame.Rect(player_x, player_y, 24, 24).colliderect(pygame.Rect(clap["x"], clap["y"], 30, 30)):
                    lives -= 1
                    if lives > 0: reset_player_position()
                    else: game_state = "GAME_OVER"

            # HUD 
            draw_text(f"SCORE: {score}", 22, WHITE, WIDTH//4, 40)
            draw_text(f"NIVEAU: {current_level}/3", 22, GREEN, 3 * WIDTH//4, 40)
            draw_text("VIES: ", 18, WHITE, WIDTH//2 - 40, 90)
            for i in range(lives): pygame.draw.circle(screen, RED, (WIDTH//2 + 10 + (i * 22), 88), 7)
            draw_text(f"RESTANTS: {dots_left}", 16, YELLOW, WIDTH//2, 120)

        elif game_state == "GAME_OVER":
            draw_text("GAME OVER", 50, RED, WIDTH//2, HEIGHT//2 - 120)
            if ellox_img: screen.blit(ellox_img, (WIDTH//2 - 40, HEIGHT//2 - 75))
            draw_text(funny_message, 18, WHITE, WIDTH//2, HEIGHT//2 + 35)
            retry_button = pygame.Rect(WIDTH//2 - 85, HEIGHT//2 + 95, 170, 45)
            pygame.draw.rect(screen, RED, retry_button, border_radius=8)
            draw_text("TRY AGAIN", 20, WHITE, WIDTH//2, HEIGHT//2 + 117)

        elif game_state == "VICTORY":
            draw_text("VICTOIRE TOTALE !", 40, GREEN, WIDTH//2, HEIGHT//2 - 60)
            draw_text(f"Score Final: {score} Pts", 22, WHITE, WIDTH//2, HEIGHT//2 - 10)
            retry_button = pygame.Rect(WIDTH//2 - 85, HEIGHT//2 + 50, 170, 45)
            pygame.draw.rect(screen, GREEN, retry_button, border_radius=8)
            draw_text("REJOUER", 20, WHITE, WIDTH//2, HEIGHT//2 + 72)

        pygame.display.flip()
        clock.tick(30)
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())