import subprocess
import re
import os
import wx

def get_video_info(file_path):
    # 使用FFmpeg命令获取视频信息
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", file_path,
        "-hide_banner"
    ]

    try:
        # 执行命令并捕获输出
        result = subprocess.run(ffmpeg_cmd, stderr=subprocess.PIPE, text=True)
        ffmpeg_output = result.stderr
    except Exception as e:
        print(f"Failed to execute FFmpeg: {e}")
        return None

    # 初始化信息变量
    width = height = bitrate = codec = color_depth = color_space = frame_rate = duration = None
    audio_codec = sample_rate = channels = None

    # 解析FFmpeg输出
    # 获取视频分辨率
    resolution_match = re.search(r"(\d{2,5})x(\d{2,5})", ffmpeg_output)
    if resolution_match:
        width, height = resolution_match.groups()

    # 获取视频编码格式
    codec_match = re.search(r"Video:\s(\w+)", ffmpeg_output)
    if codec_match:
        codec = codec_match.group(1)

    # 获取色彩深度
    color_depth_match = re.search(r"(\d{1,2})\s?bits", ffmpeg_output)
    if color_depth_match:
        color_depth = color_depth_match.group(1) + " bit"

    # 获取色彩空间
    color_space_match = re.search(r"(yuv\w+|rgb\w+)", ffmpeg_output)
    if color_space_match:
        color_space = color_space_match.group(1)

    # 获取比特率
    bitrate_match = re.search(r"bitrate:\s(\d+)\s?kb/s", ffmpeg_output)
    if bitrate_match:
        bitrate = int(bitrate_match.group(1)) * 1000

    # 获取帧率
    frame_rate_match = re.search(r"(\d+(?:\.\d+)?)\s?fps", ffmpeg_output)
    if frame_rate_match:
        frame_rate = float(frame_rate_match.group(1))

    # 获取视频时长
    duration_match = re.search(r"Duration:\s(\d+):(\d+):(\d+\.\d+)", ffmpeg_output)
    if duration_match:
        hours, minutes, seconds = map(float, duration_match.groups())
        duration = hours * 3600 + minutes * 60 + seconds

    # 获取音频信息
    audio_codec_match = re.search(r"Audio:\s(\w+)", ffmpeg_output)
    if audio_codec_match:
        audio_codec = audio_codec_match.group(1)

    # 获取音频采样率
    sample_rate_match = re.search(r"(\d+)\s?Hz", ffmpeg_output)
    if sample_rate_match:
        sample_rate = int(sample_rate_match.group(1))

    # 获取音频声道数
    channels_match = re.search(r",\s(stereo|mono|5\.1)", ffmpeg_output)
    if channels_match:
        channels = channels_match.group(1)

    # 获取文件大小
    file_size = os.path.getsize(file_path)

    # 创建视频信息字典
    video_info = {
        "resolution": f"{width}x{height}" if width and height else "Unknown",
        "bitrate": f"{bitrate / 1000:.2f} kbps" if bitrate else "Unknown",
        "video_codec": codec,
        "color_depth": color_depth if color_depth else "Unknown",
        "color_space": color_space if color_space else "Unknown",
        "frame_rate": f"{frame_rate:.2f} fps" if frame_rate else "Unknown",
        "duration": f"{duration:.2f} seconds" if duration else "Unknown",
        "file_size": f"{file_size / (1024**2):.2f} MB" if file_size else "Unknown",
        "audio_codec": audio_codec if audio_codec else "Unknown",
        "sample_rate": f"{sample_rate / 1000:.1f} kHz" if sample_rate else "Unknown",
        "channels": channels if channels else "Unknown"
    }

    return video_info

