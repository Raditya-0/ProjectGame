"""
Camera System - Mengelola kamera dan viewport.
Demonstrasi Encapsulation dan Single Responsibility Principle.
"""
import pygame
from typing import Optional, Tuple


class CameraSystem:
    """
    System untuk mengelola posisi kamera dan viewport transformations.
    Encapsulation: semua logic kamera dalam satu class.
    """
    
    def __init__(self, viewport_width: int, viewport_height: int):
        self._viewport_width = viewport_width
        self._viewport_height = viewport_height
        self._offset_x = 0.0
        self._offset_y = 0.0
        self._manual_offset_x = 0
        self._manual_offset_y = 0
        self._is_locked = False
        self._lock_center_x = 0.0
        self._right_limit = None
        
    # Properties untuk encapsulation
    @property
    def offset_x(self) -> float:
        """Get camera X offset."""
        return self._offset_x
    
    @property
    def offset_y(self) -> float:
        """Get camera Y offset."""
        return self._offset_y
    
    @property
    def viewport_width(self) -> int:
        """Get viewport width."""
        return self._viewport_width
    
    @property
    def viewport_height(self) -> int:
        """Get viewport height."""
        return self._viewport_height
    
    def set_manual_offset(self, x: int, y: int) -> None:
        """Set manual camera offset."""
        self._manual_offset_x = x
        self._manual_offset_y = y
    
    def set_right_limit(self, limit: Optional[float]) -> None:
        """Set camera right boundary limit."""
        self._right_limit = limit
    
    def lock_at(self, center_x: float) -> None:
        """Lock camera at specific X position."""
        self._is_locked = True
        self._lock_center_x = center_x
    
    def unlock(self) -> None:
        """Unlock camera to follow target."""
        self._is_locked = False
    
    def is_locked(self) -> bool:
        """Check if camera is locked."""
        return self._is_locked
    
    def follow_target(self, target_rect: pygame.Rect) -> None:
        """
        Update camera to follow target (usually player).
        Applies centering and boundary limits.
        """
        if self._is_locked:
            self._offset_x = self._lock_center_x - self._viewport_width / 2
        else:
            self._offset_x = target_rect.centerx - self._viewport_width / 2
        
        # Apply right limit if set
        if self._right_limit is not None:
            max_offset = self._right_limit - self._viewport_width / 2
            if self._offset_x > max_offset:
                self._offset_x = max_offset
        
        # Apply manual offsets
        self._offset_x += self._manual_offset_x
        self._offset_y = self._manual_offset_y
    
    def get_final_offset(self) -> Tuple[float, float]:
        """Return final camera offset untuk rendering."""
        return (self._offset_x, self._offset_y)
    
    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[float, float]:
        """Convert world coordinates to screen coordinates."""
        screen_x = world_x - self._offset_x
        screen_y = world_y - self._offset_y
        return (screen_x, screen_y)
    
    def screen_to_world(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates."""
        world_x = screen_x + self._offset_x
        world_y = screen_y + self._offset_y
        return (world_x, world_y)
    
    def is_visible(self, rect: pygame.Rect, margin: int = 0) -> bool:
        """Check if rect is visible dalam viewport (dengan margin)."""
        screen_pos = self.world_to_screen(rect.x, rect.y)
        return (
            screen_pos[0] + rect.width + margin >= 0 and
            screen_pos[0] - margin < self._viewport_width and
            screen_pos[1] + rect.height + margin >= 0 and
            screen_pos[1] - margin < self._viewport_height
        )
