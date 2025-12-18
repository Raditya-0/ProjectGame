"""
Resource Manager - Mengelola loading dan caching assets.
Demonstrasi Singleton pattern, Encapsulation, dan Resource management.
"""
import pygame
import os
from typing import Dict, List, Optional, Tuple
from utils.exception import AssetLoadError


class ResourceManager:
    """
    Singleton class untuk mengelola game assets (images, sounds, fonts).
    Encapsulation: semua asset loading logic dalam satu class.
    Caching: assets di-load sekali dan di-reuse.
    """
    
    _instance = None
    
    def __new__(cls):
        """Implement Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize resource manager (hanya sekali)."""
        if self._initialized:
            return
            
        self._initialized = True
        self._images: Dict[str, pygame.Surface] = {}
        self._image_sequences: Dict[str, List[pygame.Surface]] = {}
        self._sounds: Dict[str, pygame.mixer.Sound] = {}
        self._fonts: Dict[str, pygame.font.Font] = {}
        self._base_path = os.path.dirname(os.path.abspath(__file__))
        self._assets_path = os.path.join(self._base_path, '..', '..', 'Assets')
    
    @property
    def assets_path(self) -> str:
        """Get base assets directory path."""
        return self._assets_path
    
    def set_base_path(self, path: str) -> None:
        """Set custom base path untuk assets."""
        self._base_path = path
        self._assets_path = os.path.join(path, 'Assets')
    
    def load_image(self, relative_path: str, cache_key: Optional[str] = None, 
                   convert_alpha: bool = True) -> Optional[pygame.Surface]:
        """
        Load single image dengan caching.
        Args:
            relative_path: path relative to Assets folder
            cache_key: optional key for caching (default: relative_path)
            convert_alpha: whether to convert_alpha
        """
        if cache_key is None:
            cache_key = relative_path
        
        # Check cache
        if cache_key in self._images:
            return self._images[cache_key]
        
        # Load image
        full_path = os.path.join(self._assets_path, relative_path)
        try:
            if convert_alpha:
                image = pygame.image.load(full_path).convert_alpha()
            else:
                image = pygame.image.load(full_path).convert()
            self._images[cache_key] = image
            return image
        except pygame.error as e:
            print(str(AssetLoadError(relative_path, e)))
            return None
    
    def load_image_sequence(self, folder_path: str, cache_key: Optional[str] = None,
                           extensions: Tuple[str, ...] = ('.png', '.jpg', '.jpeg')) -> List[pygame.Surface]:
        """
        Load sequence of images dari folder.
        Useful untuk animation frames.
        """
        if cache_key is None:
            cache_key = folder_path
        
        # Check cache
        if cache_key in self._image_sequences:
            return self._image_sequences[cache_key]
        
        full_path = os.path.join(self._assets_path, folder_path)
        if not os.path.exists(full_path):
            print(f"[WARNING] Folder {full_path} not found")
            return []
        
        frames = []
        try:
            files = sorted([f for f in os.listdir(full_path) 
                          if f.lower().endswith(extensions)],
                         key=lambda x: x.lower())
            
            for filename in files:
                filepath = os.path.join(full_path, filename)
                image = pygame.image.load(filepath).convert_alpha()
                frames.append(image)
            
            self._image_sequences[cache_key] = frames
            return frames
        except Exception as e:
            print(f"[ERROR] Loading image sequence from {folder_path}: {e}")
            return []
    
    def load_scaled_image(self, relative_path: str, size: Tuple[int, int],
                         cache_key: Optional[str] = None) -> Optional[pygame.Surface]:
        """Load dan scale image."""
        if cache_key is None:
            cache_key = f"{relative_path}_{size[0]}x{size[1]}"
        
        if cache_key in self._images:
            return self._images[cache_key]
        
        image = self.load_image(relative_path, cache_key=None)
        if image:
            scaled = pygame.transform.scale(image, size)
            self._images[cache_key] = scaled
            return scaled
        return None
    
    def load_sound(self, relative_path: str, cache_key: Optional[str] = None) -> Optional[pygame.mixer.Sound]:
        """Load sound effect dengan caching."""
        if cache_key is None:
            cache_key = relative_path
        
        if cache_key in self._sounds:
            return self._sounds[cache_key]
        
        full_path = os.path.join(self._assets_path, relative_path)
        try:
            sound = pygame.mixer.Sound(full_path)
            self._sounds[cache_key] = sound
            return sound
        except pygame.error as e:
            print(f"[ERROR] Loading sound {relative_path}: {e}")
            return None
    
    def load_font(self, relative_path: str, size: int, 
                  cache_key: Optional[str] = None) -> Optional[pygame.font.Font]:
        """Load font dengan caching."""
        if cache_key is None:
            cache_key = f"{relative_path}_{size}"
        
        if cache_key in self._fonts:
            return self._fonts[cache_key]
        
        full_path = os.path.join(self._assets_path, relative_path)
        try:
            font = pygame.font.Font(full_path, size)
            self._fonts[cache_key] = font
            return font
        except Exception as e:
            print(f"[ERROR] Loading font {relative_path}: {e}")
            return None
    
    def get_system_font(self, size: int, cache_key: Optional[str] = None) -> pygame.font.Font:
        """Get system default font."""
        if cache_key is None:
            cache_key = f"system_{size}"
        
        if cache_key in self._fonts:
            return self._fonts[cache_key]
        
        font = pygame.font.SysFont(None, size)
        self._fonts[cache_key] = font
        return font
    
    def clear_cache(self) -> None:
        """Clear all cached resources."""
        self._images.clear()
        self._image_sequences.clear()
        self._sounds.clear()
        self._fonts.clear()
    
    def get_cached_image(self, cache_key: str) -> Optional[pygame.Surface]:
        """Get cached image by key."""
        return self._images.get(cache_key)
    
    def get_cached_sequence(self, cache_key: str) -> List[pygame.Surface]:
        """Get cached image sequence by key."""
        return self._image_sequences.get(cache_key, [])
