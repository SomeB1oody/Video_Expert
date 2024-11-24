import os
import subprocess

def separate_audio_video(video_input_path):
    # 检查输入文件是否存在
    if not os.path.isfile(video_input_path):
        print("Error: The video file you entered does not exist!")
        return

    # 获取文件名和扩展名
    base_name, ext = os.path.splitext(os.path.basename(video_input_path))
    output_dir = os.path.dirname(video_input_path)

    # 无音频视频的输出路径
    video_no_audio_output = os.path.join(output_dir, f"{base_name}_no_audio{ext}")
    # 纯音频文件的输出路径
    audio_output = os.path.join(output_dir, f"{base_name}.mp3")

    try:
        # 分离无音频的视频
        print("Extracting video without audio...")
        subprocess.run(
            ["ffmpeg", "-i", video_input_path, "-an", "-c:v", "copy", video_no_audio_output],
            check=True
        )
        print(f"No audio video saved to: {video_no_audio_output}")

        # 提取音频
        print("Extracting pure audio...")
        subprocess.run(
            ["ffmpeg", "-i", video_input_path, "-vn", "-acodec", "libmp3lame", audio_output],
            check=True
        )
        print(f"Pure audio files have been saved to: {audio_output}")

    except subprocess.CalledProcessError as e:
        print(f"Fail to process: {e}")


if __name__ == "__main__":
    # 在这里询问用户输入路径
    video_input_path = input("Please enter the video file path: ").strip()
    separate_audio_video(video_input_path)
