import tkinter as tk
from tkinter import ttk, scrolledtext, font, filedialog
import tkinterdnd2 as tkdnd
from nfe_parser import NFeParse, format_dict
from language_config import TRANSLATIONS
from language_selector import get_language
import os

class NFEGUI(tkdnd.Tk):
    def __init__(self):
        super().__init__()
        
        # 获取用户选择的语言
        self.lang_code = get_language()
        if not self.lang_code:  # 如果用户没有选择语言（关闭窗口），默认使用中文
            self.lang_code = 'zh_CN'
        
        # 获取翻译文本
        self.texts = TRANSLATIONS[self.lang_code]
        
        # 设置窗口标题和大小
        self.title(self.texts['window_title'])
        self.geometry("1200x800")
        
        # 创建主框架
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建顶部按钮区域
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 创建选择文件按钮
        self.select_button = ttk.Button(
            self.button_frame, 
            text=self.texts['select_file_btn'],
            command=self.select_file
        )
        self.select_button.pack(side=tk.LEFT, padx=5)
        
        # 创建选项卡
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 创建各个选项卡页面
        self.tabs = {
            self.texts['tab_bling']: tk.Text(self.notebook, wrap=tk.WORD, state='disabled'),
            self.texts['tab_basic']: scrolledtext.ScrolledText(self.notebook, wrap=tk.WORD, state='disabled'),
            self.texts['tab_emitter']: scrolledtext.ScrolledText(self.notebook, wrap=tk.WORD, state='disabled'),
            self.texts['tab_recipient']: scrolledtext.ScrolledText(self.notebook, wrap=tk.WORD, state='disabled'),
            self.texts['tab_products']: scrolledtext.ScrolledText(self.notebook, wrap=tk.WORD, state='disabled'),
            self.texts['tab_transport']: scrolledtext.ScrolledText(self.notebook, wrap=tk.WORD, state='disabled'),
            self.texts['tab_payment']: scrolledtext.ScrolledText(self.notebook, wrap=tk.WORD, state='disabled'),
            self.texts['tab_total']: scrolledtext.ScrolledText(self.notebook, wrap=tk.WORD, state='disabled'),
            self.texts['tab_additional']: scrolledtext.ScrolledText(self.notebook, wrap=tk.WORD, state='disabled')
        }

        # 添加选项卡到notebook
        for tab_name, text_widget in self.tabs.items():
            self.notebook.add(text_widget, text=tab_name)
            text_widget.config(font=('Courier', 10))

        # 为Bling税务验证页面创建特殊字体
        self.bold_font = font.Font(family='Courier', size=16, weight='bold')
        self.normal_font = font.Font(family='Courier', size=10)
        self.title_font = font.Font(family='Courier', size=12, weight='bold')
        self.small_result_font = font.Font(family='Courier', size=12, weight='bold')
        
        # 设置初始提示文本
        self.show_welcome_message()
        
        # 注册整个窗口的拖拽事件
        self.drop_target_register(tkdnd.DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_drop)
        
        # 为每个Text widget注册拖拽事件
        for text_widget in self.tabs.values():
            text_widget.drop_target_register(tkdnd.DND_FILES)
            text_widget.dnd_bind('<<Drop>>', self.handle_drop)
    
    def select_file(self):
        """处理文件选择"""
        file_path = filedialog.askopenfilename(
            title=self.texts['select_file_btn'],
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        if file_path:
            self.process_file(file_path)
    
    def handle_drop(self, event):
        """处理文件拖拽"""
        file_path = event.data
        # 处理Windows路径中的花括号
        file_path = file_path.strip('{}')
        self.process_file(file_path)
    
    def process_file(self, file_path):
        """处理XML文件"""
        try:
            # 读取XML文件
            with open(file_path, 'r', encoding='utf-8') as file:
                xml_data = file.read()
            
            # 解析XML
            nfe = NFeParse(xml_data)
            
            # 清空所有选项卡
            for text_widget in self.tabs.values():
                text_widget.config(state='normal')
                text_widget.delete(1.0, tk.END)
            
            # 显示文件名
            file_info = f"{self.texts['filename']}: {os.path.basename(file_path)}\n\n"
            for text_widget in self.tabs.values():
                text_widget.insert(tk.END, file_info)
            
            # 显示Bling税务验证信息
            bling_total = nfe.calculate_bling_total()
            tax_total = nfe.calculate_tax_total()
            xml_total = float(nfe.get_totals()['发票总额'])
            
            # 使用Text widget的tag功能来设置不同的字体和样式
            bling_tab = self.tabs[self.texts['tab_bling']]
            bling_tab.tag_configure('title', font=self.title_font)
            bling_tab.tag_configure('normal', font=self.normal_font)
            bling_tab.tag_configure('result', font=self.bold_font, foreground='blue')
            bling_tab.tag_configure('small_result', font=self.small_result_font, foreground='blue')
            bling_tab.tag_configure('warning', font=self.bold_font, foreground='red')
            bling_tab.tag_configure('success', font=self.bold_font, foreground='green')
            
            # 插入标题
            bling_tab.insert(tk.END, f"\n=== {self.texts['tab_bling']} ===\n\n", 'title')
            
            # 插入发票实际金额计算
            bling_tab.insert(tk.END, f"{self.texts['tax_invoice_amount']}：\n", 'title')
            bling_tab.insert(tk.END, "Total dos Produtos (R$) + Valor do Frete (R$) + Valor outras despesas\n", 'normal')
            bling_tab.insert(tk.END, f"{bling_total:.2f} = {nfe.get_totals()['商品总价']:.2f} + {nfe.get_totals()['运费']:.2f} + {nfe.get_totals()['其他费用']:.2f}\n\n", 'normal')
            
            # 插入税务金额计算
            bling_tab.insert(tk.END, f"{self.texts['tax_amount']}：\n", 'title')
            bling_tab.insert(tk.END, "II + IPI + PIS + COFINS + ICMS\n", 'normal')
            bling_tab.insert(tk.END, f"{tax_total:.2f} = {nfe.get_totals()['进口税']:.2f} + {nfe.get_totals()['IPI金额']:.2f} + {nfe.get_totals()['PIS金额']:.2f} + {nfe.get_totals()['COFINS金额']:.2f} + {nfe.get_totals()['ICMS金额']:.2f}\n\n", 'normal')
            
            # 插入最终结果（居中显示）
            bling_tab.insert(tk.END, "\n" + "="*50 + "\n\n", 'title')
            bling_tab.insert(tk.END, f"{self.texts['tax_invoice_amount']} = ", 'title')
            bling_tab.insert(tk.END, f"R$ {bling_total:.2f}\n\n", 'result')
            bling_tab.insert(tk.END, f"{self.texts['xml_invoice_amount']} = ", 'title')
            bling_tab.insert(tk.END, f"R$ {xml_total:.2f}\n\n", 'small_result')
            
            # 比较金额并显示结果
            if abs(bling_total - xml_total) < 0.01:  # 考虑浮点数精度，差异小于0.01认为相等
                bling_tab.insert(tk.END, f"{self.texts['amount_verification']}: ", 'title')
                bling_tab.insert(tk.END, f"{self.texts['amount_match']}\n\n", 'success')
            else:
                bling_tab.insert(tk.END, f"{self.texts['amount_verification']}: ", 'title')
                bling_tab.insert(tk.END, f"{self.texts['amount_mismatch']}\n", 'warning')
                difference = abs(bling_total - xml_total)
                bling_tab.insert(tk.END, f"{self.texts['difference_amount']}: R$ {difference:.2f}\n\n", 'warning')
            
            bling_tab.insert(tk.END, f"{self.texts['tax_amount']} = ", 'title')
            bling_tab.insert(tk.END, f"R$ {tax_total:.2f}\n", 'result')
            bling_tab.insert(tk.END, "\n" + "="*50 + "\n", 'title')
            
            # 显示其他信息
            self.tabs[self.texts['tab_basic']].insert(tk.END, format_dict(nfe.get_basic_info()))
            self.tabs[self.texts['tab_emitter']].insert(tk.END, format_dict(nfe.get_emitter_info()))
            self.tabs[self.texts['tab_recipient']].insert(tk.END, format_dict(nfe.get_recipient_info()))
            
            # 显示商品信息
            products = nfe.get_products()
            for i, product in enumerate(products, 1):
                self.tabs[self.texts['tab_products']].insert(tk.END, f"\n=== {self.texts['product_details']} {i} ===\n")
                self.tabs[self.texts['tab_products']].insert(tk.END, format_dict(product))
            
            # 显示运输信息
            transport_info = nfe.get_transport_info()
            if transport_info:
                self.tabs[self.texts['tab_transport']].insert(tk.END, format_dict(transport_info))
            else:
                self.tabs[self.texts['tab_transport']].insert(tk.END, self.texts['no_transport_info'])
            
            # 显示支付信息
            payment_info = nfe.get_payment_info()
            if payment_info:
                for i, payment in enumerate(payment_info, 1):
                    self.tabs[self.texts['tab_payment']].insert(tk.END, f"\n=== {self.texts['payment_details']} {i} ===\n")
                    self.tabs[self.texts['tab_payment']].insert(tk.END, format_dict(payment))
            else:
                self.tabs[self.texts['tab_payment']].insert(tk.END, self.texts['no_payment_info'])
            
            # 显示总计信息
            self.tabs[self.texts['tab_total']].insert(tk.END, format_dict(nfe.get_totals()))
            
            # 显示补充信息
            additional_info = nfe.get_additional_info()
            if additional_info:
                self.tabs[self.texts['tab_additional']].insert(tk.END, format_dict(additional_info))
            else:
                self.tabs[self.texts['tab_additional']].insert(tk.END, self.texts['no_additional_info'])
            
            # 处理完成后，将所有文本框设置为只读
            for text_widget in self.tabs.values():
                text_widget.config(state='disabled')
            
            # 自动切换到Bling税务验证选项卡
            self.notebook.select(0)
                
        except Exception as e:
            for text_widget in self.tabs.values():
                text_widget.config(state='normal')
                text_widget.delete(1.0, tk.END)
                text_widget.insert(tk.END, f"{self.texts['error_parse']}\n\n{self.texts['error_details']}：\n{str(e)}")
                text_widget.config(state='disabled')
    
    def show_welcome_message(self):
        """显示欢迎信息"""
        welcome_text = self.texts['welcome_title'] + "\n\n" + self.texts['instructions'] + "\n" + self.texts['start_usage']
        
        for text_widget in self.tabs.values():
            text_widget.config(state='normal')
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, welcome_text)
            text_widget.config(state='disabled')

def main():
    app = NFEGUI()
    app.mainloop()

if __name__ == '__main__':
    main() 