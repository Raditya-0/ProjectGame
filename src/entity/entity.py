import pygame
from settings import GRAVITY, ANIMATION_SPEED


class Entity:
    def __init__(self, x: int, y: int, image: pygame.Surface):
        """Base entity with position, sprite, basic rect, movement, and life state.

        Parameters:
        - x, y: spawn bottom-left position in world coordinates
        - image: initial sprite image used to derive the rect
        """
        self.image = image
        # Use bottomleft to be consistent with Player spawn logic
        self.rect = self.image.get_rect(bottomleft=(x, y))

        # Basic movement/orientation
        self.velocity = pygame.math.Vector2(0, 0)
        self.direction = 1  # 1 right, -1 left
        self.is_on_ground = True

        # Life state
        self.is_alive = True

        # Animation state
        self.animations = getattr(self, 'animations', {})
        self.state = getattr(self, 'state', 'idle')
        self.frame_index = getattr(self, 'frame_index', 0)
        self.animation_timer = getattr(self, 'animation_timer', 0)
        self.animation_finished = getattr(self, 'animation_finished', False)
        # States that should not loop (stay on last frame). Override in subclass as needed.
        self.non_looping_states = getattr(self, 'non_looping_states', {'death'})

    # ----- Common helpers -----
    def is_inside(self, rect: pygame.Rect) -> bool:
        """Return True if the entity's rect is fully inside the given rect."""
        if not rect:
            return False
        return rect.contains(self.rect)

    def collides(self, rect: pygame.Rect) -> bool:
        """Return True if the entity's rect intersects the given rect."""
        return self.rect.colliderect(rect)

    def draw(self, screen: pygame.Surface, camera_offset_x: float, camera_offset_y: float):
        """Default draw: flips on X when facing left and blits at camera-adjusted position."""
        final_image = self.image
        if self.direction == -1:
            final_image = pygame.transform.flip(self.image, True, False)
        screen.blit(final_image, (self.rect.x - camera_offset_x, self.rect.y - camera_offset_y))

    # ----- Physics -----
    def update_physics(self, platforms: list[pygame.Rect]):
        """Default platformer physics: horizontal move with collision, gravity, vertical collision.
        Works for both alive and dead (dead will still fall until ground).
        """
        if not self.is_alive:
            # When dead, ignore horizontal input but still fall and land
            self.velocity.x = 0
            self.velocity.y += GRAVITY
            self.rect.y += self.velocity.y
            for platform in platforms:
                if self.rect.colliderect(platform) and self.velocity.y > 0:
                    self.rect.bottom = platform.top
                    self.velocity.y = 0
            return

        # Horizontal move and collide
        self.rect.x += self.velocity.x
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.velocity.x > 0:
                    self.rect.right = platform.left
                elif self.velocity.x < 0:
                    self.rect.left = platform.right

        # Gravity and vertical move
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

    # ----- Animation -----
    def compute_state(self) -> str:
        """Return the current animation state name. Subclasses should override.
        Default returns current value without changes.
        """
        return self.state

    def animate(self):
        # Let subclass adjust/compute desired state
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
        """Advance one frame: physics then animation. Subclasses should call this
        after applying their input/AI to velocity/state.
        """
        self.update_physics(platforms)
        self.animate()
