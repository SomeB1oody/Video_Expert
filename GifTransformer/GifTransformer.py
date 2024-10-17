import subprocess
import os
import re

def calculate_seconds_difference(start_time: str, end_time: str) -> str:
    def time_to_seconds(time_str: str) -> int:
        # 如果是 hh:mm:ss 格式，按原逻辑转换为秒
        if ":" in time_str:
            h, m, s = map(int, time_str.split(":"))
            return h * 3600 + m * 60 + s
        else:
            # 如果是纯秒数，直接转换为整数
            return int(time_str)

    # 将开始时间和结束时间转换为秒数
    start_total_seconds = time_to_seconds(start_time)
    end_total_seconds = time_to_seconds(end_time)

    # 返回时间差，单位为秒
    return str(end_total_seconds - start_total_seconds)

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

        # 调用函数转换视频为GIF
        video_to_gif(video_path, start_time, end_time, output_path)
