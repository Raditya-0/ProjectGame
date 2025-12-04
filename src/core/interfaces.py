"""
Core interfaces untuk implementasi Abstraction dan Polymorphism.
Menggunakan ABC (Abstract Base Class) untuk mendefinisikan contract yang harus diikuti.
"""
from abc import ABC, abstractmethod
import pygame
from typing import Tuple, List


class IDrawable(ABC):
    """Interface untuk objek yang bisa di-render ke screen."""
    
    @abstractmethod
    def draw(self, screen: pygame.Surface, camera_offset_x: float, camera_offset_y: float) -> None:
        """Render objek ke screen dengan offset kamera."""
        pass


class IUpdatable(ABC):
    """Interface untuk objek yang memiliki logic update per frame."""
    
    @abstractmethod
    def update(self, *args, **kwargs) -> None:
        """Update state objek setiap frame."""
        pass


class ICollidable(ABC):
    """Interface untuk objek yang bisa berinteraksi dengan collision."""
    
    @abstractmethod
    def get_collision_rect(self) -> pygame.Rect:
        """Return rect untuk collision detection."""
        pass
    
    @abstractmethod
    def handle_collision(self, other: 'ICollidable') -> None:
        """Handle collision dengan objek lain."""
        pass


class IPhysicsBody(ABC):
    """Interface untuk objek yang dipengaruhi physics."""
    
    @abstractmethod
    def apply_physics(self, platforms: List[pygame.Rect]) -> None:
        """Apply physics (gravity, collision) ke objek."""
        pass
    
    @abstractmethod
    def get_velocity(self) -> pygame.math.Vector2:
        """Return velocity vector objek."""
        pass
    
    @abstractmethod
    def set_velocity(self, velocity: pygame.math.Vector2) -> None:
        """Set velocity vector objek."""
        pass


class IAnimatable(ABC):
    """Interface untuk objek yang memiliki animasi."""
    
    @abstractmethod
    def animate(self) -> None:
        """Update animasi frame."""
        pass
    
    @abstractmethod
    def set_animation_state(self, state: str) -> None:
        """Set state animasi."""
        pass


class IDamageable(ABC):
    """Interface untuk objek yang bisa menerima damage."""
    
    @abstractmethod
    def take_damage(self, amount: int) -> None:
        """Receive damage."""
        pass
    
    @abstractmethod
    def is_alive(self) -> bool:
        """Check if entity masih hidup."""
        pass


class IInputHandler(ABC):
    """Interface untuk objek yang handle input."""
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame event."""
        pass
