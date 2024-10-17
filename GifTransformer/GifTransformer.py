import subprocess
import os
import re

def remove_trailing_slash(path: str) -> str:
    if path.endswith('/'):
        return path[:-1]
    return path

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

def video_to_gif(video_path, start_time=None, end_time=None, output_path=None):
    command = ['ffmpeg']  # 初始命令部分

    # 如果有 start_time，则添加 -ss 参数
    if start_time:
        command.extend(['-ss', str(start_time)])

    # 添加输入文件路径
    command.extend(['-i', video_path])

    # 如果有 end_time，则计算时间差并添加 -t 参数
    if end_time:
        command.extend(
            ['-t', calculate_seconds_difference(str(start_time) if start_time else "00:00:00", str(end_time))]
        )

    # 添加 GIF 转换的选项
    command.extend([
        '-vf',
        'fps=10,scale=320:-1:flags=lanczos',  # 控制帧率和大小
        '-gifflags',
        '+transdiff',  # 优化GIF的平滑过渡
        '-y',  # 覆盖输出文件
        output_path
    ])

    try:
        subprocess.run(command, check=True)
        print(f"GIF is successfully created at：{output_path}")
    except subprocess.CalledProcessError as e:
        print(f"fail to transform：{e}")

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

    return False

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
        if os.path.exists(output_path):
            return output_path
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

def get_valid_name_input():
    while True:
        output_name = input("Output name: ")
        if is_valid_windows_filename(output_path):
            return output_name
        else:
            print(f"\tOutput name: {output_path} is invalid. Please try again.\t")

# 用户输入示例
if __name__ == "__main__":
    while True:
        # 获取有效的输入视频文件路径
        video_path = get_valid_file_path()

        # 询问用户是否需要裁剪
        crop_choice = input("Do you want to crop the video before converting to GIF? (yes/no): ").strip().lower()

        # 如果用户选择裁剪，则获取截取视频的开始时间和结束时间，确保时间格式正确
        if crop_choice == 'yes':
            start_time = get_valid_time_input("Start time (format: hh:mm:ss or s): ")
            end_time = get_valid_time_input("End time (format: hh:mm:ss or s): ")
        else:
            start_time = None
            end_time = None

        # 获取有效的输出路径
        output_path = get_valid_output_path()
        output_name = get_valid_name_input()

        output_path = remove_trailing_slash(output_path)

        output_path_ = f'{output_path}/{output_name}.gif'

        # 调用函数转换视频为GIF
        video_to_gif(video_path, start_time, end_time, output_path)
