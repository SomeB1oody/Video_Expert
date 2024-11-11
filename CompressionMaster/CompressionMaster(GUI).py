import wx
import re
import platform
import subprocess

def is_decimal_format(s: str) -> bool:
    pattern = r"^0\.0*[1-9]\d*$"
    return bool(re.match(pattern, s))

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
            "width": width,
            "height": height,
            "bitrate": bitrate,
            "codec": codec,
            "color_depth": color_depth,
            "color_space": color_space
        }

    except subprocess.CalledProcessError as e:
        raise ValueError(e)

def compress_video(input_file, output_file, scale_factor=None, bitrate=None, codec=None, frame_rate=None,
                   color_depth=None, color_space=None, denoise=False, stabilize=False):
    try:
        video_info = get_video_info(input_file)
    except ValueError as e:
        wx.MessageBox(e, 'Error', wx.OK | wx.ICON_ERROR)
        return

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
            command += ["-c:v", f"{codec}_{codec_process}"]
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
        wx.MessageBox(f'Saved at {output_file}', 'Success', wx.OK | wx.ICON_INFORMATION)
    except subprocess.CalledProcessError as e:
        wx.MessageBox(e, 'Error', wx.OK | wx.ICON_ERROR)
        return

class CompressionMasterWX(wx.Frame):
    def __init__(self, *args, **kw):
        super(CompressionMasterWX, self).__init__(*args, **kw)

        panel = wx.Panel(self)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        # 输入路径
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.file_button = wx.Button(panel, label="Select video")
        self.Bind(wx.EVT_BUTTON, self.on_select_video, self.file_button)
        self.hbox.Add(self.file_button,flag=wx.ALL, border=5)
        self.input_path_text = wx.StaticText(panel, label="Click \"Select video\" first")
        self.hbox.Add(self.input_path_text, flag=wx.ALL, border=5)
        self.vbox.Add(self.hbox, flag=wx.EXPAND)

        # 输出名称
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.name_text = wx.StaticText(panel, label="Output name:")
        self.hbox2.Add(self.name_text, flag=wx.ALL, border=5)
        self.file_name = wx.TextCtrl(panel)
        self.hbox2.Add(self.file_name, flag=wx.ALL, border=5)
        self.vbox.Add(self.hbox2, flag=wx.EXPAND)

        # 输出路径
        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.folder_button = wx.Button(panel, label="Select output folder")
        self.Bind(wx.EVT_BUTTON, self.on_select_folder, self.folder_button)
        self.hbox3.Add(self.folder_button, flag=wx.ALL, border=5)
        self.output_path_text = wx.StaticText(panel, label="Click \"Select output folder\" first")
        self.hbox3.Add(self.output_path_text, flag=wx.ALL, border=5)
        self.vbox.Add(self.hbox3, flag=wx.EXPAND)

        # 码率
        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.bitrate_text = wx.StaticText(panel, label="Bitrate:")
        self.hbox4.Add(self.bitrate_text, flag=wx.ALL, border=5)
        self.bitrate = wx.TextCtrl(panel)
        self.hbox4.Add(self.bitrate, flag=wx.ALL, border=5)
        self.vbox.Add(self.hbox4, flag=wx.EXPAND)

        # 帧率
        self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.fps_text = wx.StaticText(panel, label="fps:")
        self.hbox5.Add(self.fps_text, flag=wx.ALL, border=5)
        self.fps = wx.TextCtrl(panel)
        self.hbox5.Add(self.fps, flag=wx.ALL, border=5)
        self.vbox.Add(self.hbox5, flag=wx.EXPAND)

        # 缩放系数
        self.hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        self.scale_text = wx.StaticText(panel, label="Enter scale factor:")
        self.hbox6.Add(self.scale_text, flag=wx.ALL, border=5)
        self.scale_factor = wx.TextCtrl(panel)
        self.hbox6.Add(self.scale_factor, flag=wx.ALL, border=5)
        self.vbox.Add(self.hbox6, flag=wx.EXPAND)

        # 编码格式
        self.codec = wx.RadioBox(
            panel, label="Codec choice", choices=[
                'Unchanged', 'hevc', 'av1'
            ]
        )
        self.vbox.Add(self.codec, flag=wx.ALL, border=5)

        # 色彩空间
        self.color_space = wx.RadioBox(
            panel, label="Color space choice", choices=[
                'Unchanged', '4:2:2', '4:2:0'
            ]
        )
        self.vbox.Add(self.color_space, flag=wx.ALL, border=5)

        # 色彩深度
        self.color_depth = wx.RadioBox(
            panel, label="Color depth choice", choices=[
                'Unchanged', '8bit', '10bit'
            ]
        )
        self.vbox.Add(self.color_depth, flag=wx.ALL, border=5)

        # 去噪
        self.denoising = wx.RadioBox(
            panel, label="Enable Video Denoising", choices=[
                'No', 'Yes'
            ]
        )
        self.vbox.Add(self.denoising, flag=wx.ALL, border=5)

        # 去抖
        self.stabilization = wx.RadioBox(
            panel, label="Enable Video Stabilization", choices=[
                'No', 'Yes'
            ]
        )
        self.vbox.Add(self.stabilization, flag=wx.ALL, border=5)

        # 压缩按钮
        self.compression_button = wx.Button(panel, label="Start compression")
        self.compression_button.Bind(wx.EVT_BUTTON, self.on_compression)
        self.vbox.Add(self.compression_button, flag=wx.ALL, border=5)

        # 设置面板的布局管理器
        panel.SetSizer(self.vbox)
        panel.Layout()

    def on_select_video(self, event):
        with wx.FileDialog(None, "Select a video", wildcard="所有文件 (*.*)|*.*",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                self.input_path_text.SetLabel(f"{dialog.GetPath()}")
                self.selected_file = dialog.GetPath()

    def on_select_folder(self, event):
        with wx.DirDialog(None, "Select a folder for output", "",
                          style=wx.DD_DEFAULT_STYLE) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                self.output_path_text.SetLabel(f"{dialog.GetPath()}")
                self.selected_folder = dialog.GetPath()

    def on_compression(self, event):
        input_path = self.selected_file
        output_path = self.selected_folder
        output_name = self.file_name.GetValue()
        bitrate = self.bitrate.GetValue()
        fps = self.fps.GetValue()
        scale_factor = self.scale_factor.GetValue()
        codec = self.codec.GetStringSelection()
        color_space = self.color_space.GetStringSelection()
        color_depth = self.color_depth.GetStringSelection()
        denoising = self.denoising.GetStringSelection()
        stabilization = self.stabilization.GetStringSelection()

        if not input_path:
            wx.MessageBox("Please select a video file", "Error", wx.OK | wx.ICON_ERROR)
            return
        if not output_path:
            wx.MessageBox("Please select a folder for output", "Error", wx.OK | wx.ICON_ERROR)
            return
        if not output_name:
            wx.MessageBox("Output name cannot be empty", "Error", wx.OK | wx.ICON_ERROR)
            return

        if not bitrate.isdigit() or bitrate == "0":
            wx.MessageBox("Bitrate should be a number bigger than 0", "Error", wx.OK | wx.ICON_ERROR)
            return
        else:
            bitrate = int(bitrate)

        if not is_decimal_format(scale_factor):
            wx.MessageBox(
                'The scaling factor should be a decimal between 0 and 1',"Error", wx.OK | wx.ICON_ERROR
            )
            return
        else:
            scale_factor = float(scale_factor)

        if not fps.isdigit() or fps == "0":
            wx.MessageBox("FPS should be a number bigger than 0", "Error", wx.OK | wx.ICON_ERROR)
            return
        else:
            fps = int(fps)

        if denoising == "Yes":
            denoising = True
        else:
            denoising = False

        if stabilization == "Yes":
            stabilization = True
        else:
            stabilization = False

        if codec.lower() == "unchanged":
            codec = None
        if color_space.lower() == "unchanged":
            color_space = None
        if color_depth.lower() == "unchanged":
            color_depth = None
        else:
            if color_depth == "8bit":
                color_depth = "8"
            else:
                color_depth = "10"

        try:
            compress_video(
                input_path, f'{output_path}/{output_name}.mp4',
                scale_factor=scale_factor,
                bitrate=bitrate,
                frame_rate=fps,
                codec=codec,
                color_space=color_space,
                color_depth=color_depth,
                denoise=denoising,
                stabilize=stabilization
            )
            wx.MessageBox(
                f'Video saved as {output_path}/{output_name}.mp4',
                'Success' , wx.OK | wx.ICON_INFORMATION
            )
        except Exception as e:
            wx.MessageBox(str(e), "Error", wx.OK | wx.ICON_ERROR)
            return

if __name__ == "__main__":
    app = wx.App()
    frame = CompressionMasterWX(None)
    frame.SetTitle('Compression Master with GUI')
    frame.SetSize((400, 625))
    frame.Show()
    app.MainLoop()