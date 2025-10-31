import os
import pygame
from typing import Optional
from entity.entity import Entity
from exception import AssetLoadError


class Enemy(Entity):
    def __init__(self, x: int, y: int, initial_image: Optional[pygame.Surface] = None, size=(30, 30)):
        self.animations = {'run': [], 'idle': []}
        if initial_image is None:
            fallback = pygame.Surface(size, pygame.SRCALPHA)
            fallback.fill((0, 0, 0))
            initial_image = fallback
            self.animations['run'] = [fallback]
            self.animations['idle'] = [fallback]

        super().__init__(x, y, initial_image)

        self.state = 'idle'
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_finished = False
        self.non_looping_states = {'death'}

        self.is_dying = False
        self._idle_locked = False
        self._idle_until_ms = 0
        self.base_faces_right = True

    def draw(self, screen: pygame.Surface, camera_offset_x: float, camera_offset_y: float):
        flip = (self.direction == -1 and self.base_faces_right) or (self.direction == 1 and not self.base_faces_right)
        final_image = pygame.transform.flip(self.image, True, False) if flip else self.image
        draw_y_offset = getattr(self, 'draw_offset_y', 0)
        screen.blit(final_image, (self.rect.x - camera_offset_x, self.rect.y - camera_offset_y + draw_y_offset))

    def get_block_rect(self, width: int = 25, height: int = 25) -> pygame.Rect:
        cx, cy = self.rect.centerx, self.rect.centery
        left = int(cx - width // 2)
        top = int(cy - height // 2)
        return pygame.Rect(left, top, width, height)

    def on_player_contact(self):
        self._idle_locked = True
        duration = getattr(self, 'contact_idle_duration_ms', 400)
        self._idle_until_ms = pygame.time.get_ticks() + duration
        self.state = 'idle'

    def _is_idling_due_to_contact(self) -> bool:
        if self._idle_locked:
            if pygame.time.get_ticks() < self._idle_until_ms:
                self.state = 'idle'
                return True
            self._idle_locked = False
        return False

    def on_killed_by_player(self):
        self.is_dying = True
        self.state = 'death'
        self.frame_index = 0
        self.animation_finished = False
        self.is_alive = True
        self.remove_at_ms = pygame.time.get_ticks() + 1500
class PatrollingEnemy(Enemy):
    def __init__(self, x: int, y: int, left_bound_x: Optional[float] = None, right_bound_x: Optional[float] = None, size=(50, 50), speed: float = 2.0, sprite_dir: Optional[str] = None):
        run_frames = []
        idle_frames = []
        base_path = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(base_path, '..', '..'))
        dog_run_dir = os.path.join(project_root, 'Assets', 'Enemies', 'Dog', 'Sprites', 'Dog')
        dog_idle_dir = os.path.join(project_root, 'Assets', 'Enemies', 'Dog', 'Sprites', 'Dog-idle')

        try:
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

        initial_image = run_frames[0]
        super().__init__(x, y, initial_image, size=size)

        self.animations['run'] = run_frames
        self.animations['idle'] = idle_frames if idle_frames else [run_frames[0]]

        self.left_bound_x = left_bound_x if left_bound_x is not None else self.rect.centerx - 80
        self.right_bound_x = right_bound_x if right_bound_x is not None else self.rect.centerx + 80
        if self.left_bound_x > self.right_bound_x:
            self.left_bound_x, self.right_bound_x = self.right_bound_x, self.left_bound_x

        self.speed = abs(speed)
        self.direction = 1
        self.state = 'run'
        self.base_faces_right = False

        self.vertical_offset = 4
        self.rect.bottom -= self.vertical_offset

        self.draw_offset_y = 5

        self.contact_idle_duration_ms = 400
        self._idle_until_ms = 0
        self._idle_locked = False

    def compute_state(self) -> str:
        return super().compute_state()

    def update(self, platforms: list[pygame.Rect], player: Optional[Entity] = None):
        if self.is_dying:
            self.velocity.x = 0
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


class ChaserEnemy(Enemy):
    """Chaser with Light Bandit animations; no long cooldown, brief combat idle after a landed hit."""
    def __init__(self, x: int, y: int, size=(50, 50), speed: float = 2.5, facing: str = 'right'):
        base_path = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(base_path, '..', '..'))
        bandit_dir = os.path.join(project_root, 'Assets', 'Enemies', 'Light Bandit')

        def load_folder(folder: str) -> list[pygame.Surface]:
            frames = []
            try:
                if os.path.isdir(folder):
                    files = [f for f in os.listdir(folder) if f.lower().endswith('.png')]
                    files.sort()
                    for f in files:
                        img = pygame.image.load(os.path.join(folder, f)).convert_alpha()
                        if size:
                            img = pygame.transform.scale(img, size)
                        frames.append(img)
            except Exception as e:
                print(str(AssetLoadError(folder, e)))
            return frames

        idle_frames = load_folder(os.path.join(bandit_dir, 'Idle'))
        run_frames = load_folder(os.path.join(bandit_dir, 'Run'))
        attack_frames = load_folder(os.path.join(bandit_dir, 'Attack'))
        death_frames = load_folder(os.path.join(bandit_dir, 'Death'))
        combat_idle_frames = load_folder(os.path.join(bandit_dir, 'Combat Idle'))

        if not idle_frames:
            fallback = pygame.Surface(size, pygame.SRCALPHA)
            fallback.fill((0, 0, 0))
            idle_frames = [fallback]
        initial_img = idle_frames[0]

        super().__init__(x, y, initial_img, size=size)

        self.animations['idle'] = idle_frames
        self.animations['run'] = run_frames if run_frames else idle_frames
        self.animations['attack'] = attack_frames if attack_frames else idle_frames
        self.animations['death'] = death_frames if death_frames else idle_frames
        self.animations['combat_idle'] = combat_idle_frames if combat_idle_frames else idle_frames

        self.non_looping_states = {'attack', 'death'}

        self.speed = abs(speed)
        self.direction = 1 if facing == 'right' else -1
        self.alerted = False
        self.base_faces_right = False

        self.detect_range_x = 140
        self.detect_range_y = 80

        self.attack_range_x = 30
        self.attack_vertical_tolerance = 30
        self.combat_idle_duration_ms = 300
        self._combat_idle_until_ms = 0
        self._landed_hit_this_attack = False

        self.vertical_offset = 4
        self.rect.bottom -= self.vertical_offset

        self.draw_offset_y = 2

        atk_len = len(self.animations.get('attack', []))
        if atk_len >= 6:
            self.hit_frames = {4, 5}
        elif atk_len >= 4:
            self.hit_frames = {atk_len // 2}
        else:
            self.hit_frames = {0}

    def _player_in_proximity(self, player: Entity) -> bool:
        if player is None:
            return False
        dx = abs(player.rect.centerx - self.rect.centerx)
        dy = player.rect.bottom - self.rect.top
        return dx <= self.detect_range_x and dy <= self.detect_range_y

    def _player_jumped_over(self, player: Entity) -> bool:
        if player is None:
            return False
        dx = abs(player.rect.centerx - self.rect.centerx)
        return player.rect.bottom < self.rect.top and dx <= max(24, self.rect.width // 2 + 10)

    def _can_attack_now(self) -> bool:
        return True

    def _in_attack_range(self, player: Entity) -> bool:
        dx = abs(player.rect.centerx - self.rect.centerx)
        dy = abs(player.rect.centery - self.rect.centery)
        return dx <= self.attack_range_x and dy <= max(self.attack_vertical_tolerance, self.rect.height // 2)

    def compute_state(self) -> str:
        if not self.is_alive:
            return 'death'
        if self.state in ('attack', 'combat_idle'):
            return self.state
        return 'run' if self.alerted else 'idle'

    def update(self, platforms: list[pygame.Rect], player: Optional[Entity] = None):
        if self.is_dying:
            self.velocity.x = 0
            self._idle_locked = True
            self.state = 'idle'
            self.animate()
            return

        now = pygame.time.get_ticks()

        if player:
            contact_rect = self.get_block_rect()
            if contact_rect.colliderect(player.rect) and self.state != 'attack':
                self.alerted = True
                self.direction = 1 if (player.rect.centerx >= self.rect.centerx) else -1
                self.state = 'attack'
                self.frame_index = 0
                self.animation_finished = False
                self.velocity.x = 0
                self.step(platforms)
                return

        if self.state == 'attack':
            self.velocity.x = 0
            if player and self.is_hazard_active() and self.get_hazard_rect().colliderect(player.rect):
                self._landed_hit_this_attack = True
            self.step(platforms)
            if self.animation_finished:
                if self._landed_hit_this_attack:
                    self.state = 'combat_idle'
                    self.frame_index = 0
                    self.animation_finished = False
                    self._combat_idle_until_ms = now + self.combat_idle_duration_ms
                else:
                    self.state = 'run' if self.alerted else 'idle'
                self._landed_hit_this_attack = False
            return

        if self.state == 'combat_idle':
            self.velocity.x = 0
            self.step(platforms)
            if now >= self._combat_idle_until_ms:
                self.state = 'run' if self.alerted else 'idle'
            return

        if not self.alerted:
            if player and (self._player_in_proximity(player) or self._player_jumped_over(player)):
                self.alerted = True
                self.direction = 1 if (player.rect.centerx >= self.rect.centerx) else -1

        if self.alerted and player:
            self.direction = 1 if (player.rect.centerx >= self.rect.centerx) else -1
            if self._can_attack_now() and self._in_attack_range(player):
                self.state = 'attack'
                self.frame_index = 0
                self.animation_finished = False
                self.velocity.x = 0
            else:
                self.velocity.x = self.speed * self.direction
        else:
            self.velocity.x = 0

        self.step(platforms)

    def is_hazard_active(self) -> bool:
        if self.state != 'attack':
            return False
        return self.frame_index in getattr(self, 'hit_frames', set())

    def get_hazard_rect(self) -> pygame.Rect:
        block = self.get_block_rect()
        w = 34
        h = 28
        y = int(block.centery - h // 2)
        if self.direction == 1:
            x = block.right
        else:
            x = block.left - w
        return pygame.Rect(x, y, w, h)

