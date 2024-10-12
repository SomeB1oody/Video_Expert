import subprocess
import os
import re

def remove_trailing_backslash(path: str) -> str:
    # 如果路径以反斜杠结尾，去掉它
    if path.endswith('\\'):
        return path[:-1]
    return path

def calculate_seconds_difference(start_time: str, end_time: str) -> str:
    # 将时间字符串转换为时、分、秒
    start_h, start_m, start_s = map(int, start_time.split(":"))
    end_h, end_m, end_s = map(int, end_time.split(":"))

    # 将起始和终止时间都转换为以秒为单位
    start_total_seconds = start_h * 3600 + start_m * 60 + start_s
    end_total_seconds = end_h * 3600 + end_m * 60 + end_s

    # 返回时间差，单位为秒
    return str(end_total_seconds - start_total_seconds)

def is_valid_windows_filename(filename: str) -> bool:
    # 检查是否包含非法字符
    invalid_chars = r'[<>:"/\\|?*]'
    if re.search(invalid_chars, filename):
        return False
    # 检查是否是保留名称
    reserved_names = [
        "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
    ]
    if filename.upper() in reserved_names:
        return False
    # 检查是否以空格或点结尾
    if filename.endswith(' ') or filename.endswith('.'):
        return False
    # 检查文件名长度
    if len(filename) > 255:
        return False
    # 如果所有检查都通过，返回True
    return True

# 定义一个函数来调用 ffmpeg 截取视频片段
def cut_video_ffmpeg(video_path, start_time, end_time, output_path):
    try:
        ffmpeg_command = [
            'ffmpeg',
            '-ss', str(start_time),     # 起始时间
            '-i', video_path,          # 输入视频文件
            '-t', calculate_seconds_difference(str(start_time), str(end_time)),  # 截取的持续时间
            '-c:v', 'libx264',
            '-preset', 'veryslow',
            output_path                 # 输出文件路径
        ]

        # 调用 ffmpeg 命令
        subprocess.run(ffmpeg_command, check=True)
        print(f"Saved as: {output_path}")
        print("\tSuccess!\t")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

# 定义正则表达式来验证时间格式
def is_valid_time_format(time_str):
    # 匹配 hh:mm:ss 格式，或纯秒数格式 s
    hhmmss_pattern = r'^\d{1,2}:\d{2}:\d{2}$'  # hh:mm:ss 格式
    seconds_pattern = r'^\d+(\.\d+)?$'          # 纯秒数 s 格式
    return re.match(hhmmss_pattern, time_str) or re.match(seconds_pattern, time_str)

# 获取有效的输入视频路径
def get_valid_file_path():
    while True:
        video_path = input("Input video path: ")
        if os.path.isfile(video_path):
            return video_path
        else:
            print(f"\tInput file: {video_path} does not exist. Please try again.\t")

# 获取有效的输出路径
def get_valid_output_path():
    while True:
        output_path = input("Output path: ")
        output_path_ = remove_trailing_backslash(output_path)
        if os.path.exists(output_path_):
            return output_path_
        else:
            print(f"\tOutput path: {output_path} does not exist. Please try again.\t")

# 获取有效的时间输入
def get_valid_time_input(prompt):
    while True:
        time_str = input(prompt)
        if is_valid_time_format(time_str):
            return time_str
        else:
            print("\tInvalid time format. Please enter time in hh:mm:ss or seconds (e.g., 120 or 01:30:00).\t")

# 获取输出名称
def get_output_name():
    while True:
        output_name = input("Output name: ")
        flag = is_valid_windows_filename(output_name)
        if flag:
            return f'{output_name}.mp4'
        else:
            print(f"\tOutput name: {output_name} is not legal. Please try another one.\t")

if __name__ == "__main__":
    # 获取有效的输入视频文件路径
    video_path = get_valid_file_path()

    # 获取截取视频的开始时间和结束时间，确保时间格式正确
    start_time = get_valid_time_input("Start time (format: hh:mm:ss or s): ")
    end_time = get_valid_time_input("End time (format: hh:mm:ss or s): ")
    output_name = get_output_name()

    # 获取有效的输出路径
    output_path = get_valid_output_path()

    # 调用函数截取视频
    cut_video_ffmpeg(video_path, start_time, end_time, f'{output_path}/{output_name}')
