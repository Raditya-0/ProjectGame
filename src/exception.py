class GameException(Exception):
    """Base class for all custom game exceptions."""
    pass


class AssetLoadError(GameException):
    def __init__(self, resource: str, detail: Exception | str | None = None):
        self.resource = resource
        self.detail = detail

    def __str__(self) -> str:
        d = f" ({self.detail})" if self.detail else ""
        return f"Error memuat aset: {self.resource}{d}"


class LevelFileNotFound(GameException):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def __str__(self) -> str:
        return f"Error: File level '{self.file_path}' tidak ditemukan!"


class AudioLoadError(GameException):
    def __init__(self, file_path: str, detail: Exception | str | None = None):
        self.file_path = file_path
        self.detail = detail

    def __str__(self) -> str:
        d = f" ({self.detail})" if self.detail else ""
        return f"Tidak bisa memuat file musik: {self.file_path}{d}"


class SpriteSheetError(GameException):
    def __init__(self, file_path: str, detail: Exception | str | None = None):
        self.file_path = file_path
        self.detail = detail

    def __str__(self) -> str:
        d = f" ({self.detail})" if self.detail else ""
        return f"Error memuat sprite sheet: {self.file_path}{d}"
