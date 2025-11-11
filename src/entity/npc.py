# src/entity/npc.py
import pygame
from pathlib import Path
from .entity import Entity   

TALK_KEY = pygame.K_e

# --- Helper aset (tanpa ketergantungan file lain) ---
def project_root_from_this_file() -> Path:
    # .../src/entity/npc.py -> .../ (root ProjectGame-GIGA)
    return Path(__file__).resolve().parents[2]

def load_images_dir(*parts, key_exts=(".png", ".jpg", ".jpeg", ".bmp", ".gif")):
    base = project_root_from_this_file() / "Assets" / "npc"  
    folder = base.joinpath(*parts)
    if not folder.exists():
        print(f"[WARNING] Folder {folder} tidak ditemukan.")
        return []
    files = sorted([p for p in folder.iterdir() if p.suffix.lower() in key_exts],
                   key=lambda p: p.name.lower())
    frames = []
    for p in files:
        surf = pygame.image.load(str(p)).convert_alpha()
        frames.append(surf)
    return frames


def load_font_rel(path_in_assets: str, size=22):
    fpath = project_root_from_this_file() / "assets" / path_in_assets
    return pygame.font.Font(str(fpath), size)

class NPC(Entity):
    def __init__(self, x, y, variant="oldman", dialog_lines=None, patrol=None,
                 font_path="fonts/freesansbold.ttf", dim='both', auto_snap=True):
        # load frames dulu
        self.variant = variant
        self.idle_frames = load_images_dir(f"{variant}-idle")
        self.walk_frames = load_images_dir(f"{variant}-walk")

        if not self.idle_frames:
            surf = pygame.Surface((48, 64), pygame.SRCALPHA)
            surf.fill((255, 200, 0, 255))
            self.idle_frames = [surf]

        # ambil gambar pertama untuk dikirim ke Entity
        first_image = self.idle_frames[0]
        super().__init__(x, y, first_image)
        self.image = first_image
        self.rect = self.image.get_rect(bottomleft=(x, y))
        self.dim = dim
        self.frame_index = 0.0
        self.anim_speed = 0.15
        self.auto_snap = auto_snap 
 
        # interaksi
        self.show_prompt = False
        self.talking = False
        self.dialog_lines = dialog_lines or [
            "Halo! Tekan [E] untuk lanjut.",
            "Selamat datang di Dual Dimension!",
            "Hati-hati jebakan dan semoga sukses!",
        ]
        self.dialog_index = 0

        # patrol opsional
        self.patrol = patrol  # contoh: ((200, 420), 0.8)

        # font UI
        try:
            self.font = load_font_rel(font_path, size=22)
        except Exception:
            self.font = pygame.font.SysFont(None, 22)

    def update(self, player_rect: pygame.Rect):
        # animasi
        if len(self.idle_frames) > 1:
            self.frame_index = (self.frame_index + self.anim_speed) % len(self.idle_frames)
            self.image = self.idle_frames[int(self.frame_index)]

        # patrol sederhana
        if self.patrol:
            (x1, x2), speed = self.patrol
            self.rect.x += speed
            if self.rect.x < min(x1, x2) or self.rect.x > max(x1, x2):
                self.patrol = ((x1, x2), -speed)

        # deteksi jarak ke player
        dist_x = abs(self.rect.centerx - player_rect.centerx)
        dist_y = abs(self.rect.centery - player_rect.centery)
        self.show_prompt = (dist_x < 120 and dist_y < 120)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key == TALK_KEY and self.show_prompt:
            if not self.talking:
                self.talking = True
                self.dialog_index = 0
            else:
                self.dialog_index += 1
                if self.dialog_index >= len(self.dialog_lines):
                    self.talking = False

    def draw(self, screen, camera_offset_x=0, camera_offset_y=0):
        # gambar sprite npc
        screen.blit(self.image, (self.rect.x - camera_offset_x, self.rect.y - camera_offset_y))
        # UI (prompt/dialog)
        if self.talking:
            self._draw_dialog_box(screen, camera_offset_x, camera_offset_y)
        elif self.show_prompt:
            self._draw_prompt(screen, camera_offset_x, camera_offset_y)

    def _draw_prompt(self, screen, camera_offset_x, camera_offset_y):
        text = self.font.render("Tekan [E] untuk bicara", True, (255, 255, 255))
        w, h = text.get_size()
        pad = 6
        x = self.rect.centerx - w // 2 - camera_offset_x
        y = self.rect.y - 36 - camera_offset_y
        pygame.draw.rect(screen, (0, 0, 0), (x - pad, y - pad, w + 2*pad, h + 2*pad), border_radius=8)
        screen.blit(text, (x, y))

    def _draw_dialog_box(self, screen, camera_offset_x, camera_offset_y):
        dlg = self.dialog_lines[self.dialog_index]
        text = self.font.render(dlg, True, (255, 255, 255))
        w, h = text.get_size()
        pad = 10
        x = self.rect.centerx - w // 2 - camera_offset_x
        y = self.rect.y - 80 - camera_offset_y
        pygame.draw.rect(screen, (20, 20, 20), (x - pad, y - pad, w + 2*pad, h + 2*pad), border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), (x - pad, y - pad, w + 2*pad, h + 2*pad), 2, border_radius=10)
        screen.blit(text, (x, y))
