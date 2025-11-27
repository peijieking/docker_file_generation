import tkinter as tk
from tkinter import ttk

class ScoreTableApp:
    def __init__(self, root):
        self.root = root
        self.root.title("评分表")
        self.root.geometry("800x650")
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 上部分：要求区域
        self.create_requirements_section(main_frame)
        
        # 下部分：轮次选择区域
        self.create_rounds_section(main_frame)
        
        # 底部：成功交付成果
        self.create_result_section(main_frame)
    
    def create_requirements_section(self, parent):
        # 要求区域框架
        req_frame = ttk.LabelFrame(parent, text="要求", padding="10")
        req_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 三轮输入区域
        round_labels = ["第一轮", "第二轮", "第三轮"]
        self.round_texts = []
        
        for i, label_text in enumerate(round_labels):
            row_frame = ttk.Frame(req_frame)
            row_frame.pack(fill=tk.X, pady=(5, 5))
            
            # 轮次标签
            label = ttk.Label(row_frame, text=label_text, width=10)
            label.pack(side=tk.LEFT, padx=(0, 10))
            
            # 单行输入框
            entry = ttk.Entry(row_frame, width=60)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.round_texts.append(entry)
    
    def create_rounds_section(self, parent):
        # 轮次选择区域框架
        rounds_frame = ttk.LabelFrame(parent, text="轮次", padding="10")
        rounds_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 创建变量存储轮次输入和评分选择
        self.round_entries = []
        self.extra_entries = []  # 新增：额外的单行输入框
        self.rating_vars = [tk.StringVar(value="") for _ in range(3)]
        
        round_labels = ["第一轮", "第二轮", "第三轮"]
        
        for i, label_text in enumerate(round_labels):
            row_frame = ttk.Frame(rounds_frame)
            row_frame.pack(fill=tk.X, pady=(5, 5))
            
            # 轮次标签
            label = ttk.Label(row_frame, text=label_text, width=10)
            label.pack(side=tk.LEFT, padx=(0, 10))
            
            # 轮次输入框
            round_entry = ttk.Entry(row_frame, width=5)
            round_entry.pack(side=tk.LEFT)
            self.round_entries.append(round_entry)
            
            # "轮"文本
            wheel_label = ttk.Label(row_frame, text="轮")
            wheel_label.pack(side=tk.LEFT, padx=(2, 10))
            
            # 下拉框 - 评分选择
            rating_combo = ttk.Combobox(row_frame, textvariable=self.rating_vars[i], values=["好", "一般", "差"], width=10)
            rating_combo.pack(side=tk.LEFT, padx=(0, 10))
            # 初始为空，不设置默认选中项
    
    # 移除了不再需要的set_result方法，因为现在使用下拉框直接选择评分
    
    def create_result_section(self, parent):
        # 成功交付成果标签
        result_label = ttk.Label(parent, text="成功交付成果", font=("Arial", 12, "bold"))
        result_label.pack(anchor=tk.W, pady=(10, 10))

if __name__ == "__main__":
    root = tk.Tk()
    app = ScoreTableApp(root)
    root.mainloop()