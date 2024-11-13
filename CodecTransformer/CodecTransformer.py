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

def encode_video(input_file, output_file, codec, file_extension, start_time=0):
    # 自动添加文件扩展名到输出文件
    output_file_with_extension = f"{output_file}.{file_extension}"

    # 基本的FFmpeg命令
    ffmpeg_command = ['ffmpeg', '-i', input_file]

    # 根据检测到的硬件加速类型设置相应的编码器
    codec_process = auto_encode(codec)
    if codec_process != 'cpu':
        ffmpeg_command.extend(['-c:v', f'{codec}_{codec_process}'])
    else:
        ffmpeg_command.extend(['-c:v', codec])

    # 如果指定了开始时间，则添加此选项
    if start_time > 0:
        ffmpeg_command.extend(['-ss', str(start_time)])

    # 添加输出文件路径（包含自动添加的扩展名）
    ffmpeg_command.append(output_file_with_extension)

    # 打印并运行FFmpeg命令
    print("Running:", ' '.join(ffmpeg_command))
    subprocess.run(ffmpeg_command)

if __name__ == "__main__":
    # 获取输入文件路径、输出文件基本名称、编码器和文件扩展名
    input_file = input("Enter the path to the input video file: ").strip()
    output_file = input("Enter the base name for the output file (without extension): ").strip()
    codec = input("Enter the desired video codec (h264, hevc, vp8, vp9, av1, prores): ").strip().lower()
    file_extension = input("Enter the desired file extension (mp4, mov, mkv, webm): ").strip().lower()
    start_time = int(input("Enter the start time in seconds (default is 0): ").strip() or "0")

    # 调用编码函数进行视频编码
    encode_video(input_file, output_file, codec, file_extension, start_time)
