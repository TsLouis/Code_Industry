```python
import pytest
import pygame
import random

# Add test cases here

def test_initial_snake_length():
    assert len(snake) == 1

def test_initial_food_position():
    assert food == (400, 400)

def test_initial_direction():
    assert direction == 'RIGHT'

def test_initial_score():
    assert score == 0

def test_snake_movement():
    keys = {pygame.K_RIGHT: 'RIGHT', pygame.K_LEFT: 'LEFT', pygame.K_UP: 'UP', pygame.K_DOWN: 'DOWN'}
    for key, dir in keys.items():
        keys[pygame.K_RIGHT] = dir
        assert keys[pygame.K_RIGHT] == dir

def test_wall_collision():
    x, y = -1, -1
    assert (x < 0 or x >= SCREEN_WIDTH or y < 0 or y >= SCREEN_HEIGHT)

def test_self_collision():
    snake = [(200, 200), (180, 200)]
    x, y = 180, 200
    assert (x, y) in snake

def test_food_collision():
    snake = [(200, 200)]
    food = (200, 220)
    x, y = 200, 220
    if (x, y) == food:
        snake.append(food)
        assert len(snake) == 2

def test_food_position():
    food = (800, 600)
    assert food[0] < SCREEN_WIDTH and food[1] < SCREEN_HEIGHT

def test_score_increment():
    score = 0
    x, y = 400, 400
    food = (400, 400)
    if (x, y) == food:
        score += 1
    assert score == 1

def test_snake_length_decrement():
    snake = [(200, 200), (180, 200)]
    x, y = 180, 200
    if (x, y) in snake:
        snake.pop()
    assert len(snake) == 1
```