import subprocess
import re
import wx

def fps_input_check(fps: str) -> bool:
    # 只支持整数
    integer_seconds_pattern = r'^\d+$'
    # 支持带小数
    float_seconds_pattern = r'^\d+\.\d+$'

    if re.match(integer_seconds_pattern, fps) or re.match(float_seconds_pattern, fps): return True

    return False

def compression_input_check(compression: str) -> bool:
    integer_seconds_pattern = r'^\d+$'
    if re.match(integer_seconds_pattern, compression): return True
    return False

def is_valid_windows_filename(filename: str) -> bool:
    # 检查是否包含非法字符
    invalid_chars = r'[<>:"/\\|?*]'
    if re.search(invalid_chars, filename):
        return False
    # 检查是否是保留名称
    reserved_names = [
        "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
    ]
    if filename.upper() in reserved_names:
        return False
    # 检查是否以空格或点结尾
    if filename.endswith(' ') or filename.endswith('.'):
        return False
    # 检查文件名长度
    if len(filename) > 255:
        return False
    # 如果所有检查都通过，返回True
    return True

def is_valid_time_format(time_str):
    # 正则表达式匹配 hh:mm:ss 格式（支持秒部分带小数）
    hhmmss_pattern = r'^\d{1,2}:\d{2}:\d{2}(\.\d+)?$'
    # 正则表达式匹配纯秒数（只支持整数）
    integer_seconds_pattern = r'^\d+$'
    # 正则表达式匹配纯秒数（支持带小数）
    float_seconds_pattern = r'^\d+\.\d+$'

    # 验证是否符合任意一种格式
    if re.match(hhmmss_pattern, time_str): return True
    if re.match(integer_seconds_pattern, time_str): return True
    if re.match(float_seconds_pattern, time_str): return True

    return False

def calculate_seconds_difference(start_time: str, end_time: str) -> str:
    print(start_time, end_time)
    def time_to_seconds(time_str: str) -> float:
        # 如果是 hh:mm:ss 或者 hh:mm:ss.sss 格式，按原逻辑转换为秒
        if ":" in time_str:
            parts = time_str.split(":")
            h = int(parts[0])
            m = int(parts[1])
            s = float(parts[2])  # 支持秒部分为小数
            return h * 3600 + m * 60 + s
        else:
            # 如果是纯秒数，直接转换为浮点数
            return float(time_str)

    # 将开始时间和结束时间转换为秒数
    start_total_seconds = time_to_seconds(start_time)
    end_total_seconds = time_to_seconds(end_time)

    # 返回时间差，保留小数点后两位
    return "{:.2f}".format(end_total_seconds - start_total_seconds)

def video_to_gif(video_path, fps, width, height, start_time=None, end_time=None, output_path=None):
    print(f"Type of start_time: {type(start_time)}, Value: {start_time}")
    print(f"Type of end_time: {type(end_time)}, Value: {end_time}")
    command = ['ffmpeg']  # 初始命令部分

    # 如果有 start_time，则添加 -ss 参数
    if start_time:
        command.extend(['-ss', str(start_time)])

    # 添加输入文件路径
    command.extend(['-i', video_path])

    # 如果有 end_time，则计算时间差并添加 -t 参数
    if end_time:
        command.extend(
        ['-t', calculate_seconds_difference(str(start_time) if start_time else "00:00:00", str(end_time))]
        )

    if width and height:
        fps_and_compression = f'fps={fps}, scale={width}:{height}:flags=lanczos'
    else:
        fps_and_compression = f'fps={fps}'

    # 添加 GIF 转换的选项
    command.extend([
        '-vf',
        fps_and_compression,
        '-gifflags',
        '+transdiff',  # 优化GIF的平滑过渡
        '-y',  # 覆盖输出文件
        output_path
    ])

    try:
        subprocess.run(command, check=True)
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())  # 打印标准输出
        print(result.stderr.decode())  # 打印错误输出
        return True, f'Gif has successfully created at {output_path}'
    except subprocess.CalledProcessError as e:
        return False, e

