import pygame

class ParallaxLayer:
    def __init__(self, image, speed_ratio):
        self.image = image
        self.speed_ratio = speed_ratio
        self.x_pos = 0

    def update(self, camera_movement_x):
        self.x_pos -= camera_movement_x * self.speed_ratio

    def draw(self, surface, camera_offset_x, camera_offset_y):
            surface_width = surface.get_width()
            img_width = self.image.get_width()

            if img_width <= 0:
                return

            scroll = camera_offset_x * self.speed_ratio
            
            tiles_needed = (surface_width // img_width) + 2
            
            start_tile = int(scroll // img_width) - 1

            for i in range(start_tile, start_tile + tiles_needed + 1):
                draw_pos_x = i * img_width - scroll
                surface.blit(self.image, (draw_pos_x, 0))
