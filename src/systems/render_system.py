"""
Render System - Mengelola rendering layers dan draw calls.
Demonstrasi Encapsulation dan Layered Rendering.
"""
import pygame
from typing import List, Tuple, Optional, Dict
from core.interfaces import IDrawable


class RenderLayer:
    """Represents a rendering layer dengan priority."""
    
    def __init__(self, name: str, priority: int):
        self.name = name
        self.priority = priority
        self.drawables: List[IDrawable] = []
        self.visible = True
    
    def add(self, drawable: IDrawable) -> None:
        """Add drawable object ke layer."""
        if drawable not in self.drawables:
            self.drawables.append(drawable)
    
    def remove(self, drawable: IDrawable) -> None:
        """Remove drawable object dari layer."""
        if drawable in self.drawables:
            self.drawables.remove()
    
    def clear(self) -> None:
        """Clear all drawables dari layer."""
        self.drawables.clear()
    
    def draw(self, screen: pygame.Surface, camera_offset_x: float, camera_offset_y: float) -> None:
        """Draw all objects dalam layer."""
        if not self.visible:
            return
        for drawable in self.drawables:
            drawable.draw(screen, camera_offset_x, camera_offset_y)


class RenderSystem:
    """
    System untuk mengelola rendering dengan layer support.
    Encapsulation: semua rendering logic dalam satu class.
    """
    
    def __init__(self, screen_width: int, screen_height: int, zoom_divider: int = 2):
        self._screen_width = screen_width
        self._screen_height = screen_height
        self._zoom_divider = zoom_divider
        
        # Game surface (sebelum scaling)
        self._game_surface_width = screen_width // zoom_divider
        self._game_surface_height = screen_height // zoom_divider
        self._game_surface = pygame.Surface((self._game_surface_width, self._game_surface_height))
        
        # Main screen surface
        self._screen: Optional[pygame.Surface] = None
        
        # Render layers (sorted by priority)
        self._layers: Dict[str, RenderLayer] = {}
        self._layer_order: List[str] = []
        
        # Background color
        self._bg_color = (0, 0, 0)
        
        # Debug rendering
        self._debug_enabled = False
    
    @property
    def screen(self) -> pygame.Surface:
        """Get main screen surface."""
        return self._screen
    
    @property
    def game_surface(self) -> pygame.Surface:
        """Get game surface (before scaling)."""
        return self._game_surface
    
    @property
    def game_surface_width(self) -> int:
        """Get game surface width."""
        return self._game_surface_width
    
    @property
    def game_surface_height(self) -> int:
        """Get game surface height."""
        return self._game_surface_height
    
    def set_screen(self, screen: pygame.Surface) -> None:
        """Set main screen surface."""
        self._screen = screen
    
    def set_background_color(self, color: Tuple[int, int, int]) -> None:
        """Set background clear color."""
        self._bg_color = color
    
    def set_debug_enabled(self, enabled: bool) -> None:
        """Enable/disable debug rendering."""
        self._debug_enabled = enabled
    
    def is_debug_enabled(self) -> bool:
        """Check if debug rendering is enabled."""
        return self._debug_enabled
    
    def add_layer(self, name: str, priority: int) -> RenderLayer:
        """
        Add rendering layer.
        Lower priority renders first (background), higher priority renders last (foreground).
        """
        if name in self._layers:
            return self._layers[name]
        
        layer = RenderLayer(name, priority)
        self._layers[name] = layer
        
        # Insert in sorted order
        self._layer_order.append(name)
        self._layer_order.sort(key=lambda n: self._layers[n].priority)
        
        return layer
    
    def get_layer(self, name: str) -> Optional[RenderLayer]:
        """Get layer by name."""
        return self._layers.get(name)
    
    def remove_layer(self, name: str) -> None:
        """Remove layer."""
        if name in self._layers:
            del self._layers[name]
            self._layer_order.remove(name)
    
    def set_layer_visible(self, name: str, visible: bool) -> None:
        """Set layer visibility."""
        layer = self.get_layer(name)
        if layer:
            layer.visible = visible
    
    def clear_layer(self, name: str) -> None:
        """Clear all objects dari layer."""
        layer = self.get_layer(name)
        if layer:
            layer.clear()
    
    def clear_all_layers(self) -> None:
        """Clear all objects dari semua layers."""
        for layer in self._layers.values():
            layer.clear()
    
    def begin_frame(self) -> None:
        """Begin rendering frame - clear game surface."""
        self._game_surface.fill(self._bg_color)
    
    def render_layers(self, camera_offset_x: float, camera_offset_y: float) -> None:
        """Render all layers ke game surface."""
        for layer_name in self._layer_order:
            layer = self._layers[layer_name]
            layer.draw(self._game_surface, camera_offset_x, camera_offset_y)
    
    def end_frame(self) -> None:
        """End rendering frame - blit game surface to main screen dengan scaling."""
        if self._screen:
            scaled = pygame.transform.scale(self._game_surface, (self._screen_width, self._screen_height))
            self._screen.blit(scaled, (0, 0))
    
    def render_text(self, text: str, font: pygame.font.Font, color: Tuple[int, int, int],
                   x: int, y: int, screen: Optional[pygame.Surface] = None,
                   shadow_color: Optional[Tuple[int, int, int]] = None,
                   shadow_offset: Tuple[int, int] = (2, 2)) -> None:
        """Render text dengan optional shadow."""
        if screen is None:
            screen = self._screen
        
        if shadow_color:
            shadow_surf = font.render(text, True, shadow_color)
            shadow_rect = shadow_surf.get_rect(center=(x + shadow_offset[0], y + shadow_offset[1]))
            screen.blit(shadow_surf, shadow_rect)
        
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=(x, y))
        screen.blit(text_surf, text_rect)
    
    def render_rect(self, rect: pygame.Rect, color: Tuple[int, int, int],
                   camera_offset_x: float = 0, camera_offset_y: float = 0,
                   width: int = 0, screen: Optional[pygame.Surface] = None) -> None:
        """Render rectangle (with camera offset)."""
        if screen is None:
            screen = self._game_surface
        
        adjusted_rect = pygame.Rect(
            rect.x - camera_offset_x,
            rect.y - camera_offset_y,
            rect.width,
            rect.height
        )
        pygame.draw.rect(screen, color, adjusted_rect, width)
    
    def render_circle(self, center: Tuple[int, int], radius: int, 
                     color: Tuple[int, int, int],
                     width: int = 0, screen: Optional[pygame.Surface] = None) -> None:
        """Render circle."""
        if screen is None:
            screen = self._screen
        pygame.draw.circle(screen, color, center, radius, width)
