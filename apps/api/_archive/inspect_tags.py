import mutagen
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("InspectTags")

# Deduced path
FILE_PATH = r"Z:\radio_library\Music\_input\Grand 12 Inches\cd_5\01_-_visage_-_fade_to_grey_(dance_mix).flac"

def inspect():
    if not os.path.exists(FILE_PATH):
        logger.error(f"File STILL not found at: {FILE_PATH}")
        # Try finding it in Grand 12 Inches folder just in case
        parent = os.path.dirname(os.path.dirname(FILE_PATH))
        for root, _, files in os.walk(parent):
            for f in files:
                if "fade_to_grey" in f.lower():
                     logger.info(f"Found candidate: {os.path.join(root, f)}")
        return

    try:
        audio = mutagen.File(FILE_PATH)
        if not audio:
            logger.error("Mutagen could not open file.")
            return

        print("\n--- TAGS FOUND ---")
        tags = audio.tags
        if tags:
            for k, v in tags.items():
                print(f"{k}: {v}")
                
        print("\n--- SIMPLE SUMMARY ---")
        # Try standard keys
        print(f"Artist: {tags.get('TPE1', 'Unknown')}")
        print(f"Title: {tags.get('TIT2', 'Unknown')}")
        
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    inspect()
