import subprocess
import os
import re
import wx

def video_to_gif(video_path, start_time, end_time, output_path):
    command = [
        'ffmpeg',
        '-ss', start_time,      # 设置开始时间
        '-to', end_time,        # 设置结束时间
        '-i', video_path,       # 输入视频文件
        '-vf', 'fps=10,scale=320:-1:flags=lanczos',  # 控制帧率和大小
        '-gifflags', '+transdiff',  # 优化GIF的平滑过渡
        '-y',                    # 覆盖输出文件（如果已经存在）
        output_path
    ]

    try:
        subprocess.run(command, check=True)
        print(f"GIF已成功创建在：{output_path}")
    except subprocess.CalledProcessError as e:
        print(f"转换失败：{e}")
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
    # 获取有效的输入视频文件路径
    video_path = get_valid_file_path()

    # 获取截取视频的开始时间和结束时间，确保时间格式正确
    start_time = get_valid_time_input("Start time (format: hh:mm:ss or s): ")
    end_time = get_valid_time_input("End time (format: hh:mm:ss or s): ")

    # 获取有效的输出路径
    output_path = get_valid_output_path()
    video_to_gif(video_path, start_time, end_time, output_path)