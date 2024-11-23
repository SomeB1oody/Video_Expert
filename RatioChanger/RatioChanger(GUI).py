import os
import subprocess
import wx
import re

def stretch_video(input_path, aspect_ratio, output_path):
    try:
        # 提取宽高比例
        width_ratio, height_ratio = map(float, aspect_ratio.split(":"))
        target_aspect = width_ratio / height_ratio

        # 使用 ffmpeg 获取原始视频宽高
        probe_command = [
            "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
            "stream=width,height", "-of", "csv=p=0", input_path
        ]
        probe_result = subprocess.run(probe_command, capture_output=True, text=True)
        if probe_result.returncode != 0:
            raise RuntimeError(f"ffprobe Error: {probe_result.stderr.strip()}")

        original_width, original_height = map(int, probe_result.stdout.strip().split(","))
        original_aspect = original_width / original_height

        # 计算新宽高
        if original_aspect > target_aspect:
            new_width = int(original_height * target_aspect)
            new_height = original_height
        else:
            new_width = original_width
            new_height = int(original_width / target_aspect)

        # 构建 ffmpeg 拉伸命令
        ffmpeg_command = [
            "ffmpeg", "-i", input_path, "-vf",
            f"scale={new_width}:{new_height}", "-c:v", "libx264", "-crf", "23",
            "-preset", "medium", output_path
        ]

        # 执行 ffmpeg 命令
        subprocess.run(ffmpeg_command, check=True)

    except Exception as e:
        raise RuntimeError(f"ffmpeg Error: {e}")

def crop_video(input_path, aspect_ratio, output_path):
    try:
        # 提取宽高比例
        width_ratio, height_ratio = map(float, aspect_ratio.split(":"))
        target_aspect = width_ratio / height_ratio

        # 使用 ffmpeg 获取原始视频宽高
        probe_command = [
            "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
            "stream=width,height", "-of", "csv=p=0", input_path
        ]
        probe_result = subprocess.run(probe_command, capture_output=True, text=True)
        if probe_result.returncode != 0:
            raise RuntimeError(f"ffprobe 错误：{probe_result.stderr.strip()}")

        original_width, original_height = map(int, probe_result.stdout.strip().split(","))
        original_aspect = original_width / original_height

        # 计算裁剪区域
        if original_aspect > target_aspect:  # 宽度过长，需要裁剪左右
            new_width = int(original_height * target_aspect)
            new_height = original_height
            crop_x = (original_width - new_width) // 2
            crop_y = 0
        else:  # 高度过长，需要裁剪上下
            new_width = original_width
            new_height = int(original_width / target_aspect)
            crop_x = 0
            crop_y = (original_height - new_height) // 2

        # 构建 ffmpeg 裁剪命令
        ffmpeg_command = [
            "ffmpeg", "-i", input_path, "-vf",
            f"crop={new_width}:{new_height}:{crop_x}:{crop_y}", "-c:v", "libx264", "-crf", "23",
            "-preset", "medium", output_path
        ]

        # 执行 ffmpeg 命令
        subprocess.run(ffmpeg_command, check=True)

    except Exception as e:
        raise RuntimeError(f"ffmpeg Error: {e}")

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

class RatioChangerWX(wx.Frame):
    def __init__(self, *args, **kw):
        super(RatioChangerWX, self).__init__(*args, **kw)

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

        # 输入比例
        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3.Add(wx.StaticText(panel, label='Enter Ratio:'), flag=wx.ALL, border=5)
        self.ratio_x = wx.TextCtrl(panel)
        self.hbox3.Add(self.ratio_x, flag=wx.ALL, border=2)
        self.hbox3.Add(wx.StaticText(panel, label=':'), flag=wx.ALL, border=2)
        self.ratio_y = wx.TextCtrl(panel)
        self.hbox3.Add(self.ratio_y, flag=wx.ALL, border=2)
        self.vbox.Add(self.hbox3, flag=wx.EXPAND)

        # 拉伸还是裁剪
        self.process_type = wx.RadioBox(
            panel, label="choose a processing type", choices=[
                'stretch', 'crop'
            ]
        )
        self.vbox.Add(self.process_type, flag=wx.ALL, border=5)

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
        ratio_x = self.ratio_x.GetValue()
        ratio_y = self.ratio_y.GetValue()
        choice = self.process_type.GetStringSelection()

        if not input_path:
            wx.MessageBox('Input path is empty', 'Error', wx.OK | wx.ICON_ERROR)
            return

        if not output_path:
            wx.MessageBox('Output path is empty', 'Error', wx.OK | wx.ICON_ERROR)
            return

        if not is_valid_windows_filename(output_name):
            wx.MessageBox('Invalid output name', 'Error', wx.OK | wx.ICON_ERROR)
            return

        if not ratio_x or not ratio_y:
            wx.MessageBox('Ratio is empty', 'Error', wx.OK | wx.ICON_ERROR)
            return

        try:
            ratio_x = float(ratio_x)
            ratio_y = float(ratio_y)
        except ValueError as e:
            wx.MessageBox(str(e), 'Error', wx.OK | wx.ICON_ERROR)

        _, ext = os.path.splitext(os.path.basename(input_path))
        ratio = f'{ratio_x}:{ratio_y}'
        path = f'{output_path}/{output_name}{ext}'

        if choice == 'stretch':
            try:
                stretch_video(input_path, ratio, output_path)
                wx.MessageBox(f'File saved as {path}','Success', wx.OK | wx.ICON_INFORMATION)
            except Exception as e:
                wx.MessageBox(str(e), 'Error', wx.OK | wx.ICON_ERROR)
                return
        else:
            try:
                crop_video(input_path, output_path, ratio)
                wx.MessageBox(f'File saved as {path}','Success', wx.OK | wx.ICON_INFORMATION)
            except Exception as e:
                wx.MessageBox(str(e), 'Error', wx.OK | wx.ICON_ERROR)
                return


if __name__ == "__main__":
    app = wx.App()
    frame = RatioChangerWX(None)
    frame.SetTitle('Ratio Changer with GUI')
    frame.SetSize((400, 250))
    frame.Show()
    app.MainLoop()