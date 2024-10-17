import subprocess
import os
import re

def remove_trailing_backslash(path: str) -> str:
    # 如果路径以反斜杠结尾，去掉它
    if path.endswith('\\'):
        return path[:-1]
    return path

def calculate_seconds_difference(start_time: str, end_time: str) -> str:
    def time_to_seconds(time_str: str) -> float:
        # 如果是 hh:mm:ss 或者 hh:mm:ss.sss 格式，按原逻辑转换为秒
        if ":" in time_str:
            parts = time_str.split(":")
            h = int(parts[0])
            m = int(parts[1])
            s = float(parts[2])  # 支持秒部分为小数
            return h * 3600 + m * 60 + s
        else:
            # 如果是纯秒数，直接转换为浮点数
            return float(time_str)

    # 将开始时间和结束时间转换为秒数
    start_total_seconds = time_to_seconds(start_time)
    end_total_seconds = time_to_seconds(end_time)

    # 返回时间差，保留小数点后两位
    return "{:.2f}".format(end_total_seconds - start_total_seconds)

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
        print("\tSuccess!\t\t\t\t")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

def is_valid_time_format(time_str):
    # 正则表达式匹配 hh:mm:ss 格式（支持秒部分带小数）
    hhmmss_pattern = r'^\d{1,2}:\d{2}:\d{2}(\.\d+)?$'
    # 正则表达式匹配纯秒数（只支持整数）
    integer_seconds_pattern = r'^\d+$'
    # 正则表达式匹配纯秒数（支持带小数）
    float_seconds_pattern = r'^\d+\.\d+$'

    # 验证是否符合任意一种格式
    if re.match(hhmmss_pattern, time_str): return True
    if re.match(integer_seconds_pattern, time_str): return True
    if re.match(float_seconds_pattern, time_str): return True

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
    while True:
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
