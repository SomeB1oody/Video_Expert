import subprocess
import os

def get_duration(file_path):
    result = subprocess.run(
        ['ffprobe', '-i', file_path, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=p=0'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    return float(result.stdout.strip())

def process_audio(audio_path, video_duration, audio_duration, choice=None):
    if audio_duration > video_duration:
        output_audio = "trimmed_audio.aac"
        subprocess.run([
            'ffmpeg', '-i', audio_path, '-t', str(video_duration),
            '-c', 'copy', output_audio, '-y'
        ])
    elif audio_duration < video_duration:
        if choice == '1':
            output_audio = "padded_audio.aac"
            subprocess.run([
                'ffmpeg', '-i', audio_path, '-filter_complex',
                f"[0:a]apad=pad_dur={video_duration}[out]",
                '-map', '[out]', '-c:a', 'aac', output_audio, '-y'
            ])
        elif choice == '2':
            output_audio = audio_path
        else:
            raise ValueError("Invalid choice")
    else:
        output_audio = audio_path  # 时长相等直接使用音频

    return output_audio

def replace_audio(video_path, output_audio):
    # 生成新的输出文件名
    video_name, ext = os.path.splitext(video_path)
    output_video = f"{video_name}_with_new_audio{ext}"

    subprocess.run([
        'ffmpeg', '-i', video_path, '-i', output_audio,
        '-c:v', 'copy', '-map', '0:v:0', '-map', '1:a:0',
        '-shortest', output_video, '-y'
    ])
    print(f"Success! File saved as {output_video}")


if __name__ == "__main__":
    # 用户交互
    video_path = input("Enter video path: ")
    audio_path = input("Enter audio path:")

    if not os.path.exists(video_path):
        print("Invalid video path")
        exit(1)
    if not os.path.exists(audio_path):
        print("Invalid audio path")
        exit(1)

    # 获取视频和音频时长
    video_duration = get_duration(video_path)
    audio_duration = get_duration(audio_path)

    # 处理音频逻辑
    if audio_duration < video_duration:
        print("Audio duration is less than video, please select a processing method:")
        print("1. Mute processing: Complete the blank part of the audio for mute")
        print("2. Retain the original video audio: the less part continues to use the original video audio")
        choice = input("Enter option(1 or 2):")
    else:
        choice = None

    # 处理音频并替换
    try:
        processed_audio = process_audio(audio_path, video_duration, audio_duration, choice)
        replace_audio(video_path, processed_audio)
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)
