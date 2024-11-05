import platform
import subprocess

def detect_hardware_encoding():
    # 检测可用的硬件加速单元
    system_platform = platform.system()
    supported_encoders = []

    # 根据平台检查可用的编码器
    if system_platform in ['Windows', 'Linux']:
        # 运行FFmpeg命令以列出可用的编码器
        ffmpeg_output = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True)

        # 检查NVIDIA NVENC支持
        if "h264_nvenc" in ffmpeg_output.stdout or "hevc_nvenc" in ffmpeg_output.stdout:
            supported_encoders.append('nvenc')
        # 检查Intel QSV支持
        if "h264_qsv" in ffmpeg_output.stdout or "hevc_qsv" in ffmpeg_output.stdout:
            supported_encoders.append('qsv')
        # 检查AMD AMF支持
        if "h264_amf" in ffmpeg_output.stdout or "hevc_amf" in ffmpeg_output.stdout:
            supported_encoders.append('amf')

    elif system_platform == 'Darwin':  # macOS 平台
        # 检查VideoToolbox支持
        ffmpeg_output = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True)
        if "h264_videotoolbox" in ffmpeg_output.stdout or "hevc_videotoolbox" in ffmpeg_output.stdout:
            supported_encoders.append('videotoolbox')

    return supported_encoders

def check_hardware_encoding():
    # 检测硬件加速单元
    available_encoders = detect_hardware_encoding()

    if not available_encoders:
        print("No hardware acceleration unit detected. Encoding will be performed using the CPU.")
        return 'cpu'

    use_hw_acceleration = input(
        f"Hardware acceleration unit(s) detected: {', '.join(available_encoders)}. Use them? (yes/no): "
    ).strip().lower()

    if use_hw_acceleration == 'yes':
        return available_encoders[0]

    print("User chose not to use hardware acceleration; encoding will use the CPU.")
    return 'cpu'

def encode_video(input_file, output_file, codec, start_time=0):
    hardware_type = check_hardware_encoding()

    # 基本的FFmpeg命令
    ffmpeg_command = ['ffmpeg', '-i', input_file]

    # 添加硬件加速选项
    if hardware_type == 'nvenc':
        if codec in ['h264', 'h265']:
            ffmpeg_command.extend(['-c:v', f'{codec}_nvenc'])
        else:
            print(f"Unsupported codec for NVENC. Using CPU encoding for {codec}.")
            ffmpeg_command.extend(['-c:v', codec])

    elif hardware_type == 'qsv':
        if codec in ['h264', 'h265']:
            ffmpeg_command.extend(['-c:v', f'{codec}_qsv'])
        else:
            print(f"Unsupported codec for QSV. Using CPU encoding for {codec}.")
            ffmpeg_command.extend(['-c:v', codec])

    elif hardware_type == 'amf':
        if codec in ['h264', 'h265']:
            ffmpeg_command.extend(['-c:v', f'{codec}_amf'])
        else:
            print(f"Unsupported codec for AMF. Using CPU encoding for {codec}.")
            ffmpeg_command.extend(['-c:v', codec])

    elif hardware_type == 'videotoolbox':
        if codec in ['h264', 'h265']:
            ffmpeg_command.extend(['-c:v', f'{codec}_videotoolbox'])
        else:
            print(f"Unsupported codec for VideoToolbox. Using CPU encoding for {codec}.")
            ffmpeg_command.extend(['-c:v', codec])

    else:
        # 默认使用CPU进行编码
        if codec in ['h264', 'h265', 'vp8', 'vp9', 'av1', 'prores']:
            ffmpeg_command.extend(['-c:v', codec])
        else:
            print(f"Unsupported codec: {codec}. Using default H.264 CPU encoding.")
            ffmpeg_command.extend(['-c:v', 'h264'])

    # 如果指定了开始时间，则添加此选项
    if start_time > 0:
        ffmpeg_command.extend(['-ss', str(start_time)])

    # 添加输出文件路径
    ffmpeg_command.append(output_file)

    # 打印并运行FFmpeg命令
    print("Running:", ' '.join(ffmpeg_command))
    subprocess.run(ffmpeg_command)

if __name__ == "__main__":
    input_file = input("Enter the path to the input video file: ").strip()
    output_file = input("Enter the path for the output video file: ").strip()
    codec = input("Enter the desired video codec (h264, h265, vp8, vp9, av1, prores): ").strip().lower()
    start_time = int(input("Enter the start time in seconds (default is 0): ").strip() or "0")

    encode_video(input_file, output_file, codec, start_time)
