import subprocess

# 定义一个函数来调用 ffmpeg 截取视频片段
def cut_video_ffmpeg(video_path, start_time, end_time, output_path):
    try:
        ffmpeg_command = [
            'ffmpeg',
            '-i', video_path,          # 输入视频文件
            '-ss', str(start_time),     # 起始时间
            '-to', str(end_time),       # 终止时间
            '-c', 'copy',               # 不重新编码，直接截取
            output_path                 # 输出文件路径
        ]

        # 调用 ffmpeg 命令
        subprocess.run(ffmpeg_command, check=True)
        print(f"Saved as: {output_path}")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

# 获取用户输入
if __name__ == "__main__":
    video_path = input("Input path: ")
    start_time = input("Start:（format：hh:mm:ss or s）: ")
    end_time = input("End:（格式：hh:mm:ss or s）: ")
    output_path = input("output path: ")

    # 调用函数截取视频
    cut_video_ffmpeg(video_path, start_time, end_time, output_path)