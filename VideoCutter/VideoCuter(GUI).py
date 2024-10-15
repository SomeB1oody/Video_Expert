import subprocess
import re
import wx

def is_valid_time_format(time_str):
    # 匹配 hh:mm:ss 格式，或纯秒数格式 s
    hhmmss_pattern = r'^(\d{1,2}):([0-5]?\d):([0-5]?\d)$'  # hh:mm:ss 格式
    seconds_pattern = r'^\d+(\.\d+)?$'                     # 纯秒数 s 格式

    # 尝试匹配 hh:mm:ss 格式
    match = re.match(hhmmss_pattern, time_str)
    if match:
        hours, minutes, seconds = match.groups()
        if int(minutes) <= 59 and int(seconds) <= 59:
            return True

    # 尝试匹配纯秒数格式
    if re.match(seconds_pattern, time_str):
        return True

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
    def time_to_seconds(time_str: str) -> int:
        # 如果是 hh:mm:ss 格式，按原逻辑转换为秒
        if ":" in time_str:
            h, m, s = map(int, time_str.split(":"))
            return h * 3600 + m * 60 + s
        else:
            # 如果是纯秒数，直接转换为整数
            return int(time_str)

    # 将开始时间和结束时间转换为秒数
    start_total_seconds = time_to_seconds(start_time)
    end_total_seconds = time_to_seconds(end_time)

    # 返回时间差，单位为秒
    return str(end_total_seconds - start_total_seconds)

def cut_video_ffmpeg(video_path, start_time, end_time, output_path):
    try:
        ffmpeg_command = [
            'ffmpeg',
            '-ss', str(start_time),     # 起始时间
            '-i', video_path,          # 输入视频文件
            '-t', calculate_seconds_difference(str(start_time), str(end_time)),  # 截取的持续时间
            '-c:v', 'libx264',
            '-preset', 'veryslow',
            output_path                 # 输出文件路径
        ]

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

        # 输出路径
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.folder_button = wx.Button(panel, label="Select output folder")
        self.Bind(wx.EVT_BUTTON, self.on_select_folder, self.folder_button)
        self.hbox2.Add(self.folder_button, flag=wx.ALL, border=5)
        self.output_path_text = wx.StaticText(panel, label="Click \"Select output folder\" first")
        self.hbox2.Add(self.output_path_text, flag=wx.ALL, border=5)
        self.vbox.Add(self.hbox2, flag=wx.EXPAND)

        # 输出名称
        self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.name_text = wx.StaticText(panel, label="Output name:")
        self.hbox5.Add(self.name_text, flag=wx.ALL, border=5)
        self.file_name = wx.TextCtrl(panel)
        self.hbox5.Add(self.file_name, flag=wx.ALL, border=5)
        self.vbox.Add(self.hbox5, flag=wx.EXPAND)

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

        if not is_valid_time_format(start_time) or not is_valid_time_format(end_time):
            wx.MessageBox(
        "Invalid time format. Please enter time in hh:mm:ss or seconds (e.g., 120 or 01:30:00).",
        'Error', wx.OK | wx.ICON_ERROR)
            return

        if not is_valid_windows_filename(output_name):
            wx.MessageBox(
            f"Output name: {output_name} is invalid. Please try another one.", 'Error',
            wx.OK | wx.ICON_ERROR)
            return

        output_path_ = f'{output_path}/{output_name}.mp4'

        flag, error_message = cut_video_ffmpeg(input_path, start_time, end_time, output_path_)
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
    frame.SetSize((600, 300))
    frame.Show()
    app.MainLoop()