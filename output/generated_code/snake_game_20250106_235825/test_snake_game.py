```python
import pytest
from game import *

def test_snake_initial_position():
    assert snake_pos == [[screen_width // 2, screen_height // 2]]

def test_snake_initial_length():
    assert snake_length == 1

def test_snake_initial_direction():
    assert snake_direction == 'RIGHT'

def test_food_initial_position():
    assert food_pos[0] % cell_size == 0
    assert food_pos[1] % cell_size == 0

def test_snake_move_right():
    snake_direction = 'RIGHT'
    snake_pos[0] = [100, 100]
    move_snake()
    assert snake_pos[0] == [120, 100]

def test_snake_move_left():
    snake_direction = 'LEFT'
    snake_pos[0] = [100, 100]
    move_snake()
    assert snake_pos[0] == [80, 100]

def test_snake_move_up():
    snake_direction = 'UP'
    snake_pos[0] = [100, 100]
    move_snake()
    assert snake_pos[0] == [100, 80]

def test_snake_move_down():
    snake_direction = 'DOWN'
    snake_pos[0] = [100, 100]
    move_snake()
    assert snake_pos[0] == [100, 120]

def test_snake_eat_food():
    snake_pos[0] = food_pos
    eat_food()
    assert snake_length == 2

def test_snake_hit_wall():
    snake_pos[0] = [-1, 100]
    assert check_collision() == True

def test_snake_hit_self():
    snake_pos[0] = [100, 100]
    snake_pos.append([100, 100])
    assert check_collision() == True

def test_user_input():
    change_direction(pygame.K_LEFT)
    assert snake_direction == 'LEFT'
    change_direction(pygame.K_RIGHT)
    assert snake_direction == 'RIGHT'
    change_direction(pygame.K_UP)
    assert snake_direction == 'UP'
    change_direction(pygame.K_DOWN)
    assert snake_direction == 'DOWN'

def test_edge_conditions():
    snake_pos[0] = [screen_width - cell_size, screen_height - cell_size]
    snake_direction = 'RIGHT'
    move_snake()
    assert snake_pos[0] == [0, screen_height - cell_size]

def test_exception():
    with pytest.raises(IndexError):
        del snake_pos[-1]
```