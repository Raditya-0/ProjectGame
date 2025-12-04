"""
Input System - Mengelola semua input handling.
Demonstrasi Single Responsibility dan Observer Pattern.
"""
import pygame
from typing import Dict, List, Callable, Optional
from core.interfaces import IInputHandler


class InputSystem:
    """
    System untuk mengelola input dari keyboard, mouse, dan events.
    Encapsulation: semua input logic dalam satu class.
    """
    
    def __init__(self):
        self._key_pressed: Dict[int, bool] = {}
        self._key_just_pressed: Dict[int, bool] = {}
        self._key_just_released: Dict[int, bool] = {}
        self._mouse_pos = (0, 0)
        self._mouse_pressed: Dict[int, bool] = {}
        self._mouse_just_pressed: Dict[int, bool] = {}
        self._event_handlers: List[IInputHandler] = []
        self._enabled = True
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable input processing."""
        self._enabled = enabled
    
    def is_enabled(self) -> bool:
        """Check if input is enabled."""
        return self._enabled
    
    def register_handler(self, handler: IInputHandler) -> None:
        """Register input handler."""
        if handler not in self._event_handlers:
            self._event_handlers.append(handler)
    
    def unregister_handler(self, handler: IInputHandler) -> None:
        """Unregister input handler."""
        if handler in self._event_handlers:
            self._event_handlers.remove(handler)
    
    def clear_handlers(self) -> None:
        """Clear all input handlers."""
        self._event_handlers.clear()
    
    def update(self, events: List[pygame.event.Event]) -> None:
        """
        Process pygame events.
        Call this once per frame dengan list of pygame events.
        """
        if not self._enabled:
            return
        
        # Clear just pressed/released states
        self._key_just_pressed.clear()
        self._key_just_released.clear()
        self._mouse_just_pressed.clear()
        
        # Update mouse position
        self._mouse_pos = pygame.mouse.get_pos()
        
        # Process events
        for event in events:
            # Keyboard events
            if event.type == pygame.KEYDOWN:
                self._key_pressed[event.key] = True
                self._key_just_pressed[event.key] = True
            elif event.type == pygame.KEYUP:
                self._key_pressed[event.key] = False
                self._key_just_released[event.key] = True
            
            # Mouse events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._mouse_pressed[event.button] = True
                self._mouse_just_pressed[event.button] = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self._mouse_pressed[event.button] = False
            
            # Dispatch to handlers
            for handler in self._event_handlers:
                handler.handle_event(event)
    
    # Keyboard methods
    def is_key_pressed(self, key: int) -> bool:
        """Check if key is currently pressed."""
        return self._key_pressed.get(key, False)
    
    def is_key_just_pressed(self, key: int) -> bool:
        """Check if key was just pressed this frame."""
        return self._key_just_pressed.get(key, False)
    
    def is_key_just_released(self, key: int) -> bool:
        """Check if key was just released this frame."""
        return self._key_just_released.get(key, False)
    
    def is_any_key_pressed(self, *keys: int) -> bool:
        """Check if any of the given keys is pressed."""
        return any(self.is_key_pressed(key) for key in keys)
    
    def is_all_keys_pressed(self, *keys: int) -> bool:
        """Check if all given keys are pressed."""
        return all(self.is_key_pressed(key) for key in keys)
    
    # Mouse methods
    def get_mouse_pos(self) -> tuple:
        """Get current mouse position."""
        return self._mouse_pos
    
    def is_mouse_button_pressed(self, button: int = 1) -> bool:
        """Check if mouse button is currently pressed (1=left, 2=middle, 3=right)."""
        return self._mouse_pressed.get(button, False)
    
    def is_mouse_button_just_pressed(self, button: int = 1) -> bool:
        """Check if mouse button was just pressed this frame."""
        return self._mouse_just_pressed.get(button, False)
    
    def is_mouse_over_rect(self, rect: pygame.Rect) -> bool:
        """Check if mouse is over rect."""
        return rect.collidepoint(self._mouse_pos)
    
    def is_mouse_clicked_on_rect(self, rect: pygame.Rect, button: int = 1) -> bool:
        """Check if mouse button was just clicked on rect."""
        return self.is_mouse_button_just_pressed(button) and self.is_mouse_over_rect(rect)
    
    # Utility methods
    def reset(self) -> None:
        """Reset all input states."""
        self._key_pressed.clear()
        self._key_just_pressed.clear()
        self._key_just_released.clear()
        self._mouse_pressed.clear()
        self._mouse_just_pressed.clear()
