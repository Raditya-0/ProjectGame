import pygame
from settings import *
import assets
from entity.player import Player
from parallax import ParallaxLayer, ParallaxObject
from entity.enemy import PatrollingEnemy, ChaserEnemy
from environment.trap import load_spike_frames, TriggerTrap
from environment.campfire import load_campfire_frames, Campfire
import os
from exception import AssetLoadError, LevelFileNotFound, AudioLoadError
import UI as UI

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
        
        self.spike_frames = []
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

        self.end_triggers = []
        self.end_sequence_active = False
        self.end_sequence_mode = None
        self.end_sequence_dir = 1
        self.end_jump_started = False
        self.input_locked = False
        self.camera_lock_active = False
        self.camera_lock_center_x = 0
        self.camera_right_limit_x = None
        self.level_width_pixels = 0
        self.debug_draw = DEBUG_DRAW_HITBOXES

    def load_assets(self):
        assets_path = os.path.join(base_path, '..', 'Assets')
        self.heart_icon = assets.create_heart_surface()
        try:
            self.tile_images = {
                'G': pygame.image.load(os.path.join(assets_path, 'Tiles', 'ground.png')).convert_alpha(),
                'P': pygame.image.load(os.path.join(assets_path, 'Tiles', 'platform.png')).convert_alpha(),
            }
        except pygame.error as e:
            print(str(AssetLoadError("Tiles (ground/platform)", e)))
            self.running = False

        # Load spike frames via environment helper
        self.spike_frames = load_spike_frames(assets_path)

        self.forest_layers_images = []
        try:
            for i in range(10):
                path = os.path.join(assets_path, 'Background', f'forest_layer_{i}.png')
                image = pygame.image.load(path).convert_alpha()
                scaled_image = pygame.transform.scale(image, (self.game_surface_height * image.get_width() / image.get_height(), self.game_surface_height))
                self.forest_layers_images.append(scaled_image)
        except pygame.error as e:
            print(str(AssetLoadError("Background forest layers", e)))
            self.running = False

        try:
            self.moon_image = pygame.image.load(os.path.join(assets_path, 'Background', 'moon.png')).convert_alpha()
            self.moon_shadow_image = pygame.image.load(os.path.join(assets_path, 'Background', 'moon_shadow.png')).convert_alpha()
        except pygame.error as e:
            print(str(AssetLoadError("Background moon/moon_shadow", e)))
            self.running = False

        # Load campfire frames via environment helper
        self.campfire_frames = load_campfire_frames(assets_path)


    def setup_level(self, normal_map_file, gema_map_file, new_game=False):
        if new_game:
            self.platforms = []
            self.traps = []
            self.trigger_traps = []
            self.end_triggers = []
            self.door_rect = None
            self.campfires = []
            self.enemies = []
            self.enemy_spawns = []
            self.camera_right_limit_x = None
            self.level_width_pixels = 0

        tile_size = 40

        triggers_pos = {'normal': [], 'gema': []}
        trap_zones_pos = {'normal': [], 'gema': []}

        try:
            left_markers_normal = {}
            right_markers_normal = {}
            enemy_spawns_normal = []
            max_world_x = 0

            with open(normal_map_file, 'r') as file:
                for y, line in enumerate(file):
                    for x, char in enumerate(line):
                        world_x, world_y = x * tile_size, y * tile_size
                        rect = pygame.Rect(world_x, world_y, tile_size, tile_size)
                        if world_x > max_world_x:
                            max_world_x = world_x

                        if char in 'Gg':
                            self.platforms.append({'rect': rect, 'dim': 'both', 'char': 'G'})
                        elif char in 'Pp':
                            plat_rect = pygame.Rect(world_x, world_y, tile_size, 20)
                            self.platforms.append({'rect': plat_rect, 'dim': 'normal', 'char': 'P'})
                        elif char in 'Hh':
                            facing = 'right' if char == 'H' else 'left'
                            enemy_spawns_normal.append({'rect': rect, 'type': 'patrol', 'facing': facing})
                        elif char in 'Tt':
                            triggers_pos['normal'].append(rect)
                        elif char in 'Nn':
                            facing = 'right' if char == 'N' else 'left'
                            enemy_spawns_normal.append({'rect': rect, 'type': 'chaser_heavy', 'facing': facing})
                        elif char in 'jJ':
                            trap_zones_pos['normal'].append(rect)
                        elif char in 'yY':
                            trap_zones_pos['normal'].append(rect)
                        elif char in 'Ss':
                            self.start_pos = (world_x, world_y + tile_size)
                        elif char == 'D':
                            self.end_triggers.append({'rect': rect, 'dim': 'normal', 'mode': 'jump_walk'})
                        elif char == 'd':
                            self.end_triggers.append({'rect': rect, 'dim': 'normal', 'mode': 'walk'})
                        elif char in 'Cc':
                            self.campfires.append(Campfire(rect))
                        elif char in 'Ff':
                            facing = 'right' if char == 'F' else 'left'
                            enemy_spawns_normal.append({'rect': rect, 'type': 'chaser', 'facing': facing})
                        elif char in 'lL':
                            left_markers_normal.setdefault(y, []).append(world_x + tile_size // 2)
                        elif char in 'rR':
                            right_markers_normal.setdefault(y, []).append(world_x + tile_size // 2)
                        elif char == 'K':
                            self.camera_right_limit_x = world_x + tile_size // 2
            self.level_width_pixels = max(self.level_width_pixels, max_world_x + tile_size)
        except FileNotFoundError:
            print(str(LevelFileNotFound(normal_map_file)))
            self.running = False; return

        try:
            left_markers_gema = {}
            right_markers_gema = {}
            enemy_spawns_gema = []
            max_world_x_gema = 0

            with open(gema_map_file, 'r') as file:
                for y, line in enumerate(file):
                    for x, char in enumerate(line):
                        world_x, world_y = x * tile_size, y * tile_size
                        rect = pygame.Rect(world_x, world_y, tile_size, tile_size)
                        if world_x > max_world_x_gema:
                            max_world_x_gema = world_x

                        if char in 'Gg':
                            self.platforms.append({'rect': rect, 'dim': 'gema', 'char': 'G'})
                        elif char in 'Pp':
                            plat_rect = pygame.Rect(world_x, world_y, tile_size, 20)
                            self.platforms.append({'rect': plat_rect, 'dim': 'gema', 'char': 'P'})
                        elif char in 'Hh':
                            facing = 'right' if char == 'H' else 'left'
                            enemy_spawns_gema.append({'rect': rect, 'type': 'patrol', 'facing': facing})
                        elif char in 'Tt':
                            triggers_pos['gema'].append(rect)
                        elif char in 'Nn':
                            facing = 'right' if char == 'N' else 'left'
                            enemy_spawns_gema.append({'rect': rect, 'type': 'chaser_heavy', 'facing': facing})
                        elif char in 'jJ':
                            trap_zones_pos['gema'].append(rect)
                        elif char in 'yY':
                            trap_zones_pos['gema'].append(rect)
                        elif char in 'Cc':
                            self.campfires.append(Campfire(rect))
                        elif char in 'Ff':
                            facing = 'right' if char == 'F' else 'left'
                            enemy_spawns_gema.append({'rect': rect, 'type': 'chaser', 'facing': facing})
                        elif char == 'D':
                            self.end_triggers.append({'rect': rect, 'dim': 'gema', 'mode': 'jump_walk'})
                        elif char == 'd':
                            self.end_triggers.append({'rect': rect, 'dim': 'gema', 'mode': 'walk'})
                        elif char in 'lL':
                            left_markers_gema.setdefault(y, []).append(world_x + tile_size // 2)
                        elif char in 'rR':
                            right_markers_gema.setdefault(y, []).append(world_x + tile_size // 2)
                        elif char == 'K':
                            self.camera_right_limit_x = world_x + tile_size // 2
            self.level_width_pixels = max(self.level_width_pixels, max_world_x_gema + tile_size)
        except FileNotFoundError:
            print(str(LevelFileNotFound(gema_map_file)))
            self.running = False; return

        seen_spawn_tiles = set()

        def add_enemies_from(spawn_list, left_markers, right_markers):
            for spawn_info in spawn_list:
                spawn_rect = spawn_info.get('rect') if isinstance(spawn_info, dict) else spawn_info
                row = spawn_rect.y // tile_size
                col = spawn_rect.x // tile_size
                key = (row, col)
                if key in seen_spawn_tiles:
                    continue
                seen_spawn_tiles.add(key)

                left_list = left_markers.get(row, [])
                right_list = right_markers.get(row, [])

                sx = spawn_rect.centerx
                left_bound = max([lx for lx in left_list if lx <= sx], default=sx - 80)
                right_bound = min([rx for rx in right_list if rx >= sx], default=sx + 80)

                if new_game or not hasattr(self, 'enemy_spawns'):
                    self.enemy_spawns = getattr(self, 'enemy_spawns', [])
                stored = {
                    'x': spawn_rect.x,
                    'y': spawn_rect.bottom,
                    'left_bound': left_bound,
                    'right_bound': right_bound,
                    'type': spawn_info.get('type', 'patrol') if isinstance(spawn_info, dict) else 'patrol',
                    'facing': spawn_info.get('facing', 'right') if isinstance(spawn_info, dict) else 'right'
                }
                self.enemy_spawns.append(stored)

                etype = stored['type']
                facing = stored['facing']
                if etype == 'chaser':
                    enemy = ChaserEnemy(spawn_rect.x, spawn_rect.bottom, size=(50, 50), speed=2.5, facing=facing)
                elif etype == 'chaser_heavy':
                    enemy = ChaserEnemy(spawn_rect.x, spawn_rect.bottom, size=(50, 50), speed=2.2, facing=facing, asset_folder='Heavy Bandit')
                else:
                    enemy = PatrollingEnemy(spawn_rect.x, spawn_rect.bottom, left_bound, right_bound, size=(30, 30), speed=2.0)
                    enemy.direction = 1 if facing == 'right' else -1
                self.enemies.append(enemy)

        add_enemies_from(enemy_spawns_normal, left_markers_normal, right_markers_normal)
        add_enemies_from(enemy_spawns_gema, left_markers_gema, right_markers_gema)
        
        for trigger_rect, trap_rect in zip(triggers_pos['normal'], trap_zones_pos['normal']):
            self.trigger_traps.append(TriggerTrap(trigger_rect, trap_rect, dim='normal'))
        
        for trigger_rect, trap_rect in zip(triggers_pos['gema'], trap_zones_pos['gema']):
            self.trigger_traps.append(TriggerTrap(trigger_rect, trap_rect, dim='gema'))

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
            trap.try_activate(self.player.rect, current_dimension_str)

        if not self.end_sequence_active:
            for end_t in self.end_triggers:
                if end_t['dim'] in [current_dimension_str, 'both'] and self.player.collides(end_t['rect']):
                    self.start_end_sequence(end_t['mode'])
                    break

    def update_animated_traps(self):
        for trap in self.trigger_traps:
            trap.update(self.spike_frames)

    def update_campfires(self):
        for campfire in self.campfires:
            campfire.update(self.campfire_frames)

    def draw_campfires(self, offset_x, offset_y):
        for campfire in self.campfires:
            campfire.draw(self.game_surface, offset_x, offset_y, self.campfire_frames)

    def respawn_player(self):
        self.player.respawn(self.start_pos)
        self.spawn_invincibility_timer = self.spawn_invincibility_duration
        self.is_in_death_delay = False
        for trap in self.trigger_traps:
            trap.is_active = False
            trap.frame_index = 0.0
            trap.animation_finished = False
        self.enemies = []
        for e_info in getattr(self, 'enemy_spawns', []):
            etype = e_info.get('type', 'patrol')
            if etype == 'chaser':
                facing = e_info.get('facing', 'right')
                self.enemies.append(ChaserEnemy(e_info['x'], e_info['y'], size=(50, 50), speed=2.5, facing=facing))
            elif etype == 'chaser_heavy':
                facing = e_info.get('facing', 'right')
                self.enemies.append(ChaserEnemy(e_info['x'], e_info['y'], size=(50, 50), speed=2.2, facing=facing, asset_folder='Heavy Bandit'))
            else:
                lb = e_info.get('left_bound')
                rb = e_info.get('right_bound')
                facing = e_info.get('facing', 'right')
                pe = PatrollingEnemy(e_info['x'], e_info['y'], lb, rb, size=(30, 30), speed=2.0)
                pe.direction = 1 if facing == 'right' else -1
                self.enemies.append(pe)

    def handle_damage(self):
        if self.spawn_invincibility_timer > 0 or not self.player.is_alive or self.is_in_death_delay:
            return

        current_dimension_str = 'gema' if self.player.in_gema_dimension else 'normal'

        active_trap_rects = []
        for t in self.traps:
            if t['dim'] in [current_dimension_str, 'both']:
                active_trap_rects.append(t['rect'])
        for trap in self.trigger_traps:
            if trap.is_active and trap.dim in [current_dimension_str, 'both']:
                active_trap_rects.append(trap.get_hazard_rect())
        for enemy in getattr(self, 'enemies', []):
            if getattr(enemy, 'is_dying', False):
                continue
                if getattr(enemy, 'blocks_player', True):  # Check if enemy blocks player
                    block_rect = enemy.get_block_rect() if hasattr(enemy, 'get_block_rect') else enemy.rect
                    if self.player.rect.colliderect(block_rect):
                        if hasattr(enemy, 'on_player_contact') and enemy.is_alive:
                            enemy.on_player_contact()
            if hasattr(enemy, 'is_hazard_active') and enemy.is_hazard_active():
                hazard_rect = enemy.get_hazard_rect() if hasattr(enemy, 'get_hazard_rect') else enemy.rect
                active_trap_rects.append(hazard_rect)
                # If patrol contacts player, force idle immediately and keep idle permanently
                if isinstance(enemy, PatrollingEnemy) and hazard_rect.colliderect(self.player.rect):
                    if hasattr(enemy, 'on_player_contact') and enemy.is_alive:
                        enemy.on_player_contact()
                    # stay idle after kill/contact per request
                    setattr(enemy, 'permanent_idle', True)

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
        pass

    def start_end_sequence(self, mode: str):
        self.end_sequence_active = True
        self.end_sequence_mode = 'jump_walk' if mode == 'jump_walk' else 'walk'
        self.end_sequence_dir = 1
        self.end_jump_started = False
        self.input_locked = True
        self.camera_lock_active = True
        self.camera_lock_center_x = self.player.rect.centerx

    

    def run(self):
        level_pair = self.levels[self.current_level_index]
        self.setup_level(level_pair[0], level_pair[1], new_game=True)

        try:
            music_path = os.path.join(base_path, '..', 'Assets', 'Sound', 'music_platformer.ogg')
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(-1) 
        except pygame.error as e:
            print(str(AudioLoadError(music_path, e)))
        
        start_button_rect = pygame.Rect(SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2, 200, 50)
        exit_button_rect = pygame.Rect(SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 + 75, 200, 50)
        
        pause_button_rect = pygame.Rect(SCREEN_WIDTH - 50, 10, 40, 40)

        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            self.update_campfires()

            try:
                events_list = pygame.event.get()
            except Exception as e:
                import traceback
                print("pygame.event.get() failed:", e)
                traceback.print_exc()
                try:
                    pygame.event.clear()
                except Exception:
                    pass
                events_list = []

            for event in events_list:
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.game_state == 'playing':
                        self.prev_game_state = self.game_state
                        self.game_state = 'paused'
                    elif event.key == pygame.K_p and self.game_state == 'paused':
                        self.game_state = 'playing'
                    elif event.key == pygame.K_F3:
                        self.debug_draw = not self.debug_draw

                if self.game_state == 'playing' and hasattr(self, 'player') and not self.input_locked:
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
                    elif self.game_state == 'game_over':
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
                
                if self.end_sequence_active:
                    self.player.is_walking = True
                    self.player.direction = 1 if self.end_sequence_dir >= 0 else -1
                    self.player.velocity.x = PLAYER_SPEED * 0.8 * self.player.direction
                    if self.end_sequence_mode == 'jump_walk' and not self.end_jump_started and getattr(self.player, 'is_on_ground', False):
                        self.player.velocity.y = -JUMP_STRENGTH * 0.6
                        self.end_jump_started = True
                    self.player.step(active_platforms)
                else:
                    self.player.update(active_platforms)
                for enemy in getattr(self, 'enemies', []):
                    enemy.update(active_platforms, self.player)

                if not self.end_sequence_active:
                    for enemy in getattr(self, 'enemies', []):
                        if getattr(enemy, 'is_dying', False):
                            continue
                        if getattr(enemy, 'blocks_player', True):
                            block_rect = enemy.get_block_rect() if hasattr(enemy, 'get_block_rect') else enemy.rect
                            if self.player.rect.colliderect(block_rect):
                                if self.player.velocity.x > 0:
                                    self.player.rect.right = block_rect.left
                                elif self.player.velocity.x < 0:
                                    self.player.rect.left = block_rect.right
                                else:
                                    if self.player.rect.centerx < block_rect.centerx:
                                        self.player.rect.right = block_rect.left
                                    else:
                                        self.player.rect.left = block_rect.right
                                self.player.velocity.x = 0

                if not self.end_sequence_active:
                    attack_rect = self.player.get_attack_hitbox() if hasattr(self.player, 'get_attack_hitbox') else None
                    if attack_rect:
                        for enemy in list(getattr(self, 'enemies', [])):
                            if enemy.is_alive and not getattr(enemy, 'is_dying', False) and attack_rect.colliderect(enemy.rect):
                                if hasattr(enemy, 'on_killed_by_player'):
                                    enemy.on_killed_by_player()
                
                if self.player.is_alive:
                    self.handle_triggers()
                    if not self.end_sequence_active:
                        self.handle_damage()
                else: 
                    if self.is_in_death_delay:
                        is_ready_for_delay = (self.player.state == 'death' and self.player.animation_finished) or (self.player.state != 'death')
                        if is_ready_for_delay:
                            current_time = pygame.time.get_ticks()
                            if current_time - self.death_delay_start_time > self.death_delay_timer:
                                self.respawn_player()
                    elif self.player.hearts <= 0:
                        self.game_state = 'game_over'
                
                self.update_animated_traps()

                now_ms = pygame.time.get_ticks()
                self.enemies = [e for e in getattr(self, 'enemies', []) if not (getattr(e, 'is_dying', False) and now_ms >= getattr(e, 'remove_at_ms', 0))]
                
            elif self.game_state == 'paused':
                pass 

            if self.camera_lock_active:
                camera_offset_x = self.camera_lock_center_x - self.game_surface_width / 2
            else:
                camera_offset_x = self.player.rect.centerx - self.game_surface_width / 2
            if self.camera_right_limit_x is not None:
                max_offset = self.camera_right_limit_x - self.game_surface_width / 2
                if camera_offset_x > max_offset:
                    camera_offset_x = max_offset
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
                if trap.is_active and trap.dim in [current_dimension_str, 'both']:
                    trap.draw(self.game_surface, final_offset_x, final_offset_y, self.spike_frames)

            self.draw_campfires(final_offset_x, final_offset_y)

            for enemy in getattr(self, 'enemies', []):
                enemy.draw(self.game_surface, final_offset_x, final_offset_y)

            if self.debug_draw:
                pygame.draw.rect(self.game_surface, (0, 255, 0), pygame.Rect(self.player.rect.x - final_offset_x, self.player.rect.y - final_offset_y, self.player.rect.width, self.player.rect.height), 1)
                if hasattr(self.player, 'get_attack_hitbox'):
                    atk_rect = self.player.get_attack_hitbox()
                    if atk_rect:
                        pygame.draw.rect(self.game_surface, (255, 165, 0), pygame.Rect(atk_rect.x - final_offset_x, atk_rect.y - final_offset_y, atk_rect.width, atk_rect.height), 1)
                for enemy in getattr(self, 'enemies', []):
                    pygame.draw.rect(self.game_surface, (180, 180, 180), pygame.Rect(enemy.rect.x - final_offset_x, enemy.rect.y - final_offset_y, enemy.rect.width, enemy.rect.height), 1)
                    if hasattr(enemy, 'get_block_rect'):
                        br = enemy.get_block_rect()
                        pygame.draw.rect(self.game_surface, (0, 200, 255), pygame.Rect(br.x - final_offset_x, br.y - final_offset_y, br.width, br.height), 1)
                    if hasattr(enemy, 'is_hazard_active') and enemy.is_hazard_active():
                        hz = enemy.get_hazard_rect() if hasattr(enemy, 'get_hazard_rect') else enemy.rect
                        pygame.draw.rect(self.game_surface, (255, 0, 0), pygame.Rect(hz.x - final_offset_x, hz.y - final_offset_y, hz.width, hz.height), 1)

            
            self.player.draw(self.game_surface, final_offset_x, final_offset_y)
            
            self.screen.blit(pygame.transform.scale(self.game_surface, self.screen.get_size()), (0, 0))

            if self.game_state == 'playing' and self.end_sequence_active:
                player_screen_x = self.player.rect.x - final_offset_x
                if player_screen_x > self.game_surface_width + 40 or player_screen_x + self.player.rect.width < -40 or self.player.rect.left > self.level_width_pixels + 40:
                    self.end_sequence_active = False
                    self.input_locked = False
                    self.camera_lock_active = False
                    self.go_to_next_level()

            if self.game_state == 'playing' or self.game_state == 'paused':
                for i in range(self.player.hearts):
                    self.screen.blit(self.heart_icon, (10 + i * 35, 10))
                
                pygame.draw.circle(self.screen, (100, 100, 100), pause_button_rect.center, 20)
                if pause_button_rect.collidepoint(mouse_pos):
                    pygame.draw.circle(self.screen, (150, 150, 150), pause_button_rect.center, 20)
                
                UI.draw_text(self, "||", 32, (255, 255, 255), pause_button_rect.centerx, pause_button_rect.centery, shadow_color=None)
            
            if self.game_state == 'main_menu':
                UI.draw_text(self, "Dual Dimension", 80, (255, 255, 255), SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, shadow_color=(20, 20, 20))
                
                start_color = (150, 150, 150) if start_button_rect.collidepoint(mouse_pos) else (100, 100, 100)
                pygame.draw.rect(self.screen, start_color, start_button_rect, border_radius=10)
                UI.draw_text(self, "Mulai", 32, (255, 255, 255), start_button_rect.centerx, start_button_rect.centery)
                
                exit_color = (150, 150, 150) if exit_button_rect.collidepoint(mouse_pos) else (100, 100, 100)
                pygame.draw.rect(self.screen, exit_color, exit_button_rect, border_radius=10)
                UI.draw_text(self, "Keluar", 32, (255, 255, 255), exit_button_rect.centerx, exit_button_rect.centery)

            elif self.game_state == 'paused':
                if self.is_settings_open:
                    UI.draw_settings_menu(self)
                else:
                    UI.draw_pause_menu(self)

            elif self.game_state == 'game_over_win':
                UI.draw_win_screen(self)
            elif self.game_state == 'game_over':
                UI.draw_game_over_screen(self)
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()


