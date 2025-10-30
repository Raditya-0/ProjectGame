import os
import pygame
from entity.entity import Entity
from exception import AssetLoadError


class Enemy(Entity):
    def __init__(self, x: int, y: int, left_bound_x: float | None = None, right_bound_x: float | None = None, size=(30, 30), speed: float = 2.0):
        self.animations = {'run': [], 'idle': []}
        run_frames = []
        idle_frames = []

        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(base_path, '..', '..'))
            dog_run_dir = os.path.join(project_root, 'Assets', 'Enemies', 'Dog', 'Sprites', 'Dog')
            dog_idle_dir = os.path.join(project_root, 'Assets', 'Enemies', 'Dog', 'Sprites', 'Dog-idle')

            if os.path.isdir(dog_run_dir):
                filenames = [f for f in os.listdir(dog_run_dir) if f.lower().endswith('.png')]
                filenames.sort()
                for fname in filenames:
                    img = pygame.image.load(os.path.join(dog_run_dir, fname)).convert_alpha()
                    if size:
                        img = pygame.transform.scale(img, size)
                    run_frames.append(img)
            else:
                raise FileNotFoundError(dog_run_dir)
        except Exception as e:
            print(str(AssetLoadError(dog_run_dir, e)))
            fallback = pygame.Surface(size, pygame.SRCALPHA)
            fallback.fill((0, 0, 0))
            run_frames = [fallback] * 4

        try:
            if os.path.isdir(dog_idle_dir):
                filenames = [f for f in os.listdir(dog_idle_dir) if f.lower().endswith('.png')]
                filenames.sort()
                for fname in filenames:
                    img = pygame.image.load(os.path.join(dog_idle_dir, fname)).convert_alpha()
                    if size:
                        img = pygame.transform.scale(img, size)
                    idle_frames.append(img)
        except Exception as e:
            print(str(AssetLoadError(dog_idle_dir, e)))

        self.animations['run'] = run_frames
        self.animations['idle'] = idle_frames if idle_frames else [run_frames[0]]
        initial_image = self.animations['run'][0]
        super().__init__(x, y, initial_image)

        self.left_bound_x = left_bound_x if left_bound_x is not None else self.rect.centerx - 80
        self.right_bound_x = right_bound_x if right_bound_x is not None else self.rect.centerx + 80
        if self.left_bound_x > self.right_bound_x:
            self.left_bound_x, self.right_bound_x = self.right_bound_x, self.left_bound_x

        self.speed = abs(speed)
        self.direction = 1
        self.state = 'run'

        self.base_faces_right = False

        self.contact_idle_duration_ms = 400
        self._idle_until_ms = 0
        self._idle_locked = False

        # Death/cleanup handling
        self.is_dying = False
        self.remove_at_ms = 0

    def on_player_contact(self):
        now = pygame.time.get_ticks()
        self._idle_locked = True
        self._idle_until_ms = max(self._idle_until_ms, now + self.contact_idle_duration_ms)

    def _is_idling_due_to_contact(self) -> bool:
        return self._idle_locked or (pygame.time.get_ticks() < self._idle_until_ms)

    def clear_contact_idle(self):
        self._idle_locked = False
        self._idle_until_ms = 0

    def compute_state(self) -> str:
        if not self.is_alive:
            return 'death'
        return 'idle' if self._is_idling_due_to_contact() else 'run'

    def update(self, platforms: list[pygame.Rect]):
        # If dying, freeze in place and just animate idle until removal time
        if self.is_dying:
            self.velocity.x = 0
            # Force idle visual while dying
            self._idle_locked = True
            self.state = 'idle'
            self.animate()
            return

        if self._is_idling_due_to_contact():
            self.velocity.x = 0
        else:
            if self.direction > 0:
                if self.rect.centerx >= self.right_bound_x:
                    self.direction = -1
            else:
                if self.rect.centerx <= self.left_bound_x:
                    self.direction = 1

            self.velocity.x = self.speed * self.direction

        self.step(platforms)

    def draw(self, screen: pygame.Surface, camera_offset_x: float, camera_offset_y: float):
        final_image = self.image
        flip_x = (self.direction == -1) if self.base_faces_right else (self.direction == 1)
        if flip_x:
            final_image = pygame.transform.flip(self.image, True, False)
        screen.blit(final_image, (self.rect.x - camera_offset_x, self.rect.y - camera_offset_y))

    # Called when hit by player's attack
    def on_killed_by_player(self, remove_delay_ms: int = 400):
        if self.is_dying:
            return
        self.is_dying = True
        self.velocity.x = 0
        self._idle_locked = True
        self.state = 'idle'
        self.frame_index = 0
        self.animation_finished = False
        self.remove_at_ms = pygame.time.get_ticks() + remove_delay_ms

