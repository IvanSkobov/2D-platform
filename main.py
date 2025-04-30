import pygame
import sys
import random

# Инициализация
pygame.init()

# Настройки окна
WIDTH, HEIGHT = 800, 600
FPS = 60

	@@ -13,29 +14,45 @@
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)

# Физика
gravity = 0.5
jump_power = -10
player_speed = 5

# Параметры прыжка
MAX_JUMP_HEIGHT = 90
MAX_HORIZONTAL_DISTANCE = 200

# Создание экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Платформер: Все монетки доступны!")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

# Звуки
sound_enabled = False
try:
    pygame.mixer.init()
    jump_sound = pygame.mixer.Sound("sounds/jump.wav")
    coin_sound = pygame.mixer.Sound("sounds/coin.wav")
    hurt_sound = pygame.mixer.Sound("sounds/hurt.wav")
    game_over_sound = pygame.mixer.Sound("sounds/game_over.wav")
    sound_enabled = True
except Exception as e:
    print(f"Звуковые файлы не найдены: {e}. Игра без звука.")

# Изображения
try:
    PLAYER_NORMAL_IMG = pygame.transform.scale(pygame.image.load("images/cat_basic.png").convert_alpha(), (60, 60))
    PLAYER_BURNED_IMG = pygame.transform.scale(pygame.image.load("images/cat_burned_f3.png").convert_alpha(), (60, 60))
    COIN_IMG = pygame.transform.scale(pygame.image.load("images/coin.png").convert_alpha(), (20, 20))
    FIREBALL_IMG = pygame.transform.scale(pygame.image.load("images/fireball.png").convert_alpha(), (30, 30))
except FileNotFoundError as e:
    print(f"Не хватает изображения: {e}")
    pygame.quit()
    sys.exit()

# Классы
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
	@@ -78,15 +95,17 @@ def update(self, keys):
    def jump(self):
        if self.on_ground:
            self.vel_y = jump_power
            if sound_enabled:
                jump_sound.play()

    def take_hit(self):
        if not self.burned:
            self.image = PLAYER_BURNED_IMG
            self.burned = True
            self.burned_time = pygame.time.get_ticks()
            if sound_enabled:
                hurt_sound.play()


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, moving=False, speed=0):
	@@ -104,12 +123,14 @@ def update(self):
            if self.rect.left < 0 or self.rect.right > WIDTH:
                self.direction *= -1


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = COIN_IMG
        self.rect = self.image.get_rect(center=(x, y))


class Fireball(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
	@@ -122,46 +143,76 @@ def update(self):
        if self.rect.top > HEIGHT:
            self.kill()


# Логика проверок
def can_reach(prev_platform, new_platform):
    dx = abs(new_platform.rect.centerx - prev_platform.rect.centerx)
    dy = prev_platform.rect.top - new_platform.rect.bottom
    return dx < MAX_HORIZONTAL_DISTANCE and dy > -MAX_JUMP_HEIGHT


def coin_is_reachable(platform, coin):
    coin_to_platform_y = coin.rect.bottom - platform.rect.top
    if coin_to_platform_y > MAX_JUMP_HEIGHT or coin_to_platform_y < -20:
        return False

    if abs(coin.rect.centerx - platform.rect.centerx) > MAX_HORIZONTAL_DISTANCE:
        return False

    return True


def generate_random_level(level_num):
    platforms = []
    coins = []

    # Начальная платформа (пол)
    start_platform = Platform(0, HEIGHT - 40, WIDTH, 40)
    platforms.append(start_platform)

    last_platform = start_platform
    total_platforms = 3 + level_num * 2

    for _ in range(total_platforms):
        attempts = 0
        while attempts < 10:
            w = random.randint(80, 150)
            h = 20

            # Генерируем только "достижимые" координаты
            y = random.randint(last_platform.rect.top - MAX_JUMP_HEIGHT - 20, last_platform.rect.top - 40)
            x = random.randint(
                max(0, last_platform.rect.centerx - MAX_HORIZONTAL_DISTANCE),
                min(WIDTH - w, last_platform.rect.centerx + MAX_HORIZONTAL_DISTANCE)
            )

            moving = random.random() < 0.3
            speed = random.randint(1, 3) if moving else 0
            candidate = Platform(x, y, w, h, moving, speed)

            if can_reach(last_platform, candidate):
                coin_x = x + w // 2
                coin_y = y - 30
                coin = Coin(coin_x, coin_y)

                if coin_is_reachable(candidate, coin):
                    platforms.append(candidate)
                    coins.append(coin)
                    last_platform = candidate
                    break
            attempts += 1

    fireball_interval = max(1000, 5000 - level_num * 500)
    return {
        "platforms": platforms,
        "coins": coins,
        "fireball_interval": fireball_interval
    }


# Игровые переменные
NUM_LEVELS = 10
levels = [generate_random_level(i) for i in range(NUM_LEVELS)]

current_level = 0

	@@ -191,10 +242,12 @@ def draw_ui():
    screen.blit(font.render(f"Счёт: {score}", True, BLACK), (10, 10))
    screen.blit(font.render(f"Жизни: {lives}", True, BLACK), (10, 40))
    if paused:
        screen.blit(font.render("Пауза", True, BLACK), (WIDTH // 2 - 40, HEIGHT // 2))


def show_game_over():
    if sound_enabled:
        game_over_sound.play()
    screen.fill(BLACK)
    text = font.render("Game Over", True, WHITE)
    screen.blit(text, (WIDTH // 2 - 60, HEIGHT // 2))
	@@ -210,10 +263,21 @@ def show_level_transition(level_number):
    pygame.time.delay(2000)


def reset_game():
    global current_level, score, lives
    current_level = 0
    score = 0
    lives = 3
    load_level(current_level)
    show_level_transition(current_level)
    player.rect.topleft = (100, 500)
    player.vel_y = 0


load_level(current_level)
show_level_transition(current_level)

# Главный цикл
running = True
while running:
    clock.tick(FPS)
	@@ -235,7 +299,8 @@ def show_level_transition(level_number):

        for coin in pygame.sprite.spritecollide(player, coin_group, True):
            score += 10
            if sound_enabled:
                coin_sound.play()

        current_interval = levels[current_level]["fireball_interval"]
        if pygame.time.get_ticks() - last_fireball_time > current_interval:
	@@ -250,27 +315,32 @@ def show_level_transition(level_number):
                player.rect.topleft = (100, 500)
            if lives <= 0:
                lives = 0
                show_game_over()
                running = False

        if not coin_group:
            if current_level < len(levels) - 1:
                current_level += 1
                show_level_transition(current_level)
                load_level(current_level)
                player.rect.topleft = (100, 500)
                player.vel_y = 0
                last_fireball_time = pygame.time.get_ticks()
            else:
                screen.fill(SKY_BLUE)
                screen.blit(font.render("🎉 ПОБЕДА! Все уровни пройдены!", True, BLACK),
                            (WIDTH // 2 - 200, HEIGHT // 2))
                pygame.display.flip()
                pygame.time.delay(3000)
                reset_game()

    screen.fill(SKY_BLUE)
    platform_group.draw(screen)
    coin_group.draw(screen)
    fireball_group.draw(screen)
    player_group.draw(screen)
    draw_ui()
    pygame.display.flip()

pygame.quit()
sys.exit()
