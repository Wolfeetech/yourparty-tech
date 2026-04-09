"""
Audio Science Module
Provides logic for Harmonic Mixing using the Camelot Wheel system.
"""

import logging

logger = logging.getLogger("AudioScience")

class CamelotWheel:
    """
    Camelot Wheel Helper for Harmonic Mixing.
    Keys are represented as strings: "1A", "1B", "12A", "12B", etc.
    A = Minor, B = Major
    """
    
    # Mapping of standard keys to Camelot notation
    KEY_MAP = {
        "Abm": "1A", "G#m": "1A", "B": "1B",
        "Ebm": "2A", "D#m": "2A", "F#": "2B", "Gb": "2B",
        "Bbm": "3A", "A#m": "3A", "Db": "3B", "C#": "3B",
        "Fm": "4A", "Ab": "4B", "G#": "4B",
        "Cm": "5A", "Eb": "5B", "D#": "5B",
        "Gm": "6A", "Bb": "6B", "A#": "6B",
        "Dm": "7A", "F": "7B",
        "Am": "8A", "C": "8B",
        "Em": "9A", "G": "9B",
        "Bm": "10A", "D": "10B",
        "F#m": "11A", "Gbm": "11A", "A": "11B",
        "Dbm": "12A", "C#m": "12A", "E": "12B"
    }

    @staticmethod
    def normalize_key(key_str: str) -> str:
        """
        Normalize a key string to Camelot notation (e.g. "Am" -> "8A", "8A" -> "8A").
        Returns None if invalid.
        """
        if not key_str:
            return None
        
        k = key_str.strip().title() # Normalize case "am" -> "Am" but "8a" -> "8A" needs care
        
        # Already Camelot? (e.g. 8A, 12B)
        import re
        if re.match(r"^(1[0-2]|[1-9])[AB]$", key_str.upper()):
            return key_str.upper()
        
        # Check Standard Notation Map
        # Fix common variations
        k = k.replace("Sharp", "#").replace("Flat", "b")
        if k in CamelotWheel.KEY_MAP:
            return CamelotWheel.KEY_MAP[k]
        
        return None

    @staticmethod
    def get_compatible_keys(current_key: str) -> list[str]:
        """
        Get list of compatible keys for a given Camelot key.
        Rules:
        1. Same Key (8A -> 8A)
        2. +/- 1 Hour (8A -> 7A, 9A)
        3. Relative Major/Minor (8A -> 8B)
        
        Energy boost: +1 Semitone (+7 hours) or +2 Semitones (+2 hours) is advanced, 
        but we stick to standard harmonic mixing first.
        """
        c_key = CamelotWheel.normalize_key(current_key)
        if not c_key:
            return []
            
        # Parse Number and Letter
        num = int(c_key[:-1])
        letter = c_key[-1] # A or B
        
        compatible = []
        
        # 1. Same Key
        compatible.append(c_key)
        
        # 2. +/- 1 Hour
        prev_num = 12 if num == 1 else num - 1
        next_num = 1 if num == 12 else num + 1
        
        compatible.append(f"{prev_num}{letter}")
        compatible.append(f"{next_num}{letter}")
        
        # 3. Relative Major/Minor (Change Letter)
        other_letter = "B" if letter == "A" else "A"
        compatible.append(f"{num}{other_letter}")
        
        return compatible

if __name__ == "__main__":
    # Test
    print(f"8A Compatible: {CamelotWheel.get_compatible_keys('8A')}")
    print(f"Am Compatible: {CamelotWheel.get_compatible_keys('Am')}")
    print(f"12B Compatible: {CamelotWheel.get_compatible_keys('12B')}")
