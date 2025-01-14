```python
import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CELL_SIZE = 20
FPS = 10

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Game variables
snake = [(200, 200)]
food = (400, 400)
direction = 'RIGHT'
score = 0

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Snake Game')

clock = pygame.time.Clock()

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and direction != 'RIGHT':
        direction = 'LEFT'
    elif keys[pygame.K_RIGHT] and direction != 'LEFT':
        direction = 'RIGHT'
    elif keys[pygame.K_UP] and direction != 'DOWN':
        direction = 'UP'
    elif keys[pygame.K_DOWN] and direction != 'UP':
        direction = 'DOWN'

    # Update snake position
    x, y = snake[0]
    if direction == 'LEFT':
        x -= CELL_SIZE
    elif direction == 'RIGHT':
        x += CELL_SIZE
    elif direction == 'UP':
        y -= CELL_SIZE
    elif direction == 'DOWN':
        y += CELL_SIZE

    # Check for collision with walls
    if x < 0 or x >= SCREEN_WIDTH or y < 0 or y >= SCREEN_HEIGHT:
        pygame.quit()
        quit()

    # Check for collision with itself
    if (x, y) in snake:
        pygame.quit()
        quit()

    # Check for collision with food
    if (x, y) == food:
        snake.append(food)
        food = (random.randint(0, SCREEN_WIDTH // CELL_SIZE - 1) * CELL_SIZE, random.randint(0, SCREEN_HEIGHT // CELL_SIZE - 1) * CELL_SIZE)
        score += 1
    else:
        snake.pop()

    # Draw everything on the screen
    screen.fill(WHITE)
    for segment in snake:
        pygame.draw.rect(screen, GREEN, (segment[0], segment[1], CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, RED, (food[0], food[1], CELL_SIZE, CELL_SIZE))

    # Display score
    font = pygame.font.SysFont(None, 36)
    text = font.render(f'Score: {score}', True, (0, 0, 0))
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)
```