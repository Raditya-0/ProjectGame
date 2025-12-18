"""
Game State Manager - Mengelola state transisi game.
Memisahkan logic state dari main game loop.
"""
import pygame
from enum import Enum
from typing import Optional, Callable


class GameStateEnum(Enum):
    """Enum untuk semua game states."""
    MAIN_MENU = "main_menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    GAME_OVER_WIN = "game_over_win"


class GameStateController:
    """Controller untuk mengelola game state transitions."""
    
    def __init__(self):
        self._current_state = GameStateEnum.MAIN_MENU
        self._previous_state = GameStateEnum.MAIN_MENU
        self._state_callbacks = {}
        
    @property
    def current(self) -> GameStateEnum:
        """Get current game state."""
        return self._current_state
    
    @property
    def previous(self) -> GameStateEnum:
        """Get previous game state."""
        return self._previous_state
    
    def change_state(self, new_state: GameStateEnum):
        """Change to a new state."""
        self._previous_state = self._current_state
        self._current_state = new_state
        
        # Call callback if registered
        if new_state in self._state_callbacks:
            self._state_callbacks[new_state]()
    
    def register_callback(self, state: GameStateEnum, callback: Callable):
        """Register a callback for state entry."""
        self._state_callbacks[state] = callback
    
    def is_state(self, state: GameStateEnum) -> bool:
        """Check if current state matches."""
        return self._current_state == state
    
    def toggle_pause(self):
        """Toggle between playing and paused."""
        if self._current_state == GameStateEnum.PLAYING:
            self.change_state(GameStateEnum.PAUSED)
        elif self._current_state == GameStateEnum.PAUSED:
            self.change_state(GameStateEnum.PLAYING)
