"""
State Manager - Mengelola game states dan transitions.
Demonstrasi State Pattern dan Encapsulation.
"""
from enum import Enum
from typing import Optional, Callable, Dict


class GameState(Enum):
    """Enum untuk game states."""
    MAIN_MENU = "main_menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    GAME_OVER_WIN = "game_over_win"
    SETTINGS = "settings"
    LOADING = "loading"


class StateManager:
    """
    Mengelola game state transitions dan callbacks.
    Encapsulation: semua state logic dalam satu class.
    """
    
    def __init__(self, initial_state: GameState = GameState.MAIN_MENU):
        self._current_state = initial_state
        self._previous_state = initial_state
        self._state_callbacks: Dict[GameState, Callable] = {}
        self._transition_callbacks: Dict[tuple, Callable] = {}
    
    @property
    def current_state(self) -> GameState:
        """Get current game state."""
        return self._current_state
    
    @property
    def previous_state(self) -> GameState:
        """Get previous game state."""
        return self._previous_state
    
    def is_state(self, state: GameState) -> bool:
        """Check if current state matches given state."""
        return self._current_state == state
    
    def is_any_of(self, *states: GameState) -> bool:
        """Check if current state matches any of given states."""
        return self._current_state in states
    
    def change_state(self, new_state: GameState) -> None:
        """
        Change game state.
        Triggers transition callback if registered.
        """
        if new_state == self._current_state:
            return
        
        old_state = self._current_state
        self._previous_state = old_state
        self._current_state = new_state
        
        # Call transition callback if exists
        transition_key = (old_state, new_state)
        if transition_key in self._transition_callbacks:
            self._transition_callbacks[transition_key]()
        
        # Call enter state callback if exists
        if new_state in self._state_callbacks:
            self._state_callbacks[new_state]()
    
    def register_state_callback(self, state: GameState, callback: Callable) -> None:
        """Register callback untuk saat entering specific state."""
        self._state_callbacks[state] = callback
    
    def register_transition_callback(self, from_state: GameState, 
                                     to_state: GameState, 
                                     callback: Callable) -> None:
        """Register callback untuk specific state transition."""
        self._transition_callbacks[(from_state, to_state)] = callback
    
    def toggle_pause(self) -> None:
        """Toggle between playing and paused states."""
        if self._current_state == GameState.PLAYING:
            self.change_state(GameState.PAUSED)
        elif self._current_state == GameState.PAUSED:
            self.change_state(GameState.PLAYING)
    
    def return_to_previous(self) -> None:
        """Return to previous state."""
        self.change_state(self._previous_state)
    
    def can_accept_input(self) -> bool:
        """Check if current state allows player input."""
        return self._current_state == GameState.PLAYING
    
    def can_update_game(self) -> bool:
        """Check if current state allows game logic update."""
        return self._current_state in (GameState.PLAYING, GameState.PAUSED)
    
    def is_menu_state(self) -> bool:
        """Check if current state is a menu."""
        return self._current_state in (
            GameState.MAIN_MENU, 
            GameState.PAUSED, 
            GameState.SETTINGS
        )
    
    def is_game_over_state(self) -> bool:
        """Check if current state is game over."""
        return self._current_state in (
            GameState.GAME_OVER,
            GameState.GAME_OVER_WIN
        )
