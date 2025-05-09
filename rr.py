import pygame
import json
import colorsys

# Initialize color cycling variables
color_hue = 0
color_speed = 0.001

def get_background_color():
    global color_hue
    color_hue += color_speed
    if color_hue > 1:
        color_hue = 0
    r, g, b = colorsys.hsv_to_rgb(color_hue, 1, 1)
    return (int(r * 255), int(g * 255), int(b * 255))

def update_color_speed(ball_speed):
    global color_speed
    color_speed = min(0.005, 0.001 + (ball_speed / 50))

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Retro Rally")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (170, 170, 170)

# Paddle and Ball Properties
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
BALL_SIZE = 15

# Initialize Paddle at Bottom & Ball
player = pygame.Rect(WIDTH // 2 - PADDLE_WIDTH * 2, HEIGHT - 30, PADDLE_WIDTH * 5, PADDLE_HEIGHT // 3)
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

# Movement Speeds
START_SPEED = 2.5
SPEED_INCREMENT = 0.5
MAX_SPEED = 15
ball_speed_x, ball_speed_y = START_SPEED, START_SPEED

# Score & High Score System
score = 0
high_scores = {}
last_player_name = ""
last_player_score = 0

# Font setup
pygame.font.init()
font = pygame.font.Font(None, 36)

# Clock setup
clock = pygame.time.Clock()

# Load & Save High Scores
def save_high_scores():
    with open("high_scores.json", "w") as file:
        json.dump(high_scores, file)

def load_high_scores():
    global high_scores
    try:
        with open("high_scores.json", "r") as file:
            high_scores = json.load(file)
            if not isinstance(high_scores, dict):
                high_scores = {}
    except FileNotFoundError:
        high_scores = {}

load_high_scores()

# Show Menu
def show_menu():
    global last_player_name, last_player_score
    load_high_scores()
    while True:
        screen.fill(BLACK)
        title = font.render("Retro Rally", True, WHITE)
        instruction = font.render("Click Start or Press ENTER", True, WHITE)
        y_offset = HEIGHT // 3
        if last_player_name:
            last_score_text = font.render(f"Last: {last_player_name} - {last_player_score}", True, (255, 215, 0))
            screen.blit(last_score_text, (WIDTH // 2 - 120, y_offset - 40))
        sorted_scores = sorted(high_scores.items(), key=lambda x: x[1], reverse=True)[:10]
        for i, (player_name, player_score) in enumerate(sorted_scores):
            score_text = font.render(f"{i+1}. {player_name} - {player_score}", True, WHITE)
            screen.blit(score_text, (WIDTH // 2 - 120, y_offset))
            y_offset += 30
        start_button = pygame.Rect(WIDTH // 2 - 70, HEIGHT - 200, 140, 50)
        pygame.draw.rect(screen, WHITE, start_button)
        button_text = font.render("START", True, BLACK)
        screen.blit(title, (WIDTH // 2 - 100, HEIGHT // 8))
        screen.blit(instruction, (WIDTH // 2 - 180, HEIGHT // 4))
        screen.blit(button_text, (WIDTH // 2 - 30, HEIGHT - 190))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    return True

if not show_menu():
    exit()

# Game Over Screen with Blinking Cursor
def show_game_over_screen(final_score):
    global score, ball_speed_x, ball_speed_y, ball, last_player_name, last_player_score
    name = ""
    input_box = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 3 + 40, 240, 40)
    active = False
    cursor_visible = True
    cursor_timer = pygame.time.get_ticks()
    while True:
        screen.fill(BLACK)
        game_over_text = font.render("GAME OVER", True, WHITE)
        restart_instruction = font.render("Enter Your Name and Press ENTER", True, WHITE)
        box_color = WHITE if active else GRAY
        pygame.draw.rect(screen, box_color, input_box, 2)
        name_display = font.render(name, True, WHITE)
        screen.blit(name_display, (input_box.x + 10, input_box.y + 5))
        if active:
            if pygame.time.get_ticks() - cursor_timer > 500:
                cursor_visible = not cursor_visible
                cursor_timer = pygame.time.get_ticks()
            if cursor_visible:
                cursor = font.render("|", True, WHITE)
                screen.blit(cursor, (input_box.x + 10 + name_display.get_width(), input_box.y + 5))
        restart_button = pygame.Rect(WIDTH // 2 - 70, HEIGHT - 200, 140, 50)
        pygame.draw.rect(screen, WHITE, restart_button)
        button_text = font.render("RESTART", True, BLACK)
        screen.blit(game_over_text, (WIDTH // 2 - 80, HEIGHT // 5))
        screen.blit(restart_instruction, (WIDTH // 2 - 170, HEIGHT // 3))
        screen.blit(button_text, (WIDTH // 2 - 30, HEIGHT - 190))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN and name:
                        print(f"Saving high score: {name} - {final_score}")  # <--- THIS IS THE NEW LINE
                        high_scores[name] = max(high_scores.get(name, 0), final_score)
                        save_high_scores()
                        last_player_name = name
                        last_player_score = final_score
                        return show_menu()
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    elif len(name) < 12 and event.unicode.isprintable():
                        name += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False
                if restart_button.collidepoint(event.pos):
                    return show_menu()

# Game Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    mouse_x, _ = pygame.mouse.get_pos()
    player.x = max(0, min(WIDTH - player.width, mouse_x - player.width // 2))
    ball.x += int(ball_speed_x)
    ball.y += int(ball_speed_y)
    if ball.top <= 0:
        ball_speed_y *= -1
    if ball.left <= 0 or ball.right >= WIDTH:
        ball_speed_x *= -1
    if ball.colliderect(player) and ball_speed_y > 0:
        ball_speed_y = -min(MAX_SPEED, abs(ball_speed_y) + SPEED_INCREMENT)
        ball_speed_x = min(MAX_SPEED, ball_speed_x + SPEED_INCREMENT) if ball_speed_x > 0 else -min(MAX_SPEED, abs(ball_speed_x) + SPEED_INCREMENT)
        score += 1
    if ball.bottom >= HEIGHT:
        show_game_over_screen(score)
        score = 0
        ball.x, ball.y = WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2
        ball_speed_x, ball_speed_y = START_SPEED, START_SPEED
    screen.fill(get_background_color())
    update_color_speed(abs(ball_speed_y))
    pygame.draw.rect(screen, WHITE, player)
    pygame.draw.ellipse(screen, WHITE, ball)
    screen.blit(font.render(f"Score: {score}", True, WHITE), (WIDTH // 2 - 50, 20))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
