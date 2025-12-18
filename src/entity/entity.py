import pygame
from utils.settings import GRAVITY, ANIMATION_SPEED

# Import new OOP base class (untuk future migration)
try:
    from core.entity_base import Entity as EntityBase
    NEW_ARCHITECTURE_AVAILABLE = True
except ImportError:
    NEW_ARCHITECTURE_AVAILABLE = False


class Entity:
    """
    Legacy Entity class untuk backward compatibility.
    TODO: Migrate subclasses to use core.entity_base.Entity
    
    Prinsip OOP:
    - Encapsulation: Public interface untuk attributes (akan diganti dengan properties)
    - Inheritance: Base class untuk Player, Enemy, NPC
    - Polymorphism: Subclasses override methods seperti draw(), update()
    """
    def __init__(self, x: int, y: int, image: pygame.Surface):
        self.image = image
        self.rect = self.image.get_rect(bottomleft=(x, y))

        self.velocity = pygame.math.Vector2(0, 0)
        self.direction = 1
        self.is_on_ground = True

        self.is_alive = True

        self.animations = getattr(self, 'animations', {})
        self.state = getattr(self, 'state', 'idle')
        self.frame_index = getattr(self, 'frame_index', 0)
        self.animation_timer = getattr(self, 'animation_timer', 0)
        self.animation_finished = getattr(self, 'animation_finished', False)
        self.non_looping_states = getattr(self, 'non_looping_states', {'death'})

    def is_inside(self, rect: pygame.Rect) -> bool:
        if not rect:
            return False
        return rect.contains(self.rect)

    def collides(self, rect: pygame.Rect) -> bool:
        return self.rect.colliderect(rect)

    def draw(self, screen: pygame.Surface, camera_offset_x: float, camera_offset_y: float):
        final_image = self.image
        if self.direction == -1:
            final_image = pygame.transform.flip(self.image, True, False)
        screen.blit(final_image, (self.rect.x - camera_offset_x, self.rect.y - camera_offset_y))

    def update_physics(self, platforms: list[pygame.Rect]):
        if not self.is_alive:
            self.velocity.x = 0
            self.velocity.y += GRAVITY
            self.rect.y += self.velocity.y
            for platform in platforms:
                if self.rect.colliderect(platform) and self.velocity.y > 0:
                    self.rect.bottom = platform.top
                    self.velocity.y = 0
            return

        self.rect.x += self.velocity.x
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.velocity.x > 0:
                    self.rect.right = platform.left
                elif self.velocity.x < 0:
                    self.rect.left = platform.right

        self.velocity.y += GRAVITY
        self.rect.y += self.velocity.y
        self.is_on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.velocity.y > 0:
                    self.rect.bottom = platform.top
                    self.velocity.y = 0
                    self.is_on_ground = True
                elif self.velocity.y < 0:
                    self.rect.top = platform.bottom
                    self.velocity.y = 0

    def compute_state(self) -> str:
        return self.state

    def animate(self):
        self.state = self.compute_state()
        self.animation_timer += 1

        if self.animation_timer > ANIMATION_SPEED:
            self.animation_timer = 0
            current_animation = self.animations.get(self.state, [])

            if self.state in self.non_looping_states:
                if self.frame_index < max(0, len(current_animation) - 1):
                    self.frame_index += 1
                else:
                    self.animation_finished = True
            else:
                if len(current_animation) > 0:
                    self.frame_index = (self.frame_index + 1) % len(current_animation)

            if len(current_animation) > 0:
                self.image = current_animation[self.frame_index]

    def step(self, platforms: list[pygame.Rect]):
        self.update_physics(platforms)
        self.animate()

