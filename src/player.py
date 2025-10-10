import pygame
from settings import *

class Player:
    def __init__(self, x, y):
        self._load_animations_from_spritesheet()
        self.image = self.animations['idle'][0]
        self.rect = self.image.get_rect(bottomleft=(x, y))

        self.velocity = pygame.math.Vector2(0, 0)
        self.is_on_ground = True
        
        self.hearts = PLAYER_START_HEARTS
        self.in_gema_dimension = False
        self.direction = 1 
        
        self.state = 'idle'
        self.frame_index = 0
        self.animation_timer = 0
        
        self.is_alive = True
        self.animation_finished = False

    def _load_animations_from_spritesheet(self):
        self.animations = {'idle': [], 'run': [], 'jump': [], 'fall': [], 'death': []}
        
        try:
            idle_sheet = pygame.image.load('C:\\Users\\Lenovo\\Documents\\GitHub\\ProjectGameGIGA\\Assets\\Player\\_Idle.png').convert_alpha() 
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
            run_sheet = pygame.image.load('C:\\Users\\Lenovo\\Documents\\GitHub\\ProjectGameGIGA\\Assets\\Player\\_Run.png').convert_alpha() 
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
            jump_sheet = pygame.image.load('C:\\Users\\Lenovo\\Documents\\GitHub\\ProjectGameGIGA\\Assets\\Player\\_Jump.png').convert_alpha() 
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
            fall_sheet = pygame.image.load('C:\\Users\\Lenovo\\Documents\\GitHub\\ProjectGameGIGA\\Assets\\Player\\_Fall.png').convert_alpha() 
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

        try:
            death_sheet = pygame.image.load('C:\\Users\\Lenovo\\Documents\\GitHub\\ProjectGameGIGA\\Assets\\Player\\_Death.png').convert_alpha() 
            frame_width, frame_height, frame_count = 38, 40, 5
            left_margin, gap_width, top_margin = 36, 75, 40
            for i in range(frame_count):
                x_pos = left_margin + i * (frame_width + gap_width)
                frame_surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame_surface.blit(death_sheet, (0, 0), (x_pos, top_margin, frame_width, frame_height))
                self.animations['death'].append(frame_surface)
        except Exception as e:
            print(f"Error memuat death sheet: {e}")
            self.animations['death'].append(pygame.Surface((30, 40)))

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
        self._apply_physics(platforms)
        self._get_input()
        self._animate()

    def draw(self, screen, camera_offset_x, camera_offset_y):
        final_image = self.image
        if self.direction == -1: final_image = pygame.transform.flip(self.image, True, False)
        screen.blit(final_image, (self.rect.x - camera_offset_x, self.rect.y - camera_offset_y))
