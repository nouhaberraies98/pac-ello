import pygame
import sys
import math

# Initialisation de Pygame
pygame.init()

# Configuration de l'écran (adapté aux mobiles/navigateurs)
WIDTH, HEIGHT = 448, 512
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PAC-ELLO: Elham Ali")
clock = pygame.time.Clock()

# Couleurs Pac-Man classiques
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Configuration de la police de caractères pour les Emojis de secours
try:
    emoji_font = pygame.font.SysFont("Segoe UI Emoji", 24)
except:
    emoji_font = pygame.font.SysFont("Arial", 24)

# Chargement des images (Visage de Khaled et Clap de cinéma)
try:
    player_img = pygame.image.load("player_head.png")
    player_img = pygame.transform.scale(player_img, (24, 24))
    
    clap_img = pygame.image.load("clapperboard.png")
    clap_img = pygame.transform.scale(clap_img, (30, 30))
except:
    # Mode secours si les fichiers images ne sont pas présents
    player_img = None
    clap_img = None

# Labyrinthe Pac-Man classique (1 = Mur bleu, 0 = Pastille blanche, 2 = Vide)
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

# Variables de jeu
player_x = OFFSET_X + TILE_SIZE + 3
player_y = OFFSET_Y + TILE_SIZE + 3
player_speed = 4

# Liste des Claps Monstres
claps = [
    {"x": OFFSET_X + 7*TILE_SIZE, "y": OFFSET_Y + 5*TILE_SIZE, "dir": 1, "open": True},
    {"x": OFFSET_X + 2*TILE_SIZE, "y": OFFSET_Y + 7*TILE_SIZE, "dir": -1, "open": True}
]

score = 0
game_state = "START"  # START, PLAYING, GAME_OVER
animation_counter = 0

def draw_text(text, font_size, color, x, y):
    font = pygame.font.SysFont("Arial", font_size, bold=True)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

# Boucle principale (Totalement compatible Mobile / Pygbag)
async def main():
    global game_state, player_x, player_y, score, animation_counter
    
    while True:
        screen.fill(BLACK)  # Fond noir pur style Pac-Man
        mouse_pos = pygame.mouse.get_pos()
        animation_counter += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == "START":
                    if play_button.collidepoint(mouse_pos):
                        game_state = "PLAYING"
                        score = 0
                elif game_state == "GAME_OVER":
                    if retry_button.collidepoint(mouse_pos):
                        game_state = "START"
                        player_x = OFFSET_X + TILE_SIZE + 3
                        player_y = OFFSET_Y + TILE_SIZE + 3

        # Gestion des déplacements
        keys = pygame.key.get_pressed()
        if game_state == "PLAYING":
            if keys[pygame.K_LEFT]: player_x -= player_speed
            if keys[pygame.K_RIGHT]: player_x += player_speed
            if keys[pygame.K_UP]: player_y -= player_speed
            if keys[pygame.K_DOWN]: player_y += player_speed

        # --- ÉCRAN DE DÉMARRAGE ARSTYLISÉ RETRO ---
        if game_state == "START":
            draw_text("PAC-ELLO", 50, YELLOW, WIDTH//2, 120)
            draw_text("EAT THE HEAD EDITION", 18, RED, WIDTH//2, 180)
            draw_text("ELHAM ALI PRESENTS", 16, WHITE, WIDTH//2, HEIGHT//2 - 20)
            
            # Bouton de démarrage Rouge
            play_button = pygame.Rect(WIDTH//2 - 75, HEIGHT - 160, 150, 50)
            pygame.draw.rect(screen, RED, play_button, border_radius=5)
            draw_text("PLAY", 25, WHITE, WIDTH//2, HEIGHT - 135)
            
        # --- PHASE DE GAMEPLAY ---
        elif game_state == "PLAYING":
            # Rendu du Labyrinthe rétro
            for r_idx, row in enumerate(GRID):
                for c_idx, val in enumerate(row):
                    x = OFFSET_X + c_idx * TILE_SIZE
                    y = OFFSET_Y + r_idx * TILE_SIZE
                    if val == 1:
                        pygame.draw.rect(screen, BLUE, (x, y, TILE_SIZE, TILE_SIZE), 2)
                    elif val == 0:
                        pygame.draw.circle(screen, WHITE, (x + TILE_SIZE//2, y + TILE_SIZE//2), 3)

            # Rendu du joueur (La tête de Khaled)
            if player_img:
                screen.blit(player_img, (player_x, player_y))
            else:
                # Utilisation d'un emoji Homme si l'image est manquante
                head_emoji = emoji_font.render("👨", True, WHITE)
                screen.blit(head_emoji, (player_x, player_y - 4))

            # Comportement et Rendu des ennemis (Claps)
            for c in claps:
                c["x"] += c["dir"] * 2
                if c["x"] < OFFSET_X + TILE_SIZE or c["x"] > WIDTH - OFFSET_X - 2*TILE_SIZE:
                    c["dir"] *= -1
                
                # Animation d'ouverture mécanique du Clap
                if animation_counter % 12 == 0:
                    c["open"] = not c["open"]
                
                if clap_img:
                    if c["open"]:
                        rotated_clap = pygame.transform.rotate(clap_img, 12)
                        screen.blit(rotated_clap, (c["x"], c["y"] - 4))
                    else:
                        screen.blit(clap_img, (c["x"], c["y"]))
                else:
                    # Utilisation d'un emoji Clap Cinéma si l'image est manquante
                    clap_icon = "🎬" if c["open"] else "📁"
                    clap_emoji = emoji_font.render(clap_icon, True, WHITE)
                    screen.blit(clap_emoji, (c["x"], c["y"] - 4))

                # Détection stricte des collisions (Le clap intercepte la tête)
                player_rect = pygame.Rect(player_x, player_y, 24, 24)
                clap_rect = pygame.Rect(c["x"], c["y"], 30, 30)
                
                if player_rect.colliderect(clap_rect):
                    game_state = "GAME_OVER"

            # Interface de Score en temps réel
            draw_text(f"SCORE: {score}", 25, WHITE, WIDTH//2, 50)

        # --- ÉCRAN DE GAME OVER (L'HOMME EST MORDU) ---
        elif game_state == "GAME_OVER":
            draw_text("CRUNCH ! NOM NOM !", 35, RED, WIDTH//2, HEIGHT//2 - 50)
            draw_text("Le Clap a mangé la tête !", 20, WHITE, WIDTH//2, HEIGHT//2)
            
            retry_button = pygame.Rect(WIDTH//2 - 80, HEIGHT//2 + 60, 160, 45)
            pygame.draw.rect(screen, WHITE, retry_button, border_radius=5)
            draw_text("REESSAYER", 20, BLACK, WIDTH//2, HEIGHT//2 + 82)

        pygame.display.flip()
        clock.tick(30)
        # PAR CELLE-CI :
        await asyncio.sleep(0)

import asyncio
asyncio.run(main())