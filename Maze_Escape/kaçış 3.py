import pygame
import random
import sys
import collections
import time
import os

# ---------- AYARLAR ----------
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 40
ROWS, COLS = HEIGHT // TILE_SIZE, WIDTH // TILE_SIZE
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (200, 50, 50)
ENEMY_COLOR = (50, 100, 255)
EXIT_COLOR = (50, 200, 50)
TEXT_COLOR = (255, 215, 0)

HIGHSCORE_FILE = "highscore.txt"

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kaç Bakalım")
clock = pygame.time.Clock()
font_small = pygame.font.Font(None, 28)
font_big = pygame.font.Font(None, 72)

# ---------- LABİRENT ÜRETİMİ ----------
def generate_maze(rows, cols):
    maze = [[0 for _ in range(cols)] for _ in range(rows)]
    visited = [[False for _ in range(cols)] for _ in range(rows)]

    def dfs(r, c):
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        random.shuffle(directions)
        visited[r][c] = True
        maze[r][c] = 1
        for dr, dc in directions:
            nr, nc = r + dr * 2, c + dc * 2
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                maze[r + dr][c + dc] = 1
                dfs(nr, nc)

    sr, sc = random.randrange(0, rows, 2), random.randrange(0, cols, 2)
    dfs(sr, sc)
    return maze, (sr, sc)

# ---------- LABİRENTE EKSTRA YOLLAR AÇ ----------
def add_extra_paths(maze, count=20):
    rows, cols = len(maze), len(maze[0])
    for _ in range(count):
        r = random.randint(1, rows-2)
        c = random.randint(1, cols-2)
        maze[r][c] = 1

# ---------- BFS PATHFINDING ----------
def bfs_path(start, goal, maze):
    rows, cols = len(maze), len(maze[0])
    q = collections.deque()
    q.append((start[0], start[1]))
    parent = {(start[0], start[1]): None}
    dirs = [(0,1),(1,0),(0,-1),(-1,0)]
    while q:
        r, c = q.popleft()
        if [r, c] == goal:
            path = []
            cur = (r, c)
            while cur is not None:
                path.append([cur[0], cur[1]])
                cur = parent[cur]
            path.reverse()
            return path
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 1 and (nr, nc) not in parent:
                parent[(nr, nc)] = (r, c)
                q.append((nr, nc))
    return None

# ---------- HIGH SCORE ----------
def load_highscore():
    if not os.path.exists(HIGHSCORE_FILE):
        return None
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return float(f.read().strip())
    except:
        return None

def save_highscore(value):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(value))
    except:
        pass

# ---------- BUTON ÇİZME ----------
def draw_button(text, x, y, w, h, inactive_color, active_color):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, w, h)
    if rect.collidepoint(mouse):
        pygame.draw.rect(screen, active_color, rect)
        if click[0] == 1:
            return True
    else:
        pygame.draw.rect(screen, inactive_color, rect)

    text_surf = font_small.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    return False

