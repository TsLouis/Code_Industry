```python
import pygame
import sys

# 游戏初始化
pygame.init()

# 设置窗口大小
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Task Coordination Assistant Game")

# 游戏状态
START = 0
RUNNING = 1
END = 2
game_state = START

# 游戏主循环
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 处理用户输入
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and game_state == START:
        game_state = RUNNING
    elif keys[pygame.K_ESCAPE]:
        game_state = END

    # 渲染界面
    win.fill((255, 255, 255))
    if game_state == START:
        # 绘制开始界面
        font = pygame.font.SysFont("comicsans", 60)
        text = font.render("Press SPACE to start", 1, (0, 0, 0))
        win.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - text.get_height()/2))
    elif game_state == RUNNING:
        # 绘制游戏进行中界面
        pass
    elif game_state == END:
        # 绘制游戏结束界面
        font = pygame.font.SysFont("comicsans", 60)
        text = font.render("Game Over", 1, (255, 0, 0))
        win.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - text.get_height()/2))

    pygame.display.update()
```