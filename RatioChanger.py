import subprocess

def stretch_video(input_path, aspect_ratio):
    try:
        # 提取宽高比例
        width_ratio, height_ratio = map(float, aspect_ratio.split(":"))
        target_aspect = width_ratio / height_ratio

        # 获取输出路径
        output_path = input_path.rsplit(".", 1)[0] + f"_stretched_{aspect_ratio.replace(':', '_')}.mp4"

        # 使用 ffmpeg 获取原始视频宽高
        probe_command = [
            "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
            "stream=width,height", "-of", "csv=p=0", input_path
        ]
        probe_result = subprocess.run(probe_command, capture_output=True, text=True)
        if probe_result.returncode != 0:
            raise RuntimeError(f"ffprobe Error: {probe_result.stderr.strip()}")

        original_width, original_height = map(int, probe_result.stdout.strip().split(","))
        original_aspect = original_width / original_height

        # 计算新宽高
        if original_aspect > target_aspect:
            new_width = int(original_height * target_aspect)
            new_height = original_height
        else:
            new_width = original_width
            new_height = int(original_width / target_aspect)

        # 构建 ffmpeg 拉伸命令
        ffmpeg_command = [
            "ffmpeg", "-i", input_path, "-vf",
            f"scale={new_width}:{new_height}", "-c:v", "libx264", "-crf", "23",
            "-preset", "medium", output_path
        ]

        # 执行 ffmpeg 命令
        subprocess.run(ffmpeg_command, check=True)
        print(f"File saved as: {output_path}")

    except Exception as e:
        print(f"Error: {e}")

def crop_video(input_path, aspect_ratio):
    try:
        # 提取宽高比例
        width_ratio, height_ratio = map(float, aspect_ratio.split(":"))
        target_aspect = width_ratio / height_ratio

        # 获取输出路径
        output_path = input_path.rsplit(".", 1)[0] + f"_cropped_{aspect_ratio.replace(':', '_')}.mp4"

        # 使用 ffmpeg 获取原始视频宽高
        probe_command = [
            "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
            "stream=width,height", "-of", "csv=p=0", input_path
        ]
        probe_result = subprocess.run(probe_command, capture_output=True, text=True)
        if probe_result.returncode != 0:
            raise RuntimeError(f"ffprobe 错误：{probe_result.stderr.strip()}")

        original_width, original_height = map(int, probe_result.stdout.strip().split(","))
        original_aspect = original_width / original_height

        # 计算裁剪区域
        if original_aspect > target_aspect:  # 宽度过长，需要裁剪左右
            new_width = int(original_height * target_aspect)
            new_height = original_height
            crop_x = (original_width - new_width) // 2
            crop_y = 0
        else:  # 高度过长，需要裁剪上下
            new_width = original_width
            new_height = int(original_width / target_aspect)
            crop_x = 0
            crop_y = (original_height - new_height) // 2

        # 构建 ffmpeg 裁剪命令
        ffmpeg_command = [
            "ffmpeg", "-i", input_path, "-vf",
            f"crop={new_width}:{new_height}:{crop_x}:{crop_y}", "-c:v", "libx264", "-crf", "23",
            "-preset", "medium", output_path
        ]

        # 执行 ffmpeg 命令
        subprocess.run(ffmpeg_command, check=True)
        print(f"File saved as: {output_path}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # 用户输入
    input_video_path = input("Enter input path").strip()
    desired_aspect_ratio = input("Please enter the desired video ratio (format a:b, e.g. 16:9) :").strip()
    action = input("Please choose processing type：stretch or crop:").strip().lower()

    if action == "stretch":
        stretch_video(input_video_path, desired_aspect_ratio)
    elif action == "crop":
        crop_video(input_video_path, desired_aspect_ratio)
    else:
        print("Invalid input，Enter 'stretch' or 'crop'")