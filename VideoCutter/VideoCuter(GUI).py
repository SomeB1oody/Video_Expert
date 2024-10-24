import subprocess
import re
import wx

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

def calculate_seconds_difference(start_time: str, end_time: str) -> str:
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

def cut_video_ffmpeg(video_path, encode_mode, encode_speed, output_path, start_time=None, end_time=None):
    try:
        ffmpeg_command = ['ffmpeg']
        # 如果有 start_time，则添加 -ss 参数
        if start_time:
            ffmpeg_command.extend(['-ss', str(start_time)])

        # 添加输入文件路径
        ffmpeg_command.extend(['-i', video_path])

        # 如果有 end_time，则计算时间差并添加 -t 参数
        if end_time:
            ffmpeg_command.extend(
                ['-t', calculate_seconds_difference(str(start_time) if start_time else "00:00:00", str(end_time))]
            )

        ffmpeg_command.extend(['-c:v', encode_mode]) # 编码模式
        ffmpeg_command.extend(['-preset', encode_speed]) # 编码速度
        ffmpeg_command.append(output_path) # 输出路径

        # 调用 ffmpeg 命令
        subprocess.run(ffmpeg_command, check=True)
        return True, None

    except subprocess.CalledProcessError as e:
        return False, e

class VideoCutterWX(wx.Frame):
    def __init__(self, *args, **kw):
        super(VideoCutterWX, self).__init__(*args, **kw)

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
        self.end_time_text = wx.StaticText(panel, label="Start time:")
        self.hbox4.Add(self.end_time_text, flag=wx.ALL, border=5)
        self.end_time = wx.TextCtrl(panel)
        self.hbox4.Add(self.end_time, flag=wx.EXPAND | wx.ALL, border=5)
        self.vbox.Add(self.hbox4, flag=wx.EXPAND)

        # 编码格式单选框
        self.encode_mode = wx.RadioBox(
            panel, label="Choose encode mode:", choices=[
                'H.264', 'H.265', 'MPEG-4', 'ascii', 'VP8', 'VP9', 'H.263', 'ProRes', 'DNxHD'
            ],
            majorDimension=4,  # 每列5个选项
            style=wx.RA_SPECIFY_COLS  # 指定为按列排列
        )
        self.vbox.Add(self.encode_mode, flag=wx.ALL, border=5)

        # 编码格式单选框
        self.encode_speed = wx.RadioBox(
            panel, label="Choose encode speed:",
            choices=[
                'Ultra Fast', 'Super Fast', 'Very Fast', 'Fast',
                'Medium', 'Slow', 'Very Slow', 'Placebo'
            ],
            majorDimension=3,  # 每列5个选项
            style=wx.RA_SPECIFY_COLS  # 指定为按列排列
        )
        self.vbox.Add(self.encode_speed, flag=wx.ALL, border=5)
        self.vbox.Add(wx.StaticText(panel, label=
        "Faster speed comes with the lower compression efficiency"), flag=wx.ALL, border=5)

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

        # 剪切按钮
        self.cut_button = wx.Button(panel, label="Cut")
        self.cut_button.Bind(wx.EVT_BUTTON, self.on_cut)
        self.vbox.Add(self.cut_button, flag=wx.ALL, border=5)


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

    def on_cut(self, event):
        input_path = self.selected_file
        output_path = self.selected_folder
        start_time = self.start_time.GetValue()
        end_time = self.end_time.GetValue()
        output_name = self.file_name.GetValue()
        encode_mode = self.encode_mode.GetStringSelection()
        encode_speed = self.encode_speed.GetStringSelection()

        match encode_speed:
            case 'Ultra Fast': encode_speed = 'ultrafast'
            case 'Super Fast': encode_speed = 'superfast'
            case 'Very Fast': encode_speed = 'veryfast'
            case 'Fast': encode_speed = 'fast'
            case 'Medium': encode_speed = 'medium'
            case 'Slow': encode_speed = 'slow'
            case 'Very Slow': encode_speed = 'veryslow'
            case 'Placebo': encode_speed = 'placebo'
            case _: encode_speed = 'medium'

        match encode_mode:
            case 'H.264': encode_mode = 'libx264'
            case 'H.265': encode_mode = 'libx265'
            case 'MPEG-4': encode_mode = 'mpeg4'
            case 'vp8': encode_mode = 'vp8'
            case 'vp9': encode_mode = 'vp9'
            case 'ProRes': encode_mode = 'prores'
            case 'DNxHD': encode_mode = 'dnxhd'
            case _: encode_mode = 'libx264'

        if not input_path:
            wx.MessageBox('Input path is empty', 'Error', wx.OK | wx.ICON_ERROR)
            return

        if not output_path:
            wx.MessageBox('Output path is empty', 'Error', wx.OK | wx.ICON_ERROR)
            return

        if not output_name:
            wx.MessageBox('Output name is empty', 'Error', wx.OK | wx.ICON_ERROR)
            return

        if start_time:
            if not is_valid_time_format(start_time):
                wx.MessageBox(
                "Invalid start time format. Please enter time in hh:mm:ss or seconds (e.g., 120 or 01:30:00).",
                'Error', wx.OK | wx.ICON_ERROR)
                return

        if end_time:
            if not is_valid_time_format(end_time):
                wx.MessageBox(
                "Invalid end time format. Please enter time in hh:mm:ss or seconds (e.g., 120 or 01:30:00).",
                'Error', wx.OK | wx.ICON_ERROR)
                return

        if not is_valid_windows_filename(output_name):
            wx.MessageBox(
                f"Output name: {output_name} is invalid. Please try another one.", 'Error',
                wx.OK | wx.ICON_ERROR)
            return

        output_path_ = f'{output_path}/{output_name}.mp4'

        flag, error_message = cut_video_ffmpeg(
            input_path, encode_mode, encode_speed, output_path_, start_time, end_time
        )
        if flag:
            wx.MessageBox(f"video saved as{output_path_}", 'Success', wx.OK | wx.ICON_INFORMATION)
            return
        else:
            wx.MessageBox(error_message, 'Error', wx.OK | wx.ICON_ERROR)
            return


if __name__ == "__main__":
    app = wx.App()
    frame = VideoCutterWX(None)
    frame.SetTitle('Video Cutter WX')
    frame.SetSize((375, 500))
    frame.Show()
    app.MainLoop()
