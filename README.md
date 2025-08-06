# Short-Form Quote Video Generator

This project automatically generates short-form videos featuring quotes by combining voiceover, subtitles, and video clips.

## Features
- **Text-to-Speech**: Generates voiceover using ElevenLabs TTS (via `tts_eleven`).
- **Subtitles**: Creates and styles subtitles from the generated audio (`stt` and `pysrt`).
- **Video Editing**: Trims, concatenates, and overlays subtitles on video clips using FFmpeg (`ffmpeg-python`).
- **Audio Mixing**: Mixes the TTS voiceover with background music tracks and applies fade effects.

## Getting Started

### Prerequisites
- Python 3.8+
- FFmpeg (installed and available in your `PATH`)
- ElevenLabs API key (set via environment or configuration in `tts_eleven`)

### Installation
Install the required Python packages:
```bash
pip install ffmpeg-python pysrt elevenlabs
```

### Usage
1. Place your source video clips in `assets/clips/`.
2. Add background music (`.mp3`) to `assets/music/`.
3. (Optional) Prepare quotes or audio files in `audio/` for batch processing.
4. Run the main script:
```bash
python src/main.py
```

To generate a video from a specific quote:
```bash
python src/main.py generate_video_from_quote "Your quote here" --voice british --song assets/music/example.mp3
```

The generated videos will be saved in the `quotes_output/` directory.

## Project Structure
```
.
├── assets/
│   ├── clips/        # Source video clips
│   └── music/        # Background music tracks
├── audio/            # Generated audio (TTS outputs)
├── quotes_output/    # Final generated videos
├── src/
│   ├── main.py       # Entry point for video generation
│   ├── render_video.py  # Handles FFmpeg video processing
│   ├── tts_eleven.py # ElevenLabs TTS wrapper
│   └── stt.py        # Subtitle generation utilities
└── subtitles/        # Generated subtitle files
```

## Configuration
- **Voices**: Edit the `VOICES` list in `src/main.py`.
- **Volumes & Durations**: Adjust audio volumes and fade settings in `src/render_video.py`.
- **Subtitle Styling**: Customize font, size, and position in `src/render_video.py` under the FFmpeg subtitles filter.

---
_Minimal, customizable pipeline for creating engaging short-form quote videos._
