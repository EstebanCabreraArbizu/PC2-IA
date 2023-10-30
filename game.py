import pygame
import sys
import random
import heapq

# Inicialización de Pygame
pygame.init()

# Configuración del juego
WIDTH, HEIGHT = 800, 400  # Ancho doble para la pantalla dividida
GRID_SIZE = 20
GRID_WIDTH = WIDTH // (2 * GRID_SIZE)  # Dividido en 2 para la pantalla dividida
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 7

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
HEAD_COLOR = (0, 128, 0)  # Color de la cabeza de la serpiente (verde oscuro)

# Inicialización de la pantalla dividida
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Menu del area
areaMenu = pygame.display.set_mode((WIDTH, HEIGHT))

# Divide la pantalla en dos áreas iguales
area1 = screen.subsurface(0, 0, WIDTH // 2, HEIGHT)
area2 = screen.subsurface(WIDTH // 2, 0, WIDTH // 2, HEIGHT)

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.g = 0
        self.h = 0
        self.f = 0
        self.parent = None

    def __lt__(self, other):
        return self.f < other.f

class Snake:
    def __init__(self, area):
        self.body = [(GRID_WIDTH // 4, GRID_HEIGHT // 2)]
        self.direction = (0, 0)
        self.is_hungry = True
        self.area = area
        self.score = 0 #Puntaje de la serpiente

    def grow(self):
        tail = self.body[-1]
        dx, dy = self.direction
        new_tail = (tail[0] - dx, tail[1] - dy)
        self.body.append(new_tail)

    def move(self, apple):
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        self.body.insert(0, new_head)

        if new_head == apple.position:
            apple.randomize_position(self)
            self.grow()
            self.score += 1 #Obtiene más puntaje
            self.is_hungry = len(self.body) < GRID_WIDTH * GRID_HEIGHT
        else:
            self.body.pop()

class Apple:
    def __init__(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))

    def randomize_position(self, snake):
        while True:
            new_position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if new_position not in snake.body:
                self.position = new_position
                break

def manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def find_path(grid, start, end, body):
    open_list = []
    closed_set = set()

    start_node = Node(start[0], start[1])
    end_node = Node(end[0], end[1])

    heapq.heappush(open_list, start_node)

    while open_list:
        current = heapq.heappop(open_list)

        if current.x == end_node.x and current.y == end_node.y:
            path = []
            while current:
                path.append((current.x, current.y))
                current = current.parent
            return path[::-1]

        closed_set.add((current.x, current.y))

        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            x, y = current.x, current.y
            new_x, new_y = x + dx, y + dy

            if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:
                neighbor = Node(new_x, new_y)
                if (
                    grid[new_y][new_x] != 1
                    and (neighbor.x, neighbor.y) not in closed_set
                    and (neighbor.x, neighbor.y) not in body
                ):
                    neighbor.g = current.g + 1
                    neighbor.h = manhattan_distance((neighbor.x, neighbor.y), (end_node.x, end_node.y))
                    neighbor.f = neighbor.g + neighbor.h
                    neighbor.parent = current
                    heapq.heappush(open_list, neighbor)

    return None
def show_winner(winner, snake1score, snake2score):
    font = pygame.font.Font(None, 36)
    winner = [
        f"{winner}",
        "",
        "Puntajes",
        "",
        "Player: "f"{snake1score}",
        "IA: "f"{snake2score}",
        "",
        "Presiona ENTER para continuar",
    ]
    areaMenu.fill(BLACK)
    for i, line in enumerate(winner):
        text = font.render(line, True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, 50 + i * 30))
        areaMenu.blit(text, text_rect)
    pygame.display.update()
    waiting_for_enter = True
    while waiting_for_enter:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting_for_enter = False

def show_instructions():
    instructions = [
        "Instrucciones:",
        "Tu controlas a la serpiente en la caja blanca, mientras que la IA controla la serpeiente en la caja negra.",
        "El objetivo es comer tantas manzanas como puedas antes de morir.",
        "Usa las flechas direccionales (o las teclas'W', 'A', 'S', 'D') para controlar la dirección de tu serpiente.",
        "Si deseas terminar el juego puedes presionar la tecla 'escape' (ESC)",
        "!DISFRUTA!",
        "",
        "Presiona ENTER para continuar",
    ]

    font = pygame.font.Font('arial.ttf', 17)
    areaMenu.fill(BLACK)
    for i, line in enumerate(instructions):
        text = font.render(line, True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, 50 + i * 30))
        areaMenu.blit(text, text_rect)
    pygame.display.update()
    waiting_for_enter = True
    while waiting_for_enter:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting_for_enter = False
def return_to_menu():
   main()  # Calls the main menu function to return to the main menu.

def run_game():
    snake2 = Snake(area2)  # IA
    snake1 = Snake(area1)  # Jugador
    apple1 = Apple()  # Manzana para el jugador
    apple2 = Apple()  # Manzana para la IA
    snake1_die = False
    snake2_die = False

    clock = pygame.time.Clock()
    font = pygame.font.Font('arial.ttf', 20)
    waiting_for_other_to_die_snake1 = False
    waiting_for_other_to_die_snake2 = False
    
    # Direcciones opuestas (para evitar que el jugador se voltee)
    opposite_directions = {
        (1, 0): (-1, 0), # Derecha <-> Izquierda
        (-1, 0): (1, 0), # Izquierda <-> Derecha
        (0, 1): (0, -1), # Abajo <-> Arriba
        (0, -1): (0, 1)  # Arriba <-> Abajo
    }

    while True:
        grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)] # Inicializa la cuadrícula en cada iteración

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == ord('w'):
                    if snake1.direction != (0, 1): # Evita el movimiento hacia abajo si la serpiente se mueve hacia arriba
                        snake1.direction = (0, -1) # Arriba
                elif event.key == pygame.K_DOWN or event.key == ord('s'):
                    if snake1.direction != (0, -1): # Evita el movimiento hacia arriba si la serpiente se mueve hacia abajo
                        snake1.direction = (0, 1) # Abajo
                elif event.key == pygame.K_LEFT or event.key == ord('a'):
                    if snake1.direction != (1, 0): # Evita el movimiento hacia la derecha si la serpiente se mueve hacia la izquierda
                        snake1.direction = (-1, 0) # Izquierda
                elif event.key == pygame.K_RIGHT or event.key == ord('d'):
                    if snake1.direction != (-1, 0): # Evita el movimiento hacia la izquierda si la serpiente se mueve hacia la derecha
                        snake1.direction = (1, 0) # Derecha
                #Terminar el juego
                elif event.key == pygame.K_ESCAPE:
                    GameOver()
                         
        # Marcar la serpiente en el mapa
        for segment in snake2.body:
            x, y = segment
            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                grid[y][x] = 2  # En el caso de la serpiente IA

        # Marcar la serpiente en el mapa (Jugador)
        for segment in snake1.body:
            x, y = segment
            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                grid[y][x] = 4  # En el caso de la serpiente del jugador

        # Marcar las manzanas en el mapa
        x1, y1 = apple1.position
        x2, y2 = apple2.position
        grid[y1][x1] = 3
        grid[y2][x2] = 5

        # Generar una nueva posición para la manzana si es necesario
        if snake1.body[0] == apple1.position:
            apple1.randomize_position(snake1)
        if snake2.body[0] == apple2.position:
            apple2.randomize_position(snake2)

        # Implementar A* aquí (planificar la ruta desde la cabeza de la serpiente hasta la manzana)
        if snake2.is_hungry: # Puedes agregar una condición para planificar la ruta solo cuando la serpiente tiene hambre
            path = find_path(grid, snake2.body[0], apple2.position, snake2.body)
            if path:
                next_position = path[1] # La siguiente posición en la ruta
                dx = next_position[0] - snake2.body[0][0]
                dy = next_position[1] - snake2.body[0][1]

                if (dx, dy) != opposite_directions.get(snake2.direction, (0, 0)):
                    snake2.direction = (dx, dy)

        # Moviemientos de los jugadores solo si estan vivos
        if not snake1_die:
            snake1.move(apple1)
        if not snake2_die:
            snake2.move(apple2)

        # Verificar colisiones
        head = snake2.body[0]
        if (
            head[0] < 0
            or head[0] >= GRID_WIDTH
            or head[1] < 0
            or head[1] >= GRID_HEIGHT
            or head in snake2.body[1:]
        ):
            # show_winner("Jugador" if snake1.score > snake2.score else "Gana la IA")
            # return_to_menu()
            waiting_for_other_to_die_snake2 = True
            snake2.direction = (0, 0)
            snake2_die = True

        # Verificar colisiones (Jugador)
        head = snake1.body[0]
        if (
            head[0] < 0
            or head[0] >= GRID_WIDTH
            or head[1] < 0
            or head[1] >= GRID_HEIGHT
            or head in snake1.body[1:]
        ):
            # show_winner("IA" if snake2.score > snake1.score else "Ganaste")
            # return_to_menu()
            waiting_for_other_to_die_snake1 = True
            snake1.direction = (0, 0)
            snake1_die = True
        
        def GameOver():
            if snake1.score > snake2.score:
                show_winner("YOU WINS", snake1.score, snake2.score)
            else:
                show_winner("IA WINS", snake1.score, snake2.score)
            return_to_menu()
        
        # Solo si los 2 jugadores murieron se dice al ganador
        if waiting_for_other_to_die_snake1 and waiting_for_other_to_die_snake2:
            GameOver()
                
        # Dibuja la pantalla y los elementos del juego
        area2.fill(BLACK)
        area1.fill(WHITE)
        
        text = font.render("Manzanas Comidas: " + str(snake1.score), True, BLACK)
        area1.blit(text, [0, 0])
        text = font.render("Manzanas Comidas: " + str(snake2.score), True, WHITE)
        area2.blit(text, [0,0])
        
        # Dibuja las serpientes y la manzana
        # Dibuja el cuerpo de la serpiente(PLAYER)
        for segment in snake1.body[1:]:
            pygame.draw.rect(area1, GREEN, (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        # Dibuja la cabeza de la serpiente (color personalizado)
        pygame.draw.rect(area1, HEAD_COLOR, (snake1.body[0][0] * GRID_SIZE, snake1.body[0][1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        # Dibuja la manzana
        pygame.draw.rect(area1, (255, 0, 0), (apple1.position[0] * GRID_SIZE, apple1.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        # Dibuja el cuerpo de la serpiente (IA)
        for segment in snake2.body[1:]:
            pygame.draw.rect(area2, GREEN, (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        # Dibuja la cabeza de la serpiente (color personalizado)
        pygame.draw.rect(area2, HEAD_COLOR, (snake2.body[0][0] * GRID_SIZE, snake2.body[0][1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        # Dibuja la manzana
        pygame.draw.rect(area2, (255, 0, 0), (apple2.position[0] * GRID_SIZE, apple2.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        pygame.display.update()
        clock.tick(FPS)

class GameOver(Exception):
    pass

def main():
    # MENU
    menu_options = ["Iniciar Juego", "Instrucciones", "Salir"]
    current_option = 0  # Opción seleccionada actualmente
    in_menu = True
    # Definición de la fuente para el menú
    font = pygame.font.Font(None, 36)

    while in_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    current_option = (current_option - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    current_option = (current_option + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    if current_option == 0:  # "Iniciar Juego"
                        try:
                            run_game()
                        except GameOver:
                            pass  # Continuar con el menú después de que el juego termine
                    elif current_option == 1:  # "Instrucciones"
                        show_instructions()
                        # Mostrar instrucciones (puedes implementarlo)
                    elif current_option == 2:  # "Salir"
                        pygame.quit()
                        sys.exit()

        area1.fill(BLACK)
        area2.fill(BLACK)
        
        # Calcular el centro de la pantalla
        center_x = WIDTH // 2
        center_y = HEIGHT // 2
        # Ajustar el desplazamiento vertical del texto
        for i, option in enumerate(menu_options):
            if i == current_option:
                color = (255, 165, 0)  # Color resaltado para la opción seleccionada
            else:
                color = WHITE
            text = font.render(option, True, color)
            text_rect = text.get_rect(center=(center_x, center_y + (i - 1) * 40))  # Alinea verticalmente el texto
            areaMenu.blit(text, text_rect)  # Dibuja el menú 

        pygame.display.update()

if __name__ == "__main__":
    main()
