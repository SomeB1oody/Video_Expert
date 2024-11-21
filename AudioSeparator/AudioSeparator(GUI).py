import os
import subprocess
import wx

def separate_audio_video(video_input_path, output_path, run_video, run_audio):
    # 获取文件名和扩展名
    base_name, ext = os.path.splitext(os.path.basename(video_input_path))
    # 无音频视频的输出路径
    video_no_audio_output = os.path.join(output_path, f"{base_name}_no_audio{ext}")
    # 纯音频文件的输出路径
    audio_output = os.path.join(output_path, f"{base_name}.mp3")

    try:
        if run_video:
            subprocess.run(
                ["ffmpeg", "-i", video_input_path, "-an", "-c:v", "copy", video_no_audio_output],
                check=True
            )

        # 提取音频
        if run_audio:
            subprocess.run(
                ["ffmpeg", "-i", video_input_path, "-vn", "-acodec", "libmp3lame", audio_output],
                check=True
            )

    except subprocess.CalledProcessError as e:
        raise ValueError(e)

class AudioSeparatorWX(wx.Frame):
    def __init__(self, *args, **kw):
        super(AudioSeparatorWX, self).__init__(*args, **kw)

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

        # 选择视频音频输出
        self.output_choice = wx.ListBox(
            panel, choices=['Audio', 'video'], style=wx.LB_EXTENDED
        )
        self.vbox.Add(self.output_choice, flag=wx.ALL, border=5)

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
        output_path = self.selected_folder + '/'
        output_choice = self.output_choice.GetSelection()

        # 确保处理数组或单个整数两种情况
        if isinstance(output_choice, int):  # 如果是整数，包装成单元素列表
            output_choice = [output_choice]

        run_video = False
        run_audio = False

        # 检查选中项
        if 0 in output_choice:
            run_audio = True
        if 1 in output_choice:
            run_video = True

        if not run_video and not run_audio:
            wx.MessageBox("Please select output type(s)", "Error")

        if not input_path:
            wx.MessageBox("Please select a video file first", "Error", wx.OK | wx.ICON_ERROR)
            return
        if not output_path:
            wx.MessageBox("Please select an output folder first", "Error", wx.OK | wx.ICON_ERROR)
            return

        try:
            separate_audio_video(input_path, output_path, run_video, run_audio)
            wx.MessageBox(f"File saved at {output_path}", "Success", wx.OK | wx.ICON_INFORMATION)
        except ValueError as e:
            wx.MessageBox(str(e), "Error", wx.OK | wx.ICON_ERROR)
            return


if __name__ == "__main__":
    app = wx.App()
    frame = AudioSeparatorWX(None)
    frame.SetTitle('Audio Separator with GUI')
    frame.SetSize((400, 250))
    frame.Show()
    app.MainLoop()