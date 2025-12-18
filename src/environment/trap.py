import os
import pygame
from utils.exception import AssetLoadError


def load_spike_frames(assets_path: str) -> list[pygame.Surface]:
    """Load spike animation frames from Assets/Tiles/spike_animation.png."""
    frames: list[pygame.Surface] = []
    try:
        sheet_path = os.path.join(assets_path, 'Tiles', 'spike_animation.png')
        spike_sheet = pygame.image.load(sheet_path).convert_alpha()
        frame_width, frame_height, frame_count = 40, 40, 4
        left_margin, gap_width, top_margin = 0, 0, 0
        for i in range(frame_count):
            x_pos = left_margin + i * (frame_width + gap_width)
            y_pos = top_margin
            frame_surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame_surface.blit(spike_sheet, (0, 0), (x_pos, y_pos, frame_width, frame_height))
            frames.append(frame_surface)
    except Exception as e:
        print(str(AssetLoadError("Tiles spike_animation.png", e)))
    return frames


class TriggerTrap:
    """A trigger zone that activates a spike animation and becomes hazardous when active."""
    def __init__(self, trigger_rect: pygame.Rect, trap_rect: pygame.Rect, dim: str):
        self.trigger_rect = trigger_rect
        self.trap_rect = trap_rect
        self.dim = dim  # 'normal' | 'gema' | 'both'
        self.is_active: bool = False
        self.frame_index: float = 0.0
        self.animation_finished: bool = False

    def try_activate(self, player_rect: pygame.Rect, current_dimension: str):
        if not self.is_active and (self.dim in [current_dimension, 'both']):
            if player_rect.colliderect(self.trigger_rect):
                self.is_active = True

    def update(self, frames: list[pygame.Surface], animation_speed: float = 0.2):
        if self.is_active and not self.animation_finished:
            self.frame_index += animation_speed
            if frames:
                if self.frame_index >= len(frames):
                    self.animation_finished = True
                    self.frame_index = len(frames) - 1

    def draw(self, surface: pygame.Surface, offset_x: float, offset_y: float, frames: list[pygame.Surface]):
        if not self.is_active or not frames:
            return
        idx = int(self.frame_index)
        if 0 <= idx < len(frames):
            frame_to_draw = frames[idx]
            scaled_image = pygame.transform.scale(frame_to_draw, (self.trap_rect.width, self.trap_rect.height))
            vertical_offset = 20
            draw_y = self.trap_rect.y + vertical_offset
            surface.blit(scaled_image, (self.trap_rect.x - offset_x, draw_y - offset_y))

    def get_hazard_rect(self) -> pygame.Rect:
        return self.trap_rect.copy()
