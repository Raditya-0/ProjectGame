# src/entity/npc.py
import pygame
from pathlib import Path
from .entity import Entity   

TALK_KEY = pygame.K_e

# --- Dialog Presets ---
NPC_DIALOGS = {
    'oldman_normal': (
        "Halo, traveler!",
        "Selamat datang di dunia Dual Dimension.",
        "Di sini kamu bisa berpindah antara dua dimensi.",
        "Untuk mengalahkan musuh,\n klik touchpad saat dekat.",
        "Gunakan kemampuanmu dengan bijak.",
        "Semoga perjalananmu lancar!"
    ),
    'oldman_gema': (
        "Ini adalah dimensi gema.",
        "Semuanya di sini berbeda dari dunia normal.",
        "Platform dan musuh bisa berbeda.",
        "Untuk mengalahkan musuh,\n   klik touchpad saat dekat.",
        "Berhati-hatilah di sini.",
        "Jangan lupa untuk kembali ke dimensi normal!"
    ),
    'woman_normal': (
        "Halo, traveler!",
        "Selamat datang di dunia Dual Dimension.",
        "Di sini kamu bisa berpindah antara dua dimensi.",
        "Untuk mengalahkan musuh,\n klik touchpad saat dekat.",
        "Gunakan kemampuanmu dengan bijak.",
        "Semoga perjalananmu lancar!"
    ),
    'woman_gema': (
        "Ini adalah dimensi gema.",
        "Semuanya di sini berbeda dari dunia normal.",
        "Platform dan musuh bisa berbeda.",
        "Untuk mengalahkan musuh,\n klik touchpad saat dekat.",
        "Berhati-hatilah di sini.",
        "Jangan lupa untuk kembali ke dimensi normal!"
    ),
    'bearded_normal': (
        "Selamat datang, petualang!",
        "Aku akan mengajarkanmu mekanik penting.",
        "Tekan [SHIFT] untuk berpindah dimensi.",
        "Kamu bisa berpindah kapan saja!",
        "Gunakan ini dengan bijak \n  untuk menghindari bahaya.",
        "Selamat berpetualang!"
    ),
    'bearded_gema': (
        "Oh, kamu sudah di dimensi gema!",
        "Dimensi ini penuh misteri dan bahaya.",
        "Beberapa platform hanya muncul di dimensi ini.",
        "Tekan [SHIFT] untuk kembali ke dimensi normal.",
        "Jangan terlalu lama di sini!"
    ),
    'hat-man_normal': (
        "Hati-hati dengan musuh di depan!",
        "Mereka sangat berbahaya.",
        "Semoga beruntung!"
    ),
    'hat-man_gema': (
        "Selamat datang di dimensi gema.",
        "Di sini semuanya berbeda.",
        "Berhati-hatilah dalam melangkah.",
        "Hindari Trap."
    ),
}

def get_npc_dialog(variant, dim):
    """Helper function untuk mendapatkan dialog preset berdasarkan variant dan dimensi"""
    key = f"{variant}_{dim}"
    return NPC_DIALOGS.get(key, NPC_DIALOGS.get(f"{variant}_normal", (
        "Halo! Tekan [E] untuk lanjut.",
        "Selamat datang di Dual Dimension!",
        "Hati-hati jebakan dan semoga sukses!",
    )))

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
        self.anim_speed = 0.08
        self.auto_snap = auto_snap 
 
        # interaksi
        self.show_prompt = False
        self.talking = False
        # Simpan dialog sebagai tuple (immutable) untuk memastikan urutan tidak berubah
        if dialog_lines is not None:
            self.dialog_lines = tuple(dialog_lines)
        else:
            # Gunakan preset dialog berdasarkan variant dan dim
            self.dialog_lines = get_npc_dialog(variant, dim if dim in ('normal', 'gema') else 'normal')
        self.dialog_index = 0
        
        # Simpan total dialog untuk safety check
        self.total_dialogs = len(self.dialog_lines)

        # patrol opsional
        self.patrol = patrol  # contoh: ((200, 420), 0.8)

        # font UI
        try:
            self.font = load_font_rel(font_path, size=16)
        except Exception:
            self.font = pygame.font.SysFont(None, 16)

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
                # Mulai percakapan dari awal (index 0)
                self.talking = True
                self.dialog_index = 0
            else:
                # Lanjut ke dialog berikutnya
                self.dialog_index += 1
                # Pastikan index tidak melebihi jumlah dialog
                if self.dialog_index >= len(self.dialog_lines):
                    # Selesai, tutup dialog dan reset ke 0
                    self.talking = False
                    self.dialog_index = 0

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
        # Safety check: pastikan index valid
        if self.dialog_index < 0 or self.dialog_index >= len(self.dialog_lines):
            self.dialog_index = 0
            
        # Ambil dialog sesuai index saat ini
        dlg = self.dialog_lines[self.dialog_index]
        
        # Split by newline untuk multi-line support
        lines = dlg.split('\n')
        text_surfaces = [self.font.render(line, True, (255, 255, 255)) for line in lines]
        
        # Hitung ukuran box berdasarkan line terpanjang dan jumlah baris
        max_w = max(surf.get_width() for surf in text_surfaces)
        line_height = text_surfaces[0].get_height()
        total_h = line_height * len(lines) + (len(lines) - 1) * 5  # 5px spacing antar baris
        
        pad = 10
        x = self.rect.centerx - max_w // 2 - camera_offset_x
        y = self.rect.y - 80 - camera_offset_y
        
        # Draw background box
        pygame.draw.rect(screen, (20, 20, 20), (x - pad, y - pad, max_w + 2*pad, total_h + 2*pad), border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), (x - pad, y - pad, max_w + 2*pad, total_h + 2*pad), 2, border_radius=10)
        
        # Draw each line
        current_y = y
        for surf in text_surfaces:
            screen.blit(surf, (x, current_y))
            current_y += line_height + 5
