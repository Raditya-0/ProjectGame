"""
Base Entity class yang implement multiple interfaces untuk demonstrasi Inheritance dan Polymorphism.
Menggunakan Encapsulation dengan protected/private attributes.
"""
import pygame
from typing import Dict, List, Optional
from utils.settings import GRAVITY, ANIMATION_SPEED
from core.interfaces import (
    IDrawable, IUpdatable, ICollidable, 
    IPhysicsBody, IAnimatable
)


class Entity(IDrawable, IUpdatable, ICollidable, IPhysicsBody, IAnimatable):
    """
    Abstract base class untuk semua game entities.
    Implementasi:
    - Encapsulation: menggunakan _ prefix untuk protected attributes
    - Inheritance: base class untuk Player, Enemy, NPC
    - Polymorphism: implementasi interface methods yang bisa di-override
    - Abstraction: implement dari multiple interfaces
    """
    
    def __init__(self, x: int, y: int, image: pygame.Surface):
        # Protected attributes (encapsulation)
        self._image = image
        self._rect = self._image.get_rect(bottomleft=(x, y))
        self._velocity = pygame.math.Vector2(0, 0)
        self._direction = 1  # 1 = right, -1 = left
        self._is_on_ground = True
        self._is_alive = True
        
        # Animation attributes
        self._animations: Dict[str, List[pygame.Surface]] = {}
        self._state = 'idle'
        self._frame_index = 0.0
        self._animation_timer = 0
        self._animation_finished = False
        self._non_looping_states = {'death'}
    
    # Properties untuk encapsulation (getter/setter)
    @property
    def image(self) -> pygame.Surface:
        """Get current image."""
        return self._image
    
    @image.setter
    def image(self, value: pygame.Surface):
        """Set current image."""
        self._image = value
    
    @property
    def rect(self) -> pygame.Rect:
        """Get collision rect."""
        return self._rect
    
    @property
    def velocity(self) -> pygame.math.Vector2:
        """Get velocity vector."""
        return self._velocity
    
    @velocity.setter
    def velocity(self, value: pygame.math.Vector2):
        """Set velocity vector."""
        self._velocity = value
    
    @property
    def direction(self) -> int:
        """Get facing direction."""
        return self._direction
    
    @direction.setter
    def direction(self, value: int):
        """Set facing direction."""
        self._direction = value
    
    @property
    def is_on_ground(self) -> bool:
        """Check if entity is on ground."""
        return self._is_on_ground
    
    @property
    def state(self) -> str:
        """Get current animation state."""
        return self._state
    
    @property
    def frame_index(self) -> float:
        """Get current frame index."""
        return self._frame_index
    
    @frame_index.setter
    def frame_index(self, value: float):
        """Set frame index."""
        self._frame_index = value
    
    @property
    def animation_timer(self) -> int:
        """Get animation timer."""
        return self._animation_timer
    
    @property
    def animation_finished(self) -> bool:
        """Check if current animation finished."""
        return self._animation_finished
    
    @property
    def animations(self) -> Dict[str, List[pygame.Surface]]:
        """Get animations dictionary."""
        return self._animations
    
    @property
    def non_looping_states(self) -> set:
        """Get set of non-looping animation states."""
        return self._non_looping_states
    
    # ICollidable implementation
    def get_collision_rect(self) -> pygame.Rect:
        """Return rect untuk collision detection."""
        return self._rect
    
    def handle_collision(self, other: 'Entity') -> None:
        """Handle collision dengan entity lain. Override di subclass."""
        pass
    
    def collides(self, rect: pygame.Rect) -> bool:
        """Check collision dengan rect."""
        return self._rect.colliderect(rect)
    
    def is_inside(self, rect: pygame.Rect) -> bool:
        """Check if entity sepenuhnya di dalam rect."""
        if not rect:
            return False
        return rect.contains(self._rect)
    
    # IPhysicsBody implementation
    def get_velocity(self) -> pygame.math.Vector2:
        """Return velocity vector."""
        return self._velocity
    
    def set_velocity(self, velocity: pygame.math.Vector2) -> None:
        """Set velocity vector."""
        self._velocity = velocity
    
    def apply_physics(self, platforms: List[pygame.Rect]) -> None:
        """
        Apply physics (gravity, platform collision).
        Override method untuk custom physics.
        """
        if not self._is_alive:
            self._velocity.x = 0
            self._velocity.y += GRAVITY
            self._rect.y += self._velocity.y
            for platform in platforms:
                if self._rect.colliderect(platform) and self._velocity.y > 0:
                    self._rect.bottom = platform.top
                    self._velocity.y = 0
            return
        
        # Horizontal movement
        self._rect.x += self._velocity.x
        for platform in platforms:
            if self._rect.colliderect(platform):
                if self._velocity.x > 0:
                    self._rect.right = platform.left
                elif self._velocity.x < 0:
                    self._rect.left = platform.right
        
        # Vertical movement dengan gravity
        self._velocity.y += GRAVITY
        self._rect.y += self._velocity.y
        self._is_on_ground = False
        
        for platform in platforms:
            if self._rect.colliderect(platform):
                if self._velocity.y > 0:
                    self._rect.bottom = platform.top
                    self._velocity.y = 0
                    self._is_on_ground = True
                elif self._velocity.y < 0:
                    self._rect.top = platform.bottom
                    self._velocity.y = 0
    
    # IAnimatable implementation
    def set_animation_state(self, state: str) -> None:
        """Set animation state."""
        if self._state != state:
            self._state = state
            self._frame_index = 0.0
            self._animation_timer = 0
            self._animation_finished = False
    
    def animate(self) -> None:
        """Update animation frame. Override untuk custom animation logic."""
        self._state = self._compute_state()
        self._animation_timer += 1
        
        if self._animation_timer > ANIMATION_SPEED:
            self._animation_timer = 0
            current_animation = self._animations.get(self._state, [])
            
            if self._state in self._non_looping_states:
                if self._frame_index < max(0, len(current_animation) - 1):
                    self._frame_index += 1
                else:
                    self._animation_finished = True
            else:
                if len(current_animation) > 0:
                    self._frame_index = (self._frame_index + 1) % len(current_animation)
            
            if len(current_animation) > 0:
                self._image = current_animation[int(self._frame_index)]
    
    def _compute_state(self) -> str:
        """
        Compute animation state based on entity conditions.
        Override di subclass untuk custom state logic.
        """
        return self._state
    
    # IDrawable implementation
    def draw(self, screen: pygame.Surface, camera_offset_x: float, camera_offset_y: float) -> None:
        """Render entity ke screen dengan flip berdasarkan direction."""
        final_image = self._image
        if self._direction == -1:
            final_image = pygame.transform.flip(self._image, True, False)
        screen.blit(final_image, (self._rect.x - camera_offset_x, self._rect.y - camera_offset_y))
    
    # IUpdatable implementation
    def update(self, *args, **kwargs) -> None:
        """
        Update entity state. Default implementation calls physics and animation.
        Override untuk custom update logic.
        """
        platforms = kwargs.get('platforms', [])
        self.apply_physics(platforms)
        self.animate()
    
    def is_alive(self) -> bool:
        """Check if entity masih hidup."""
        return self._is_alive
    
    def step(self, platforms: List[pygame.Rect]) -> None:
        """Legacy method untuk backward compatibility."""
        self.apply_physics(platforms)
        self.animate()
