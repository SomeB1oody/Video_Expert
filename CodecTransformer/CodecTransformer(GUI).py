import platform
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
        h264_support += ['cpu']
        return h264_support
    elif selected_codec == 'hevc':
        hevc_support += ['cpu']
        return hevc_support
    elif selected_codec == 'av1':
        av1_support += ['cpu']
        return av1_support
    elif selected_codec == 'prores':
        prores_support += ['cpu']
        return prores_support
    elif selected_codec == 'vp8':
        vp8_support += ['cpu']
        return vp8_support
    elif selected_codec == 'vp9':
        vp9_support += ['cpu']
        return vp9_support
    else:
        return ['cpu']

class CodecTransformerWX(wx.Frame):
    def __init__(self, *args, **kw):
        super(CodecTransformerWX, self).__init__(*args, **kw)

        panel = wx.Panel(self)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        # 输入路径
        self.hbox_ = wx.BoxSizer(wx.HORIZONTAL)
        self.file_button = wx.Button(panel, label="Select video")
        self.Bind(wx.EVT_BUTTON, self.on_select_video, self.file_button)
        self.hbox_.Add(self.file_button,flag=wx.ALL, border=5)
        self.input_path_text = wx.StaticText(panel, label="Click \"Select video\" first")
        self.hbox_.Add(self.input_path_text, flag=wx.ALL, border=5)
        self.vbox.Add(self.hbox_, flag=wx.EXPAND)

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

        # 子水平布局 hbox
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # 添加 encode_mode 列表和标题
        encode_mode_box = wx.BoxSizer(wx.VERTICAL)
        encode_mode_label = wx.StaticText(panel, label="Encode mode")
        self.encode_mode = wx.ListBox(
            panel, choices=[
                'h264', 'hevc', 'vp8', 'vp9', 'av1', 'prores'
            ], style=wx.LB_SINGLE
        )
        self.encode_mode.Bind(wx.EVT_LISTBOX, self.on_encode_mode)
        encode_mode_box.Add(encode_mode_label, flag=wx.ALL, border=5)
        encode_mode_box.Add(self.encode_mode, flag=wx.ALL, border=5)

        # 添加 encoder_choice 列表和标题
        encoder_box = wx.BoxSizer(wx.VERTICAL)
        encoder_label = wx.StaticText(panel, label="Encoder")
        self.encoder_choice = wx.ListBox(panel, choices=[], style=wx.LB_SINGLE)
        encoder_box.Add(encoder_label, flag=wx.ALL, border=5)
        encoder_box.Add(self.encoder_choice, flag=wx.ALL, border=5)

        # 添加 output_format 列表和标题
        output_format_box = wx.BoxSizer(wx.VERTICAL)
        output_format_label = wx.StaticText(panel, label="Output format")
        self.output_format = wx.ListBox(panel, choices=[], style=wx.LB_SINGLE)
        output_format_box.Add(output_format_label, flag=wx.ALL, border=5)
        output_format_box.Add(self.output_format, flag=wx.ALL, border=5)

        # 将各个垂直 BoxSizer 添加到水平布局中
        hbox.Add(encode_mode_box, flag=wx.ALL, border=5)
        hbox.Add(encoder_box, flag=wx.ALL, border=5)
        hbox.Add(output_format_box, flag=wx.ALL, border=5)

        # 将水平布局添加到主垂直布局中
        self.vbox.Add(hbox, flag=wx.ALL, border=5)

        # 转换按钮
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

    def on_encode_mode(self, event):
        if self.encode_mode.GetStringSelection() =='h264':
            self.output_format.Set(['.mp4', '.mov', '.mkv'])

        elif self.encode_mode.GetStringSelection() =='hevc':
            self.output_format.Set(['.mp4', '.mov', '.mkv'])

        elif self.encode_mode.GetStringSelection() =='vp8':
            self.output_format.Set(['.mkv', '.webm'])

        elif self.encode_mode.GetStringSelection() =='vp9':
            self.output_format.Set(['.mkv', '.webm'])

        elif self.encode_mode.GetStringSelection() == 'av1':
            self.output_format.Set(['.mkv', '.webm'])

        elif self.encode_mode.GetStringSelection() == 'prores':
            self.output_format.Set(['.mov'])

        support_encoders_list = auto_encode(self.encode_mode.GetStringSelection())
        self.encoder_choice.Set(support_encoders_list)

    def on_transform(self, event):
        encode_mode = self.encode_mode.GetStringSelection()
        encoder_choice = self.encoder_choice.GetStringSelection()
        input_path = self.selected_file
        output_path = self.selected_folder
        output_name = self.file_name.GetValue()
        output_format = self.output_format.GetStringSelection()

        if not input_path:
            wx.MessageBox('Please select an input file', 'Error', wx.OK | wx.ICON_ERROR)
            return

        if not output_path:
            wx.MessageBox('Please select an output folder', 'Error', wx.OK | wx.ICON_ERROR)
            return

        if not is_valid_windows_filename(output_name):
            wx.MessageBox('Output name is invalid', 'Error', wx.OK | wx.ICON_ERROR)
            return

        path = f'{output_path}/{output_name}{output_format}'

        ffmpeg_command = ['ffmpeg', '-i', input_path]

        if encoder_choice == 'nvenc':
            ffmpeg_command.extend(['-c:v', f'{encode_mode}_nvenc'])

        elif encoder_choice == 'amf':
            ffmpeg_command.extend(['-c:v', f'{encode_mode}_amf'])

        elif encoder_choice == 'qsv':
            ffmpeg_command.extend(['-c:v', f'{encode_mode}_qsv'])

        elif encoder_choice == 'videotoolbox':
            ffmpeg_command.extend(['-c:v', f'{encode_mode}_videotoolbox'])

        else:
            ffmpeg_command.extend(['-c:v', f'{encode_mode}'])

        ffmpeg_command.append(path)

        try:
            subprocess.run(ffmpeg_command)
            wx.MessageBox(f'Video saved at {path}', 'Success', wx.OK | wx.ICON_INFORMATION)
            return
        except Exception as e:
            wx.MessageBox(f'Error: {e}', 'Error', wx.OK | wx.ICON_ERROR)
            return

if __name__ == "__main__":
    app = wx.App()
    frame = CodecTransformerWX(None)
    frame.SetTitle('Codec Transformer with GUI')
    frame.SetSize((600, 350))
    frame.Show()
    app.MainLoop()
