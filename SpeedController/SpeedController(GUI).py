import os
import subprocess
import wx
import re

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

def change_video_speed(video_path, output_path, speed, keep_pitch):
    try:
        # 速度超过atempo的处理
        atempo_filters = []
        while speed > 2.0:
            atempo_filters.append("atempo=2.0")
            speed /= 2.0
        atempo_filters.append(f"atempo={speed}")
        atempo_filter = ",".join(atempo_filters)

        if keep_pitch.lower() == 'y':
            # 保持音调
            cmd = [
                "ffmpeg", "-i", video_path, "-filter_complex",
                f"[0:v]setpts={1/speed}*PTS[v];[0:a]{atempo_filter}[a]",
                "-map", "[v]", "-map", "[a]", output_path
            ]
        else:
            # 不保持音调
            cmd = [
                "ffmpeg", "-i", video_path, "-filter_complex",
                f"[0:v]setpts={1/speed}*PTS[v];[0:a]{atempo_filter}[a]",
                "-map", "[v]", "-map", "[a]", output_path
            ]

        # 调用ffmpeg命令
        subprocess.run(cmd, check=True)
    except ValueError as ve:
        raise ValueError(ve)
    except subprocess.CalledProcessError as e:
        raise ValueError(e)

class SpeedControllerWX(wx.Frame):
    def __init__(self, *args, **kw):
        super(SpeedControllerWX, self).__init__(*args, **kw)

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

        # 速度
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.speed_text = wx.StaticText(panel, label="Speed:")
        self.hbox.Add(self.speed_text, flag=wx.ALL, border=5)
        self.speed = wx.TextCtrl(panel)
        self.hbox.Add(self.speed, flag=wx.ALL, border=5)
        self.vbox.Add(self.hbox, flag=wx.EXPAND)

        # 是否缩放
        self.pitch = wx.RadioBox(
            panel, label="Keep pitch", choices=[
                'Yes', 'No'
            ]
        )
        self.vbox.Add(self.pitch, flag=wx.ALL, border=5)

        # 转换按钮
        self.transform_button = wx.Button(panel, label="Process")
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

    def on_transform(self, event):
        input_path = self.selected_file
        output_path = self.selected_folder
        output_name = self.file_name.GetValue()
        speed = self.speed.GetValue()
        pitch = self.pitch.GetStringSelection().lower()
        pitch = pitch[0]

        _, ext = os.path.splitext(os.path.basename(input_path))
        
        if is_valid_time_format(output_name):
            wx.MessageBox("Invalid file name, please try another one!", "Error", wx.OK | wx.ICON_ERROR)
            return

        path = f'{output_path}/{output_name}{ext}'

        try:
            speed = float(speed)
            if speed <= 0:
                wx.MessageBox('Speed must be greater than zero!', 'Error', wx.OK | wx.ICON_ERROR)
                return
        except ValueError as e:
            wx.MessageBox(str(e), 'Error', wx.OK | wx.ICON_ERROR)
            return

        try:
            change_video_speed(input_path, path, speed, pitch)
            wx.MessageBox(f'File saved as {path}', 'Success', wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(str(e), 'Error', wx.OK | wx.ICON_ERROR)
            return

if __name__ == "__main__":
    app = wx.App()
    frame = SpeedControllerWX(None)
    frame.SetTitle('Speed Controller with GUI')
    frame.SetSize((400, 250))
    frame.Show()
    app.MainLoop()
