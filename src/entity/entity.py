import pygame


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

        # Life state
        self.is_alive = True

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
