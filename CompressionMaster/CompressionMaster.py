import re
import platform
import subprocess

def auto_encode(selected_codec):
    # 检测可用的硬件加速单元
    system_platform = platform.system()
    h264_support = []
    hevc_support = []
    vp8_support = []
    vp9_support = []
    av1_support = []
    prores_support = []

    # 运行FFmpeg命令以列出可用的编码器
    ffmpeg_output = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True)
    # 根据平台检查可用的编码器
    if system_platform in ['Windows', 'Linux']:

        # 检查NVIDIA NVENC支持
        if "h264_nvenc" in ffmpeg_output.stdout:
            h264_support.append('nvenc')
        if "hevc_nvenc" in ffmpeg_output.stdout:
            hevc_support.append('nvenc')
        if "av1_nvenc" in ffmpeg_output.stdout:
            av1_support.append('nvenc')
        if "prores_nvenc" in ffmpeg_output.stdout:
            prores_support.append('nvenc')
        if "vp8_nvenc" in ffmpeg_output.stdout:
            vp8_support.append('nvenc')
        if "vp9_nvenc" in ffmpeg_output.stdout:
            vp9_support.append('nvenc')

        # 检查Intel QSV支持
        if "h264_qsv" in ffmpeg_output.stdout:
            h264_support.append('qsv')
        if "hevc_qsv" in ffmpeg_output.stdout:
            hevc_support.append('qsv')
        if "av1_qsv" in ffmpeg_output.stdout:
            av1_support.append('qsv')
        if "prores_qsv" in ffmpeg_output.stdout:
            prores_support.append('qsv')
        if "vp8_qsv" in ffmpeg_output.stdout:
            vp8_support.append('qsv')
        if "vp9_qsv" in ffmpeg_output.stdout:
            vp9_support.append('qsv')

        # 检查AMD AMF支持
        if "h264_amf" in ffmpeg_output.stdout:
            h264_support.append('amf')
        if "hevc_amf" in ffmpeg_output.stdout:
            hevc_support.append('amf')
        if "av1_amf" in ffmpeg_output.stdout:
            av1_support.append('amf')
        if "prores_amf" in ffmpeg_output.stdout:
            prores_support.append('amf')
        if "vp8_amf" in ffmpeg_output.stdout:
            vp8_support.append('amf')
        if "vp9_amf" in ffmpeg_output.stdout:
            vp9_support.append('amf')

    elif system_platform == 'Darwin':  # macOS 平台
        if "h264_videotoolbox" in ffmpeg_output.stdout:
            h264_support.append('videotoolbox')
        if "hevc_videotoolbox" in ffmpeg_output.stdout:
            hevc_support.append('videotoolbox')
        if 'prores_videotoolbox' in ffmpeg_output.stdout:
            prores_support.append('videotoolbox')
        if 'av1_videotoolbox' in ffmpeg_output.stdout:
            av1_support.append('videotoolbox')
        if 'vp8_videotoolbox' in ffmpeg_output.stdout:
            vp8_support.append('videotoolbox')
        if 'vp9_videotoolbox' in ffmpeg_output.stdout:
            vp9_support.append('videotoolbox')

    if selected_codec == 'h264':
        if h264_support:
            return h264_support[0]
        else:
            return 'cpu'
    elif selected_codec == 'hevc':
        if hevc_support:
            return hevc_support[0]
        else:
            return 'cpu'
    elif selected_codec == 'av1':
        if av1_support:
            return av1_support[0]
        else:
            return 'cpu'
    elif selected_codec == 'prores':
        if prores_support:
            return prores_support[0]
        else:
            return 'cpu'
    elif selected_codec == 'vp8':
        if vp8_support:
            return vp8_support[0]
        else:
            return 'cpu'
    elif selected_codec == 'vp9':
        if vp9_support:
            return vp9_support[0]
        else:
            return 'cpu'
    else:
        return 'cpu'

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
        print("Cannot get video info:", e)
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
        codec_process = auto_encode(codec)
        if codec_process != 'cpu':
            command += ["-c:v", f'{codec}_{codec_process}']
        else:
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
        print("Compression complete")
    except subprocess.CalledProcessError as e:
        print("Fail to compress:", e)

# 获取用户输入
input_file = input("Please enter video path")
output_file = input("please enter a path for output")

# 分辨率
resolution = input("Please enter the resolution scaling factor:")
resolution = resolution if resolution else None

# 码率
bitrate = input("Enter bitrate")
bitrate = bitrate if bitrate else None

# 编码格式
print("Choose an encode mode: 1.H.265 2.AV1  3.H.264")
codec_choice = input("Please choose (1/2/3)：")
codec = {"1": "hevc", "2": "av1", "3": "h264"}.get(codec_choice, "hevc")

# 帧率
frame_rate = input("Please enter the target frame rate (for example, 24, press Enter to skip) :")
frame_rate = int(frame_rate) if frame_rate else None

# 色深和色彩空间
print("Choose a color depth: 1. 8-bit  2. 10-bit")
color_depth_choice = input("Please choose (1/2)：")
color_depth = "10" if color_depth_choice == "2" else "8"

print("choose a color space: 1. 4:2:0  2. 4:2:2")
color_space_choice = input("Please choose (1/2)：")
color_space = "4:2:2" if color_space_choice == "2" else "4:2:0"

# 去噪和去抖
denoise = input("If enable Video Denoising(y/n)：").lower() == "y"
stabilize = input("If enable Video Stabilization(y/n)：").lower() == "y"

# 调用视频压缩函数
compress_video(
    input_file, output_file, resolution, bitrate, codec, frame_rate, color_depth, color_space, denoise, stabilize
)
