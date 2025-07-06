import sys
import os
if sys.platform == "win32":
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

import pygame
import random
import time

# Initialize
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rhythm Game")

# Load and set window icon
logo_image = pygame.image.load(os.path.join("assets", "logo.png"))
pygame.display.set_icon(logo_image)

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 36)
small_font = pygame.font.SysFont("Arial", 24)

# Paths
hit_sound_path = os.path.join("assets", "hit.wav")
menu_music_path = os.path.join("assets", "menu_music.wav")

# Load hit sound
try:
    hit_sound = pygame.mixer.Sound(hit_sound_path)
except Exception as e:
    print("Failed to load hit sound:", e)
    hit_sound = None

# Set music volume
pygame.mixer.music.set_volume(0.5)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
GREEN = (0, 200, 0)
BLUE = (0, 100, 255)
RED = (200, 0, 0)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)
ORANGE = (255, 140, 0)

# Constants
ARROW_SIZE = 60
HIT_WINDOW = 80
TARGET_Y = HEIGHT - 100

# Lanes and key mappings
lanes = {
    'A': 100,
    'S': 200,
    'NUMPAD5': 300,
    'NUMPAD6': 400
}
custom_key_map = {
    pygame.K_a: 'A',
    pygame.K_s: 'S',
    pygame.K_KP5: 'NUMPAD5',
    pygame.K_KP6: 'NUMPAD6'
}
arrow_color = WHITE

# Health loss and win scores per difficulty
health_loss_per_mode = {6: 10, 9: 15, 12: 20, 16: 30}
win_score_per_mode = {6: 10000, 9: 20000, 12: 40000, 16: 200000}

# Arrow class
class Arrow:
    def __init__(self, key, fall_speed):
        self.key = key
        self.x = lanes[key]
        self.y = -ARROW_SIZE
        self.hit = False
        self.speed = fall_speed
        self.spawn_time = time.time()

    def move(self, dt):
        self.y += self.speed * dt * 60

    def draw(self, surface):
        if not self.hit:
            pygame.draw.rect(surface, arrow_color, (self.x, self.y, ARROW_SIZE, ARROW_SIZE))
            label = font.render(get_key_display(self.key), True, BLACK)
            surface.blit(label, (self.x + 20, self.y + 10))

def get_key_display(key_str):
    for code, val in custom_key_map.items():
        if val == key_str:
            name = pygame.key.name(code)
            return name.upper()
    return key_str[-1]

