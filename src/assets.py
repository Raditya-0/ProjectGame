import pygame
from settings import *

# def create_platform_surface(width, height, dimension):
#     color = COLOR_PLATFORM_NORMAL if dimension == 'normal' else COLOR_PLATFORM_GEMA
#     surface = pygame.Surface((width, height))
#     surface.fill(color)
#     return surface

# def create_trap_surface(width, height):
#     surface = pygame.Surface((width, height), pygame.SRCALPHA)
#     num_spikes = width // 20
#     for i in range(num_spikes):
#         points = [(i*20, height), (i*20 + 10, 0), (i*20 + 20, height)]
#         pygame.draw.polygon(surface, COLOR_TRAP, points)
#     return surface

def create_door_surface(width, height):
    surface = pygame.Surface((width, height))
    surface.fill((139, 69, 19))
    pygame.draw.circle(surface, (255, 223, 0), (int(width*0.8), int(height/2)), 3)
    return surface

def create_heart_surface():
    surface = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.polygon(surface, (255, 0, 0), [(15, 30), (0, 10), (15, 15), (30, 10)])
    pygame.draw.circle(surface, (255, 0, 0), (8, 8), 8)
    pygame.draw.circle(surface, (255, 0, 0), (22, 8), 8)
    return surface

def scale_surface(surface, scale_factor):
    new_size = (int(surface.get_width() * scale_factor), int(surface.get_height() * scale_factor))
    return pygame.transform.scale(surface, new_size)
