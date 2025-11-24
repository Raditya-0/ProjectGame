import json
import os


class SaveManager:
    """Manages player save data."""
    
    def __init__(self, save_file: str = "player_save.json"):
        # Save file in the project root directory
        base_path = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(base_path, '..'))
        self.save_path = os.path.join(project_root, save_file)
        
    def save_progress(self, current_level: int, hearts: int = 3):
        """Save current player progress."""
        data = {
            "current_level": current_level,
            "hearts": hearts
        }
        
        try:
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Progress saved: Level {current_level}")
        except Exception as e:
            print(f"Failed to save progress: {e}")
    
    def load_progress(self) -> dict:
        """Load saved progress. Returns dict with current_level and hearts."""
        if not os.path.exists(self.save_path):
            # No save file, return default (start from level 1)
            return {"current_level": 1, "hearts": 3}
        
        try:
            with open(self.save_path, 'r') as f:
                data = json.load(f)
            print(f"Progress loaded: Level {data.get('current_level', 1)}")
            return data
        except Exception as e:
            print(f"Failed to load progress: {e}")
            return {"current_level": 1, "hearts": 3}
    
    def clear_save(self):
        """Delete save file (reset progress)."""
        if os.path.exists(self.save_path):
            try:
                os.remove(self.save_path)
                print("Save file deleted")
            except Exception as e:
                print(f"Failed to delete save: {e}")
    
    def get_last_level(self) -> int:
        """Get the last level player was on."""
        data = self.load_progress()
        return data.get("current_level", 1)
