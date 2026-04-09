import os
import re
from pymongo import MongoClient
from collections import Counter
import logging

# Load Config
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'apps', 'api')))
from config_secrets import MONGO_URI, MOOD_RULES

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("SmartTagger")

def derive_genre_from_path(relative_path):
    """
    Extracts a cleaner genre from Beatport folder structures.
    e.g. "Music/_input/Beatport - Top 100 Tech House..." -> "Tech House"
    """
    if not relative_path:
        return None

    path_str = relative_path.replace("\\", "/")
    parts = path_str.split("/")
    
    # 1. Look for known genres in the path parts directly (case insensitive)
    # Flatten rules to list of keywords
    all_keywords = []
    for keywords in MOOD_RULES.values():
        all_keywords.extend(keywords)
        
    # Check each part of the path
    for part in parts:
        part_clean = part.lower().replace("_", " ").replace("-", " ")
        for kw in all_keywords:
            if kw.lower() in part_clean:
                # Found a strict match!
                # But we want the original casing from the rule if possible
                return kw 

    # 2. Fallback: Heuristic parsing of "Beatport ... Genre" folders
    # e.g. "Beatport - Top 100 Tech House"
    for part in parts:
        if "beatport" in part.lower():
            # Try to strip common prefixes
            clean = re.sub(r'beatport.*?-', '', part, flags=re.IGNORECASE)
            clean = re.sub(r'top 100', '', clean, flags=re.IGNORECASE)
            clean = re.sub(r'secret weapons', '', clean, flags=re.IGNORECASE)
            clean = re.sub(r'weekend picks', '', clean, flags=re.IGNORECASE)
            clean = re.sub(r'[\(\[].*?[\)\]]', '', clean) # Remove (Year) [Format] etc
            clean = clean.replace("_", " ").strip()
            
            # If the remaining string matches a known rule keyword, return that keyword
            for kw in all_keywords:
                if kw.lower() in clean.lower():
                    return kw
            
            if len(clean) > 3: # If result is still substantial, use it as a custom genre?
                 return clean.title()

    # 3. Last Resort: Top level folder if not "Music" or "Unknown"
    if len(parts) > 0 and parts[0] not in ["Music", "Unknown", "_input"]:
        return parts[0]
        
    return None

def assign_mood(genre):
    if not genre: return None
    for mood, keywords in MOOD_RULES.items():
        if any(k.lower() in genre.lower() for k in keywords):
            return mood
    return None

def run_smart_tagging(dry_run=True):
    client = MongoClient(MONGO_URI)
    db = client["yourparty"]
    collection = db["tracks"]
    
    logger.info(f"Connected to DB: {db.name}")
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
    
    cursor = collection.find({})
    stats = Counter()
    
    for track in cursor:
        original_genre = track.get("genre", "")
        # If genre is "Unknown" or looks like a filename/path (contains / or \), try to fix it
        # Actually, let's just ALWAYS try to derive a better genre if the current one isn't in our "Good List"
        
        rel_path = track.get("relative_path", "")
        derived_genre = derive_genre_from_path(rel_path)
        
        new_mood = None
        final_genre = original_genre
        
        if derived_genre:
            final_genre = derived_genre
            new_mood = assign_mood(final_genre)
            
        # Decision Time
        updates = {}
        
        # Update Genre if it changed and looks valid
        if final_genre and final_genre != original_genre and final_genre != "Unknown":
            updates["genre"] = final_genre
            stats["genre_updated"] += 1
            
        # Update Mood if we found a new one
        if new_mood:
             if track.get("mood") != new_mood:
                 updates["mood"] = new_mood
                 stats[f"mood_set_{new_mood}"] += 1
        
        if updates:
            if dry_run:
                # Log sample
                if stats["total_updates"] < 20: # Only log first 20
                     logger.info(f"[UPDATE] {track.get('title')} | Path: ...{rel_path[-30:]}")
                     logger.info(f"   -> Old Genre: '{original_genre}' | New Genre: '{updates.get('genre', '-')}'")
                     logger.info(f"   -> Old Mood:  '{track.get('mood')}' | New Mood:  '{updates.get('mood', '-')}'")
            else:
                collection.update_one({"_id": track["_id"]}, {"$set": updates})
            stats["total_updates"] += 1
            
    logger.info("--- SUMMARY ---")
    for k, v in stats.items():
        logger.info(f"{k}: {v}")

if __name__ == "__main__":
    # Default to Dry Run unless argument "live" is passed
    is_live = "live" in sys.argv
    run_smart_tagging(dry_run=not is_live)
