import os
import sys
import random

# Adjust the system path to include the required modules
sys.path.append(os.path.abspath('../../reddit_bot/src'))

# Local imports from other modules
from render_video import prepare_video_clips
from stt import *
from tts_eleven import *

# Global configurations
AUDIO_OUTPUT_PATH = "../audio/audio.mp3"
SUBTITLES_OUTPUT_PATH = "../subtitles/subtitles.srt"
VOICES = ["watts", "bukowski", "robot","british"]

def quick(song=None):
    """Generates a video from the given quote using specified voice and song."""
    if song is None:
        song = random_song()

    print(f"Using song: {song}")
    prepare_video_clips(AUDIO_OUTPUT_PATH, song, SUBTITLES_OUTPUT_PATH, "../assets/clips")
    print("Video generation completed successfully.")

def random_song(folder_path="../assets/music"):
    """Returns a random MP3 file path from the specified folder."""
    files = os.listdir(folder_path)
    mp3_files = [f for f in files if f.endswith('.mp3')]
    return os.path.normpath(os.path.join(folder_path, random.choice(mp3_files))) if mp3_files else None

def generate_video_from_quote(quote, voice=None, song=None):
    """Generates a video from the given quote using specified voice and song."""
    if voice is None:
        voice = random.choice(VOICES)
    if song is None:
        song = random_song()

    print(f"Using song: {song} and voice: {voice}")
    generate_tts(quote, AUDIO_OUTPUT_PATH, voice=voice)
    generate_srt(AUDIO_OUTPUT_PATH, SUBTITLES_OUTPUT_PATH, quotes=True)
    prepare_video_clips(AUDIO_OUTPUT_PATH, song, SUBTITLES_OUTPUT_PATH, "../assets/clips")
    print("Video generation completed successfully.")

def enhanced(folder_path="../audio/enhanced"):
    """Process all non-used MP3 files in the specified folder to generate videos."""
    files = os.listdir(folder_path)
    used_index = max([int(f.split('_')[1].split('.')[0]) for f in files if f.startswith('used_')] + [0]) + 1

    for f in files:
        if f.endswith('.mp3') and not f.startswith('used_'):
            try:
                audio_path = os.path.join(folder_path, f)
                generate_srt(audio_path, SUBTITLES_OUTPUT_PATH, quotes=True)
                prepare_video_clips(audio_path, random_song(), SUBTITLES_OUTPUT_PATH, "../assets/clips")
                os.rename(audio_path, os.path.join(folder_path, f"used_{used_index}.mp3"))
                used_index += 1
                print(f"Processed {f} successfully.")
            except Exception as e:
                print(f"Error processing {f}: {e}")

# Sample usage:
if __name__ == "__main__":
    quote = """
C'est quoi réussir sa vie? Rire souvent et beaucoup ; gagner le respect des gens intelligents et l'affection des enfants ; savoir qu'un être a respiré plus aisément parce que vous avez vécu. C'est cela réussir sa vie. 
    """
    quick(song="../assets/music/dogsong.mp3")
    #generate_video_from_quote(quote,voice="british")

    enhanced()
