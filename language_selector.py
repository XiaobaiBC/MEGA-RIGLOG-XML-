import tkinter as tk
from tkinter import ttk

class LanguageSelector(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # 设置窗口
        self.title("Language Selection / 语言选择 / Seleção de Idioma")
        self.geometry("400x300")
        self.resizable(False, False)
        
        # 居中窗口
        self.center_window()
        
        # 创建主框架
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题标签
        title_label = ttk.Label(
            main_frame,
            text="Please select your language\n请选择您的语言\nPor favor, selecione seu idioma",
            font=('Arial', 12, 'bold'),
            justify=tk.CENTER
        )
        title_label.pack(pady=20)
        
        # 创建语言按钮
        style = ttk.Style()
        style.configure('Language.TButton', font=('Arial', 11), padding=10)
        
        # 简体中文按钮
        self.zh_btn = ttk.Button(
            main_frame,
            text="简体中文",
            style='Language.TButton',
            command=lambda: self.select_language('zh_CN')
        )
        self.zh_btn.pack(fill=tk.X, pady=5)
        
        # English button
        self.en_btn = ttk.Button(
            main_frame,
            text="English",
            style='Language.TButton',
            command=lambda: self.select_language('en_US')
        )
        self.en_btn.pack(fill=tk.X, pady=5)
        
        # Português button
        self.pt_btn = ttk.Button(
            main_frame,
            text="Português",
            style='Language.TButton',
            command=lambda: self.select_language('pt_BR')
        )
        self.pt_btn.pack(fill=tk.X, pady=5)
        
        self.selected_language = None
        
    def center_window(self):
        """将窗口居中显示"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def select_language(self, lang_code):
        """选择语言"""
        self.selected_language = lang_code
        self.quit()
        
def get_language():
    """显示语言选择窗口并返回选择的语言代码"""
    app = LanguageSelector()
    app.mainloop()
    selected_language = app.selected_language
    app.destroy()
    return selected_language 