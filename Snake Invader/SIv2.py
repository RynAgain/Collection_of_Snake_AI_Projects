import pygame
import random
from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions

# Initialize pygame
pygame.init()

# Set up RGB matrix emulator
options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.brightness = 50
matrix = RGBMatrix(options=options)  # Use RGBMatrix directly

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Game settings
player_x = 32
player_y = 56
player_speed = 2
bullet_speed = -4
enemy_speed = 1
player_size = 3
bullet_size = 1
enemy_size = 3

# Bullet
bullet_x, bullet_y = None, None
bullet_active = False

# Enemy
enemy_x = random.randint(0, 61)  # Keep within bounds for enemy size
enemy_y = 0

# Helper function to draw a rectangle using SetPixel
def draw_rectangle(matrix, x, y, width, height, color):
    r, g, b = color
    for i in range(width):
        matrix.SetPixel(x + i, y, r, g, b)          # Top side
        matrix.SetPixel(x + i, y + height - 1, r, g, b)  # Bottom side
    for j in range(height):
        matrix.SetPixel(x, y + j, r, g, b)          # Left side
        matrix.SetPixel(x + width - 1, y + j, r, g, b)  # Right side

# Game loop
running = True
while running:
    # Clear the screen
    matrix.Clear()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player_x = max(0, player_x - player_speed)
            if event.key == pygame.K_RIGHT:
                player_x = min(61, player_x + player_speed)
            if event.key == pygame.K_SPACE and not bullet_active:
                bullet_x, bullet_y = player_x + 1, player_y - 2  # Position bullet above player
                bullet_active = True

    # Update bullet position
    if bullet_active:
        bullet_y += bullet_speed
        if bullet_y < 0:
            bullet_active = False

    # Update enemy position
    enemy_y += enemy_speed
    if enemy_y > 63:  # Reset enemy when it goes out of bounds
        enemy_x = random.randint(0, 61)
        enemy_y = 0

    # Collision detection
    if bullet_active and abs(bullet_x - enemy_x) < enemy_size and abs(bullet_y - enemy_y) < enemy_size:
        bullet_active = False
        enemy_x = random.randint(0, 61)
        enemy_y = 0  # Reset enemy

    # Draw player
    draw_rectangle(matrix, player_x, player_y, player_size, player_size, WHITE)

    # Draw bullet
    if bullet_active:
        matrix.SetPixel(bullet_x, bullet_y, *GREEN)

    # Draw enemy
    draw_rectangle(matrix, enemy_x, enemy_y, enemy_size, enemy_size, RED)

    # Delay for frame rate control
    pygame.time.delay(50)  # Adjust for game speed

pygame.quit()
