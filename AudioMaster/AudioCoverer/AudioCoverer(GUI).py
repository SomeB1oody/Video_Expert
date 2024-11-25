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

def get_duration(file_path):
    result = subprocess.run(
        ['ffprobe', '-i', file_path, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=p=0'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    return float(result.stdout.strip())

def process_audio(audio_path, video_duration, audio_duration, choice=None):
    if audio_duration > video_duration:
        output_audio = "trimmed_audio.aac"
        subprocess.run([
            'ffmpeg', '-i', audio_path, '-t', str(video_duration),
            '-c', 'copy', output_audio, '-y'
        ])
    elif audio_duration < video_duration:
        if choice == '1':
            output_audio = "padded_audio.aac"
            subprocess.run([
                'ffmpeg', '-i', audio_path, '-filter_complex',
                f"[0:a]apad=pad_dur={video_duration}[out]",
                '-map', '[out]', '-c:a', 'aac', output_audio, '-y'
            ])
        elif choice == '2':
            output_audio = audio_path
        else:
            raise ValueError("Invalid choice")
    else:
        output_audio = audio_path  # 时长相等直接使用音频

    return output_audio

def replace_audio(video_path, output_audio, output_video):
    subprocess.run([
        'ffmpeg', '-i', video_path, '-i', output_audio,
        '-c:v', 'copy', '-map', '0:v:0', '-map', '1:a:0',
        '-shortest', output_video, '-y'
    ])

class AudioCovererWX(wx.Frame):
    def __init__(self, *args, **kw):
        super(AudioCovererWX, self).__init__(*args, **kw)

        panel = wx.Panel(self)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        # 输入视频路径
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.file_button = wx.Button(panel, label="Select video")
        self.Bind(wx.EVT_BUTTON, self.on_select_video, self.file_button)
        self.hbox.Add(self.file_button,flag=wx.ALL, border=5)
        self.input_path_text = wx.StaticText(panel, label="Click \"Select video\" first")
        self.hbox.Add(self.input_path_text, flag=wx.ALL, border=5)
        self.vbox.Add(self.hbox, flag=wx.EXPAND)

        # 输入音频路径
        self.hbox_ = wx.BoxSizer(wx.HORIZONTAL)
        self.audio_button = wx.Button(panel, label="Select audio")
        self.Bind(wx.EVT_BUTTON, self.on_select_audio, self.audio_button)
        self.hbox_.Add(self.audio_button,flag=wx.ALL, border=5)
        self.input_path_text_ = wx.StaticText(panel, label="Click \"Select audio\" first")
        self.hbox_.Add(self.input_path_text_, flag=wx.ALL, border=5)
        self.vbox.Add(self.hbox_, flag=wx.EXPAND)

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

        # 选择覆盖模式
        self.cover_mode = wx.RadioBox(
            panel, label="choose a cover mode", choices=[
                'Mute processing', 'Retain the original video audio'
            ]
        )
        self.vbox.Add(self.cover_mode, flag=wx.ALL, border=5)

        # 处理按钮
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

    def on_select_audio(self, event):
        with wx.FileDialog(None, "Select audio", wildcard="所有文件 (*.*)|*.*",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                self.input_path_text_.SetLabel(f"{dialog.GetPath()}")
                self.selected_file_ = dialog.GetPath()

    def on_select_folder(self, event):
        with wx.DirDialog(None, "Select a folder for output", "",
                          style=wx.DD_DEFAULT_STYLE) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                self.output_path_text.SetLabel(f"{dialog.GetPath()}")
                self.selected_folder = dialog.GetPath()

    def on_transform(self, event):
        input_video_path = self.selected_file
        input_audio_path = self.selected_file_
        output_video_path = self.selected_folder
        output_name = self.file_name.GetValue()
        cover_mode = self.cover_mode.GetStringSelection()

        if not input_video_path:
            wx.MessageBox('Input video path cannot be empty', 'Error', wx.OK | wx.ICON_ERROR)
            return
        if not input_audio_path:
            wx.MessageBox('Input audio path cannot be empty', 'Error', wx.OK | wx.ICON_ERROR)
            return
        if not is_valid_windows_filename(output_name):
            wx.MessageBox('Invalid output name', 'Error', wx.OK | wx.ICON_ERROR)
            return
        if not output_video_path:
            wx.MessageBox('Output video path cannot be empty', 'Error', wx.OK | wx.ICON_ERROR)
            return

        _, ext = os.path.splitext(input_video_path)
        output_path = f'{output_video_path}/{output_name}{ext}'

        video_duration = get_duration(input_video_path)
        audio_duration = get_duration(input_audio_path)

        if cover_mode == 'Mute processing':
            cover_mode = '1'
        else:
            cover_mode = '2'

        processed_audio = process_audio(input_audio_path, video_duration, audio_duration, cover_mode)
        try:
            replace_audio(input_video_path, processed_audio, output_path)
            wx.MessageBox(f'File saved as {output_path}', 'Success', wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(str(e), 'Error', wx.OK | wx.ICON_ERROR)
            return


if __name__ == "__main__":
    app = wx.App()
    frame = AudioCovererWX(None)
    frame.SetTitle('Audio Coverer with GUI')
    frame.SetSize((450, 300))
    frame.Show()
    app.MainLoop()