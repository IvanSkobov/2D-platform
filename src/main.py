import pygame
from game import Game


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("2D Platformer")
    clock = pygame.time.Clock()

    game = Game(screen)

    running = True
    while running:
        if not game.game_active:  # <--- Вот здесь меняем game.running на game.game_active
            running = show_game_over_screen(screen, clock)
            if running:  # Если пользователь выбрал рестарт
                game = Game(screen)
            else:
                break

        game.run()


def show_game_over_screen(screen, clock):
    font = pygame.font.SysFont("Arial", 36)
    text = font.render("Game Over! Press R to restart or Q to quit", True, (255, 0, 0))
    text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                elif event.key == pygame.K_q:
                    return False

        screen.fill((0, 0, 0))
        screen.blit(text, text_rect)
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
    pygame.quit()