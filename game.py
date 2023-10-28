import pygame
import random
from collections import namedtuple
# Constants
WIDTH, HEIGHT = 400, 400
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
WHITE = (255, 255, 255)
CUSTOM_GREEN = (33, 86, 50)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)


# Snake class
class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)  # Initial direction: right

    def move(self, food):
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

        self.body.insert(0, new_head)
        if new_head == food:
            return True
        else:
            self.body.pop()
            return False

    def set_direction(self, direction):
        if direction == 'UP':
            self.direction = (0, -1)
        elif direction == 'DOWN':
            self.direction = (0, 1)
        elif direction == 'LEFT':
            self.direction = (-1, 0)
        elif direction == 'RIGHT':
            self.direction = (1, 0)

    def get_head(self):
        return self.body[0]

    def is_collision(self):
        head = self.get_head()
        return (
            head[0] < 0 or head[0] >= GRID_WIDTH
            or head[1] < 0 or head[1] >= GRID_HEIGHT
            or head in self.body[1:]
        )
    

# Food class
class Food:
    def __init__(self):
        self.position = self.randomize_position()

    def randomize_position(self):
        return (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))

    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

# A* algorithm with Manhattan distance heuristic
def astar_search(snake, food):
    open_set = [snake.get_head()]
    came_from = {}

    g_score = {cell: float('inf') for cell in open_set}
    g_score[snake.get_head()] = 0

    f_score = {cell: g_score[cell] + manhattan_distance(cell, food.position) for cell in open_set}

    while open_set:
        current = min(open_set, key=lambda cell: f_score[cell])

        if current == food.position:
            return reconstruct_path(came_from, current)

        open_set.remove(current)

        for neighbor in get_neighbors(current):
            tentative_g_score = g_score[current] + 1

            if tentative_g_score < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + manhattan_distance(neighbor, food.position)

                if neighbor not in open_set:
                    open_set.append(neighbor)

    return None

def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_neighbors(cell):
    neighbors = [(cell[0] + 1, cell[1]), (cell[0] - 1, cell[1]), (cell[0], cell[1] + 1), (cell[0], cell[1] - 1)]
    return [neighbor for neighbor in neighbors if 0 <= neighbor[0] < GRID_WIDTH and 0 <= neighbor[1] < GRID_HEIGHT]

def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.insert(0, current)
    return path

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake Game with A* AI')
font = pygame.font.Font('arial.ttf', 20)
snake = Snake()
food = Food()
clock = pygame.time.Clock()
score = 0
# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # AI control
    path = astar_search(snake, food)
    if path:
        next_cell = path[1]
        head = snake.get_head()
        if next_cell[0] > head[0]:
            snake.set_direction('RIGHT')
        elif next_cell[0] < head[0]:
            snake.set_direction('LEFT')
        elif next_cell[1] > head[1]:
            snake.set_direction('DOWN')
        elif next_cell[1] < head[1]:
            snake.set_direction('UP')

    if snake.move(food.position):
        food.position = food.randomize_position()
        score += 1

    if snake.is_collision():
        running = False

    # Draw the game
    screen.fill(BLACK)

    for segment in snake.body:
        if segment == snake.get_head():
            pygame.draw.rect(screen, CUSTOM_GREEN, (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
            continue
        pygame.draw.rect(screen, GREEN, (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        text = font.render("Score: " + str(score), True, WHITE)
        screen.blit(text, [0, 0])
    food.draw(screen)
    pygame.display.update()
    clock.tick(10)
print('Final Score', score)
pygame.quit()