# ---------- MENÜ ----------
def menu():
    highscore = load_highscore()
    while True:
        screen.fill((30, 30, 30))
        title_text = font_big.render("Kaç Bakalım", True, TEXT_COLOR)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//3))

        if highscore is not None:
            hs_text = font_small.render(f"Best Time: {highscore:.2f}s", True, TEXT_COLOR)
            screen.blit(hs_text, (WIDTH//2 - hs_text.get_width()//2, HEIGHT//3 + 100))

        play_clicked = draw_button("Play", WIDTH//2 - 75, HEIGHT//2, 150, 50, WHITE, (200,200,200))
        quit_clicked = draw_button("Quit", WIDTH//2 - 75, HEIGHT//2 + 70, 150, 50, WHITE, (200,200,200))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

        if play_clicked:
            return 'play'
        if quit_clicked:
            quit_game()

        pygame.display.flip()
        clock.tick(60)

# ---------- ÇIKIŞ ----------
def quit_game():
    pygame.quit()
    sys.exit()

# ---------- OYUN DÖNGÜSÜ ----------
def game_loop():
    maze, _ = generate_maze(ROWS, COLS)
    add_extra_paths(maze, count=20)

    # Oyuncu başlangıç
    player_pos = [0, 0]
    while maze[player_pos[0]][player_pos[1]] == 0:
        player_pos[1] += 1
        if player_pos[1] >= COLS:
            player_pos[1] = 0
            player_pos[0] += 1

    # Düşman başlangıç
    enemy_pos = [ROWS - 1, COLS - 1]
    while maze[enemy_pos[0]][enemy_pos[1]] == 0:
        enemy_pos[1] -= 1
        if enemy_pos[1] < 0:
            enemy_pos[1] = COLS - 1
            enemy_pos[0] -= 1

    # Çıkış konumu
    exit_pos = [0, COLS - 1]
    if maze[exit_pos[0]][exit_pos[1]] == 0:
        for c in range(COLS-1, -1, -1):
            if maze[0][c] == 1:
                exit_pos = [0, c]
                break

    highscore = load_highscore()
    start_time = time.time()
    enemy_move_cooldown = 0.2
    last_enemy_move = time.time()
    move_cooldown = 0.12
    last_move = 0
    win = False
    lose = False

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        now = time.time()
        screen.fill(BLACK)

        # Labirent çizimi
        for r in range(ROWS):
            for c in range(COLS):
                if maze[r][c] == 1:
                    pygame.draw.rect(screen, WHITE, (c*TILE_SIZE, r*TILE_SIZE, TILE_SIZE, TILE_SIZE))

        pygame.draw.rect(screen, EXIT_COLOR, (exit_pos[1]*TILE_SIZE, exit_pos[0]*TILE_SIZE, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(screen, PLAYER_COLOR, (player_pos[1]*TILE_SIZE, player_pos[0]*TILE_SIZE, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(screen, ENEMY_COLOR, (enemy_pos[1]*TILE_SIZE, enemy_pos[0]*TILE_SIZE, TILE_SIZE, TILE_SIZE))

        elapsed = now - start_time
        screen.blit(font_small.render(f"Time: {elapsed:.2f}s", True, TEXT_COLOR), (10, 10))
        if highscore is not None:
            screen.blit(font_small.render(f"Best: {highscore:.2f}s", True, TEXT_COLOR), (10, 34))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

        keys = pygame.key.get_pressed()
        if not win and not lose and now - last_move > move_cooldown:
            moved = False
            if keys[pygame.K_UP] and player_pos[0] > 0 and maze[player_pos[0]-1][player_pos[1]] == 1:
                player_pos[0] -= 1; moved = True
            elif keys[pygame.K_DOWN] and player_pos[0] < ROWS-1 and maze[player_pos[0]+1][player_pos[1]] == 1:
                player_pos[0] += 1; moved = True
            elif keys[pygame.K_LEFT] and player_pos[1] > 0 and maze[player_pos[0]][player_pos[1]-1] == 1:
                player_pos[1] -= 1; moved = True
            elif keys[pygame.K_RIGHT] and player_pos[1] < COLS-1 and maze[player_pos[0]][player_pos[1]+1] == 1:
                player_pos[1] += 1; moved = True
            if moved: last_move = now

        # Düşman AI
        if not win and not lose and now - last_enemy_move > enemy_move_cooldown:
            enemy_path = bfs_path(enemy_pos, player_pos, maze)
            if enemy_path and len(enemy_path) > 1:
                enemy_pos = enemy_path[1]
            last_enemy_move = now

        if player_pos == exit_pos and not win:
            win = True
            finish_time = now - start_time
            if highscore is None or finish_time < highscore:
                save_highscore(finish_time)
                highscore = finish_time

        if player_pos == enemy_pos and not lose:
            lose = True

        if win:
            txt = font_big.render("Kazandın!", True, (255, 80, 80))
            screen.fill(BLACK)
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - txt.get_height()//2))

            play_clicked = draw_button("Play", WIDTH//2 - 75, HEIGHT//2 + 80, 150, 50, WHITE, (200,200,200))

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 'menu'

            if play_clicked:
                return 'play'

        elif lose:
            txt = font_big.render("Yakalandın!", True, (255, 80, 80))
            screen.fill(BLACK)
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - txt.get_height()//2))

            retry_clicked = draw_button("Tekrar Dene", WIDTH//2 - 75, HEIGHT//2 + 80, 150, 50, WHITE, (200,200,200))

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 'menu'

            if retry_clicked:
                return 'play'

        pygame.display.flip()

# ---------- ANA DÖNGÜ ----------
def main():
    while True:
        action = menu()
        if action == 'play':
            while True:
                result = game_loop()
                if result == 'menu':
                    break
                elif result == 'play':
                    continue
        else:
            break

main()
