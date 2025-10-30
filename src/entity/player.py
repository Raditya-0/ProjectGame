import os
import pygame
from settings import *
from entity.entity import Entity

base_path = os.path.dirname(os.path.abspath(__file__))
# entity/player.py is under src/entity, while Assets/ is at the repo root alongside src/
project_root = os.path.abspath(os.path.join(base_path, '..', '..'))
assets_path = os.path.join(project_root, 'Assets')

class Player(Entity):
    def __init__(self, x, y):
        self._load_animations_from_spritesheet()
        initial_image = self.animations['idle'][0]
        super().__init__(x, y, initial_image)

        self.is_on_ground = True

        self.hearts = PLAYER_START_HEARTS
        self.in_gema_dimension = False

        self.state = 'idle'
        self.frame_index = 0
        self.animation_timer = 0

        self.animation_finished = False

    def _load_animations_from_spritesheet(self):
        self.animations = {'idle': [], 'run': [], 'jump': [], 'fall': [], 'death': []}
        player_asset_path = os.path.join(assets_path, 'Player')

        try:
            idle_sheet_path = os.path.join(player_asset_path, '_Idle.png')
            idle_sheet = pygame.image.load(idle_sheet_path).convert_alpha() 
            frame_width, frame_height, frame_count = 21, 38, 10
            left_margin, gap_width, top_margin = 44, 99, 42
            for i in range(frame_count):
                x_pos = left_margin + i * (frame_width + gap_width)
                frame_surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame_surface.blit(idle_sheet, (0, 0), (x_pos, top_margin, frame_width, frame_height))
                self.animations['idle'].append(frame_surface)
        except Exception as e:
            print(f"Error memuat idle sheet: {e}")
            self.animations['idle'].append(pygame.Surface((21, 38)))

        try:
            run_sheet_path = os.path.join(player_asset_path, '_Run.png')
            run_sheet = pygame.image.load(run_sheet_path).convert_alpha() 
            frame_width, frame_height, frame_count = 30, 40, 10
            left_margin, gap_width, top_margin = 43, 90, 40
            for i in range(frame_count):
                x_pos = left_margin + i * (frame_width + gap_width)
                frame_surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame_surface.blit(run_sheet, (0, 0), (x_pos, top_margin, frame_width, frame_height))
                self.animations['run'].append(frame_surface)
        except Exception as e:
            print(f"Error memuat run sheet: {e}")
            self.animations['run'].append(pygame.Surface((30, 40)))
            
        try:
            jump_sheet_path = os.path.join(player_asset_path, '_Jump.png')
            jump_sheet = pygame.image.load(jump_sheet_path).convert_alpha() 
            frame_width, frame_height, frame_count = 25, 38, 3
            left_margin, gap_width, top_margin = 44, 95, 42
            for i in range(frame_count):
                x_pos = left_margin + i * (frame_width + gap_width)
                frame_surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame_surface.blit(jump_sheet, (0, 0), (x_pos, top_margin, frame_width, frame_height))
                self.animations['jump'].append(frame_surface)
        except Exception as e:
            print(f"Error memuat jump sheet: {e}")
            self.animations['jump'].append(pygame.Surface((30, 40)))
            
        try:
            fall_sheet_path = os.path.join(player_asset_path, '_Fall.png')
            fall_sheet = pygame.image.load(fall_sheet_path).convert_alpha() 
            frame_width, frame_height, frame_count = 29, 38, 3
            left_margin, gap_width, top_margin = 39, 91, 42
            for i in range(frame_count):
                x_pos = left_margin + i * (frame_width + gap_width)
                frame_surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame_surface.blit(fall_sheet, (0, 0), (x_pos, top_margin, frame_width, frame_height))
                self.animations['fall'].append(frame_surface)
        except Exception as e:
            print(f"Error memuat fall sheet: {e}")
            self.animations['fall'].append(pygame.Surface((30, 40)))

        frame_count = 10
        asset_folder = os.path.join(player_asset_path, 'Death')
        self.animations['death'] = [] 

        try:
            for i in range(1, frame_count + 1):
                file_name = f'_Death{i}.png'
                full_path = os.path.join(asset_folder, file_name)

                # Load the image and convert it for better performance
                frame_surface = pygame.image.load(full_path).convert_alpha()
                self.animations['death'].append(frame_surface)

            print("Death animation loaded successfully.")

        except Exception as e:
            print(f"Error loading death animation: {e}")
            self.animations['death'].append(pygame.Surface((30, 40), pygame.SRCALPHA))

    def _get_input(self):
        if not self.is_alive: return
        self.is_walking = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.velocity.x = -PLAYER_SPEED; self.direction = -1; self.is_walking = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.velocity.x = PLAYER_SPEED; self.direction = 1; self.is_walking = True
        else: self.velocity.x = 0
            
    def _apply_physics(self, platforms):
        if not self.is_alive:
            self.velocity.x = 0 
            self.velocity.y += GRAVITY
            self.rect.y += self.velocity.y
            for platform in platforms:
                if self.rect.colliderect(platform) and self.velocity.y > 0:
                    self.rect.bottom = platform.top
                    self.velocity.y = 0
            return

        self.rect.x += self.velocity.x
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.velocity.x > 0: self.rect.right = platform.left
                elif self.velocity.x < 0: self.rect.left = platform.right
        self.velocity.y += GRAVITY
        self.rect.y += self.velocity.y
        self.is_on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.velocity.y > 0: self.rect.bottom = platform.top; self.velocity.y = 0; self.is_on_ground = True
                elif self.velocity.y < 0: self.rect.top = platform.bottom; self.velocity.y = 0

    def _update_animation_state(self):
        if not self.is_alive:
            self.state = 'death'
            return
        
        if not self.is_on_ground:
            if self.velocity.y < 0: self.state = 'jump'
            else: self.state = 'fall'
        elif self.is_walking: self.state = 'run'
        else: self.state = 'idle'

    def _animate(self):
        self._update_animation_state()
        self.animation_timer += 1
        
        if self.animation_timer > ANIMATION_SPEED:
            self.animation_timer = 0
            current_animation = self.animations[self.state]
            
            if self.state == 'death':
                if self.frame_index < len(current_animation) - 1:
                    self.frame_index += 1
                else:
                    self.animation_finished = True 
            else: 
                if len(current_animation) > 0: 
                    self.frame_index = (self.frame_index + 1) % len(current_animation)
            
            if len(current_animation) > 0:
                self.image = current_animation[self.frame_index]

    def jump(self):
        if self.is_on_ground and self.is_alive: self.velocity.y = -JUMP_STRENGTH

    def shift_dimension(self):
        if self.is_alive: self.in_gema_dimension = not self.in_gema_dimension

    def take_damage(self):
        if self.is_alive:
            self.hearts -= 1
            print(f"Hati berkurang! Sisa: {self.hearts}")
            if self.hearts <= 0:
                self.die()
    
    def die(self):
        if self.is_alive:
            self.is_alive = False
            self.animation_finished = False
            self.frame_index = 0
            print("Pemain masuk ke state mati.")

    def respawn(self, pos):
        self.rect.bottomleft = pos
        self.velocity.x = 0
        self.velocity.y = 0
        self.is_on_ground = True
        self.is_alive = True
        self.animation_finished = False
        
        self.frame_index = 0
        self.state = 'idle'
        if len(self.animations['idle']) > 0:
            self.image = self.animations['idle'][self.frame_index]
        
        if self.hearts <= 0:
            self.hearts = PLAYER_START_HEARTS

    def update(self, platforms):
        # Read input first, then apply physics, then animate. This keeps input responsive.
        self._get_input()
        self._apply_physics(platforms)
        self._animate()

    def handle_event(self, event):
        """Handle incoming pygame events relevant for the player.

        This keeps per-player input handling inside the Player class and allows
        `main.py` to be focused on game flow.
        """
        if not self.is_alive: return

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_UP, pygame.K_w]:
                self.jump()
            if event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
                self.shift_dimension()

    def apply_hazards(self, hazard_rects, fall_limit_y, is_invincible=False):
        """Check and apply damage from environment hazards.

        Inputs:
        - hazard_rects: iterable of pygame.Rect that can damage the player
        - fall_limit_y: y threshold beyond which falling counts as damage
        - is_invincible: if True, ignores incoming damage (e.g., spawn i-frames)

        Returns a dict when damage was applied, else None. Example:
        { 'source': 'trap'|'fall', 'temporary_death': True|False, 'delay_ms': int }
        temporary_death=True means hearts remain but we play death anim + respawn delay.
        """
        if is_invincible or not self.is_alive:
            return None

        damage_source = None
        # Fall off-screen check
        if self.rect.top > fall_limit_y:
            damage_source = 'fall'
        else:
            # Trap collision check
            for r in hazard_rects:
                if self.rect.colliderect(r):
                    damage_source = 'trap'
                    break

        if not damage_source:
            return None

        # Apply damage and decide death behavior
        self.take_damage()

        if not self.is_alive:
            # Hearts <= 0 inside take_damage() already called die()
            return {'source': damage_source, 'temporary_death': False, 'delay_ms': 0}

        # Temporary death: play death animation and request respawn delay
        self.die()
        delay_ms = 500 if damage_source in ('fall', 'trap') else 500
        return {'source': damage_source, 'temporary_death': True, 'delay_ms': delay_ms}
