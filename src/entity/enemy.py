import pygame
from entity.entity import Entity


class Enemy(Entity):
    def __init__(self, x: int, y: int, left_bound_x: float | None = None, right_bound_x: float | None = None, size=(30, 30), speed: float = 2.0):
        # Create a simple black box as the enemy sprite
        image = pygame.Surface(size, pygame.SRCALPHA)
        image.fill((0, 0, 0))
        super().__init__(x, y, image)

        # Patrol bounds in world coordinates (pixels)
        self.left_bound_x = left_bound_x if left_bound_x is not None else self.rect.centerx - 80
        self.right_bound_x = right_bound_x if right_bound_x is not None else self.rect.centerx + 80
        if self.left_bound_x > self.right_bound_x:
            self.left_bound_x, self.right_bound_x = self.right_bound_x, self.left_bound_x

        self.speed = abs(speed)
        # Start moving to the right by default
        self.direction = 1

        # No animations by default for a simple enemy; it will use 'idle' state image
        self.animations = {}
        self.state = 'idle'

    def compute_state(self) -> str:
        # If moving horizontally set run else idle; dead state can be handled by base if needed
        if not self.is_alive:
            return 'death'
        return 'run' if abs(self.velocity.x) > 0.01 else 'idle'

    def update(self, platforms: list[pygame.Rect]):
        # Patrol logic: move between left and right bounds and flip when reaching ends
        # Choose direction based on bounds
        if self.direction > 0:
            # heading right
            if self.rect.centerx >= self.right_bound_x:
                self.direction = -1
        else:
            # heading left
            if self.rect.centerx <= self.left_bound_x:
                self.direction = 1

        # Apply horizontal speed
        self.velocity.x = self.speed * self.direction

        # Advance physics + animation
        self.step(platforms)
