import subprocess
import os

def change_video_speed(video_path, output_path, speed, keep_pitch):
    # 检查文件是否存在
    if not os.path.isfile(video_path):
        raise FileNotFoundError("输入文件不存在，请检查路径！")

    # 检查输出路径是否有效
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        raise FileNotFoundError("输出路径不存在，请检查路径！")

    try:
        if keep_pitch == 'y':
            # 保持音调：视频变速 (setpts) + 音频保持音调 (atempo 可能需要多次分段)
            command = [
                'ffmpeg',
                '-i', video_path,
                '-vf', f"setpts={1/speed}*PTS",
                '-filter:a', f"atempo={speed}",
                '-y',  # 自动覆盖输出文件
                output_path
            ]
        else:
            # 不保持音调：视频变速 (setpts) + 音频直接变速
            command = [
                'ffmpeg',
                '-i', video_path,
                '-vf', f"setpts={1/speed}*PTS",
                '-af', f"atempo={speed}",
                '-y',  # 自动覆盖输出文件
                output_path
            ]

        # 执行 FFmpeg 命令
        subprocess.run(command, check=True)
        print(f"视频处理完成！已保存到: {output_path}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"处理视频时出错: {e}")
    except Exception as e:
        raise RuntimeError(f"发生错误: {e}")

if __name__ == "__main__":
    # 询问用户输入
    video_path = input("请输入视频文件路径: ").strip()

    try:
        speed = float(input("请输入变速倍率 (大于0): "))
        if speed <= 0:
            raise ValueError("变速倍率必须大于0!")
    except ValueError as e:
        print(e)
        exit(1)

    keep_pitch = input("是否保持音调？(y/n): ").strip().lower()
    if keep_pitch not in ['y', 'n']:
        print("请输入 'y' 或 'n'!")
        exit(1)

    output_path = input("请输入输出文件的完整路径（包括文件名和扩展名）: ").strip()
    if not output_path:
        print("输出路径不能为空！")
        exit(1)

    try:
        change_video_speed(video_path, output_path, speed, keep_pitch)
    except Exception as e:
        print(e)
