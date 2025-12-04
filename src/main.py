"""
Main Game - Entry point dan main game loop.
Refactored untuk lebih modular dengan separation of concerns.
"""
import pygame
import os

# Core controllers
from core.game_state import GameStateController, GameStateEnum
from core.level_controller import LevelController
from core.entity_manager import EntityManager
from core.camera_controller import CameraController
from core.asset_loader import AssetLoader

# Game systems
from environment.trap import TriggerTrap
from environment.campfire import Campfire
from graphics.parallax import ParallaxLayer, ParallaxObject
from entity.npc import NPC
from entity.boss import Boss
from entity.enemy import PatrollingEnemy, ChaserEnemy

# Managers and settings
from managers.save_manager import SaveManager
from graphics import UI
from utils.settings import *
from utils.exception import AssetLoadError, AudioLoadError


class Game:
    """Main game class - orchestrates all game systems."""
    
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        pygame.mixer.init()
        
        # Display setup
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.game_surface_width = SCREEN_WIDTH // CAMERA_ZOOM_DIVIDER
        self.game_surface_height = SCREEN_HEIGHT // CAMERA_ZOOM_DIVIDER
        self.game_surface = pygame.Surface((self.game_surface_width, self.game_surface_height))
        pygame.display.set_caption(TITLE)
        
        # Core systems
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 40)
        
        # Controllers
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.state_controller = GameStateController()
        self.level_controller = LevelController(os.path.join(base_path, "levels"))
        self.entity_manager = EntityManager()
        self.camera = CameraController(
            self.game_surface_width, 
            self.game_surface_height,
            CAMERA_MANUAL_OFFSET_X,
            CAMERA_MANUAL_OFFSET_Y
        )
        
        # Asset loader
        assets_path = os.path.join(base_path, '..', 'Assets')
        self.asset_loader = AssetLoader(assets_path)
        
        # Save manager
        self.save_manager = SaveManager()
        
        # Level data
        self.platforms = []
        self.trigger_traps = []
        self.end_triggers = []
        self.level_width_pixels = 0
        
        # Cached level data to prevent re-parsing
        self._cached_normal_data = None
        self._cached_gema_data = None
        
        # Parallax
        self.parallax_layers = []
        self.moon_object = None
        self.moon_shadow_object = None
        
        # Game state
        self.spawn_invincibility_timer = 0
        self.spawn_invincibility_duration = 10
        self.death_delay_timer = 0
        self.death_delay_start_time = 0
        self.is_in_death_delay = False
        
        # End sequence state
        self.end_sequence_active = False
        self.end_sequence_mode = None
        self.end_sequence_dir = 1
        self.end_jump_started = False
        self.input_locked = False
        
        # Settings
        self.is_music_paused = False
        self.is_settings_open = False
        self.debug_draw = DEBUG_DRAW_HITBOXES
        
        # Click cooldown to prevent spam clicking
        self.last_click_time = 0
        self.click_cooldown_ms = 300  # 300ms between clicks
        
        # Initialize
        self._load_initial_assets()
    
    def _load_initial_assets(self):
        """Load all game assets."""
        try:
            self.asset_loader.load_all_assets(self.game_surface_height)
            self.asset_loader.load_music('music_platformer.ogg')
        except (AssetLoadError, AudioLoadError) as e:
            print(f"Asset loading error: {e}")
            self.running = False
    
    def setup_level(self, new_game=False, force_reparse=False):
        """Setup current level from level controller."""
        if new_game:
            self.platforms = []
            self.trigger_traps = []
            self.end_triggers = []
            self.camera.set_right_limit(None)
            self.level_width_pixels = 0
            self.entity_manager.clear_all()
            self._cached_normal_data = None
            self._cached_gema_data = None
        
        # Get level file paths
        normal_path, gema_path = self.level_controller.get_level_paths()
        
        # Parse or use cached data
        if force_reparse or self._cached_normal_data is None or self._cached_gema_data is None:
            normal_data = self.level_controller.parse_level_file(normal_path)
            gema_data = self.level_controller.parse_level_file(gema_path)
            self._cached_normal_data = normal_data
            self._cached_gema_data = gema_data
        else:
            normal_data = self._cached_normal_data
            gema_data = self._cached_gema_data
        
        # Setup platforms (copy rects to avoid shared references)
        for p in normal_data['platforms']:
            self.platforms.append({'rect': p['rect'].copy(), 'dim': 'normal', 'char': p['char']})
        for p in gema_data['platforms']:
            self.platforms.append({'rect': p['rect'].copy(), 'dim': 'gema', 'char': p['char']})
        
        # Setup trigger traps (copy rects to avoid shared references)
        for trigger_rect, trap_rect in zip(normal_data['triggers'], normal_data['trap_zones']):
            self.trigger_traps.append(TriggerTrap(trigger_rect.copy(), trap_rect.copy(), dim='normal'))
        for trigger_rect, trap_rect in zip(gema_data['triggers'], gema_data['trap_zones']):
            self.trigger_traps.append(TriggerTrap(trigger_rect.copy(), trap_rect.copy(), dim='gema'))
        
        # Setup end triggers (copy rects to avoid shared references)
        for et in normal_data['end_triggers']:
            self.end_triggers.append({'rect': et['rect'].copy(), 'dim': 'normal', 'mode': et['mode']})
        for et in gema_data['end_triggers']:
            self.end_triggers.append({'rect': et['rect'].copy(), 'dim': 'gema', 'mode': et['mode']})
        
        # Setup entities
        if new_game or not self.entity_manager.player:
            start_pos = normal_data['start_pos'] or (100, 100)
            self.entity_manager.create_player(start_pos[0], start_pos[1])
        
        # Setup enemies
        if new_game:
            self._setup_enemies(normal_data, gema_data)
            self._setup_npcs(normal_data['npc_spawns'], gema_data['npc_spawns'])
            self._setup_campfires(normal_data['campfires'], gema_data['campfires'])
        
        # Setup parallax
        if new_game:
            self._setup_parallax()
        
        # Camera and level bounds
        self.level_width_pixels = max(normal_data['max_width'], gema_data['max_width']) + 40
        if normal_data['camera_right_limit'] or gema_data['camera_right_limit']:
            limit = normal_data['camera_right_limit'] or gema_data['camera_right_limit']
            self.camera.set_right_limit(limit)
        
        self.spawn_invincibility_timer = self.spawn_invincibility_duration
    
    def _setup_enemies(self, normal_data, gema_data):
        """Setup enemies from level data."""
        tile_size = self.level_controller.tile_size
        
        for spawn in normal_data['enemy_spawns']:
            spawn_rect = spawn['rect']
            row = spawn_rect.y // tile_size
            
            # Calculate patrol bounds
            left_list = normal_data['left_markers'].get(row, [])
            right_list = normal_data['right_markers'].get(row, [])
            sx = spawn_rect.centerx
            left_bound = max([lx for lx in left_list if lx <= sx], default=sx - 80)
            right_bound = min([rx for rx in right_list if rx >= sx], default=sx + 80)
            
            self.entity_manager.add_enemy(
                spawn['type'], spawn_rect, spawn['facing'],
                left_bound, right_bound
            )
        
        for spawn in gema_data['enemy_spawns']:
            spawn_rect = spawn['rect']
            row = spawn_rect.y // tile_size
            
            left_list = gema_data['left_markers'].get(row, [])
            right_list = gema_data['right_markers'].get(row, [])
            sx = spawn_rect.centerx
            left_bound = max([lx for lx in left_list if lx <= sx], default=sx - 80)
            right_bound = min([rx for rx in right_list if rx >= sx], default=sx + 80)
            
            self.entity_manager.add_enemy(
                spawn['type'], spawn_rect, spawn['facing'],
                left_bound, right_bound
            )
    
    def _setup_npcs(self, normal_spawns, gema_spawns):
        """Setup NPCs from level data."""
        self.entity_manager.npcs = NPC.spawn_from_maps(normal_spawns, gema_spawns)
        
        # Snap NPCs to ground
        for npc in self.entity_manager.npcs:
            dim = getattr(npc, 'dim', 'normal')
            if getattr(npc, 'auto_snap', True):
                self.snap_actor_to_ground(npc.rect, dim=dim, max_dx=200)
    
    def _setup_campfires(self, normal_campfires, gema_campfires):
        """Setup campfires from level data."""
        for rect in normal_campfires:
            self.entity_manager.add_campfire(Campfire(rect))
        for rect in gema_campfires:
            self.entity_manager.add_campfire(Campfire(rect))
    
    def _setup_parallax(self):
        """Setup parallax layers."""
        self.parallax_layers = []
        speeds = [0.55, 0.5, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1]
        
        for i, image in enumerate(self.asset_loader.forest_layers):
            if i < len(speeds):
                layer = ParallaxLayer(image, speeds[i])
                self.parallax_layers.append(layer)
        
        self.moon_object = ParallaxObject(self.asset_loader.moon_image, 0.045, 50, x_offset=150)
        self.moon_shadow_object = ParallaxObject(self.asset_loader.moon_shadow_image, 0.05, 60, x_offset=160)
    
    def respawn_player(self):
        """Respawn player and reset level state."""
        self.entity_manager.respawn_player()
        self.entity_manager.respawn_all_enemies()
        self.spawn_invincibility_timer = self.spawn_invincibility_duration
        self.is_in_death_delay = False
        
        # Reset end sequence state
        self.end_sequence_active = False
        self.input_locked = False
        self.camera.unlock_camera()
        
        for trap in self.trigger_traps:
            trap.is_active = False
            trap.frame_index = 0.0
            trap.animation_finished = False
    
    def quick_restart_level(self):
        """Quick restart current level without re-parsing files."""
        print("[DEBUG] Starting quick_restart_level...")
        
        # Reset game state flags
        self.end_sequence_active = False
        self.input_locked = False
        self.is_in_death_delay = False
        self.spawn_invincibility_timer = self.spawn_invincibility_duration
        self.camera.unlock_camera()
        
        # Reset platforms and triggers
        self.platforms = []
        self.trigger_traps = []
        self.end_triggers = []
        
        # Reuse cached level data
        if self._cached_normal_data and self._cached_gema_data:
            normal_data = self._cached_normal_data
            gema_data = self._cached_gema_data
            
            # Setup platforms
            for p in normal_data['platforms']:
                self.platforms.append({'rect': p['rect'].copy(), 'dim': 'normal', 'char': p['char']})
            for p in gema_data['platforms']:
                self.platforms.append({'rect': p['rect'].copy(), 'dim': 'gema', 'char': p['char']})
            
            # Setup trigger traps
            for trigger_rect, trap_rect in zip(normal_data['triggers'], normal_data['trap_zones']):
                self.trigger_traps.append(TriggerTrap(trigger_rect.copy(), trap_rect.copy(), dim='normal'))
            for trigger_rect, trap_rect in zip(gema_data['triggers'], gema_data['trap_zones']):
                self.trigger_traps.append(TriggerTrap(trigger_rect.copy(), trap_rect.copy(), dim='gema'))
            
            # Setup end triggers
            for et in normal_data['end_triggers']:
                self.end_triggers.append({'rect': et['rect'].copy(), 'dim': 'normal', 'mode': et['mode']})
            for et in gema_data['end_triggers']:
                self.end_triggers.append({'rect': et['rect'].copy(), 'dim': 'gema', 'mode': et['mode']})
        
        # Respawn player and enemies
        self.respawn_player()
        print("[DEBUG] quick_restart_level completed")
    
    def handle_triggers(self):
        """Handle trigger activation."""
        player = self.entity_manager.player
        if not player.is_alive:
            return
        
        current_dim = 'gema' if player.in_gema_dimension else 'normal'
        
        # Activate traps
        for trap in self.trigger_traps:
            trap.try_activate(player.rect, current_dim)
        
        # Check end triggers
        if not self.end_sequence_active:
            for end_t in self.end_triggers:
                if end_t['dim'] in [current_dim, 'both'] and player.collides(end_t['rect']):
                    self.start_end_sequence(end_t['mode'])
                    break
    
    def handle_damage(self):
        """Handle player damage from hazards."""
        player = self.entity_manager.player
        
        if self.spawn_invincibility_timer > 0 or not player.is_alive or self.is_in_death_delay:
            return
        
        current_dim = 'gema' if player.in_gema_dimension else 'normal'
        active_hazards = []
        chaser_that_hit = None
        
        # Collect trap hazards
        for trap in self.trigger_traps:
            if trap.is_active and trap.dim in [current_dim, 'both']:
                active_hazards.append(trap.get_hazard_rect())
        
        # Collect enemy hazards
        for enemy in self.entity_manager.enemies:
            if getattr(enemy, 'is_dying', False):
                continue
            
            if hasattr(enemy, 'is_hazard_active') and enemy.is_hazard_active():
                hazard_rect = enemy.get_hazard_rect() if hasattr(enemy, 'get_hazard_rect') else enemy.rect
                active_hazards.append(hazard_rect)
                
                # Handle enemy contact
                if isinstance(enemy, PatrollingEnemy) and hazard_rect.colliderect(player.rect):
                    if hasattr(enemy, 'on_player_contact') and enemy.is_alive:
                        enemy.on_player_contact()
                    setattr(enemy, 'permanent_idle', True)
                
                if isinstance(enemy, ChaserEnemy) and hazard_rect.colliderect(player.rect):
                    chaser_that_hit = enemy
            
            # Boss special attacks
            if isinstance(enemy, Boss):
                active_hazards.extend(enemy.get_spell_hazards())
                if hasattr(enemy, 'is_melee_active') and enemy.is_melee_active():
                    active_hazards.append(enemy.get_melee_hazard_rect())
        
        # Apply damage
        result = player.apply_hazards(active_hazards, SCREEN_HEIGHT, is_invincible=False)
        if result:
            if chaser_that_hit:
                setattr(chaser_that_hit, 'permanent_combat_idle', True)
                chaser_that_hit.state = 'combat_idle'
                chaser_that_hit.frame_index = 0
                chaser_that_hit.velocity.x = 0
            
            if result.get('temporary_death'):
                self.is_in_death_delay = True
                self.death_delay_timer = result.get('delay_ms', 500)
                self.death_delay_start_time = pygame.time.get_ticks()
    
    def handle_combat(self):
        """Handle player attacks on enemies."""
        player = self.entity_manager.player
        attack_rect = player.get_attack_hitbox() if hasattr(player, 'get_attack_hitbox') else None
        
        if not attack_rect:
            return
        
        for enemy in self.entity_manager.get_active_enemies():
            if attack_rect.colliderect(enemy.rect):
                if isinstance(enemy, Boss):
                    if hasattr(enemy, 'take_damage'):
                        enemy.take_damage(1)
                elif hasattr(enemy, 'on_killed_by_player'):
                    enemy.on_killed_by_player()
    
    def handle_enemy_blocking(self):
        """Handle enemy blocking player movement."""
        player = self.entity_manager.player
        
        for enemy in self.entity_manager.enemies:
            if getattr(enemy, 'is_dying', False):
                continue
            
            if not getattr(enemy, 'blocks_player', True):
                continue
            
            # Get blocking rect
            if hasattr(enemy, 'get_invisible_wall_rect'):
                block_rect = enemy.get_invisible_wall_rect()
            elif hasattr(enemy, 'get_block_rect'):
                block_rect = enemy.get_block_rect()
            else:
                block_rect = enemy.rect
            
            # Check collision and push player
            if player.rect.colliderect(block_rect):
                if player.velocity.x > 0:
                    player.rect.right = block_rect.left
                elif player.velocity.x < 0:
                    player.rect.left = block_rect.right
                else:
                    if player.rect.centerx < block_rect.centerx:
                        player.rect.right = block_rect.left
                    else:
                        player.rect.left = block_rect.right
                player.velocity.x = 0
    
    def start_end_sequence(self, mode: str):
        """Start level end sequence."""
        self.end_sequence_active = True
        self.end_sequence_mode = mode
        self.end_sequence_dir = 1
        self.end_jump_started = False
        self.input_locked = True
        self.camera.lock_camera(self.entity_manager.player.rect.centerx)
    
    def update_end_sequence(self, active_platforms):
        """Update end sequence animation."""
        player = self.entity_manager.player
        
        player.is_walking = True
        player.direction = 1 if self.end_sequence_dir >= 0 else -1
        player.velocity.x = PLAYER_SPEED * 0.8 * player.direction
        
        if self.end_sequence_mode == 'jump_walk' and not self.end_jump_started:
            if getattr(player, 'is_on_ground', False):
                player.velocity.y = -JUMP_STRENGTH * 0.6
                self.end_jump_started = True
        
        player.step(active_platforms)
        
        # Check if sequence complete
        camera_offset = self.camera.get_offset(player.rect)
        player_screen_x = player.rect.x - camera_offset[0]
        
        if (player_screen_x > self.game_surface_width + 40 or 
            player_screen_x + player.rect.width < -40 or 
            player.rect.left > self.level_width_pixels + 40):
            self.end_sequence_active = False
            self.input_locked = False
            self.camera.unlock_camera()
            self.go_to_next_level()
    
    def go_to_next_level(self):
        """Advance to next level."""
        current_hearts = self.entity_manager.player.hearts
        
        if self.level_controller.advance_level():
            # Save progress
            self.save_manager.save_progress(self.level_controller.current_level, current_hearts)
            self.setup_level(new_game=True)
            self.entity_manager.player.hearts = current_hearts
        else:
            # All levels completed
            self.state_controller.change_state(GameStateEnum.GAME_OVER_WIN)
    
    def update(self):
        """Main update loop."""
        player = self.entity_manager.player
        
        # Update invincibility
        if self.spawn_invincibility_timer > 0:
            self.spawn_invincibility_timer -= 1
        
        # Get active platforms for current dimension
        current_dim = 'gema' if player.in_gema_dimension else 'normal'
        active_platforms = [p['rect'] for p in self.platforms if p['dim'] in [current_dim, 'both']]
        
        # Update based on game state
        if self.end_sequence_active:
            self.update_end_sequence(active_platforms)
        else:
            # Normal gameplay
            player.update(active_platforms)
            
            # Update all entities
            for enemy in self.entity_manager.enemies:
                enemy.update(active_platforms, player)
            
            # Update NPCs
            for npc in self.entity_manager.npcs:
                if getattr(npc, 'dim', 'both') in (current_dim, 'both'):
                    npc.update(player.rect)
            
            # Handle interactions
            if player.is_alive:
                self.handle_triggers()
                self.handle_damage()
                self.handle_enemy_blocking()
                self.handle_combat()
        
        # Update animated elements
        for trap in self.trigger_traps:
            trap.update(self.asset_loader.spike_frames)
        
        for campfire in self.entity_manager.campfires:
            campfire.update(self.asset_loader.campfire_frames)
        
        # Handle death
        if not player.is_alive:
            if self.is_in_death_delay:
                is_ready = (player.state == 'death' and player.animation_finished) or (player.state != 'death')
                if is_ready:
                    current_time = pygame.time.get_ticks()
                    if current_time - self.death_delay_start_time > self.death_delay_timer:
                        self.respawn_player()
            elif player.hearts <= 0:
                self.state_controller.change_state(GameStateEnum.GAME_OVER)
        
        # Cleanup dead enemies
        self.entity_manager.cleanup_dead_enemies()
    
    def draw(self):
        """Main draw loop."""
        player = self.entity_manager.player
        
        # Get camera offset
        camera_offset = self.camera.get_offset(player.rect)
        
        # Clear screen
        current_dim = 'gema' if player.in_gema_dimension else 'normal'
        bg_color = COLOR_BG_GEMA if current_dim == 'gema' else COLOR_BG_NORMAL
        self.game_surface.fill(bg_color)
        
        # Draw parallax
        for layer in reversed(self.parallax_layers):
            layer.draw(self.game_surface, camera_offset[0], 0)
        
        if current_dim == 'gema':
            self.moon_shadow_object.draw(self.game_surface, camera_offset[0])
            self.moon_object.draw(self.game_surface, camera_offset[0])
        
        # Draw platforms
        for p in self.platforms:
            if p['dim'] in [current_dim, 'both']:
                tile_image = self.asset_loader.tile_images.get(p['char'])
                if tile_image:
                    scaled_image = pygame.transform.scale(tile_image, (p['rect'].width, p['rect'].height))
                    self.game_surface.blit(scaled_image, (p['rect'].x - camera_offset[0], p['rect'].y - camera_offset[1]))
        
        # Draw traps
        for trap in self.trigger_traps:
            if trap.is_active and trap.dim in [current_dim, 'both']:
                trap.draw(self.game_surface, camera_offset[0], camera_offset[1], self.asset_loader.spike_frames)
        
        # Draw campfires
        for campfire in self.entity_manager.campfires:
            campfire.draw(self.game_surface, camera_offset[0], camera_offset[1], self.asset_loader.campfire_frames)
        
        # Draw entities
        self.entity_manager.draw_all(self.game_surface, camera_offset[0], camera_offset[1])
        
        # Debug draw
        if self.debug_draw:
            self._draw_debug(camera_offset, current_dim)
        
        # Scale to screen
        self.screen.blit(pygame.transform.scale(self.game_surface, self.screen.get_size()), (0, 0))
    
    def _draw_debug(self, camera_offset, current_dim):
        """Draw debug hitboxes."""
        player = self.entity_manager.player
        
        # Player hitbox
        pygame.draw.rect(self.game_surface, (0, 255, 0),
            pygame.Rect(player.rect.x - camera_offset[0], player.rect.y - camera_offset[1],
                       player.rect.width, player.rect.height), 1)
        
        # Attack hitbox
        if hasattr(player, "get_attack_hitbox"):
            atk_rect = player.get_attack_hitbox()
            if atk_rect:
                pygame.draw.rect(self.game_surface, (255, 165, 0),
                    pygame.Rect(atk_rect.x - camera_offset[0], atk_rect.y - camera_offset[1],
                               atk_rect.width, atk_rect.height), 1)
        
        # Enemy hitboxes
        for enemy in self.entity_manager.enemies:
            pygame.draw.rect(self.game_surface, (180, 180, 180),
                pygame.Rect(enemy.rect.x - camera_offset[0], enemy.rect.y - camera_offset[1],
                           enemy.rect.width, enemy.rect.height), 1)
        
        # NPC hitboxes
        for npc in self.entity_manager.npcs:
            if getattr(npc, "dim", "both") in (current_dim, "both"):
                pygame.draw.rect(self.game_surface, (0, 255, 255),
                    pygame.Rect(npc.rect.x - camera_offset[0], npc.rect.y - camera_offset[1],
                               npc.rect.width, npc.rect.height), 1)
    
    def snap_actor_to_ground(self, actor_rect, dim='normal', max_dx=160):
        """Snap actor to nearest ground platform."""
        r = self.ground_rect_at_or_near(actor_rect.centerx, dim, max_dx)
        if r:
            actor_rect.bottom = r.top
            actor_rect.centerx = max(r.left + actor_rect.width//2,
                                    min(r.right - actor_rect.width//2, actor_rect.centerx))
            return True
        return False
    
    def ground_rect_at_or_near(self, x, dim='normal', max_dx=160):
        """Find ground rect at or near x position."""
        exact = [p['rect'] for p in self.platforms
                if p['dim'] in [dim, 'both'] and p['rect'].left <= x <= p['rect'].right]
        if exact:
            return min(exact, key=lambda r: r.top)
        
        near = [(abs(x - r.centerx), r) for r in
                (p['rect'] for p in self.platforms if p['dim'] in [dim, 'both'])]
        near = [t for t in near if t[0] <= max_dx]
        if near:
            return min(near, key=lambda t: (t[0], t[1].top))[1]
        
        return None
    
    def run(self):
        """Main game loop."""
        # Load saved progress
        save_data = self.save_manager.load_progress()
        self.level_controller.set_level(save_data.get('current_level', 1))
        self.setup_level(new_game=True)
        
        # UI buttons
        from graphics.ui_buttons import UIButtons
        ui_buttons = UIButtons()
        
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            
            # Event handling
            try:
                events_list = pygame.event.get()
            except Exception:
                pygame.event.clear()
                events_list = []
            
            for event in events_list:
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state_controller.is_state(GameStateEnum.PLAYING):
                            self.state_controller.toggle_pause()
                    elif event.key == pygame.K_p:
                        if self.state_controller.is_state(GameStateEnum.PAUSED):
                            self.state_controller.toggle_pause()
                    elif event.key == pygame.K_F3:
                        self.debug_draw = not self.debug_draw
                
                # Player input
                if self.state_controller.is_state(GameStateEnum.PLAYING) and not self.input_locked:
                    if self.entity_manager.player:
                        self.entity_manager.player.handle_event(event)
                    
                    # NPC input
                    player = self.entity_manager.player
                    current_dim = 'gema' if player.in_gema_dimension else 'normal'
                    for npc in self.entity_manager.npcs:
                        if getattr(npc, 'dim', 'both') in (current_dim, 'both'):
                            npc.handle_event(event, player.rect)
                
                # UI input
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    ui_buttons.handle_click(self, mouse_pos)
            
            # Update
            if self.state_controller.is_state(GameStateEnum.PLAYING):
                self.update()
            
            # Draw
            self.draw()
            
            # Draw UI
            ui_buttons.draw_ui(self, mouse_pos)
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()