class InfoGetterWX(wx.Frame):
    def __init__(self, *args, **kw):
        super(InfoGetterWX, self).__init__(*args, **kw)

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

        # 获取按钮
        self.get_button = wx.Button(panel, label="Get")
        self.get_button.Bind(wx.EVT_BUTTON, self.on_get)
        self.vbox.Add(self.get_button, flag=wx.ALL, border=5)

        # 分辨率
        self.resolution_text = wx.StaticText(panel, label="Resolution:")
        self.vbox.Add(self.resolution_text, flag=wx.ALL, border=5)

        # 码率
        self.bitrate_text = wx.StaticText(panel, label="Bitrate:")
        self.vbox.Add(self.bitrate_text, flag=wx.ALL, border=5)

        # 编码格式
        self.codec_text = wx.StaticText(panel, label="Codec:")
        self.vbox.Add(self.codec_text, flag=wx.ALL, border=5)

        # 色深
        self.color_depth_text = wx.StaticText(panel, label="Color depth:")
        self.vbox.Add(self.color_depth_text, flag=wx.ALL, border=5)

        # 色彩空间
        self.color_space_text = wx.StaticText(panel, label="Color space:")
        self.vbox.Add(self.color_space_text, flag=wx.ALL, border=5)

        # 帧率
        self.frame_rate_text = wx.StaticText(panel, label="Frame rate:")
        self.vbox.Add(self.frame_rate_text, flag=wx.ALL, border=5)

        # 时长
        self.duration_text = wx.StaticText(panel, label="Duration:")
        self.vbox.Add(self.duration_text, flag=wx.ALL, border=5)

        # 文件大小
        self.file_size_text = wx.StaticText(panel, label="File size:")
        self.vbox.Add(self.file_size_text, flag=wx.ALL, border=5)

        # 音频编码格式
        self.audio_codec_text = wx.StaticText(panel, label="Audio codec:")
        self.vbox.Add(self.audio_codec_text, flag=wx.ALL, border=5)

        # 音频采样率
        self.sample_rate_text = wx.StaticText(panel, label="Sample rate:")
        self.vbox.Add(self.sample_rate_text, flag=wx.ALL, border=5)

        # 声道
        self.channels_text = wx.StaticText(panel, label="Channels:")
        self.vbox.Add(self.channels_text, flag=wx.ALL, border=5)

        # 设置面板的布局管理器
        panel.SetSizer(self.vbox)
        panel.Layout()

    def on_select_video(self, event):
        with wx.FileDialog(None, "Select a video", wildcard="所有文件 (*.*)|*.*",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                self.input_path_text.SetLabel(f"{dialog.GetPath()}")
                self.selected_file = dialog.GetPath()

    def on_get(self, event):
        video_path = self.selected_file

        if not video_path:
            wx.MessageBox('Please select a video file first', 'Error', wx.OK | wx.ICON_ERROR)
            return

        try:
            video_info = get_video_info(video_path)
            wx.MessageBox("Successfully get video info", "Success", wx.OK | wx.ICON_INFORMATION)
        except ValueError as e:
            wx.MessageBox(str(e), "Error", wx.OK | wx.ICON_ERROR)
            return

        self.resolution_text.SetLabel(f'Resolution: {video_info["resolution"]}')
        self.bitrate_text.SetLabel(f'Bitrate: {video_info["bitrate"]}')
        self.codec_text.SetLabel(f'Codec: {video_info["video_codec"]}')
        self.color_depth_text.SetLabel(f'Color depth: {video_info["color_depth"]}')
        self.color_space_text.SetLabel(f'Color space: {video_info["color_space"]}')
        self.frame_rate_text.SetLabel(f'Frame rate: {video_info["frame_rate"]}')
        self.duration_text.SetLabel(f'Duration: {video_info["duration"]}')
        self.file_size_text.SetLabel(f'File size: {video_info["file_size"]}')
        self.audio_codec_text.SetLabel(f'audio_codec: {video_info["audio_codec"]}')
        self.sample_rate_text.SetLabel(f'Sample rate: {video_info["sample_rate"]}')
        self.channels_text.SetLabel(f'Channels: {video_info["channels"]}')

if __name__ == "__main__":
    app = wx.App()
    frame = InfoGetterWX(None)
    frame.SetTitle('Info Getter with GUI')
    frame.SetSize((400, 400))
    frame.Show()
    app.MainLoop()