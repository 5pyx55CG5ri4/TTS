import asyncio
import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, scrolledtext, ttk

import edge_tts
import pygame


class TTSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("小说推文工具")
        self.root.geometry("600x700")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tts_page = TTSPage(self.notebook)

        self.notebook.add(self.tts_page, text="TTS(文字转语音)")


class TTSPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(self, text="TTS(文字转语音)", font=("Helvetica", 24, "bold"))
        title_label.pack(pady=10)

        text_frame = tk.Frame(self)
        text_frame.pack(padx=10, pady=10)

        self.text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, width=60, height=15,
                                                   font=("Helvetica", 12))
        self.text_area.pack(padx=10, pady=10)

        control_frame = tk.Frame(self)
        control_frame.pack(padx=10, pady=5)

        rate_label = tk.Label(control_frame, text="语速:", font=("Helvetica", 12))
        rate_label.grid(row=0, column=0, padx=5)

        self.rate_slider = tk.Scale(control_frame, from_=-100, to=100, orient=tk.HORIZONTAL, length=200)
        self.rate_slider.grid(row=0, column=1, padx=5)

        pitch_label = tk.Label(control_frame, text="语调:", font=("Helvetica", 12))
        pitch_label.grid(row=1, column=0, padx=5)

        self.pitch_slider = tk.Scale(control_frame, from_=-50, to=50, orient=tk.HORIZONTAL, length=200)
        self.pitch_slider.grid(row=1, column=1, padx=5)

        voice_label = tk.Label(control_frame, text="音色:", font=("Helvetica", 12))
        voice_label.grid(row=2, column=0, padx=5)

        self.voice_combobox = tk.StringVar()
        self.voice_combobox.set("晓晓")
        self.voice_dropdown = tk.OptionMenu(control_frame, self.voice_combobox, "晓晓", "晓伊", "云健", "云希", "云扬",
                                            "云夏", "陕西方言")
        self.voice_dropdown.config(font=("Helvetica", 12))
        self.voice_dropdown.grid(row=2, column=1, padx=5)

        generate_button = tk.Button(self, text="生成语音", command=self.start_generate_speech,
                                    font=("Helvetica", 14, "bold"),
                                    bg="#4CAF50", fg="white")
        generate_button.pack(padx=10, pady=10)

        self.progress_bar = ttk.Progressbar(self, mode="indeterminate")
        self.progress_bar.pack(padx=10, pady=10, fill=tk.X)

        self.play_button = tk.Button(self, text="播放语音", command=self.play_audio, font=("Helvetica", 14, "bold"),
                                     bg="#4CAF50", fg="white", state=tk.DISABLED)
        self.play_button.pack(padx=10, pady=10)

    async def text_to_speech(self, text, rate, pitch, voice):
        filename = datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".mp3"
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await communicate.save(filename)
        self.audio_filename = filename

    def generate_speech(self):
        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("警告", "请输入文本内容")
            return

        rate = f"{self.rate_slider.get():+d}%"
        pitch_value = self.pitch_slider.get()
        pitch = f"{pitch_value:+d}Hz" if pitch_value != 0 else "+0Hz"  # 如果pitch为0，则设置为字符串"0Hz"
        voice = self.voice_combobox.get()
        voice_code = voice_mapping[voice]

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.text_to_speech(text, rate, pitch, voice_code))

        self.progress_bar.stop()
        self.play_button.config(state=tk.NORMAL)
        messagebox.showinfo("完成", f"语音生成完毕，保存在{self.audio_filename}")

    def start_generate_speech(self):
        self.progress_bar.start()
        threading.Thread(target=self.generate_speech).start()

    def play_audio(self):
        if hasattr(self, "audio_filename"):
            pygame.mixer.init()
            pygame.mixer.music.load(self.audio_filename)
            pygame.mixer.music.play()
        else:
            messagebox.showwarning("警告", "没有可播放的语音文件")


# 定义可用的音色和对应的中文名称
voice_mapping = {
    "晓晓": "zh-CN-XiaoxiaoNeural",
    "晓伊": "zh-CN-XiaoyiNeural",
    "云健": "zh-CN-YunjianNeural",
    "云希": "zh-CN-YunxiNeural",
    "云扬": "zh-CN-YunyangNeural",
    "云夏": "zh-CN-YunxiaNeural",
    "陕西方言": "zh-CN-shaanxi-XiaoniNeural",
}

if __name__ == '__main__':
    root = tk.Tk()
    app = TTSApp(root)
    root.mainloop()
