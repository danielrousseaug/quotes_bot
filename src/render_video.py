import ffmpeg
import pysrt
import os
import random
import re
import pysrt

def sticky_subs(srt_file_path):
    with open(srt_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Regular expression to find the timecode line
    timecode_re = re.compile(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})')
    
    # List to store the adjusted lines
    adjusted_lines = []
    # Variable to store the new start time for the next subtitle
    next_start_time = "00:00:00,000"
    
    # Iterate through lines and collect all timecodes
    for line in lines:
        match = timecode_re.search(line)
        if match:
            start_time, end_time = match.groups()
            # Update the line with the new start and end times
            new_line = line.replace(start_time, next_start_time).replace(end_time, start_time)
            adjusted_lines.append(new_line)
            # Update next_start_time for the next subtitle
            next_start_time = start_time
        else:
            adjusted_lines.append(line)
    
    # Adjust the last subtitle to end at its start time
    if adjusted_lines:
        last_timecode_line = adjusted_lines[-2]
        match = timecode_re.search(last_timecode_line)
        if match:
            last_start_time, last_end_time = match.groups()
            adjusted_lines[-2] = last_timecode_line.replace(last_end_time, last_start_time)

    # Write to output file
    with open(srt_file_path, 'w', encoding='utf-8') as output_file:
        output_file.writelines(adjusted_lines)



def split_subs(srt_file, max_length=40):
    subs = pysrt.open(srt_file)
    for sub in subs:
        words = sub.text.split()
        new_text = []
        current_line = []

        for word in words:
            if len(' '.join(current_line + [word])) > max_length:
                new_text.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)

        if current_line:
            new_text.append(' '.join(current_line))

        sub.text = '\n'.join(new_text)
    
    # Save the modified subtitles to a new file
    subs.save(srt_file, encoding='utf-8')




def next_available_filename(directory):
    """ Returns the next available filename in the format 'quotes_video_n.mp4' """
    if not os.path.exists(directory):
        os.makedirs(directory)
    files = [f for f in os.listdir(directory) if f.startswith('quotes_video_') and f.endswith('.mp4')]
    numbers = []
    for f in files:
        try:
            number = int(f.replace('quotes_video_', '').replace('.mp4', ''))
            numbers.append(number)
        except ValueError:
            continue  # Skip files that do not conform to the expected format
    next_number = max(numbers) + 1 if numbers else 1
    return os.path.join(directory, f"quotes_video_{next_number}.mp4")

# Example usage
directory = "C:\\Users\\danie\\OneDrive\\Desktop\\shorts_bots\\quotes_bot\\src\\assets\\clips"
next_filename = next_available_filename(directory)
print(next_filename)


def mp3_regex(text):
    # Regex pattern to find the first string of letters followed by .mp3
    pattern = r'\b[a-zA-Z]+\.mp3\b'
    # Search for the first match
    match = re.search(pattern, text)
    return match.group(0) if match else None

def adjust_subtitle_timing(subtitles):
    for i in range(len(subtitles) - 1):
        subtitles[i]['end'] = subtitles[i + 1]['start']
    return subtitles

def prepare_video_clips(audio_path, music_path, subtitle_path, video_folder,fade_duration=3):
    split_subs(subtitle_path)
    fps=60
    volumes = {
        "qkthr.mp3": 0.2,
        "solo.mp3": 0.5,
        "moon.mp3": 0.28,
        "core.mp3": 0.33,
        "onemoreday.mp3":0.22,
        "cry.mp3":0.4,
        "someday.mp3":0.4,
        "dogsong.mp3":0.4
    }
    

    music_volume = volumes[mp3_regex(music_path)]
    
    output_directory = '../quotes_output'  # Set the output directory name
    output_path = next_available_filename(output_directory)  # Determine the next available output filename
    
    # Load subtitles
    subs = pysrt.open(subtitle_path)

    # List all video files in the video folder
    video_files = [f for f in os.listdir(video_folder) if f.endswith(('.mp4', '.avi', '.mov'))]
    random.shuffle(video_files)

    used_videos = []
    video_streams = []

    for i,sub in enumerate(subs):
        print(sub)
        # Calculate subtitle duration in seconds
        start_time = sub.start.ordinal / 1000  # pysrt uses milliseconds
        if(i == 0): 
            start_time = 0
        end_time = sub.end.ordinal / 1000
        duration = end_time - start_time

        # Check if the current subtitle is not the last one
        if i < len(subs) - 1:
            # Make the end time of the current subtitle the start time of the next one
            next_sub = subs[i + 1]
            sub.end = next_sub.start
        else:
            # For the last subtitle, you may want to define a custom duration or handling
            # For example, add 3 seconds to the last subtitle's end time
            sub.end = end_time = sub.end.ordinal 

        # Select a random video file not yet used
        for video in video_files:
            if video not in used_videos:
                selected_video = video
                used_videos.append(video)
                break

        if i == len(subs)-1: duration += fade_duration
        video_path = os.path.join(video_folder, selected_video)
        video_input = ffmpeg.input(video_path, stream_loop=-1)
        video_segment = video_input.trim(duration=duration).setpts('PTS-STARTPTS')
        video_streams.append(video_segment)

    # Concatenate all video segments
    concatenated_video = ffmpeg.concat(*video_streams, v=1, a=0)

    # Audio processing
    primary_audio = ffmpeg.input(audio_path)
    music_audio = ffmpeg.input(music_path)
    
    # Get duration of primary audio in seconds
    audio_info = ffmpeg.probe(audio_path)
    audio_duration = float(audio_info['format']['duration'])
    
    # Calculate number of loops required for the music
    music_info = ffmpeg.probe(music_path)
    music_duration = float(music_info['format']['duration'])
    loops_needed = int(audio_duration // music_duration + 1)

    # Create a looped music track
    looped_music = ffmpeg.concat(*(music_audio for _ in range(loops_needed)), v=0, a=1).filter('atrim', duration=audio_duration+fade_duration).filter('volume', volume=music_volume)

    # Mix primary audio with looped music
    mixed_audio = ffmpeg.filter([looped_music,primary_audio], 'amix', inputs=2, duration='first')

    # Fade out audio and video
    mixed_audio = ffmpeg.filter(mixed_audio, 'afade', type='out', start_time=audio_duration, duration=fade_duration)
    concatenated_video = ffmpeg.filter(concatenated_video, 'fade', type='out', start_frame=int(audio_duration * fps), nb_frames=int(fade_duration * fps))  # Assuming a frame rate of 30 fps



    # Add and style subtitles
    styled_video = ffmpeg.filter(
        concatenated_video,
        'subtitles',
        subtitle_path,
        # force_style='FontName=Arial,FontSize=6,PrimaryColour=&H00FFFF,Outline=0.5,Alignment=10'
        force_style='FontName=Arial,FontSize=50,PrimaryColour=&H00B3FF,Outline=2,Alignment=10,playResX=1440,playResY=2560'
    )
    

    # Combine styled video with audio
    output = ffmpeg.output(styled_video, mixed_audio, output_path, vcodec='h264_nvenc', acodec='aac')#.global_args('-loglevel', 'warning')
    output.run()

# Example usage:
# prepare_video_clips('audio/audio.mp3', 'audio/music/qkthr.mp3', 'subtitles/subtitles.srt', 'clips')
