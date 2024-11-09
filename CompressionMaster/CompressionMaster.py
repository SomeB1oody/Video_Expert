import subprocess
import re

def get_video_info(video_path):
    # 使用 ffprobe 命令来获取视频的详细信息
    command = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,bit_rate,codec_name,pix_fmt",
        "-of", "default=noprint_wrappers=1", video_path
    ]

    try:
        # 运行命令并捕获输出
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = result.stdout

        # 提取码率、分辨率、编码格式、色彩位深和色彩空间
        width = int(re.search(r"width=(\d+)", output).group(1))
        height = int(re.search(r"height=(\d+)", output).group(1))
        bitrate = int(re.search(r"bit_rate=(\d+)", output).group(1)) if re.search(r"bit_rate=(\d+)", output) else None
        codec = re.search(r"codec_name=([\w\d]+)", output).group(1)
        pix_fmt = re.search(r"pix_fmt=([\w\d]+)", output).group(1)

        # 解析色彩位深和色彩空间
        color_depth_match = re.search(r"yuv(\d+)p(\d+)", pix_fmt)
        color_depth = color_depth_match.group(1) if color_depth_match else "unknown"
        color_space = f"{color_depth_match.group(2)[0]}:{color_depth_match.group(2)[1]}" if color_depth_match else "unknown"

        return {
            "resolution": f"{width}x{height}",
            "bitrate": bitrate,
            "codec": codec,
            "color_depth": color_depth,
            "color_space": color_space
        }

    except subprocess.CalledProcessError as e:
        print("无法获取视频信息:", e)
        return None

def compress_video(input_file, output_file, scale_factor=None, bitrate=None, codec=None, frame_rate=None,
                   color_depth=None, color_space=None, denoise=False, stabilize=False):
    video_info = get_video_info(input_file)

    # 基础 FFmpeg 命令
    command = ["ffmpeg", "-i", input_file]

    # 获取原始分辨率
    if scale_factor:
        width, height = video_info["width"], video_info["height"]
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        command += ["-vf", f"scale={new_width}:{new_height}"]

    # 设置码率
    if bitrate:
        command += ["-b:v", bitrate]

    # 设置编码格式
    if codec:
        command += ["-c:v", codec]

    # 设置帧率
    if frame_rate:
        command += ["-r", str(frame_rate)]

    # 设置色深和色彩空间
    if color_depth or color_space:
        if color_depth and color_space:
            command += ["-pix_fmt", f"yuv{color_space.replace(':', '')}p{color_depth}le"]
        else:
            if color_depth:
                command += ["-pix_fmt", f"yuv{video_info['color_space'].replace(':', '')}p{color_depth}le"]
            else:
                command += ["-pix_fmt", f"yuv{color_space.replace(':', '')}p{video_info['color_depth']}le"]

    # 添加去噪和去抖
    if denoise:
        command += ["-vf", "hqdn3d=1.5:1.5:6.0:6.0"]
    if stabilize:
        command += ["-vf", "deshake"]

    # 输出文件设置
    command += [output_file]

    # 执行命令
    try:
        subprocess.run(command, check=True)
        print("视频压缩完成！")
    except subprocess.CalledProcessError as e:
        print("视频压缩失败:", e)

# 获取用户输入
input_file = input("请输入源视频文件路径：")
output_file = input("请输入输出视频文件路径：")

# 分辨率
resolution = input("请输入分辨率缩放系数：")
resolution = resolution if resolution else None

# 码率
bitrate = input("请输入目标码率 (例如 1000k，直接按回车跳过)：")
bitrate = bitrate if bitrate else None

# 编码格式
print("选择编码格式：1. H.265 (libx265)  2. AV1 (libaom-av1)  3. H.264 (libx264)")
codec_choice = input("请输入编码格式选项 (1/2/3)：")
codec = {"1": "libx265", "2": "libaom-av1", "3": "libx264"}.get(codec_choice, "libx265")

# 帧率
frame_rate = input("请输入目标帧率 (例如 24，直接按回车跳过)：")
frame_rate = int(frame_rate) if frame_rate else None

# 色深和色彩空间
print("选择色深：1. 8-bit  2. 10-bit")
color_depth_choice = input("请输入色深选项 (1/2)：")
color_depth = "10" if color_depth_choice == "2" else "8"

print("选择色彩空间：1. 4:2:0  2. 4:2:2")
color_space_choice = input("请输入色彩空间选项 (1/2)：")
color_space = "4:2:2" if color_space_choice == "2" else "4:2:0"

# 去噪和去抖
denoise = input("是否启用去噪？(y/n)：").lower() == "y"
stabilize = input("是否启用去抖？(y/n)：").lower() == "y"

# 调用视频压缩函数
compress_video(
    input_file, output_file, resolution, bitrate, codec, frame_rate, color_depth, color_space, denoise, stabilize
)
