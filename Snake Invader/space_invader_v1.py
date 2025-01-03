import pygame
import random
import math
from pygame import mixer

pygame.init()

# Screen settings
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Space Invaders")

# Background
background = pygame.image.load("background.webp")
background = pygame.transform.scale(background, (800, 600))

# Player
player_img = pygame.image.load("player.webp")
player_img = pygame.transform.scale(player_img, (64, 64))
player_x = 370
player_y = 480
player_x_change = 0
player_health = 3  # Player health

# Enemy setup with types
enemy_img = []
enemy_x = []
enemy_y = []
enemy_x_change = []
enemy_y_change = []
enemy_type = []
num_of_enemies = 6

def create_enemies():
    for i in range(num_of_enemies):
        enemy_img.append(pygame.image.load("enemy.webp"))
        enemy_img[i] = pygame.transform.scale(enemy_img[i], (64, 64))
        enemy_x.append(random.randint(0, 735))
        enemy_y.append(random.randint(50, 150))
        enemy_x_change.append(0.3)
        enemy_y_change.append(40)
        enemy_type.append(random.choice(['normal', 'fast', 'zigzag']))

create_enemies()

# Bullet
bullet_img = pygame.image.load("bullet.webp")
bullet_img = pygame.transform.scale(bullet_img, (32, 32))
bullet_x = 0
bullet_y = 480
bullet_y_change = 0.5
bullet_state = "ready"

# Score and Level
score_value = 0
level = 1  # Level variable
high_score = 0
font = pygame.font.Font("5x8.bdf", 32)

# Game over
over_font = pygame.font.Font("5x8.bdf", 64)

def show_score(x, y):
    score = font.render("Score: " + str(score_value) + " | Level: " + str(level), True, (255, 255, 255))
    screen.blit(score, (x, y))

def game_over_text():
    over_text = over_font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(over_text, (200, 250))

def player(x, y):
    screen.blit(player_img, (x, y))

def enemy(x, y, i):
    screen.blit(enemy_img[i], (x, y))

def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bullet_img, (x + 16, y + 10))

def is_collision(enemy_x, enemy_y, bullet_x, bullet_y):
    distance = math.sqrt((math.pow(enemy_x - bullet_x, 2)) + (math.pow(enemy_y - bullet_y, 2)))
    return distance < 27

def reset_bullet():
    global bullet_state, bullet_y
    bullet_y = 480
    bullet_state = "ready"

def reset_enemies():
    """ Reset enemy positions and speed on level-up without increasing total count """
    for i in range(num_of_enemies):
        enemy_x[i] = random.randint(0, 735)
        enemy_y[i] = random.randint(50, 150)
        enemy_x_change[i] = 0.3 + level * 0.05  # Slightly faster each level

# Game loop
running = True
while running:
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player_x_change = -0.5
            if event.key == pygame.K_RIGHT:
                player_x_change = 0.5
            if event.key == pygame.K_SPACE and bullet_state == "ready":
                bullet_x = player_x
                fire_bullet(bullet_x, bullet_y)

        if event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                player_x_change = 0

    player_x += player_x_change
    player_x = max(0, min(player_x, 736))

    # Enemy movement and behavior
    for i in range(num_of_enemies):
        if enemy_y[i] > 440:
            player_health -= 1
            enemy_y[i] = random.randint(50, 150)
            enemy_x[i] = random.randint(0, 735)

        enemy_x[i] += enemy_x_change[i]
        if enemy_x[i] <= 0 or enemy_x[i] >= 736:
            enemy_x_change[i] *= -1
            enemy_y[i] += enemy_y_change[i]

        collision = is_collision(enemy_x[i], enemy_y[i], bullet_x, bullet_y)
        if collision:
            score_value += 10
            reset_bullet()
            enemy_x[i] = random.randint(0, 735)
            enemy_y[i] = random.randint(50, 150)

        enemy(enemy_x[i], enemy_y[i], i)

    # Bullet movement
    if bullet_y <= 0:
        reset_bullet()
    if bullet_state == "fire":
        fire_bullet(bullet_x, bullet_y)
        bullet_y -= bullet_y_change

    # Level up: Reset enemies instead of adding more
    if score_value >= level * 60:  # Example threshold for leveling up
        level += 1
        reset_enemies()

    player(player_x, player_y)
    show_score(10, 10)

    if player_health <= 0:
        game_over_text()
        running = False

    pygame.display.update()
