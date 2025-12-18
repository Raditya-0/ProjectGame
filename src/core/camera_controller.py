"""
Camera Controller - Mengelola camera movement dan viewport.
"""
import pygame
from typing import Optional


class CameraController:
    """Controller untuk camera/viewport management."""
    
    def __init__(self, viewport_width: int, viewport_height: int, 
                 manual_offset_x: int = 0, manual_offset_y: int = 0):
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.manual_offset_x = manual_offset_x
        self.manual_offset_y = manual_offset_y
        
        # Camera lock state
        self.is_locked = False
        self.lock_center_x = 0
        
        # Camera limits
        self.right_limit_x: Optional[float] = None
        
    def lock_camera(self, center_x: float):
        """Lock camera at a specific x position."""
        self.is_locked = True
        self.lock_center_x = center_x
    
    def unlock_camera(self):
        """Unlock camera to follow target again."""
        self.is_locked = False
    
    def set_right_limit(self, limit_x: Optional[float]):
        """Set right boundary limit for camera."""
        self.right_limit_x = limit_x
    
    def get_offset(self, target_rect: pygame.Rect) -> tuple:
        """
        Calculate camera offset based on target (usually player).
        Returns (offset_x, offset_y) tuple.
        """
        # Calculate base offset
        if self.is_locked:
            camera_offset_x = self.lock_center_x - self.viewport_width / 2
        else:
            camera_offset_x = target_rect.centerx - self.viewport_width / 2
        
        # Apply right limit if set
        if self.right_limit_x is not None:
            max_offset = self.right_limit_x - self.viewport_width / 2
            if camera_offset_x > max_offset:
                camera_offset_x = max_offset
        
        # Add manual offsets
        final_offset_x = camera_offset_x + self.manual_offset_x
        final_offset_y = self.manual_offset_y
        
        return (final_offset_x, final_offset_y)
    
    def world_to_screen(self, world_pos: tuple, offset: tuple) -> tuple:
        """Convert world coordinates to screen coordinates."""
        return (world_pos[0] - offset[0], world_pos[1] - offset[1])
    
    def screen_to_world(self, screen_pos: tuple, offset: tuple) -> tuple:
        """Convert screen coordinates to world coordinates."""
        return (screen_pos[0] + offset[0], screen_pos[1] + offset[1])
