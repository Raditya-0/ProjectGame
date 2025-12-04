"""
Level Manager - Mengelola level loading, transitions, dan progression.
Demonstrasi Encapsulation dan Composition.
"""
import pygame
import os
from typing import List, Tuple, Dict, Optional
from utils.exception import LevelFileNotFound


class LevelData:
    """Data class untuk level information."""
    
    def __init__(self, level_number: int, normal_map: str, gema_map: str):
        self.level_number = level_number
        self.normal_map_path = normal_map
        self.gema_map_path = gema_map
        self.is_completed = False
    
    def __repr__(self):
        return f"Level {self.level_number}: {self.normal_map_path}"


class LevelManager:
    """
    Mengelola level loading dan progression.
    Encapsulation: semua level logic dalam satu class.
    """
    
    def __init__(self, base_path: str):
        self._base_path = base_path
        self._levels: List[LevelData] = []
        self._current_level_index = 0
        self._tile_size = 40
    
    @property
    def current_level_number(self) -> int:
        """Get current level number (1-indexed)."""
        return self._current_level_index + 1
    
    @property
    def total_levels(self) -> int:
        """Get total number of levels."""
        return len(self._levels)
    
    @property
    def current_level(self) -> Optional[LevelData]:
        """Get current level data."""
        if 0 <= self._current_level_index < len(self._levels):
            return self._levels[self._current_level_index]
        return None
    
    def add_level(self, normal_map: str, gema_map: str) -> None:
        """Add level to manager."""
        level_num = len(self._levels) + 1
        level_data = LevelData(level_num, normal_map, gema_map)
        self._levels.append(level_data)
    
    def load_levels_from_folder(self, folder_path: str) -> None:
        """Load all levels dari folder (convention: level_X_normal.txt, level_X_gema.txt)."""
        full_path = os.path.join(self._base_path, folder_path)
        if not os.path.exists(full_path):
            print(f"[WARNING] Levels folder not found: {full_path}")
            return
        
        # Find all level files
        level_files = {}
        for filename in os.listdir(full_path):
            if filename.startswith('level_') and filename.endswith('.txt'):
                # Parse level_X_type.txt
                parts = filename.replace('.txt', '').split('_')
                if len(parts) >= 3:
                    level_num = int(parts[1])
                    map_type = parts[2]  # 'normal' or 'gema'
                    
                    if level_num not in level_files:
                        level_files[level_num] = {}
                    level_files[level_num][map_type] = os.path.join(full_path, filename)
        
        # Add levels in order
        for level_num in sorted(level_files.keys()):
            if 'normal' in level_files[level_num] and 'gema' in level_files[level_num]:
                self.add_level(
                    level_files[level_num]['normal'],
                    level_files[level_num]['gema']
                )
    
    def set_current_level(self, level_number: int) -> bool:
        """
        Set current level by number (1-indexed).
        Returns True if successful.
        """
        index = level_number - 1
        if 0 <= index < len(self._levels):
            self._current_level_index = index
            return True
        return False
    
    def go_to_next_level(self) -> bool:
        """
        Advance to next level.
        Returns True if there is a next level, False if already at last level.
        """
        if self._current_level_index < len(self._levels) - 1:
            self._current_level_index += 1
            return True
        return False
    
    def reset_to_first_level(self) -> None:
        """Reset to first level."""
        self._current_level_index = 0
    
    def is_last_level(self) -> bool:
        """Check if current level is the last one."""
        return self._current_level_index >= len(self._levels) - 1
    
    def parse_map_file(self, filepath: str) -> Dict:
        """
        Parse map file dan return dictionary dengan parsed data.
        Returns dict with: platforms, enemies, npcs, triggers, etc.
        """
        result = {
            'platforms': [],
            'enemies': [],
            'npcs': [],
            'triggers': [],
            'traps': [],
            'campfires': [],
            'end_triggers': [],
            'start_pos': None,
            'camera_limit': None,
            'left_markers': {},
            'right_markers': {},
            'max_width': 0
        }
        
        try:
            with open(filepath, 'r') as file:
                for y, line in enumerate(file):
                    for x, char in enumerate(line):
                        world_x, world_y = x * self._tile_size, y * self._tile_size
                        rect = pygame.Rect(world_x, world_y, self._tile_size, self._tile_size)
                        
                        if world_x > result['max_width']:
                            result['max_width'] = world_x
                        
                        # Parse different tile types
                        if char in 'Gg':
                            result['platforms'].append({'rect': rect, 'char': 'G'})
                        elif char in 'Pp':
                            plat_rect = pygame.Rect(world_x, world_y, self._tile_size, 20)
                            result['platforms'].append({'rect': plat_rect, 'char': 'P'})
                        elif char in 'Hh':
                            facing = 'right' if char == 'H' else 'left'
                            result['enemies'].append({'rect': rect, 'type': 'patrol', 'facing': facing})
                        elif char in 'Ff':
                            facing = 'right' if char == 'F' else 'left'
                            result['enemies'].append({'rect': rect, 'type': 'chaser', 'facing': facing})
                        elif char in 'Nn':
                            facing = 'right' if char == 'N' else 'left'
                            result['enemies'].append({'rect': rect, 'type': 'chaser_heavy', 'facing': facing})
                        elif char in 'Bb':
                            facing = 'right' if char == 'B' else 'left'
                            result['enemies'].append({'rect': rect, 'type': 'boss', 'facing': facing})
                        elif char in 'Aa':
                            facing = 'left' if char == 'A' else 'right'
                            result['npcs'].append({'rect': rect, 'type': 'A', 'facing': facing})
                        elif char in 'Qq':
                            facing = 'left' if char == 'Q' else 'right'
                            result['npcs'].append({'rect': rect, 'type': 'Q', 'facing': facing})
                        elif char in 'Ww':
                            facing = 'left' if char == 'W' else 'right'
                            result['npcs'].append({'rect': rect, 'type': 'W', 'facing': facing})
                        elif char in 'Tt':
                            result['triggers'].append(rect)
                        elif char in 'jJyY':
                            result['traps'].append(rect)
                        elif char in 'Cc':
                            result['campfires'].append(rect)
                        elif char == 'D':
                            result['end_triggers'].append({'rect': rect, 'mode': 'jump_walk'})
                        elif char == 'd':
                            result['end_triggers'].append({'rect': rect, 'mode': 'walk'})
                        elif char in 'Ss':
                            result['start_pos'] = (world_x, world_y + self._tile_size)
                        elif char == 'K':
                            result['camera_limit'] = world_x + self._tile_size // 2
                        elif char in 'lL':
                            result['left_markers'].setdefault(y, []).append(world_x + self._tile_size // 2)
                        elif char in 'rR':
                            result['right_markers'].setdefault(y, []).append(world_x + self._tile_size // 2)
            
            result['max_width'] += self._tile_size
            return result
            
        except FileNotFoundError:
            print(str(LevelFileNotFound(filepath)))
            raise
    
    def get_level_paths(self, level_number: int) -> Optional[Tuple[str, str]]:
        """Get (normal_map, gema_map) paths untuk level number (1-indexed)."""
        index = level_number - 1
        if 0 <= index < len(self._levels):
            level = self._levels[index]
            return (level.normal_map_path, level.gema_map_path)
        return None
