# main.py
# File utama (Logika Jeda Kematian & Animasi)

import pygame
from settings import *
import assets
from player import Player
from level import level_1_layout, level_2_layout

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.game_surface_width = SCREEN_WIDTH // CAMERA_ZOOM_DIVIDER
        self.game_surface_height = SCREEN_HEIGHT // CAMERA_ZOOM_DIVIDER
        self.game_surface = pygame.Surface((self.game_surface_width, self.game_surface_height))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 40)
        self.load_assets()
        self.levels = [level_1_layout, level_2_layout]
        self.current_level_index = 0
        self.spawn_invincibility_timer = 0
        self.spawn_invincibility_duration = 10
        
        self.death_delay_timer = 0
        self.death_delay_start_time = 0
        self.is_in_death_delay = False

    def load_assets(self): self.heart_icon = assets.create_heart_surface()
        
    def setup_level(self, layout, new_game=False):
        start_platform_data = layout[0]
        start_x, platform_top_y = 100, start_platform_data[1]
        start_y = platform_top_y - 1
        self.start_pos = (start_x, start_y)
        self.player = Player(start_x, start_y)
        
        # Hanya reset jebakan jika ini game baru / game over total
        if new_game:
            self.trigger_traps = []
            self.platforms, self.traps, self.door_rect = [], [], None
            for item in layout:
                if isinstance(item, dict):
                    if item['type'] == 'trigger_trap':
                        tr, tp = item['trigger_rect'], item['trap_rect']
                        self.trigger_traps.append({'trigger_rect': pygame.Rect(tr), 'trap_rect': pygame.Rect(tp), 'dim': item['dim'], 'is_active': False})
                else:
                    x, y, w, h, dimension, obj_type = item
                    rect = pygame.Rect(x, y, w, h)
                    if obj_type == 'platform': self.platforms.append({'rect': rect, 'dim': dimension})
                    elif obj_type == 'trap': self.traps.append({'rect': rect, 'dim': dimension})
                    elif obj_type == 'door': self.door_rect = rect
        
        self.spawn_invincibility_timer = self.spawn_invincibility_duration

    def handle_triggers(self):
        if not self.player.is_alive: return
        current_dimension_str = 'gema' if self.player.in_gema_dimension else 'normal'
        for trap in self.trigger_traps:
            if not trap['is_active'] and (trap['dim'] in [current_dimension_str, 'both']):
                if self.player.rect.colliderect(trap['trigger_rect']): trap['is_active'] = True

    def respawn_player(self):
        self.player.respawn(self.start_pos)
        self.spawn_invincibility_timer = self.spawn_invincibility_duration
        self.is_in_death_delay = False

    def handle_damage(self):
        if self.spawn_invincibility_timer > 0 or not self.player.is_alive or self.is_in_death_delay: return
        
        damage_source = None
        if self.player.rect.top > SCREEN_HEIGHT:
            damage_source = 'fall'
            
        current_dimension_str = 'gema' if self.player.in_gema_dimension else 'normal'
        active_trap_rects = [t['rect'] for t in self.traps if t['dim'] in [current_dimension_str, 'both']]
        for trap in self.trigger_traps:
            if trap['is_active'] and trap['dim'] in [current_dimension_str, 'both']:
                active_trap_rects.append(trap['trap_rect'])
        for trap_rect in active_trap_rects:
            if self.player.rect.colliderect(trap_rect):
                damage_source = 'trap'
                break
                
        if damage_source:
            # Panggil take_damage dan die.
            self.player.take_damage()
            self.player.die()

            # Jika masih ada sisa hati, mulai jeda 0.5 detik.
            # Logika ini sekarang berlaku untuk SEMUA jenis kerusakan.
            if self.player.hearts > 0:
                self.is_in_death_delay = True
                self.death_delay_timer = 300 # Jeda 0.3 detik
                self.death_delay_start_time = pygame.time.get_ticks()

    def go_to_next_level(self):
        """Menaikkan indeks level, memuat level baru, dan mempertahankan HP."""
        # --- PERUBAHAN: Simpan HP saat ini sebelum ganti level ---
        current_hearts = self.player.hearts

        self.current_level_index += 1
        if self.current_level_index < len(self.levels):
            print(f"Memuat Level {self.current_level_index + 1}...")
            self.setup_level(self.levels[self.current_level_index], new_game=True)
            
            # --- PERUBAHAN: Terapkan kembali HP yang disimpan ke player baru ---
            self.player.hearts = current_hearts
        else:
            self.running = False
            print("Selamat! Anda telah menyelesaikan semua level!")

    def check_level_completion(self):
        if self.player.is_alive and self.door_rect and self.door_rect.contains(self.player.rect):
            self.go_to_next_level()

    def run(self):
            self.setup_level(self.levels[self.current_level_index], new_game=True)
            
            camera_offset_x = 0
            camera_offset_y = 0
            
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key in [pygame.K_SPACE, pygame.K_UP, pygame.K_w]:
                            self.player.jump()
                        if event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
                            self.player.shift_dimension()

                if self.spawn_invincibility_timer > 0:
                    self.spawn_invincibility_timer -= 1

                current_dimension_str = 'gema' if self.player.in_gema_dimension else 'normal'
                active_platforms = [p['rect'] for p in self.platforms if p['dim'] in [current_dimension_str, 'both']]
                
                # Selalu update player untuk menangani fisika dan animasi
                self.player.update(active_platforms)
                
                if self.player.is_alive:
                    # Jika pemain hidup, jalankan semua logika game
                    self.handle_triggers()
                    self.handle_damage()
                    self.check_level_completion()
                else: 
                    # Jika pemain mati, tangani logika jeda dan game over
                    if self.is_in_death_delay:
                        is_ready_for_delay = (self.player.state == 'death' and self.player.animation_finished) or (self.player.state != 'death')
                        if is_ready_for_delay:
                            current_time = pygame.time.get_ticks()
                            if current_time - self.death_delay_start_time > self.death_delay_timer:
                                self.respawn_player()
                    
                    # Logika Game Over: kembali ke Level 1
                    elif self.player.hearts <= 0:
                        print("Game Over! Kembali ke Level 1...")
                        self.current_level_index = 0 # Reset ke level pertama
                        self.setup_level(self.levels[self.current_level_index], new_game=True)

                # --- Logika Kamera dan Drawing ---
                camera_offset_x = self.player.rect.centerx - self.game_surface_width / 2
                camera_offset_y = CAMERA_MANUAL_OFFSET_Y # Kamera Y terkunci
                
                final_offset_x = camera_offset_x + CAMERA_MANUAL_OFFSET_X
                final_offset_y = camera_offset_y
                
                self.game_surface.fill(COLOR_BG_GEMA if self.player.in_gema_dimension else COLOR_BG_NORMAL)
                
                # Gambar semua platform
                for p in self.platforms:
                    if p['dim'] in [current_dimension_str, 'both']:
                        surf = assets.create_platform_surface(p['rect'].width, p['rect'].height, p['dim'])
                        self.game_surface.blit(surf, (p['rect'].x - final_offset_x, p['rect'].y - final_offset_y))
                
                # Gambar semua jebakan yang aktif
                active_trap_surfaces = []
                for t in self.traps:
                    if t['dim'] in [current_dimension_str, 'both']:
                        active_trap_surfaces.append((t['rect'], assets.create_trap_surface(t['rect'].width, t['rect'].height)))
                for trap in self.trigger_traps:
                    if trap['is_active'] and trap['dim'] in [current_dimension_str, 'both']:
                        surf = assets.create_trap_surface(trap['trap_rect'].width, trap['trap_rect'].height)
                        active_trap_surfaces.append((trap['trap_rect'], surf))
                for rect, surf in active_trap_surfaces:
                    self.game_surface.blit(surf, (rect.x - final_offset_x, rect.y - final_offset_y))

                # Gambar pintu
                if self.door_rect:
                    door_surf = assets.create_door_surface(self.door_rect.width, self.door_rect.height)
                    self.game_surface.blit(door_surf, (self.door_rect.x - final_offset_x, self.door_rect.y - final_offset_y))
                
                # Gambar pemain
                self.player.draw(self.game_surface, final_offset_x, final_offset_y)
                
                # Skalakan game surface ke layar utama
                self.screen.blit(pygame.transform.scale(self.game_surface, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))

                # Gambar UI Hati di atas segalanya
                for i in range(self.player.hearts):
                    self.screen.blit(self.heart_icon, (10 + i * 35, 10))

                pygame.display.flip()
                self.clock.tick(FPS)
                
            pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()