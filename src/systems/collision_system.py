"""
Collision System - Mengelola semua collision detection dan resolution.
Demonstrasi Single Responsibility dan Composition.
"""
import pygame
from typing import List, Dict, Optional, Tuple, Any
from core.interfaces import ICollidable


class CollisionSystem:
    """
    System untuk mengelola collision detection dan resolution.
    Encapsulation: semua collision logic dalam satu class.
    """
    
    def __init__(self):
        self._collision_groups: Dict[str, List[ICollidable]] = {}
        self._platform_cache: List[pygame.Rect] = []
    
    def register_group(self, group_name: str) -> None:
        """Register collision group."""
        if group_name not in self._collision_groups:
            self._collision_groups[group_name] = []
    
    def add_to_group(self, group_name: str, collidable: ICollidable) -> None:
        """Add collidable object to group."""
        if group_name not in self._collision_groups:
            self.register_group(group_name)
        self._collision_groups[group_name].append(collidable)
    
    def clear_group(self, group_name: str) -> None:
        """Clear all objects from group."""
        if group_name in self._collision_groups:
            self._collision_groups[group_name].clear()
    
    def get_group(self, group_name: str) -> List[ICollidable]:
        """Get collision group."""
        return self._collision_groups.get(group_name, [])
    
    def check_collision(self, rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
        """Check if two rects collide."""
        return rect1.colliderect(rect2)
    
    def check_collision_list(self, rect: pygame.Rect, rect_list: List[pygame.Rect]) -> List[pygame.Rect]:
        """Return list of rects that collide with given rect."""
        return [r for r in rect_list if rect.colliderect(r)]
    
    def resolve_platform_collision_x(self, entity_rect: pygame.Rect, 
                                     platforms: List[pygame.Rect], 
                                     velocity_x: float) -> Tuple[pygame.Rect, float]:
        """
        Resolve horizontal collision dengan platforms.
        Returns: (updated_rect, updated_velocity_x)
        """
        for platform in platforms:
            if entity_rect.colliderect(platform):
                if velocity_x > 0:
                    entity_rect.right = platform.left
                elif velocity_x < 0:
                    entity_rect.left = platform.right
                velocity_x = 0
        return entity_rect, velocity_x
    
    def resolve_platform_collision_y(self, entity_rect: pygame.Rect,
                                     platforms: List[pygame.Rect],
                                     velocity_y: float) -> Tuple[pygame.Rect, float, bool]:
        """
        Resolve vertical collision dengan platforms.
        Returns: (updated_rect, updated_velocity_y, is_on_ground)
        """
        is_on_ground = False
        for platform in platforms:
            if entity_rect.colliderect(platform):
                if velocity_y > 0:
                    entity_rect.bottom = platform.top
                    velocity_y = 0
                    is_on_ground = True
                elif velocity_y < 0:
                    entity_rect.top = platform.bottom
                    velocity_y = 0
        return entity_rect, velocity_y, is_on_ground
    
    def get_overlapping_entities(self, rect: pygame.Rect, group_name: str) -> List[ICollidable]:
        """Get all entities dalam group yang overlap dengan rect."""
        group = self.get_group(group_name)
        return [entity for entity in group if entity.get_collision_rect().colliderect(rect)]
    
    def check_point_in_rect(self, point: Tuple[int, int], rect: pygame.Rect) -> bool:
        """Check if point is inside rect."""
        return rect.collidepoint(point)
    
    def get_distance(self, rect1: pygame.Rect, rect2: pygame.Rect) -> float:
        """Get distance between centers of two rects."""
        dx = rect1.centerx - rect2.centerx
        dy = rect1.centery - rect2.centery
        return (dx * dx + dy * dy) ** 0.5
    
    def get_nearest(self, rect: pygame.Rect, group_name: str) -> Optional[ICollidable]:
        """Get nearest entity dalam group ke rect."""
        group = self.get_group(group_name)
        if not group:
            return None
        
        min_dist = float('inf')
        nearest = None
        for entity in group:
            dist = self.get_distance(rect, entity.get_collision_rect())
            if dist < min_dist:
                min_dist = dist
                nearest = entity
        return nearest