# Button helpers
def draw_button(text, x, y, width, height, color):
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, WHITE, rect, 3)
    label = font.render(text, True, WHITE)
    screen.blit(label, (x + width // 2 - label.get_width() // 2, y + height // 2 - label.get_height() // 2))
    return rect

def draw_small_button(text, x, y, width, height, color):
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, WHITE, rect, 2)
    label = small_font.render(text, True, WHITE)
    screen.blit(label, (x + width // 2 - label.get_width() // 2, y + height // 2 - label.get_height() // 2))
    return rect

def show_message_screen():
    message = (
        "Hello! thank you for downloading my game.\n"
        "even tho this game is really bad.\n"
        "dont expect much from a 13 year old.\n"
        "yep! a 13 year old made this.\n"
        "I even made the sound track.\n"
        "If you could just share this game to somebody\n"
        "that would be great!"
    )
    lines = message.split("\n")
    running = True
    while running:
        screen.fill(BLACK)
        y_start = 150
        for i, line in enumerate(lines):
            label = small_font.render(line, True, WHITE)
            screen.blit(label, (WIDTH // 2 - label.get_width() // 2, y_start + i*40))

        info = small_font.render("Press any key or click to return", True, GRAY)
        screen.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT - 80))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                running = False

def settings_menu():
    global custom_key_map, arrow_color
    changing_key = None
    colors = [WHITE, RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE]
    color_index = colors.index(arrow_color)

    while True:
        screen.fill(BLACK)
        title = font.render("Settings", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

        back_btn = draw_button("⬅ BACK", WIDTH // 2 - 100, 700, 200, 60, GRAY)
        color_btn = draw_button(f"Arrow Color", WIDTH // 2 - 100, 150, 200, 60, colors[color_index])

        y_pos = 250
        for key, lane in sorted(lanes.items(), key=lambda x: x[1]):
            display = get_key_display(key)
            btn = draw_button(f"{key} = {display}", WIDTH // 2 - 100, y_pos, 200, 60, GRAY)
            if changing_key == key:
                pygame.draw.rect(screen, RED, btn, 3)
            y_pos += 80

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(event.pos):
                    return
                elif color_btn.collidepoint(event.pos):
                    color_index = (color_index + 1) % len(colors)
                    arrow_color = colors[color_index]
                y_pos = 250
                for key, lane in sorted(lanes.items(), key=lambda x: x[1]):
                    btn = pygame.Rect(WIDTH // 2 - 100, y_pos, 200, 60)
                    if btn.collidepoint(event.pos):
                        changing_key = key
                    y_pos += 80
            elif event.type == pygame.KEYDOWN and changing_key:
                # Remove old key if it exists
                keys_to_remove = [k for k, v in custom_key_map.items() if v == changing_key]
                for k in keys_to_remove:
                    del custom_key_map[k]
                custom_key_map[event.key] = changing_key
                changing_key = None

def main_menu():
    if not pygame.mixer.music.get_busy():
        try:
            pygame.mixer.music.load(menu_music_path)
            pygame.mixer.music.play(-1)
        except pygame.error as e:
            print("Failed to load menu music:", e)

    while True:
        screen.fill(BLACK)
        title = font.render("[Select Difficulty]", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        easy_btn = draw_button("[E] EASY", WIDTH // 2 - 100, 200, 200, 60, GREEN)
        medium_btn = draw_button("[M] MEDIUM", WIDTH // 2 - 100, 290, 200, 60, BLUE)
        insane_btn = draw_button("[I] INSANE", WIDTH // 2 - 100, 380, 200, 60, RED)
        unfair_btn = draw_button("[U] UNFAIR", WIDTH // 2 - 100, 470, 200, 60, PURPLE)
        auto_btn = draw_button("[A] AUTO", WIDTH // 2 - 100, 560, 200, 60, ORANGE)
        settings_btn = draw_small_button("⚙ SETTINGS", 20, 20, 150, 40, GRAY)
        message_btn = draw_small_button("a message for you", WIDTH // 2 - 100, 700, 200, 40, GRAY)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if easy_btn.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    return {"mode": "manual", "fall_speed": 6, "spawn_rate": 16}
                elif medium_btn.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    return {"mode": "manual", "fall_speed": 9, "spawn_rate": 10}
                elif insane_btn.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    return {"mode": "manual", "fall_speed": 12, "spawn_rate": 6}
                elif unfair_btn.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    return {"mode": "manual", "fall_speed": 16, "spawn_rate": 2}
                elif auto_btn.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    return auto_difficulty_menu()
                elif settings_btn.collidepoint(event.pos):
                    settings_menu()
                elif message_btn.collidepoint(event.pos):
                    show_message_screen()
def auto_difficulty_menu():
    while True:
        screen.fill(BLACK)
        title = font.render("[Auto Difficulty]", True, ORANGE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        easy_btn = draw_button("[E] EASY", WIDTH // 2 - 100, 200, 200, 60, GREEN)
        medium_btn = draw_button("[M] MEDIUM", WIDTH // 2 - 100, 290, 200, 60, BLUE)
        insane_btn = draw_button("[I] INSANE", WIDTH // 2 - 100, 380, 200, 60, RED)
        unfair_btn = draw_button("[U] UNFAIR", WIDTH // 2 - 100, 470, 200, 60, PURPLE)
        back_btn = draw_button("⬅ BACK", WIDTH // 2 - 100, 560, 200, 60, GRAY)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if easy_btn.collidepoint(event.pos):
                    return {"mode": "auto", "fall_speed": 6, "spawn_rate": 16}
                elif medium_btn.collidepoint(event.pos):
                    return {"mode": "auto", "fall_speed": 9, "spawn_rate": 10}
                elif insane_btn.collidepoint(event.pos):
                    return {"mode": "auto", "fall_speed": 12, "spawn_rate": 6}
                elif unfair_btn.collidepoint(event.pos):
                    return {"mode": "auto", "fall_speed": 16, "spawn_rate": 2}
                elif back_btn.collidepoint(event.pos):
                    if not pygame.mixer.music.get_busy():
                        try:
                            pygame.mixer.music.load(menu_music_path)
                            pygame.mixer.music.play(-1)
                        except pygame.error as e:
                            print("Failed to load menu music:", e)
                    return main_menu()

def draw_main_menu_button():
    return draw_button("MAIN MENU", WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 60, GRAY)

def draw_stop_auto_button():
    rect = pygame.Rect(WIDTH - 110, 10, 100, 40)
    pygame.draw.rect(screen, ORANGE, rect)
    pygame.draw.rect(screen, WHITE, rect, 2)
    label = font.render("Stop Auto", True, WHITE)
    screen.blit(label, (rect.x + rect.width//2 - label.get_width()//2, rect.y + rect.height//2 - label.get_height()//2))
    return rect

def run_game(settings):
    arrows = []
    spawn_timer = 0
    score = 0
    health = 100
    game_over = False
    win = False

    fall_speed = settings["fall_speed"]
    health_loss = health_loss_per_mode.get(fall_speed, 20)
    win_score = win_score_per_mode.get(fall_speed, 40000)

    while True:
        dt = clock.tick(60) / 1000
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if not game_over and not win and settings["mode"] == "manual":
                if event.type == pygame.KEYDOWN and event.key in custom_key_map:
                    lane = custom_key_map[event.key]
                    hit = False
                    for arrow in arrows:
                        if arrow.key == lane and not arrow.hit:
                            if abs(arrow.y - TARGET_Y) < HIT_WINDOW:
                                arrow.hit = True
                                score += 100
                                health = min(100, health + 10)
                                hit = True
                                if hit_sound:
                                    hit_sound.play()
                                break
                    if not hit:
                        score -= 25
                        health -= health_loss
            elif game_over or win:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if main_menu_button.collidepoint(event.pos):
                        pygame.mixer.music.play(-1)
                        return
            elif settings["mode"] == "auto":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if stop_auto_button.collidepoint(event.pos):
                        return

        if not game_over and not win:
            spawn_timer += 1
            if spawn_timer >= settings["spawn_rate"]:
                arrows.append(Arrow(random.choice(list(lanes.keys())), fall_speed))
                spawn_timer = 0

            if settings["mode"] == "auto":
                for arrow in arrows:
                    if not arrow.hit and abs(arrow.y - TARGET_Y) < HIT_WINDOW:
                        arrow.hit = True
                        score += 100
                        health = min(100, health + 10)
                        if hit_sound:
                            hit_sound.play()

            for arrow in arrows:
                arrow.move(dt)
                arrow.draw(screen)

            for key, x in lanes.items():
                pygame.draw.rect(screen, RED, (x, TARGET_Y, ARROW_SIZE, ARROW_SIZE), 3)

            screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
            screen.blit(font.render(f"Health: {health}", True, GREEN if health > 30 else RED), (WIDTH - 200, 10))

            remaining_arrows = []
            for arrow in arrows:
                if not arrow.hit:
                    age = time.time() - arrow.spawn_time
                    if arrow.y > HEIGHT:
                        score -= 50
                        health -= health_loss
                    elif age >= 10:
                        continue
                    else:
                        remaining_arrows.append(arrow)
                else:
                    remaining_arrows.append(arrow)
            arrows = remaining_arrows

            if health <= 0:
                game_over = True

            if score >= win_score:
                win = True

        if game_over:
            game_over_text = font.render("GAME OVER", True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - 120, HEIGHT // 2 - 50))
            main_menu_button = draw_main_menu_button()
        elif win:
            win_text = font.render("YOU WIN!", True, GREEN)
            screen.blit(win_text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
            main_menu_button = draw_main_menu_button()

        if settings["mode"] == "auto" and not game_over and not win:
            stop_auto_button = draw_stop_auto_button()

        pygame.display.flip()

# Entry point
if __name__ == "__main__":
    while True:
        selected_settings = main_menu()
        run_game(selected_settings)
