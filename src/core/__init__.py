"""
Core module - Base interfaces dan classes untuk game architecture.
"""
from .interfaces import (
    IDrawable,
    IUpdatable,
    ICollidable,
    IPhysicsBody,
    IAnimatable,
    IDamageable,
    IInputHandler
)
from .entity_base import Entity
from .game_state import GameStateController, GameStateEnum
from .level_controller import LevelController
from .entity_manager import EntityManager
from .camera_controller import CameraController
from .asset_loader import AssetLoader

__all__ = [
    'IDrawable',
    'IUpdatable',
    'ICollidable',
    'IPhysicsBody',
    'IAnimatable',
    'IDamageable',
    'IInputHandler',
    'Entity',
    'GameStateController',
    'GameStateEnum',
    'LevelController',
    'EntityManager',
    'CameraController',
    'AssetLoader',
]
