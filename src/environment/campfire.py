import os
import pygame
from utils.exception import AssetLoadError


def load_campfire_frames(assets_path: str) -> list[pygame.Surface]:
    """Load campfire frames by scanning the Campfire folder and sorting PNGs."""
    frames: list[pygame.Surface] = []
    try:
        campfire_dir = os.path.join(assets_path, 'Background', 'Campfire')
        if os.path.isdir(campfire_dir):
            files = [f for f in os.listdir(campfire_dir) if f.lower().endswith('.png')]
            files.sort()
            for fname in files:
                full = os.path.join(campfire_dir, fname)
                image = pygame.image.load(full).convert_alpha()
                frames.append(image)
        else:
            raise FileNotFoundError(campfire_dir)
    except Exception as e:
        print(str(AssetLoadError("Background Campfire frames", e)))
    return frames


class Campfire:
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.frame_index: float = 0.0

    def update(self, frames: list[pygame.Surface], animation_speed: float = 0.15):
        if not frames:
            return
        self.frame_index += animation_speed
        if self.frame_index >= len(frames):
            self.frame_index = 0.0

    def draw(self, surface: pygame.Surface, offset_x: float, offset_y: float, frames: list[pygame.Surface]):
        if not frames:
            return
        idx = int(self.frame_index)
        if 0 <= idx < len(frames):
            image_to_draw = frames[idx]
            scaled_image = pygame.transform.scale(image_to_draw, (self.rect.width, self.rect.height))
            vertical_offset = 10
            surface.blit(scaled_image, (self.rect.x - offset_x, self.rect.y - offset_y + vertical_offset))
