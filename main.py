import pygame, sys
import imageio
import numpy as np

from DoublyLinkedMatrix import DoublyLinkedMatrix

# --- Setup ---
matrix_data = [
    [0, 0, 1, 0, 1, 1, 0],
    [1, 0, 0, 1, 0, 0, 1],
    [0, 1, 1, 0, 0, 1, 0],
    [1, 0, 0, 1, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 1],
    [0, 0, 0, 1, 1, 0, 1]
]
matrix = DoublyLinkedMatrix(matrix_data)
search_iterator = matrix.search(step_mode=True)

# --- Pygame setup ---
pygame.init()
cell_size = 60
cols = len(matrix_data[0])
rows = len(matrix_data)
total_width = (cols + 4) * cell_size
total_height = (rows + 3) * cell_size
screen = pygame.display.set_mode((total_width, total_height))
pygame.display.set_caption("Dancing Links Visualizer")
font = pygame.font.SysFont(None, 24)
bg_color = (30, 30, 30)
green = (0, 255, 0)
blue = (0, 0, 255)
overlay_half = cell_size // 2
grid_width = cols * cell_size
margin_x = (total_width - grid_width) // 2
margin_y = cell_size * 2
clock = pygame.time.Clock()

# fire an event every 1000ms
STEP_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(STEP_EVENT, 1000)

frames = []
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == STEP_EVENT:
            try:
                next(search_iterator)
            except StopIteration:
                running = False

    screen.fill(bg_color)

    # draw links
    for r in range(rows):
        y = margin_y + r * cell_size + cell_size // 2
        pygame.draw.line(screen, green, (0, y), (total_width, y), 2)
    for c in range(cols):
        x = margin_x + c * cell_size + cell_size // 2
        pygame.draw.line(screen, blue, (x, 0), (x, total_height), 2)

    # active columns
    active_cols = []
    h = matrix.header.right
    while h != matrix.header:
        active_cols.append(h)
        h = h.right

    # draw covered nodes
    for node in matrix.nodes:
        if node.row is not None and node.col not in active_cols:
            bx = margin_x + node.x * cell_size + cell_size // 2
            by = margin_y + node.y * cell_size + cell_size // 2
            rect = pygame.Rect(bx - overlay_half, by - overlay_half,
                               overlay_half*2, overlay_half*2)
            pygame.draw.rect(screen, bg_color, rect)

    # draw nodes
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
        rect = pygame.Rect(nx - 8, ny - 8, 16, 16)
        pygame.draw.rect(screen, color, rect, width=2)

    # draw text
    action_surf = font.render(matrix.current_action, True, (255, 255, 255))
    screen.blit(action_surf, (20, 20))
    sol_text = "Solution Stack: " + str(matrix.current_solution)
    sol_surf = font.render(sol_text, True, (255, 255, 255))
    screen.blit(sol_surf, (total_width - sol_surf.get_width() - 20, 20))

    pygame.display.flip()

    # capture frame
    buf = pygame.surfarray.array3d(screen)
    frame = np.transpose(buf, (1, 0, 2))
    frames.append(frame)

    clock.tick(60)

# write gif and cleanup
imageio.mimsave('stepbystep.gif', frames, duration=1)
pygame.quit()
sys.exit()
