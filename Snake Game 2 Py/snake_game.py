import pygame
import time
import random
import numpy as np
from snake_ai import DQNSnakeAI

# Initialize pygame
pygame.init()

# Colors
white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)

# Display dimensions
dis_width = 800
dis_height = 600

# Create display
dis = pygame.display.set_mode((dis_width, dis_height))
pygame.display.set_caption('Snake Game')

# Clock
clock = pygame.time.Clock()

# Snake block size
snake_block = 10
snake_speed = 15

# Font style
font_style = pygame.font.SysFont(None, 50)
score_font = pygame.font.SysFont(None, 35)

def our_snake(snake_block, snake_list):
    for x in snake_list:
        pygame.draw.rect(dis, green, [x[0], x[1], snake_block, snake_block])

def message(msg, color):
    mesg = font_style.render(msg, True, color)
    dis.blit(mesg, [dis_width / 6, dis_height / 3])

def load_high_score():
    try:
        with open("high_score.txt", "r") as f:
            return int(f.read())
    except FileNotFoundError:
        return 0

def save_high_score(score):
    with open("high_score.txt", "w") as f:
        f.write(str(score))

def display_score(score, high_score):
    value = score_font.render("Your Score: " + str(score), True, yellow)
    dis.blit(value, [0, 0])
    high_score_value = score_font.render("High Score: " + str(high_score), True, yellow)
    dis.blit(high_score_value, [0, 30])

def gameLoop():
    episode = 0
    grid_width = dis_width // snake_block
    grid_height = dis_height // snake_block
    state_size = (grid_width, grid_height)
    action_size = 4
    max_moves = grid_width * grid_height
    ai_agent = DQNSnakeAI(state_size, action_size, max_moves)

    while True:
        game_over = False

        x1 = dis_width / 2
        y1 = dis_height / 2

        x1_change = 0
        y1_change = 0

        snake_List = []
        Length_of_snake = 1

        foodx = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
        foody = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0

        high_score = load_high_score()
        current_score = 0

        direction = None

        while not game_over:

            # AI chooses action
            state = ai_agent.get_state((x1, y1), snake_List, (foodx, foody))
            action = ai_agent.choose_action(state, Length_of_snake)

            if action == 0 and direction != 'DOWN':  # UP
                x1_change = 0
                y1_change = -snake_block
                direction = 'UP'
            elif action == 1 and direction != 'LEFT':  # RIGHT
                x1_change = snake_block
                y1_change = 0
                direction = 'RIGHT'
            elif action == 2 and direction != 'UP':  # DOWN
                x1_change = 0
                y1_change = snake_block
                direction = 'DOWN'
            elif action == 3 and direction != 'RIGHT':  # LEFT
                x1_change = -snake_block
                y1_change = 0
                direction = 'LEFT'

            x1 += x1_change
            y1 += y1_change

            # Check for collisions
            if x1 >= dis_width or x1 < 0 or y1 >= dis_height or y1 < 0:
                game_over = True

            dis.fill(black)
            pygame.draw.rect(dis, red, [foodx, foody, snake_block, snake_block])
            snake_Head = [x1, y1]
            snake_List.append(snake_Head)
            if len(snake_List) > Length_of_snake:
                del snake_List[0]

            for x in snake_List[:-1]:
                if x == snake_Head:
                    game_over = True

            our_snake(snake_block, snake_List)
            display_score(current_score, high_score)

            pygame.display.update()

            reward = -0.1  # Small penalty for each move

            if x1 == foodx and y1 == foody:
                foodx = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
                foody = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0
                Length_of_snake += 1
                current_score += 1
                if current_score > high_score:
                    high_score = current_score
                reward = 10  # Reward for eating food

            if game_over:
                reward = -100  # Penalty for dying

            # Store experience in replay buffer
            next_state = ai_agent.get_state((x1, y1), snake_List, (foodx, foody))
            done = game_over
            ai_agent.remember(state, action, reward, next_state, done)
            state = next_state

            ai_agent.learn()

            clock.tick(snake_speed)

        save_high_score(high_score)
        episode += 1
        ai_agent.evaluate(episode)

gameLoop()
