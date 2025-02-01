import displayio
from blinka_displayio_pygamedisplay import PyGameDisplay
import pygame
from adafruit_display_text import label
import random
import os
import time


pygame.init()


SCREEN_WIDTH = 128
SCREEN_HEIGHT = 128


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Monkey Banana Game")


ASSET_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dependencies")
BACKGROUND_IMAGES = [
    os.path.join(ASSET_PATH, f"background{i}.bmp")
    for i in range(4)
]
MONKEY_IMAGES = {
    "right": os.path.join(ASSET_PATH, "monkey_right.bmp"),
    "left": os.path.join(ASSET_PATH, "monkey_left.bmp"),
}
BANANA_IMAGES = {
    "normal": os.path.join(ASSET_PATH, "banana_normal.bmp"),
    "rotten": os.path.join(ASSET_PATH, "banana_rotten.bmp"),
    "super": os.path.join(ASSET_PATH, "banana_super.bmp"),
}


backgrounds = [pygame.image.load(img) for img in BACKGROUND_IMAGES]
monkey_right = pygame.image.load(MONKEY_IMAGES["right"])
monkey_left = pygame.image.load(MONKEY_IMAGES["left"])
banana_images = {key: pygame.image.load(img) for key, img in BANANA_IMAGES.items()}


monkey_right = pygame.transform.scale(monkey_right, (32, 32))
monkey_left = pygame.transform.scale(monkey_left, (32, 32))
for key in banana_images:
    banana_images[key] = pygame.transform.scale(banana_images[key], (32, 32))

clock = pygame.time.Clock()


monkey_x = SCREEN_WIDTH // 2 - 16
monkey_y = SCREEN_HEIGHT - 32
monkey_speed = 3
monkey_direction = "right"
hearts = 3
score = 0

banana_list = []
banana_speed = 2
banana_spawn_rate = 30

background_index = 0

game_running = False
game_over_displayed = False

last_background_switch = time.time()

def spawn_banana():
    banana_type = random.choices(
        ["normal", "rotten", "super"], weights=[60, 25, 15], k=1
    )[0]
    x = random.randint(0, SCREEN_WIDTH - 32)
    y = -32
    return {"type": banana_type, "x": x, "y": y}

def move_bananas():
    global banana_speed
    for banana in banana_list:
        banana["y"] += banana_speed

def check_collisions():
    global hearts, score, banana_speed
    for banana in banana_list[:]:
        if (
            banana["x"] < monkey_x + 32
            and banana["x"] + 32 > monkey_x
            and banana["y"] < monkey_y + 32
            and banana["y"] + 32 > monkey_y
        ):
            if banana["type"] == "normal":
                score += 1
            elif banana["type"] == "rotten":
                hearts -= 1
            elif banana["type"] == "super":
                hearts = min(3, hearts + 1)
                score += 3
            banana_list.remove(banana)
    if score % 10 == 0 and score > 0:
        banana_speed = int(banana_speed * 1.10)

def draw_game():
    global background_index, last_background_switch
    current_time = time.time()
    
    if current_time - last_background_switch >= 1.0:  
        background_index = (background_index + 1) % len(backgrounds)
        last_background_switch = current_time
    
    screen.blit(backgrounds[background_index], (0, 0))
    
    if monkey_direction == "right":
        screen.blit(monkey_right, (monkey_x, monkey_y))
    else:
        screen.blit(monkey_left, (monkey_x, monkey_y))
    for banana in banana_list:
        screen.blit(banana_images[banana["type"]], (banana["x"], banana["y"]))
    for i in range(hearts):
        pygame.draw.ellipse(screen, (255, 0, 0), (5 + i * 15, 5, 10, 10))
    font = pygame.font.SysFont(None, 24)
    score_text = font.render(f"Score: {score}", True, (255, 0, 0))
    screen.blit(score_text, (SCREEN_WIDTH - 90, 5))

def reset_game():
    global monkey_x, monkey_y, hearts, score, banana_list, banana_speed, game_running, game_over_displayed
    monkey_x = SCREEN_WIDTH // 2 - 16
    monkey_y = SCREEN_HEIGHT - 32
    hearts = 3
    score = 0
    banana_list = []
    banana_speed = 2
    game_running = False
    game_over_displayed = False

running = True
frame_count = 0
while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if not game_running:
        if hearts <= 0:
            
            font = pygame.font.SysFont(None, 16)
            game_over_text = font.render("You Lost!", True, (255, 0, 0))
            restart_text = font.render("Press SPACE to restart", True, (255, 255, 255))
            
            
            game_over_x = SCREEN_WIDTH // 2 - game_over_text.get_width() // 2
            game_over_y = SCREEN_HEIGHT // 2 - 10
            restart_x = SCREEN_WIDTH // 2 - restart_text.get_width() // 2
            restart_y = SCREEN_HEIGHT // 2 + 5
            
            screen.blit(game_over_text, (game_over_x, game_over_y))
            screen.blit(restart_text, (restart_x, restart_y))
            
            if keys[pygame.K_SPACE]:
                reset_game()
                game_running = True
        else:
            font = pygame.font.SysFont(None, 18)
            start_text = font.render("Press Space to Start", True, (255, 255, 255))
            screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 - start_text.get_height() // 2))
            if keys[pygame.K_SPACE]:
                game_running = True
    else:
        if keys[pygame.K_LEFT] and monkey_x > 0:
            monkey_x -= monkey_speed
            monkey_direction = "left"
        if keys[pygame.K_RIGHT] and monkey_x < SCREEN_WIDTH - 32:
            monkey_x += monkey_speed
            monkey_direction = "right"
        if frame_count % banana_spawn_rate == 0:
            banana_list.append(spawn_banana())
        move_bananas()
        check_collisions()
        banana_list = [b for b in banana_list if b["y"] < SCREEN_HEIGHT]
        draw_game()
        if hearts <= 0:
            game_running = False

    pygame.display.flip()
    clock.tick(30)
    frame_count += 1

pygame.quit()
