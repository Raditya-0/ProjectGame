import pygame

def draw_text(game, text, size, color, x, y, center_aligned=True, shadow_color=None, shadow_offset=3):
    font = pygame.font.Font(None, size)

    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()

    if shadow_color:
        shadow_surface = font.render(text, True, shadow_color)
        shadow_rect = shadow_surface.get_rect()
        if center_aligned:
            shadow_rect.center = (x + shadow_offset, y + shadow_offset)
        else:
            shadow_rect.topleft = (x + shadow_offset, y + shadow_offset)
        game.screen.blit(shadow_surface, shadow_rect)

    if center_aligned:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    game.screen.blit(text_surface, text_rect)


def draw_pause_menu(game):
    overlay = pygame.Surface((game.screen.get_width(), game.screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    game.screen.blit(overlay, (0, 0))

    draw_text(game, "Paused", 80, (255, 255, 255), game.screen.get_width() / 2, game.screen.get_height() / 4, shadow_color=(20, 20, 20))

    game.resume_button = pygame.Rect(game.screen.get_width() / 2 - 100, game.screen.get_height() / 2 - 75, 200, 50)
    game.restart_button = pygame.Rect(game.screen.get_width() / 2 - 100, game.screen.get_height() / 2, 200, 50)
    game.settings_button = pygame.Rect(game.screen.get_width() / 2 - 100, game.screen.get_height() / 2 + 75, 200, 50)
    game.main_menu_button = pygame.Rect(game.screen.get_width() / 2 - 100, game.screen.get_height() / 2 + 150, 200, 50)

    buttons = [
        (game.resume_button, "Lanjutkan"),
        (game.restart_button, "Ulangi"),
        (game.settings_button, "Pengaturan"),
        (game.main_menu_button, "Menu Utama"),
    ]
    mouse_pos = pygame.mouse.get_pos()
    for rect, text in buttons:
        color = (150, 150, 150) if rect.collidepoint(mouse_pos) else (100, 100, 100)
        pygame.draw.rect(game.screen, color, rect, border_radius=10)
        draw_text(game, text, 32, (255, 255, 255), rect.centerx, rect.centery)


def draw_settings_menu(game):
    overlay = pygame.Surface((game.screen.get_width(), game.screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    game.screen.blit(overlay, (0, 0))

    draw_text(game, "Pengaturan", 60, (255, 255, 255), game.screen.get_width() / 2, game.screen.get_height() / 4, shadow_color=(20, 20, 20))

    game.music_button = pygame.Rect(game.screen.get_width() / 2 - 100, game.screen.get_height() / 2, 200, 50)
    game.back_button = pygame.Rect(game.screen.get_width() / 2 - 100, game.screen.get_height() / 2 + 75, 200, 50)

    music_text = "Musik: Off" if game.is_music_paused else "Musik: On"
    mouse_pos = pygame.mouse.get_pos()
    music_color = (150, 150, 150) if game.music_button.collidepoint(mouse_pos) else (100, 100, 100)
    pygame.draw.rect(game.screen, music_color, game.music_button, border_radius=10)
    draw_text(game, music_text, 32, (255, 255, 255), game.music_button.centerx, game.music_button.centery)

    back_color = (150, 150, 150) if game.back_button.collidepoint(mouse_pos) else (100, 100, 100)
    pygame.draw.rect(game.screen, back_color, game.back_button, border_radius=10)
    draw_text(game, "Kembali", 32, (255, 255, 255), game.back_button.centerx, game.back_button.centery)


def draw_win_screen(game):
    overlay = pygame.Surface((game.screen.get_width(), game.screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    game.screen.blit(overlay, (0, 0))

    draw_text(game, "Selamat! Semua Level Selesai!", 60, (255, 255, 255), game.screen.get_width() / 2, game.screen.get_height() / 4)

    game.restart_button = pygame.Rect(game.screen.get_width() / 2 - 100, game.screen.get_height() / 2, 200, 50)
    game.main_menu_button = pygame.Rect(game.screen.get_width() / 2 - 100, game.screen.get_height() / 2 + 75, 200, 50)

    buttons = [
        (game.restart_button, "Restart"),
        (game.main_menu_button, "Menu Utama"),
    ]

    mouse_pos = pygame.mouse.get_pos()
    for rect, text in buttons:
        color = (150, 150, 150) if rect.collidepoint(mouse_pos) else (100, 100, 100)
        pygame.draw.rect(game.screen, color, rect, border_radius=10)
        draw_text(game, text, 32, (255, 255, 255), rect.centerx, rect.centery)


def draw_game_over_screen(game):
    overlay = pygame.Surface((game.screen.get_width(), game.screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    game.screen.blit(overlay, (0, 0))

    draw_text(game, "Game Over", 60, (255, 255, 255), game.screen.get_width() / 2, game.screen.get_height() / 4)

    game.restart_button = pygame.Rect(game.screen.get_width() / 2 - 100, game.screen.get_height() / 2, 200, 50)
    game.main_menu_button = pygame.Rect(game.screen.get_width() / 2 - 100, game.screen.get_height() / 2 + 75, 200, 50)

    buttons = [
        (game.restart_button, "Restart"),
        (game.main_menu_button, "Menu Utama"),
    ]

    mouse_pos = pygame.mouse.get_pos()
    for rect, text in buttons:
        color = (150, 150, 150) if rect.collidepoint(mouse_pos) else (100, 100, 100)
        pygame.draw.rect(game.screen, color, rect, border_radius=10)
        draw_text(game, text, 32, (255, 255, 255), rect.centerx, rect.centery)