class GifTransformerWX(wx.Frame):
    def __init__(self, *args, **kw):
        super(GifTransformerWX, self).__init__(*args, **kw)

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
        self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.name_text = wx.StaticText(panel, label="Output name:")
        self.hbox5.Add(self.name_text, flag=wx.ALL, border=5)
        self.file_name = wx.TextCtrl(panel)
        self.hbox5.Add(self.file_name, flag=wx.ALL, border=5)
        self.vbox.Add(self.hbox5, flag=wx.EXPAND)

        # 输出路径
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.folder_button = wx.Button(panel, label="Select output folder")
        self.Bind(wx.EVT_BUTTON, self.on_select_folder, self.folder_button)
        self.hbox2.Add(self.folder_button, flag=wx.ALL, border=5)
        self.output_path_text = wx.StaticText(panel, label="Click \"Select output folder\" first")
        self.hbox2.Add(self.output_path_text, flag=wx.ALL, border=5)
        self.vbox.Add(self.hbox2, flag=wx.EXPAND)

        # 时间输入
        self.vbox.Add(wx.StaticText(panel, label=
        "Enter time(format: hh:mm:ss or s):"), flag=wx.ALL, border=5)

        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.start_time_text = wx.StaticText(panel, label="Start time:")
        self.hbox3.Add(self.start_time_text, flag=wx.ALL, border=5)
        self.start_time = wx.TextCtrl(panel)
        self.hbox3.Add(self.start_time, flag=wx.EXPAND | wx.ALL, border=5)
        self.vbox.Add(self.hbox3, flag=wx.EXPAND)

        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.end_time_text = wx.StaticText(panel, label="End time:")
        self.hbox4.Add(self.end_time_text, flag=wx.ALL, border=5)
        self.end_time = wx.TextCtrl(panel)
        self.hbox4.Add(self.end_time, flag=wx.EXPAND | wx.ALL, border=5)
        self.vbox.Add(self.hbox4, flag=wx.EXPAND)

        # 输入帧率
        self.hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        self.fps_text = wx.StaticText(panel, label="Gif FPS(10 is recommended):")
        self.hbox6.Add(self.fps_text, flag=wx.ALL, border=5)
        self.fps = wx.TextCtrl(panel)
        self.hbox6.Add(self.fps, flag=wx.ALL, border=5)
        self.vbox.Add(self.hbox6, flag=wx.EXPAND)

        # 是否缩放
        self.compression = wx.RadioBox(
            panel, label="Compression", choices=[
                'No', 'Yes'
            ]
        )
        self.Bind(wx.EVT_RADIOBOX, self.compression_or_not, self.compression)
        self.vbox.Add(self.compression, flag=wx.ALL, border=5)

        # 压缩
        self.hbox7 = wx.BoxSizer(wx.HORIZONTAL)
        self.width_text = wx.StaticText(panel, label="Enter width:")
        self.hbox7.Add(self.width_text, flag=wx.ALL, border=5)
        self.width = wx.TextCtrl(panel)
        self.width.Enable(False)
        self.hbox7.Add(self.width, flag=wx.ALL, border=5)

        self.height_text = wx.StaticText(panel, label="Enter height:")
        self.hbox7.Add(self.height_text, flag=wx.ALL, border=5)
        self.height = wx.TextCtrl(panel)
        self.height.Enable(False)
        self.hbox7.Add(self.height, flag=wx.ALL, border=5)
        self.vbox.Add(self.hbox7, flag=wx.EXPAND)

        # 剪切按钮
        self.transform_button = wx.Button(panel, label="Transform")
        self.transform_button.Bind(wx.EVT_BUTTON, self.on_transform)
        self.vbox.Add(self.transform_button, flag=wx.ALL, border=5)

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

    def compression_or_not(self, event):
        selection = self.compression.GetStringSelection()

        if selection == 'No':
            self.width.Enable(False)
            self.height.Enable(False)
        else:
            self.width.Enable(True)
            self.height.Enable(True)

    def on_transform(self, event):
        input_path = self.selected_file
        output_path = self.selected_folder
        output_name = self.file_name.GetValue()
        fps = self.fps.GetValue()
        compression_or_not = self.compression.GetStringSelection()

        if compression_or_not == 'No':
            width, height = None, None
        else:
            width, height = self.width.GetValue(), self.height.GetValue()
            if compression_input_check(width) or compression_input_check(height):
                wx.MessageBox('Width or height input invalid', 'Error', wx.OK | wx.ICON_ERROR)
                return

        if not fps_input_check(fps):
            wx.MessageBox('fps input is invalid', 'Error', wx.OK | wx.ICON_ERROR)
            return

        if not is_valid_windows_filename(output_name):
            wx.MessageBox(
                f"Output name: {output_name} is invalid. Please try another one.", 'Error',
                wx.OK | wx.ICON_ERROR
            )
            return

        start_time = self.start_time.GetValue()
        end_time = self.end_time.GetValue()

        if start_time:
            if not is_valid_time_format(start_time):
                wx.MessageBox(
                "Invalid time format. Please enter time in hh:mm:ss or seconds (e.g., 120 or 01:30:00).",
                'Error', wx.OK | wx.ICON_ERROR
                )
                return

        if end_time:
            if not is_valid_time_format(end_time):
                wx.MessageBox(
                    "Invalid time format. Please enter time in hh:mm:ss or seconds (e.g., 120 or 01:30:00).",
                    'Error', wx.OK | wx.ICON_ERROR
                )
                return

        if not input_path or not output_path or not output_name:
            wx.MessageBox(
                "The required information is not filled in",'Error', wx.OK | wx.ICON_ERROR
            )
            return

        output_path_ = f'{output_path}/{output_name}.gif'

        print(end_time)

        flag, message_ = video_to_gif(input_path, fps, width, height, start_time, end_time, output_path_)

        if not flag:
            wx.MessageBox(message_, 'Error', wx.OK | wx.ICON_ERROR)
            return
        else:
            wx.MessageBox(message_,'Success',wx.OK | wx.ICON_INFORMATION)
            return

if __name__ == "__main__":
    app = wx.App()
    frame = GifTransformerWX(None)
    frame.SetTitle('Video Cutter with GUI')
    frame.SetSize((400, 400))
    frame.Show()
    app.MainLoop()