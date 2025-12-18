"""
Graphics module - Parallax dan UI rendering.
"""
from .parallax import ParallaxLayer, ParallaxObject
from .UI import draw_text, draw_pause_menu, draw_settings_menu, draw_win_screen, draw_game_over_screen

__all__ = [
    'ParallaxLayer',
    'ParallaxObject',
    'draw_text',
    'draw_pause_menu',
    'draw_settings_menu',
    'draw_win_screen',
    'draw_game_over_screen'
]
