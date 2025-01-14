
import pygame
import random

pygame.init()

# 游戏界面设置
screen_width = 800
screen_height = 600
cell_size = 20
fps = 10

# 颜色定义
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)

# 游戏状态
game_over = False

# 初始化窗口
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('贪吃蛇游戏')

# 蛇的初始位置和长度
snake_pos = [[screen_width // 2, screen_height // 2]]
snake_length = 1
snake_direction = 'RIGHT'

# 食物位置
food_pos = [random.randrange(1, screen_width // cell_size) * cell_size,
            random.randrange(1, screen_height // cell_size) * cell_size]

# 游戏主循环
clock = pygame.time.Clock()
while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and snake_direction != 'RIGHT':
                snake_direction = 'LEFT'
            elif event.key == pygame.K_RIGHT and snake_direction != 'LEFT':
                snake_direction = 'RIGHT'
            elif event.key == pygame.K_UP and snake_direction != 'DOWN':
                snake_direction = 'UP'
            elif event.key == pygame.K_DOWN and snake_direction != 'UP':
                snake_direction = 'DOWN'

    # 移动蛇
    if snake_direction == 'RIGHT':
        snake_pos[0][0] += cell_size
    elif snake_direction == 'LEFT':
        snake_pos[0][0] -= cell_size
    elif snake_direction == 'UP':
        snake_pos[0][1] -= cell_size
    elif snake_direction == 'DOWN':
        snake_pos[0][1] += cell_size

    # 判断是否吃到食物
    if snake_pos[0] == food_pos:
        snake_length += 1
        food_pos = [random.randrange(1, screen_width // cell_size) * cell_size,
                    random.randrange(1, screen_height // cell_size) * cell_size]

    # 绘制界面
    screen.fill(black)
    pygame.draw.rect(screen, green, [food_pos[0], food_pos[1], cell_size, cell_size])
    for pos in snake_pos:
        pygame.draw.rect(screen, white, [pos[0], pos[1], cell_size, cell_size])

    pygame.display.update()

    # 控制蛇的长度
    if len(snake_pos) > snake_length:
        del snake_pos[-1]

    # 判断游戏是否结束
    if snake_pos[0][0] < 0 or snake_pos[0][0] >= screen_width or snake_pos[0][1] < 0 or snake_pos[0][1] >= screen_height:
        game_over = True
    for pos in snake_pos[1:]:
        if pos == snake_pos[0]:
            game_over = True

    clock.tick(fps)

pygame.quit()
