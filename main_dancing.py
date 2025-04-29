import pygame
import sys
import random
import imageio
from pygame import surfarray
from DoublyLinkedMatrix import DoublyLinkedMatrix

# --- Configuration for random matrix ---
rows = 15
cols = 15
density = 0.5   # probability of 1 in each cell

def generate_matrix(r, c, d):
    return [[1 if random.random() < d else 0 for _ in range(c)] for _ in range(r)]

matrix_data = generate_matrix(rows, cols, density)
matrix = DoublyLinkedMatrix(matrix_data)
search_iterator = matrix.search(step_mode=True)

pygame.init()
cell_size = 40
total_width = (cols + 4) * cell_size
total_height = (rows + 4) * cell_size
screen = pygame.display.set_mode((total_width, total_height))
pygame.display.set_caption("Dancing Links Random Matrix")
font = pygame.font.SysFont(None, 20)
bg_color = (30, 30, 30)
green = (0, 255, 0)
blue = (0, 0, 255)
overlay_half = cell_size // 2
margin_x = (total_width - cols * cell_size) // 2
margin_y = cell_size * 2
clock = pygame.time.Clock()

frames = []
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    try:
        next(search_iterator)
    except StopIteration:
        break

    screen.fill(bg_color)

    active_cols = []
    h = matrix.header.right
    while h != matrix.header:
        active_cols.append(h)
        h = h.right

    for r in range(rows):
        y = margin_y + r * cell_size + cell_size // 2
        pygame.draw.line(screen, green, (0, y), (total_width, y), 1)
    for c in range(cols):
        x = margin_x + c * cell_size + cell_size // 2
        pygame.draw.line(screen, blue, (x, 0), (x, total_height), 1)

    for node in matrix.nodes:
        if node.row is not None and node.col not in active_cols:
            bx = margin_x + node.x * cell_size + cell_size // 2
            by = margin_y + node.y * cell_size + cell_size // 2
            rect = pygame.Rect(bx - overlay_half, by - overlay_half,
                               overlay_half * 2, overlay_half * 2)
            pygame.draw.rect(screen, bg_color, rect)

    for node in matrix.nodes:
        nx = margin_x + node.x * cell_size + cell_size // 2
        ny = margin_y + node.y * cell_size + cell_size // 2
        if node.col == matrix.current_column and node.row is None:
            color = green
        elif node == matrix.current_row:
            color = blue
        elif node.row is not None and node.col not in active_cols:
            color = (80, 80, 80)
        elif node.row is None:
            color = (255, 255, 0)
        else:
            color = (0, 200, 200)
        rect = pygame.Rect(nx - 6, ny - 6, 12, 12)
        pygame.draw.rect(screen, color, rect, 1)

    sol_text = "Stack: " + str(matrix.current_solution)
    sol_surf = font.render(sol_text, True, (255, 255, 255))
    screen.blit(sol_surf, (total_width - sol_surf.get_width() - 10, 10))

    pygame.display.flip()
    frames.append(surfarray.array3d(screen).swapaxes(0, 1))
    clock.tick(30)

pygame.quit()

imageio.mimsave('dancing.gif', frames, fps=30)
sys.exit()
