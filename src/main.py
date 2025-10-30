import pygame
from settings import *
import assets
from entity.player import Player
from parallax import ParallaxLayer, ParallaxObject
from entity.enemy import Enemy
import os

base_path = os.path.dirname(os.path.abspath(__file__))
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.game_surface_width = SCREEN_WIDTH // CAMERA_ZOOM_DIVIDER
        self.game_surface_height = SCREEN_HEIGHT // CAMERA_ZOOM_DIVIDER
        self.game_surface = pygame.Surface((self.game_surface_width, self.game_surface_height))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 40)
        self.game_state = 'main_menu'
        self.prev_game_state = 'main_menu'
        
        self.spike_animation_frames = []
        self.parallax_layers = []
        
        self.levels = [
            (os.path.join(base_path, "levels", "level_1_normal.txt"), os.path.join(base_path, "levels", "level_1_gema.txt")),
            (os.path.join(base_path, "levels", "level_2_normal.txt"), os.path.join(base_path, "levels", "level_2_gema.txt")),
            (os.path.join(base_path, "levels", "level_3_normal.txt"), os.path.join(base_path, "levels", "level_3_gema.txt")),
            (os.path.join(base_path, "levels", "level_4_normal.txt"), os.path.join(base_path, "levels", "level_4_gema.txt"))
        ]
        self.load_assets()
        self.current_level_index = 0
        
        self.spawn_invincibility_timer = 0
        self.spawn_invincibility_duration = 10
        self.death_delay_timer = 0
        self.death_delay_start_time = 0
        self.is_in_death_delay = False

        self.is_music_paused = False
        self.is_settings_open = False

    def load_assets(self):
        assets_path = os.path.join(base_path, '..', 'Assets')
        self.heart_icon = assets.create_heart_surface()
        try:
            self.tile_images = {
                'G': pygame.image.load(os.path.join(assets_path, 'Tiles', 'ground.png')).convert_alpha(),
                'P': pygame.image.load(os.path.join(assets_path, 'Tiles', 'platform.png')).convert_alpha(),
            }
        except pygame.error as e:
            print(f"Error saat memuat gambar tile: {e}")
            self.running = False

        try:
            spike_sheet = pygame.image.load(os.path.join(assets_path, 'Tiles', 'spike_animation.png')).convert_alpha()
            frame_width, frame_height, frame_count = 40, 40, 4
            left_margin, gap_width, top_margin = 0, 0, 0
            for i in range(frame_count):
                x_pos = left_margin + i * (frame_width + gap_width)
                y_pos = top_margin
                frame_surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame_surface.blit(spike_sheet, (0, 0), (x_pos, y_pos, frame_width, frame_height))
                self.spike_animation_frames.append(frame_surface)
        except pygame.error as e:
            print(f"Error saat memuat animasi duri: {e}")
            self.running = False

        self.forest_layers_images = []
        try:
            for i in range(10):
                path = os.path.join(assets_path, 'Background', f'forest_layer_{i}.png')
                image = pygame.image.load(path).convert_alpha()
                scaled_image = pygame.transform.scale(image, (self.game_surface_height * image.get_width() / image.get_height(), self.game_surface_height))
                self.forest_layers_images.append(scaled_image)
        except pygame.error as e:
            print(f"Error saat memuat gambar background hutan: {e}")
            self.running = False

        try:
            self.moon_image = pygame.image.load(os.path.join(assets_path, 'Background', 'moon.png')).convert_alpha()
            self.moon_shadow_image = pygame.image.load(os.path.join(assets_path, 'Background', 'moon_shadow.png')).convert_alpha()
        except pygame.error as e:
            print(f"Error saat memuat gambar bulan: {e}")
            self.running = False

        self.campfire_animation_frames = []
        try:
            for i in range(1, 8):
                path = os.path.join(assets_path, 'Background', 'Campfire', f'campFire{i}.png')
                image = pygame.image.load(path).convert_alpha()
                self.campfire_animation_frames.append(image)
        except pygame.error as e:
            print(f"Error saat memuat animasi api unggun: {e}")
            self.running = False


    def setup_level(self, normal_map_file, gema_map_file, new_game=False):
        if new_game:
            self.platforms = []
            self.traps = []
            self.trigger_traps = []
            self.door_rect = None
            self.campfires = []
            self.enemies = []

        tile_size = 40

        triggers_pos = {'normal': [], 'gema': []}
        trap_zones_pos = {'normal': [], 'gema': []}

        try:
            # Collect patrol markers and enemy spawns for normal map
            left_markers_normal = {}
            right_markers_normal = {}
            enemy_spawns_normal = []

            with open(normal_map_file, 'r') as file:
                for y, line in enumerate(file):
                    for x, char in enumerate(line):
                        world_x, world_y = x * tile_size, y * tile_size
                        rect = pygame.Rect(world_x, world_y, tile_size, tile_size)

                        if char in 'Gg':
                            self.platforms.append({'rect': rect, 'dim': 'both', 'char': 'G'})
                        elif char in 'Pp':
                            self.platforms.append({'rect': rect, 'dim': 'normal', 'char': 'P'})
                        elif char in 'Tt':
                            triggers_pos['normal'].append(rect)
                        elif char in 'jJ':
                            trap_zones_pos['normal'].append(rect)
                        elif char in 'Ss':
                            self.start_pos = (world_x, world_y + tile_size)
                        elif char in 'Dd':
                            self.door_rect = pygame.Rect(world_x, world_y, tile_size, tile_size * 1)
                        elif char in 'eE':
                            enemy_spawns_normal.append(rect)
                        elif char in 'lL':
                            left_markers_normal.setdefault(y, []).append(world_x + tile_size // 2)
                        elif char in 'rR':
                            right_markers_normal.setdefault(y, []).append(world_x + tile_size // 2)
        except FileNotFoundError:
            print(f"Error: File '{normal_map_file}' tidak ditemukan!")
            self.running = False; return

        try:
            # Collect platforms/traps for gema, and also accept enemy markers in gema
            left_markers_gema = {}
            right_markers_gema = {}
            enemy_spawns_gema = []

            with open(gema_map_file, 'r') as file:
                for y, line in enumerate(file):
                    for x, char in enumerate(line):
                        world_x, world_y = x * tile_size, y * tile_size
                        rect = pygame.Rect(world_x, world_y, tile_size, tile_size)
                        
                        if char in 'GPp':
                           self.platforms.append({'rect': rect, 'dim': 'gema', 'char': 'P'})
                        elif char in 'Tt':
                            triggers_pos['gema'].append(rect)
                        elif char in 'jJ':
                            trap_zones_pos['gema'].append(rect)
                        elif char in 'Cc': 
                            self.campfires.append({
                                'rect': rect,
                                'frame_index': 0.0,
                            })
                        elif char in 'eE':
                            enemy_spawns_gema.append(rect)
                        elif char in 'lL':
                            left_markers_gema.setdefault(y, []).append(world_x + tile_size // 2)
                        elif char in 'rR':
                            right_markers_gema.setdefault(y, []).append(world_x + tile_size // 2)
        except FileNotFoundError:
            print(f"Error: File '{gema_map_file}' tidak ditemukan!")
            self.running = False; return

        # Build enemies from markers found in BOTH maps. If markers are placed in gema,
        # also spawn them (so enemies exist regardless of which map they were defined in).
        # Deduplicate by tile position to avoid double-instantiation.
        seen_spawn_tiles = set()

        def add_enemies_from(spawn_list, left_markers, right_markers):
            for spawn_rect in spawn_list:
                row = spawn_rect.y // tile_size
                col = spawn_rect.x // tile_size
                key = (row, col)
                if key in seen_spawn_tiles:
                    continue
                seen_spawn_tiles.add(key)

                left_list = left_markers.get(row, [])
                right_list = right_markers.get(row, [])

                # Find nearest left <= spawn_x and nearest right >= spawn_x
                sx = spawn_rect.centerx
                left_bound = max([lx for lx in left_list if lx <= sx], default=sx - 80)
                right_bound = min([rx for rx in right_list if rx >= sx], default=sx + 80)

                enemy = Enemy(spawn_rect.x, spawn_rect.bottom, left_bound, right_bound, size=(30, 30), speed=2.0)
                self.enemies.append(enemy)

        add_enemies_from(enemy_spawns_normal, left_markers_normal, right_markers_normal)
        add_enemies_from(enemy_spawns_gema, left_markers_gema, right_markers_gema)
        
        for trigger_rect, trap_rect in zip(triggers_pos['normal'], trap_zones_pos['normal']):
            self.trigger_traps.append({
                'trigger_rect': trigger_rect, 'trap_rect': trap_rect, 
                'dim': 'normal', 'is_active': False, 
                'frame_index': 0.0, 'animation_finished': False
            })
        
        for trigger_rect, trap_rect in zip(triggers_pos['gema'], trap_zones_pos['gema']):
            self.trigger_traps.append({
                'trigger_rect': trigger_rect, 'trap_rect': trap_rect, 
                'dim': 'gema', 'is_active': False, 
                'frame_index': 0.0, 'animation_finished': False
            })

        if new_game or not hasattr(self, 'player'):
            if hasattr(self, 'start_pos'):
                self.player = Player(self.start_pos[0], self.start_pos[1])
            else:
                self.player = Player(100, 100)
                print("Peringatan: 'S' (start position) tidak ditemukan!")
        else:
            self.player.respawn(self.start_pos)
        
        if new_game:
            self.parallax_layers = []
            speeds = [0.55, 0.5, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1]
            for i in range(len(self.forest_layers_images)):
                if i < len(speeds):
                    layer = ParallaxLayer(self.forest_layers_images[i], speeds[i])
                    self.parallax_layers.append(layer)

        if new_game:
            self.parallax_layers = []
            speeds = [0.55, 0.5, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1]

            for i in range(len(self.forest_layers_images)):
                if i < len(speeds):
                    layer = ParallaxLayer(self.forest_layers_images[i], speeds[i])
                    self.parallax_layers.append(layer)

            self.moon_object = ParallaxObject(self.moon_image, 0.045, 50, x_offset=150)
            self.moon_shadow_object = ParallaxObject(self.moon_shadow_image, 0.05, 60, x_offset=160)

        self.spawn_invincibility_timer = self.spawn_invincibility_duration

    def handle_triggers(self):
        if not self.player.is_alive: return
        current_dimension_str = 'gema' if self.player.in_gema_dimension else 'normal'
        for trap in self.trigger_traps:
            if not trap['is_active'] and (trap['dim'] in [current_dimension_str, 'both']):
                if self.player.collides(trap['trigger_rect']):
                    trap['is_active'] = True

    def update_animated_traps(self):
        SPIKE_ANIMATION_SPEED = 0.2
        for trap in self.trigger_traps:
            if trap['is_active'] and not trap['animation_finished']:
                trap['frame_index'] += SPIKE_ANIMATION_SPEED
                if trap['frame_index'] >= len(self.spike_animation_frames):
                    trap['animation_finished'] = True
                    trap['frame_index'] = len(self.spike_animation_frames) - 1

    def update_campfires(self):
        CAMPFIRE_ANIMATION_SPEED = 0.15
        for campfire in self.campfires:
            campfire['frame_index'] += CAMPFIRE_ANIMATION_SPEED
            if campfire['frame_index'] >= len(self.campfire_animation_frames):
                campfire['frame_index'] = 0.0

    def draw_campfires(self, offset_x, offset_y):
        vertical_offset = 10
        
        for campfire in self.campfires:
            current_frame_index = int(campfire['frame_index'])
            if 0 <= current_frame_index < len(self.campfire_animation_frames):
                image_to_draw = self.campfire_animation_frames[current_frame_index]
                
                scaled_image = pygame.transform.scale(image_to_draw, (campfire['rect'].width, campfire['rect'].height))
                
                self.game_surface.blit(scaled_image, (campfire['rect'].x - offset_x, campfire['rect'].y - offset_y + vertical_offset))

    def respawn_player(self):
        self.player.respawn(self.start_pos)
        self.spawn_invincibility_timer = self.spawn_invincibility_duration
        self.is_in_death_delay = False
        for trap in self.trigger_traps:
            trap['is_active'] = False
            trap['frame_index'] = 0.0
            trap['animation_finished'] = False
        # Clear enemy idle lock so they resume patrol after player respawns
        for enemy in getattr(self, 'enemies', []):
            if hasattr(enemy, 'clear_contact_idle'):
                enemy.clear_contact_idle()

    def handle_damage(self):
        """Build active hazards and delegate damage logic to Player.apply_hazards."""
        if self.spawn_invincibility_timer > 0 or not self.player.is_alive or self.is_in_death_delay:
            return

        current_dimension_str = 'gema' if self.player.in_gema_dimension else 'normal'

        # Build list of active hazard rectangles based on current dimension and triggers
        active_trap_rects = []
        for t in self.traps:
            if t['dim'] in [current_dimension_str, 'both']:
                active_trap_rects.append(t['rect'])
        for trap in self.trigger_traps:
            if trap['is_active'] and trap['dim'] in [current_dimension_str, 'both']:
                active_trap_rects.append(trap['trap_rect'])
        # Enemies act as hazards too; if player collides, trigger enemy idle reaction
        for enemy in getattr(self, 'enemies', []):
            if self.player.rect.colliderect(enemy.rect):
                if hasattr(enemy, 'on_player_contact'):
                    enemy.on_player_contact()
            active_trap_rects.append(enemy.rect)

        # Delegate to player: it will apply damage and tell us if we need a respawn delay
        result = self.player.apply_hazards(active_trap_rects, SCREEN_HEIGHT, is_invincible=False)
        if result:
            if result.get('temporary_death'):
                self.is_in_death_delay = True
                self.death_delay_timer = result.get('delay_ms', 500)
                self.death_delay_start_time = pygame.time.get_ticks()

    def go_to_next_level(self):
        current_hearts = self.player.hearts
        self.current_level_index += 1
        if self.current_level_index < len(self.levels):
            level_pair = self.levels[self.current_level_index]
            self.setup_level(level_pair[0], level_pair[1], new_game=True)
            self.player.hearts = current_hearts
        else:
            self.game_state = 'game_over_win'

    def check_level_completion(self):
        if self.player.is_alive and self.player.is_inside(self.door_rect):
            self.go_to_next_level()

    def draw_text(self, text, size, color, x, y, center_aligned=True, shadow_color=None, shadow_offset=3):
        font = pygame.font.Font(None, size)
        
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()

        if shadow_color:
            shadow_surface = font.render(text, True, shadow_color)
            shadow_rect = shadow_surface.get_rect()
            if center_aligned:
                shadow_rect.center = (x + shadow_offset, y + shadow_offset)
            else:
                shadow_rect.topleft = (x + shadow_offset, y + shadow_offset)
            self.screen.blit(shadow_surface, shadow_rect)
        
        if center_aligned:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)

    def draw_pause_menu(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        self.draw_text("Paused", 80, (255, 255, 255), SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, shadow_color=(20, 20, 20))

        self.resume_button = pygame.Rect(SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 - 75, 200, 50)
        self.restart_button = pygame.Rect(SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2, 200, 50)
        self.settings_button = pygame.Rect(SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 + 75, 200, 50)
        self.main_menu_button = pygame.Rect(SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 + 150, 200, 50)

        buttons = [
            (self.resume_button, "Lanjutkan"),
            (self.restart_button, "Ulangi"),
            (self.settings_button, "Pengaturan"),
            (self.main_menu_button, "Menu Utama")
        ]
        mouse_pos = pygame.mouse.get_pos()
        for rect, text in buttons:
            color = (150, 150, 150) if rect.collidepoint(mouse_pos) else (100, 100, 100)
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            self.draw_text(text, 32, (255, 255, 255), rect.centerx, rect.centery)

    def draw_settings_menu(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        self.draw_text("Pengaturan", 60, (255, 255, 255), SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, shadow_color=(20, 20, 20))
        
        self.music_button = pygame.Rect(SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2, 200, 50)
        self.back_button = pygame.Rect(SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 + 75, 200, 50)

        music_text = "Musik: Off" if self.is_music_paused else "Musik: On"
        
        mouse_pos = pygame.mouse.get_pos()
        music_color = (150, 150, 150) if self.music_button.collidepoint(mouse_pos) else (100, 100, 100)
        pygame.draw.rect(self.screen, music_color, self.music_button, border_radius=10)
        self.draw_text(music_text, 32, (255, 255, 255), self.music_button.centerx, self.music_button.centery)

        back_color = (150, 150, 150) if self.back_button.collidepoint(mouse_pos) else (100, 100, 100)
        pygame.draw.rect(self.screen, back_color, self.back_button, border_radius=10)
        self.draw_text("Kembali", 32, (255, 255, 255), self.back_button.centerx, self.back_button.centery)

    def draw_win_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) 
        self.screen.blit(overlay, (0, 0))
        
        self.draw_text("Selamat! Semua Level Selesai!", 60, (255, 255, 255), SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)

        self.restart_button = pygame.Rect(SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2, 200, 50)
        self.main_menu_button = pygame.Rect(SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 + 75, 200, 50)

        buttons = [
            (self.restart_button, "Restart"),
            (self.main_menu_button, "Menu Utama")
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        for rect, text in buttons:
            color = (150, 150, 150) if rect.collidepoint(mouse_pos) else (100, 100, 100)
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            self.draw_text(text, 32, (255, 255, 255), rect.centerx, rect.centery)

    def run(self):
        level_pair = self.levels[self.current_level_index]
        self.setup_level(level_pair[0], level_pair[1], new_game=True)

        try:
            music_path = os.path.join(base_path, '..', 'Assets', 'Sound', 'music_platformer.ogg')
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(-1) 
        except pygame.error as e:
            print(f"Tidak bisa memuat file musik: {e}")
        
        start_button_rect = pygame.Rect(SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2, 200, 50)
        exit_button_rect = pygame.Rect(SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 + 75, 200, 50)
        
        pause_button_rect = pygame.Rect(SCREEN_WIDTH - 50, 10, 40, 40)

        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            self.update_campfires()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.game_state == 'playing':
                        self.prev_game_state = self.game_state
                        self.game_state = 'paused'
                    elif event.key == pygame.K_p and self.game_state == 'paused':
                        self.game_state = 'playing'

                # Forward input events to the player when playing so Player handles its own controls
                if self.game_state == 'playing' and hasattr(self, 'player'):
                    # Player.handle_event will ignore events it doesn't care about
                    self.player.handle_event(event)
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.game_state == 'main_menu':
                        if start_button_rect.collidepoint(mouse_pos):
                            self.game_state = 'playing'
                        if exit_button_rect.collidepoint(mouse_pos):
                            self.running = False
                    elif self.game_state == 'playing':
                        if pause_button_rect.collidepoint(mouse_pos):
                            self.prev_game_state = self.game_state
                            self.game_state = 'paused'
                    elif self.game_state == 'paused':
                        if self.is_settings_open:
                            if self.music_button.collidepoint(mouse_pos):
                                if self.is_music_paused:
                                    pygame.mixer.music.unpause()
                                else:
                                    pygame.mixer.music.pause()
                                self.is_music_paused = not self.is_music_paused
                            if self.back_button.collidepoint(mouse_pos):
                                self.is_settings_open = False
                        else:
                            if self.resume_button.collidepoint(mouse_pos):
                                self.game_state = 'playing'
                            if self.restart_button.collidepoint(mouse_pos):
                                self.respawn_player()
                                self.game_state = 'playing'
                            if self.settings_button.collidepoint(mouse_pos):
                                self.is_settings_open = True
                            if self.main_menu_button.collidepoint(mouse_pos):
                                self.current_level_index = 0
                                level_pair = self.levels[self.current_level_index]
                                self.setup_level(level_pair[0], level_pair[1], new_game=True)
                                self.game_state = 'main_menu'
                    elif self.game_state == 'game_over_win':
                        if self.restart_button.collidepoint(mouse_pos):
                            self.current_level_index = 0
                            level_pair = self.levels[self.current_level_index]
                            self.setup_level(level_pair[0], level_pair[1], new_game=True)
                            self.player.hearts = PLAYER_START_HEARTS
                            self.game_state = 'playing' 
                        if self.main_menu_button.collidepoint(mouse_pos):
                            self.current_level_index = 0
                            level_pair = self.levels[self.current_level_index]
                            self.setup_level(level_pair[0], level_pair[1], new_game=True)
                            self.game_state = 'main_menu' 

            if self.game_state == 'playing':
                if self.spawn_invincibility_timer > 0:
                    self.spawn_invincibility_timer -= 1
                
                current_dimension_str = 'gema' if self.player.in_gema_dimension else 'normal'
                active_platforms = [p['rect'] for p in self.platforms if p['dim'] in [current_dimension_str, 'both']]
                
                self.player.update(active_platforms)
                # Update enemies
                for enemy in getattr(self, 'enemies', []):
                    enemy.update(active_platforms)
                
                if self.player.is_alive:
                    self.handle_triggers()
                    self.handle_damage()
                    self.check_level_completion()
                else: 
                    if self.is_in_death_delay:
                        is_ready_for_delay = (self.player.state == 'death' and self.player.animation_finished) or (self.player.state != 'death')
                        if is_ready_for_delay:
                            current_time = pygame.time.get_ticks()
                            if current_time - self.death_delay_start_time > self.death_delay_timer:
                                self.respawn_player()
                    elif self.player.hearts <= 0:
                        print("Game Over! Kembali ke Level 1...")
                        self.current_level_index = 0
                        level_pair = self.levels[self.current_level_index]
                        self.setup_level(level_pair[0], level_pair[1], new_game=True)
                        self.player.hearts = PLAYER_START_HEARTS
                
                self.update_animated_traps()
                
            elif self.game_state == 'paused':
                pass 

            camera_offset_x = self.player.rect.centerx - self.game_surface_width / 2
            camera_offset_y = CAMERA_MANUAL_OFFSET_Y
            final_offset_x = camera_offset_x + CAMERA_MANUAL_OFFSET_X
            final_offset_y = camera_offset_y
            
            self.game_surface.fill(COLOR_BG_GEMA if self.player.in_gema_dimension else COLOR_BG_NORMAL)
            for layer in reversed(self.parallax_layers):
                layer.draw(self.game_surface, camera_offset_x, 0)
            
            current_dimension_str = 'gema' if self.player.in_gema_dimension else 'normal'

            for layer in reversed(self.parallax_layers):
                layer.draw(self.game_surface, camera_offset_x, 0)

            if self.player.in_gema_dimension:
                self.moon_shadow_object.draw(self.game_surface, camera_offset_x)
                self.moon_object.draw(self.game_surface, camera_offset_x)

            for p in self.platforms:
                if p['dim'] in [current_dimension_str, 'both']:
                    tile_image = self.tile_images.get(p.get('char'))
                    if tile_image:
                        scaled_image = pygame.transform.scale(tile_image, (p['rect'].width, p['rect'].height))
                        self.game_surface.blit(scaled_image, (p['rect'].x - final_offset_x, p['rect'].y - final_offset_y))

            for trap in self.trigger_traps:
                if trap['is_active'] and trap['dim'] in [current_dimension_str, 'both']:
                    frame_to_draw = self.spike_animation_frames[int(trap['frame_index'])]
                    scaled_image = pygame.transform.scale(frame_to_draw, (trap['trap_rect'].width, trap['trap_rect'].height))
                    
                    vertical_offset = 20
                    draw_y = trap['trap_rect'].y + vertical_offset
                    
                    self.game_surface.blit(scaled_image, (trap['trap_rect'].x - final_offset_x, draw_y - final_offset_y))

            self.draw_campfires(final_offset_x, final_offset_y)

            # Draw enemies
            for enemy in getattr(self, 'enemies', []):
                enemy.draw(self.game_surface, final_offset_x, final_offset_y)

            if self.door_rect:
                door_surf = assets.create_door_surface(self.door_rect.width, self.door_rect.height)
                self.game_surface.blit(door_surf, (self.door_rect.x - final_offset_x, self.door_rect.y - final_offset_y))
            
            self.player.draw(self.game_surface, final_offset_x, final_offset_y)
            
            self.screen.blit(pygame.transform.scale(self.game_surface, self.screen.get_size()), (0, 0))

            if self.game_state == 'playing' or self.game_state == 'paused':
                for i in range(self.player.hearts):
                    self.screen.blit(self.heart_icon, (10 + i * 35, 10))
                
                pygame.draw.circle(self.screen, (100, 100, 100), pause_button_rect.center, 20)
                if pause_button_rect.collidepoint(mouse_pos):
                    pygame.draw.circle(self.screen, (150, 150, 150), pause_button_rect.center, 20)
                
                self.draw_text("||", 32, (255, 255, 255), pause_button_rect.centerx, pause_button_rect.centery, shadow_color=None)
            
            if self.game_state == 'main_menu':
                self.draw_text("Dual Dimension", 80, (255, 255, 255), SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, shadow_color=(20, 20, 20))
                
                start_color = (150, 150, 150) if start_button_rect.collidepoint(mouse_pos) else (100, 100, 100)
                pygame.draw.rect(self.screen, start_color, start_button_rect, border_radius=10)
                self.draw_text("Mulai", 32, (255, 255, 255), start_button_rect.centerx, start_button_rect.centery)
                
                exit_color = (150, 150, 150) if exit_button_rect.collidepoint(mouse_pos) else (100, 100, 100)
                pygame.draw.rect(self.screen, exit_color, exit_button_rect, border_radius=10)
                self.draw_text("Keluar", 32, (255, 255, 255), exit_button_rect.centerx, exit_button_rect.centery)

            elif self.game_state == 'paused':
                if self.is_settings_open:
                    self.draw_settings_menu()
                else:
                    self.draw_pause_menu()

            elif self.game_state == 'game_over_win':
                self.draw_win_screen()
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()
