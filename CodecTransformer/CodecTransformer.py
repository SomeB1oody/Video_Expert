import platform
import subprocess

def detect_hardware_encoding():
    # 检测可用的硬件加速单元
    system_platform = platform.system()
    supported_encoders = []
    av1_support = []
    prores_support = []

    # 根据平台检查可用的编码器
    if system_platform in ['Windows', 'Linux']:
        # 运行FFmpeg命令以列出可用的编码器
        ffmpeg_output = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True)

        # 检查NVIDIA NVENC支持
        if "h264_nvenc" in ffmpeg_output.stdout or "hevc_nvenc" in ffmpeg_output.stdout:
            supported_encoders.append('nvenc')
            if "av1_nvenc" in ffmpeg_output.stdout:
                av1_support.append('nvenc')
            if "prores_nvenc" in ffmpeg_output.stdout:
                prores_support.append('nvenc')
        # 检查Intel QSV支持
        if "h264_qsv" in ffmpeg_output.stdout or "hevc_qsv" in ffmpeg_output.stdout:
            supported_encoders.append('qsv')
            if "av1_qsv" in ffmpeg_output.stdout:
                av1_support.append('qsv')
            if "prores_qsv" in ffmpeg_output.stdout:
                prores_support.append('qsv')
        # 检查AMD AMF支持
        if "h264_amf" in ffmpeg_output.stdout or "hevc_amf" in ffmpeg_output.stdout:
            supported_encoders.append('amf')
            if "av1_amf" in ffmpeg_output.stdout:
                av1_support.append('amf')
            if "prores_amf" in ffmpeg_output.stdout:
                prores_support.append('amf')

    elif system_platform == 'Darwin':  # macOS 平台
        # 检查VideoToolbox支持
        ffmpeg_output = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True)
        if "h264_videotoolbox" in ffmpeg_output.stdout or "hevc_videotoolbox" in ffmpeg_output.stdout:
            supported_encoders.append('videotoolbox')
            if 'av1_videotoolbox' in ffmpeg_output.stdout:
                av1_support.append('videotoolbox')
            if 'prores_videotoolbox' in ffmpeg_output.stdout:
                prores_support.append('videotoolbox')

    return supported_encoders, av1_support, prores_support

def check_hardware_encoding():
    # 检测硬件加速单元
    available_encoders, _, _ = detect_hardware_encoding()

    # 如果没有检测到硬件加速单元，则返回'cpu'并使用CPU编码
    if not available_encoders:
        print("No hardware acceleration unit detected. Encoding will be performed using the CPU.")
        return 'cpu'

    # 提示用户是否希望使用检测到的硬件加速单元
    use_hw_acceleration = input(
        f"Hardware acceleration unit(s) detected: {', '.join(available_encoders)}. Use them? (yes/no): "
    ).strip().lower()

    # 如果用户选择使用硬件加速，则返回第一个可用的加速类型
    if use_hw_acceleration == 'yes':
        return available_encoders[0]

    # 如果用户选择不使用硬件加速，则使用CPU编码
    print("User chose not to use hardware acceleration; encoding will use the CPU.")
    return 'cpu'

def encode_video(input_file, output_file, codec, file_extension, start_time=0):
    # 检查是否有可用的硬件加速类型
    hardware_type, av1_support, prores_support = check_hardware_encoding()

    # 自动添加文件扩展名到输出文件
    output_file_with_extension = f"{output_file}.{file_extension}"

    # 基本的FFmpeg命令
    ffmpeg_command = ['ffmpeg', '-i', input_file]

    # 根据检测到的硬件加速类型设置相应的编码器
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
        # 如果没有可用的硬件加速类型，则使用CPU编码
        if codec in ['h264', 'h265', 'vp8', 'vp9', 'av1', 'prores']:
            if codec == 'av1':
                if av1_support:
                    ffmpeg_command.extend(['-c:v', f'av1_{av1_support[0]}'])
                else:
                    ffmpeg_command.extend(['-c:v', 'av1'])
            elif codec == 'prores':
                if prores_support:
                    ffmpeg_command.extend(['-c:v', f'prores_{prores_support[0]}'])
                else:
                    ffmpeg_command.extend(['-c:v', 'prores'])
            else:
                ffmpeg_command.extend(['-c:v', codec])
        else:
            print(f"Unsupported codec: {codec}. Using default H.264 CPU encoding.")
            ffmpeg_command.extend(['-c:v', 'h264'])

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
    codec = input("Enter the desired video codec (h264, h265, vp8, vp9, av1, prores): ").strip().lower()
    file_extension = input("Enter the desired file extension (mp4, mov, mkv, webm): ").strip().lower()
    start_time = int(input("Enter the start time in seconds (default is 0): ").strip() or "0")

    # 调用编码函数进行视频编码
    encode_video(input_file, output_file, codec, file_extension, start_time)
