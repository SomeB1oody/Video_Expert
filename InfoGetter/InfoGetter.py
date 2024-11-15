import subprocess
import re
import os

def get_video_info(file_path):
    if not os.path.exists(file_path):
        print("file path does not exist!")
        return None

    # 使用FFmpeg命令获取视频信息
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", file_path,
        "-hide_banner"
    ]

    try:
        # 执行命令并捕获输出
        result = subprocess.run(ffmpeg_cmd, stderr=subprocess.PIPE, text=True)
        ffmpeg_output = result.stderr
    except Exception as e:
        print(f"Failed to execute FFmpeg: {e}")
        return None

    # 初始化信息变量
    width = height = bitrate = codec = color_depth = color_space = frame_rate = duration = None
    audio_codec = sample_rate = channels = None

    # 解析FFmpeg输出
    # 获取视频分辨率
    resolution_match = re.search(r"(\d{2,5})x(\d{2,5})", ffmpeg_output)
    if resolution_match:
        width, height = resolution_match.groups()

    # 获取视频编码格式
    codec_match = re.search(r"Video:\s(\w+)", ffmpeg_output)
    if codec_match:
        codec = codec_match.group(1)

    # 获取色彩深度
    color_depth_match = re.search(r"(\d{1,2})\s?bits", ffmpeg_output)
    if color_depth_match:
        color_depth = color_depth_match.group(1) + " bit"

    # 获取色彩空间
    color_space_match = re.search(r"(yuv\w+|rgb\w+)", ffmpeg_output)
    if color_space_match:
        color_space = color_space_match.group(1)

    # 获取比特率
    bitrate_match = re.search(r"bitrate:\s(\d+)\s?kb/s", ffmpeg_output)
    if bitrate_match:
        bitrate = int(bitrate_match.group(1)) * 1000

    # 获取帧率
    frame_rate_match = re.search(r"(\d+(?:\.\d+)?)\s?fps", ffmpeg_output)
    if frame_rate_match:
        frame_rate = float(frame_rate_match.group(1))

    # 获取视频时长
    duration_match = re.search(r"Duration:\s(\d+):(\d+):(\d+\.\d+)", ffmpeg_output)
    if duration_match:
        hours, minutes, seconds = map(float, duration_match.groups())
        duration = hours * 3600 + minutes * 60 + seconds

    # 获取音频信息
    audio_codec_match = re.search(r"Audio:\s(\w+)", ffmpeg_output)
    if audio_codec_match:
        audio_codec = audio_codec_match.group(1)

    # 获取音频采样率
    sample_rate_match = re.search(r"(\d+)\s?Hz", ffmpeg_output)
    if sample_rate_match:
        sample_rate = int(sample_rate_match.group(1))

    # 获取音频声道数
    channels_match = re.search(r",\s(stereo|mono|5\.1)", ffmpeg_output)
    if channels_match:
        channels = channels_match.group(1)

    # 获取文件大小
    file_size = os.path.getsize(file_path)

    # 创建视频信息字典
    video_info = {
        "resolution": f"{width}x{height}" if width and height else "Unknown",
        "bitrate": f"{bitrate / 1000:.2f} kbps" if bitrate else "Unknown",
        "video_codec": codec,
        "color_depth": color_depth if color_depth else "Unknown",
        "color_space": color_space if color_space else "Unknown",
        "frame_rate": f"{frame_rate:.2f} fps" if frame_rate else "Unknown",
        "duration": f"{duration:.2f} seconds" if duration else "Unknown",
        "file_size": f"{file_size / (1024**2):.2f} MB" if file_size else "Unknown",
        "audio_codec": audio_codec if audio_codec else "Unknown",
        "sample_rate": f"{sample_rate / 1000:.1f} kHz" if sample_rate else "Unknown",
        "channels": channels if channels else "Unknown"
    }

    return video_info

# 用户输入视频路径
video_path = input("Enter the video file path: ")
info = get_video_info(video_path)
if info:
    print("Video Information:")
    for key, value in info.items():
        print(f"{key.capitalize()}: {value}")
