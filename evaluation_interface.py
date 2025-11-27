
# -*- coding: utf-8 -*-
"""
评估界面 - 上下结构
上面：输入框 + Add Path 按钮
下面：标签框显示评估指标

功能说明：
- 支持多种评估指标：任务完成轮次、语言统一、重复动作、成功交付成果、上下文理解、工具调用、用户ID
- 每个标签页显示相应的评分标准和示例内容
- 支持markdown格式文本显示，提供美观的界面效果
- 包含用户ID信息显示功能
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import re
import glob
import json
import urllib.parse


# 语言统一页面的评分标准
language_unity_scoring = """
# 0分 
除专有名词外，频繁切换为英语，模型表现差。 
# 1分 
除专有名词外，偶尔切换为英语，模型表现一般。 
# 2分 
除专有名词外,模型全程纯中文，无任何中英文混用"""

# 工具调用页面的评分标准
tool_calls_scoring = """
根据评分标准，输出示例，根据 用户输入 进行仿写,仅对 工具调用 进行评论 

# 评分标准 
### 精简版评分标准
- 2分：自主调用合适工具，操作（查改代码/制定计划等）合理易懂，无无效/错误调用，工具使用精准高效。
- 1分：工具完成核心操作，多数行为合理；少量无效调用（如重复查看文件），无错误调用，不影响核心任务。
- 0分：工具调用严重问题，大量无效/错误调用（如改无关/敏感文件）；或必要时未调用，操作混乱，阻碍任务。

# 输出示例
## 评分
2分
## 依据
- 工具调用统计 ：总调用次数15次，成功15次，失败0次，正在执行0次，失败率0%
- 第一轮对话 ：调用5次工具,全部成功
- 第二轮对话 ：调用7次工具,全部成功
- 第三轮对话 ：调用3次工具,全部成功
模型自主调用合适的工具，无错误调用,无调用失败,工具使用精准高效，综合评分为2分。

# 用户输入
"""

# 上下文理解页面的评分标准
context_understanding_scoring = """
根据评分标准，输出示例，根据 用户输入 进行仿写,仅对 上下文理解 进行评论 

# 评分标准 
### 精简版评分标准
- 2分：准确理解用户需求，上下文理解准确，无理解偏差，模型表现好。
- 1分：基本理解用户需求，存在少量理解偏差但不影响核心任务，模型表现一般。
- 0分：严重理解偏差，无法准确理解用户需求，模型表现差。

# 输出示例
## 评分
2分
## 依据
- 第一轮对话 ：准确理解创建番茄钟应用的需求
- 第二轮对话 ：准确理解修复默认时间显示问题的需求
- 第三轮对话 ：准确理解添加自定义时长按钮功能的需求
模型准确理解用户需求，上下文理解准确，无理解偏差，综合评分为2分。

# 用户输入
"""

# 成功交付成果页面的评分标准
delivery_success_scoring = """
根据评分标准，输出示例，根据 用户输入 进行仿写,仅对 成功交付成果 进行评论 

# 评分标准 
### 精简版评分标准
0 分：模型无法完成任务，或交付物严重不满足要求，表现差。
1 分：模型能完成任务，但交付物质量一般，存在一些明显不足，表现一般。
2 分：模型出色完成任务，交付物完全满足要求且质量较高，表现好。

# 输出示例
## 评分
2分
## 依据
- 第一轮对话 ：成功创建番茄钟应用
- 第二轮对话 ：成功修复默认时间显示问题
- 第三轮对话 ：成功添加自定义时长按钮功能
模型成功交付所有成果，功能完整可用，综合评分为2分。

# 用户输入
"""

# 任务完成轮次标签的默认文字
task_rounds_text_default = """
根据评分标准，输出示例，根据 用户输入 进行仿写,仅对 任务完成轮次 进行评论 

# 要求
- 限制在100字内
- 使用 - 符号进行列表项编号
- 分析要具体到代码中的变量或函数
- 单轮对话重复命令小于5次不是异常

# 评分标准 
0分: 模型完成任务花费的轮次极多，存在反复检查文件，反复思考类似问题，轮次表现差 
1分: 模型完成任务花费轮次适中，轮次表现一般 
2分: 模型完成任务花费轮次极少，轮次表现好 

# 输出示例 
## 评分 
0分 
## 依据 
- 第一轮对话 ：共5轮,创建完整番茄钟应用并验证，轮次合理 
- 第二轮对话 ：共6轮,成功修复默认时间显示问题并验证，轮次合理 
- 第三轮对话 ：共5轮,添加自定义时长按钮功能,轮次合理 
综上,三轮对话总轮次16轮，模型表现高效

# 用户输入
"""

# 重复动作标签的默认文字
repetition_actions_text_default = """
根据评分标准，输出示例，根据 用户输入 进行仿写,仅对 重复动作 进行评论 
# 要求
- 限制在100字内
- 使用 - 符号进行列表项编号
- 分析要具体到代码中的变量或函数
- 单轮对话重复命令小于5次不是异常

# 评分标准 
0分：模型存在大量无意义重复行为，进行低效分析或工具调用，表现差。 
1分：模型偶有少量重复分析或工具调用，但不影响核心任务完成，表现一般。 
2分：模型无重复行为，分析精准，工具调用高效且必要，表现好。 

# 输出示例 
## 评分 
2分 
## 依据 
- 第一轮 
- 第二轮 
- 第三轮 
综上，...,所以综合评分为x分

# 用户输入
"""

# 用户ID标签的默认文字
user_id_text_default = """
#Trae UID 
公司电脑:   2860245352454452 
家用电脑： 3088943772611786 

# 一面千识 用户 ID 
2111
"""

class EvaluationInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("评估界面")
        self.root.geometry("800x600")
        
        # 设置窗口居中显示
        self.center_window()
        
        # 设置样式
        self.setup_styles()
        
        # 创建界面
        self.create_interface()
    
    def center_window(self):
        """将窗口居中显示"""
        # 更新窗口以确保获取正确的尺寸
        self.root.update_idletasks()
        
        # 获取屏幕宽度和高度
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 获取窗口宽度和高度
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        
        # 如果窗口尺寸为1（默认值），使用geometry设置的尺寸
        if window_width <= 1 or window_height <= 1:
            geometry = self.root.geometry()
            if 'x' in geometry:
                parts = geometry.split('x')
                if len(parts) >= 2:
                    window_width = int(parts[0])
                    window_height = int(parts[1].split('+')[0])
        
        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2-40
        
        # 设置窗口位置
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def setup_styles(self):
        """设置ttk样式"""
        style = ttk.Style()
        
        # 配置标签框样式
        style.configure("CustomLabelframe.TLabelframe", 
                        background="#f0f0f0", 
                        bordercolor="#cccccc",
                        relief="solid")
        style.configure("CustomLabelframe.TLabelframe.Label", 
                       background="#f0f0f0",
                       foreground="#333333",
                       font=('Arial', 10, 'bold'))
        
        # 配置按钮样式
        style.configure("Custom.TButton",
                       font=('Arial', 9),
                       padding=(10, 5))
        
        # 配置输入框样式
        style.configure("Custom.TEntry",
                       font=('Arial', 9),
                       padding=(5, 5))
        
    def create_interface(self):
        """创建界面组件"""
        
        # 上面部分：输入框和按钮
        self.create_top_section()
        
        # 下面部分：标签框
        self.create_bottom_section()
        
        # 底部状态栏
        self.create_status_bar()
        
        # 自动获取并分析已打开的窗口目录
        self.auto_analyze_opened_windows()
        
    def create_top_section(self):
        """创建上面部分 - 输入框和按钮"""
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=5)
        
        # 选择目录标签
        input_label = ttk.Label(top_frame, text="选择目录:", font=('Arial', 9))
        input_label.grid(row=0, column=0, sticky="w", padx=(0, 5))
        
        # 下拉选择框 - 显示当前目录和已打开的窗口目录
        self.folder_var = tk.StringVar()
        self.folder_combo = ttk.Combobox(top_frame, 
                                        textvariable=self.folder_var,
                                        width=50, 
                                        font=('Arial', 9))
        self.folder_combo.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        
        # 设置当前目录为默认值
        current_dir = os.getcwd()
        self.folder_var.set(current_dir)
        
        # 自动获取已打开的窗口目录并添加到下拉框
        try:
            folders = read_opened_windows_folders_from_trae_storage()
            # 如果获取到目录，添加到下拉框（避免重复）
            if folders:
                # 确保当前目录在列表中且在首位
                all_folders = [current_dir] + [f for f in folders if f != current_dir]
                self.folder_combo['values'] = all_folders
        except Exception as e:
            print(f"获取已打开目录时出错: {e}")
        
        # 选择目录按钮
        self.add_button = ttk.Button(top_frame, 
                                   text="选择目录", 
                                   style="Custom.TButton",
                                   command=self.on_directory_action)
        self.add_button.grid(row=0, column=2, padx=(0, 0))
        
        # 配置网格权重
        top_frame.columnconfigure(1, weight=1)
        
        # 绑定下拉选择框事件
        self.folder_combo.bind('<<ComboboxSelected>>', self.on_folder_selected)
        
        # 初始化path_entry属性（为了兼容性）
        self.path_entry = self.folder_combo
        
    def create_bottom_section(self):
        """创建下面部分 - 可点击的标签页"""
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill="both", expand=True, padx=10, pady=(2, 10))
        
        # 创建Notebook（标签页容器）
        self.notebook = ttk.Notebook(bottom_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # 定义评估指标
        evaluation_metrics = [
            "git push",
            "任务完成轮次",
            "语言统一", 
            "重复动作",
            "成功交付成果",
            "上下文理解",
            "工具调用",
            "用户ID"
        ]
        
        # 创建标签页
        self.create_tabs(evaluation_metrics)
        
        # 绑定标签页切换事件
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def create_status_bar(self):
        """创建底部状态栏"""
        # 创建状态栏框架
        status_frame = ttk.Frame(self.root, relief="sunken", borderwidth=1)
        status_frame.pack(side="bottom", fill="x", padx=10, pady=(0, 5))
        
        # 状态栏标签
        self.status_label = ttk.Label(status_frame, 
                                     text="就绪", 
                                     font=('Arial', 9),
                                     foreground="#666666",
                                     anchor="w")
        self.status_label.pack(side="left", fill="x", expand=True, padx=5, pady=2)
    
    def update_status(self, message):
        """更新状态栏消息"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message)
            # 3秒后自动清除状态消息
            self.root.after(3000, lambda: self.status_label.config(text="就绪"))
        
    def create_tabs(self, metrics):
        """创建多个标签页"""
        
        for metric in metrics:
            # 为每个指标创建一个标签页
            tab_frame = ttk.Frame(self.notebook, padding="10")
            self.notebook.add(tab_frame, text=metric)
            
            # 创建标签页内容
            self.create_tab_content(tab_frame, metric)
            
    def create_tab_content(self, parent, title):
        """创建单个标签页的内容"""
        # 特殊处理git push标签页
        if title == "git push":
            self.create_git_push_tab_content(parent)
            return
        
        # 创建内容框架
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill="both", expand=True)
        
        # 创建文本区域和按钮的容器
        text_button_frame = ttk.Frame(content_frame)
        text_button_frame.pack(fill="both", expand=True)
        
        # 创建文本区域
        text_frame = ttk.Frame(text_button_frame)
        text_frame.pack(fill="both", expand=True)
        
        # 文本区域 - 设置为可编辑模式
        content_text = tk.Text(text_frame, 
                              font=('Arial', 10),
                              wrap="word",
                              bg="#f9f9f9",
                              relief="solid",
                              borderwidth=1)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=content_text.yview)
        content_text.configure(yscrollcommand=scrollbar.set)
        
        content_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 插入示例内容
        sample_content = self.get_sample_content(title)
        content_text.insert("1.0", sample_content)
        # 不再设置为只读，保持可编辑状态
        
        # 创建按钮框架（放在右下角）
        button_frame = ttk.Frame(text_button_frame)
        button_frame.pack(side="bottom", fill="x", pady=(10, 0))
        
        # 为所有标签页添加复制按钮
        copy_button = ttk.Button(button_frame, 
                               text="复制内容",
                               style="Custom.TButton",
                               command=lambda: self.copy_text_content(content_text))
        copy_button.pack(side="right", padx=(10, 0))
        
        # 存储文本组件引用
        setattr(self, f"{title.replace(' ', '_').lower()}_text", content_text)

    def create_git_push_tab_content(self, parent):
        """创建git push标签页的上下结构布局"""
        # 创建主框架
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill="both", expand=True)
        
        # 上方区域：分支名称输入框
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill="x", padx=20, pady=20)
        
        # 分支名称标签
        branch_label = ttk.Label(top_frame, text="分支名称:", font=('Arial', 10, 'bold'))
        branch_label.pack(side="left", padx=(0, 10))
        
        # 分支名称输入框
        self.branch_entry = ttk.Entry(top_frame, font=('Arial', 10), width=30)
        self.branch_entry.pack(side="left", padx=(0, 20))
        self.branch_entry.insert(0, "seed_01")  # 默认值
        
        # 下方区域：命令显示区
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        
        # 命令显示文本区域
        commands_frame = ttk.Frame(bottom_frame)
        commands_frame.pack(fill="both", expand=True)
        
        self.commands_text = tk.Text(commands_frame, 
                                   font=('Courier New', 10),
                                   wrap="word",
                                   bg="#f5f5f5",
                                   relief="solid",
                                   borderwidth=1,
                                   state="normal")
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(commands_frame, orient="vertical", command=self.commands_text.yview)
        self.commands_text.configure(yscrollcommand=scrollbar.set)
        
        self.commands_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 创建按钮框架（放在右下角）
        button_frame = ttk.Frame(bottom_frame)
        button_frame.pack(side="bottom", fill="x", pady=(10, 0))
        
        # 添加复制按钮
        copy_button = ttk.Button(button_frame, 
                               text="复制内容",
                               style="Custom.TButton",
                               command=lambda: self.copy_text_content(self.commands_text))
        copy_button.pack(side="right", padx=10, pady=5)
        
        # 初始显示命令
        self.update_git_commands_display()
        
        # 绑定分支名称输入框的变化事件
        self.branch_entry.bind('<KeyRelease>', lambda event: self.update_git_commands_display())

    def update_git_commands_display(self):
        """根据分支名称更新命令显示"""
        branch_name = self.branch_entry.get().strip()
        if not branch_name:
            branch_name = "seed_01"
        
        commands = f"""git checkout main
git checkout -b {branch_name}
git add .
git commit -m update
git push -u origin {branch_name}"""
        
        self.commands_text.config(state="normal")
        self.commands_text.delete("1.0", "end")
        self.commands_text.insert("1.0", commands)
        self.commands_text.config(state="disabled")

    def execute_git_commands(self):
        """执行Git命令序列"""
        branch_name = self.branch_entry.get().strip()
        if not branch_name:
            messagebox.showerror("错误", "请输入分支名称")
            return
        
        # 导入git_operations模块
        from git_operations import execute_git_commands
        
        # 执行Git命令
        success, message = execute_git_commands(branch_name)
        
        if success:
            messagebox.showinfo("成功", f"Git命令执行成功！\n{message}")
        else:
            messagebox.showerror("错误", f"Git命令执行失败！\n{message}")
        
    def on_tab_changed(self, event):
        """标签页切换事件处理"""
        current_tab = self.notebook.index(self.notebook.select())
        tab_text = self.notebook.tab(current_tab, "text")
        print(f"切换到标签页: {tab_text}")
        

        
    def get_sample_content(self, title):
        """根据标题获取示例内容"""
        sample_contents = {
            "任务完成轮次": "当前任务已完成3轮对话\n- 第一轮：创建基础工具\n- 第二轮：界面优化\n- 第三轮：功能完善",
            "语言统一": "# 0分 \n除专有名词外，频繁切换为英语，模型表现差。 \n# 1分 \n除专有名词外，偶尔切换为英语，模型表现一般。 \n# 2分 \n除专有名词外,模型全程纯中文，无任何中英文混用",
            "重复动作": "检测到2次重复操作：\n- 文件路径验证\n- 界面刷新",
            "成功交付成果": delivery_success_scoring,
            "上下文理解": context_understanding_scoring,
            "工具调用": tool_calls_scoring,
            "用户ID": user_id_text_default
        }
        return sample_contents.get(title, "暂无数据")
        
    def add_path(self):
        """处理Add Path按钮点击事件 - 兼容旧代码"""
        self.on_directory_action()
        
    def on_directory_action(self):
        """选择目录按钮的回调函数 - 直接打开文件选择对话框"""
        # 直接弹出目录选择对话框
        selected_path = filedialog.askdirectory(
            title="选择包含log文件的目录",
            initialdir=os.getcwd()
        )
        
        if not selected_path:
            return  # 用户取消了选择
            
        # 更新下拉框的值
        self.folder_var.set(selected_path)
        
        # 检查是否需要将新选择的目录添加到下拉列表中
        current_values = list(self.folder_combo['values'])
        if selected_path not in current_values:
            # 将新目录添加到列表首位
            current_values.insert(0, selected_path)
            self.folder_combo['values'] = current_values
        
        # 调用process_selected_folder处理目录
        self.process_selected_folder(selected_path)
        
        # 更新状态栏
        self.update_status(f"✓ 文件分析完成 + {selected_path}")
    
    def count_rounds_in_file(self, file_path):
        """统计指定文件中的轮次数量 - 使用count_rounds.py的方法"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # 使用正则表达式查找轮次标记
            # 模式："我"后面跟着任意字符，然后是"toolName:"
            pattern = r'我[\s\S]*?toolName:'
            matches = re.findall(pattern, content)
            
            # 统计轮次数量
            round_count = len(matches)
            
            return round_count
            
        except FileNotFoundError:
            print(f"错误: 文件 {file_path} 不存在")
            return 0
        except Exception as e:
            print(f"错误: 读取文件时发生异常 - {e}")
            return 0
             
    def count_tool_stats_in_file(self, file_path):
        """统计指定文件中的工具调用数据 - 使用count_tool_stats.py的方法"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # 使用正则表达式匹配toolName、status和command
            tool_pattern = r'toolName:\s*(\w+)'
            status_pattern = r'status:\s*(\w+)'
            command_pattern = r'command:\s*(.*?)(?=\n\s*\w+:|\Z)'
            
            # 查找所有匹配的toolName、status和command
            tool_names = re.findall(tool_pattern, content)
            statuses = re.findall(status_pattern, content)
            commands = re.findall(command_pattern, content, re.DOTALL)
            
            # 统计数量
            from collections import defaultdict
            tool_count = defaultdict(int)
            status_count = defaultdict(int)
            command_count = defaultdict(int)
            
            for tool in tool_names:
                tool_count[tool] += 1
            
            for status in statuses:
                status_count[status] += 1
            
            for command in commands:
                # 清理命令文本，去除多余空格和换行
                clean_command = command.strip()
                if clean_command:
                    command_count[clean_command] += 1
            
            # 计算各种状态的数量
            success_count = status_count.get('success', 0)
            running_count = status_count.get('running', 0)
            failed_count = status_count.get('failed', 0) + status_count.get('error', 0)
            
            # 计算失败率
            total_statuses = len(statuses)
            if total_statuses > 0:
                failure_rate = (failed_count / total_statuses) * 100
            else:
                failure_rate = 0
            
            return {
                'total_tools': len(tool_names),
                'success_count': success_count,
                'failed_count': failed_count,
                'running_count': running_count,
                'failure_rate': failure_rate,
                'tool_count': dict(tool_count),
                'status_count': dict(status_count),
                'command_count': dict(command_count),
                'total_commands': len(commands)
            }
            
        except FileNotFoundError:
            print(f"错误: 文件 {file_path} 不存在")
            return None
        except Exception as e:
            print(f"错误: 读取文件时发生异常 - {e}")
            return None
             
    def extract_human_comments(self, file_path):
        """提取指定文件中的人类评语 - 使用extract_human_comments.py的方法"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # 使用正则表达式匹配人类评语格式
            # 模式：# 人类评语\n```\n评语内容\n```
            pattern = r'# 人类评语\s*```\s*(.*?)\s*```'
            matches = re.findall(pattern, content, re.DOTALL)
            
            if matches:
                # 返回第一个人类评语（如果有多个，取第一个）
                return matches[0].strip()
            else:
                return "无人类评语"
                
        except FileNotFoundError:
            print(f"错误: 文件 {file_path} 不存在")
            return "文件不存在"
        except Exception as e:
            print(f"错误: 读取文件时发生异常 - {e}")
            return "读取错误"

    def copy_text_content(self, tab_name):
        """复制指定标签页的文本内容到剪贴板"""
        try:
            # 从text_widgets字典中获取对应的文本组件
            if hasattr(self, 'text_widgets') and tab_name in self.text_widgets:
                text_widget = self.text_widgets[tab_name]
                # 获取文本内容
                content = text_widget.get("1.0", "end-1c")
                if content:
                    # 复制到剪贴板
                    self.root.clipboard_clear()
                    self.root.clipboard_append(content)
                    # 在状态栏显示成功消息
                    self.update_status("✓ 内容已复制到剪贴板")
                else:
                    # 在状态栏显示失败消息
                    self.update_status("⚠ 文本内容为空，无法复制")
            else:
                # 在状态栏显示错误消息
                self.update_status(f"✗ 未找到标签页 '{tab_name}' 的文本组件")
        except Exception as e:
            # 在状态栏显示错误消息
            self.update_status(f"✗ 复制过程中发生错误: {str(e)}")
    
    def update_label_content(self, path, log_files, file_stats=None, total_rounds=0):
        """根据文件路径和log文件列表更新标签框内容"""
        try:
            content_text = getattr(self, "任务完成轮次_text")
            content_text.delete("1.0", "end")
            
            # 精简显示内容：使用全局变量
            stats_info = task_rounds_text_default
            
            # 显示各对话轮次统计
            if file_stats:
                stats_info += ""
                
                # 根据文件名生成对应的描述
                for stat in file_stats:
                    # 正确分割文件名和轮次信息
                    if ":" in stat:
                        filename, rounds_info = stat.split(":", 1)
                        filename = filename.strip()
                        rounds_info = rounds_info.strip()
                        
                        # 提取轮次数字
                        rounds_match = re.search(r'(\d+)', rounds_info)
                        if rounds_match:
                            rounds = rounds_match.group(1)
                        else:
                            rounds = "0"
                        
                        # 提取人类评语
                        human_comment = self.extract_human_comments(os.path.join(path, filename))
                        
                        # 根据文件名生成对应的轮次序号
                        if "第一轮" in filename:
                            round_num = "一"
                        elif "第二轮" in filename:
                            round_num = "二"
                        elif "第三轮" in filename:
                            round_num = "三"
                        else:
                            # 尝试从文件名中提取轮次信息
                            round_match = re.search(r'第(.*?)轮', filename)
                            if round_match:
                                round_num = round_match.group(1)
                            else:
                                round_num = "未知"
                        
                        # 按照新格式显示：第{x}轮对话 ：共{x}轮,{人类评语}
                        stats_info += f"第{round_num}轮对话 ：共{rounds}轮,{human_comment}\n"
                
                stats_info += "\n"
            
            content_text.insert("1.0", stats_info)
        except AttributeError:
            pass
    
    def update_tool_stats_content(self, path, log_files):
        """根据文件路径和log文件列表更新工具调用统计内容"""
        try:
            content_text = getattr(self, "工具调用_text")
            content_text.delete("1.0", "end")
            
            # 使用全局变量作为基础内容
            stats_info = tool_calls_scoring
            
            # 统计所有文件的工具调用数据
            if log_files:
                total_tools = 0
                total_success = 0
                total_failed = 0
                total_running = 0
                file_stats = []
                
                for log_file in sorted(log_files):
                    tool_stats = self.count_tool_stats_in_file(log_file)
                    if tool_stats:
                        filename = os.path.basename(log_file)
                        total_tools += tool_stats['total_tools']
                        total_success += tool_stats['success_count']
                        total_failed += tool_stats['failed_count']
                        total_running += tool_stats['running_count']
                        
                        # 根据文件名生成对应的轮次序号
                        if "第一轮" in filename:
                            round_num = "一"
                        elif "第二轮" in filename:
                            round_num = "二"
                        elif "第三轮" in filename:
                            round_num = "三"
                        else:
                            # 尝试从文件名中提取轮次信息
                            round_match = re.search(r'第(.*?)轮', filename)
                            if round_match:
                                round_num = round_match.group(1)
                            else:
                                round_num = "未知"
                        
                        # 计算当前文件的失败率
                        if tool_stats['total_tools'] > 0:
                            file_failure_rate = (tool_stats['failed_count'] / tool_stats['total_tools']) * 100
                        else:
                            file_failure_rate = 0
                        
                        file_stats.append(f"第{round_num}轮对话 ：总调用次数{tool_stats['total_tools']}次，成功{tool_stats['success_count']}次，失败{tool_stats['failed_count']}次，正在运行{tool_stats['running_count']}次")
                
                # 计算总失败率
                if total_tools > 0:
                    total_failure_rate = (total_failed / total_tools) * 100
                else:
                    total_failure_rate = 0
                
                # 添加各对话轮次统计
                if file_stats:
                    stats_info += ""
                    for stat in file_stats:
                        stats_info += f"{stat}\n"
                    
                    stats_info += f"\n综上,{len(log_files)}轮对话总调用次数{total_tools}次，成功{total_success}次，失败{total_failed}次，失败率{total_failure_rate:.0f}%"
                    
                    # 根据失败率添加评分建议
                    if total_failure_rate >= 50:
                        stats_info += "，模型表现差"
                    elif total_failure_rate >= 20:
                        stats_info += "，模型表现一般"
                    else:
                        stats_info += "，模型表现好"
                
                stats_info += "\n"
            
            content_text.insert("1.0", stats_info)
        except AttributeError:
            pass
    
    def update_context_content(self, path, log_files):
        """根据文件路径和log文件列表更新上下文理解内容"""
        try:
            content_text = getattr(self, "上下文理解_text")
            content_text.delete("1.0", "end")
            
            # 使用全局变量作为基础内容
            stats_info = context_understanding_scoring
            
            # 统计所有文件的人类评语数据
            if log_files:
                file_stats = []
                
                for log_file in sorted(log_files):
                    human_comment = self.extract_human_comments(log_file)
                    if human_comment and human_comment != "无人类评语":
                        filename = os.path.basename(log_file)
                        
                        # 根据文件名生成对应的轮次序号
                        if "第一轮" in filename:
                            round_num = "一"
                        elif "第二轮" in filename:
                            round_num = "二"
                        elif "第三轮" in filename:
                            round_num = "三"
                        else:
                            # 尝试从文件名中提取轮次信息
                            round_match = re.search(r'第(.*?)轮', filename)
                            if round_match:
                                round_num = round_match.group(1)
                            else:
                                round_num = "未知"
                        
                        file_stats.append(f"第{round_num}轮对话 ：{human_comment}")
                
                # 添加各对话轮次评语
                if file_stats:
                    stats_info += ""
                    for stat in file_stats:
                        stats_info += f"{stat}\n"
                
                stats_info += "\n"
            
            content_text.insert("1.0", stats_info)
        except AttributeError:
            pass
    
    def update_delivery_content(self, path, log_files):
        """根据文件路径和log文件列表更新成功交付成果内容"""
        try:
            content_text = getattr(self, "成功交付成果_text")
            content_text.delete("1.0", "end")
            
            # 使用全局变量作为基础内容
            stats_info = delivery_success_scoring
            
            # 统计所有文件的人类评语数据
            if log_files:
                file_stats = []
                
                for log_file in sorted(log_files):
                    human_comment = self.extract_human_comments(log_file)
                    if human_comment and human_comment != "无人类评语":
                        filename = os.path.basename(log_file)
                        
                        # 根据文件名生成对应的轮次序号
                        if "第一轮" in filename:
                            round_num = "一"
                        elif "第二轮" in filename:
                            round_num = "二"
                        elif "第三轮" in filename:
                            round_num = "三"
                        else:
                            # 尝试从文件名中提取轮次信息
                            round_match = re.search(r'第(.*?)轮', filename)
                            if round_match:
                                round_num = round_match.group(1)
                            else:
                                round_num = "未知"
                        
                        file_stats.append(f"第{round_num}轮对话 ：{human_comment}")
                
                # 添加各对话轮次交付成果
                if file_stats:
                    stats_info += "\n"
                    for stat in file_stats:
                        stats_info += f"{stat}\n"
                    
                stats_info += "\n"
            
            content_text.insert("1.0", stats_info)
        except AttributeError:
            pass

    def update_repetition_content(self, path, log_files):
        """根据文件路径和log文件列表更新重复动作内容，显示工具使用次数统计"""
        try:
            content_text = getattr(self, "重复动作_text")
            content_text.delete("1.0", "end")
            
            # 使用全局变量作为基础内容
            stats_info = repetition_actions_text_default
            
            # 统计所有文件的工具使用次数
            if log_files:
                all_tool_counts = {}
                all_command_counts = {}
                file_tool_stats = []
                file_command_stats = []
                
                for log_file in sorted(log_files):
                    tool_stats = self.count_tool_stats_in_file(log_file)
                    if tool_stats:
                        filename = os.path.basename(log_file)
                        
                        # 根据文件名生成对应的轮次序号
                        if "第一轮" in filename:
                            round_num = "一"
                            display_name = "第一轮对话"
                        elif "第二轮" in filename:
                            round_num = "二"
                            display_name = "第二轮对话"
                        elif "第三轮" in filename:
                            round_num = "三"
                            display_name = "第三轮对话"
                        else:
                            # 尝试从文件名中提取轮次信息
                            round_match = re.search(r'第(.*?)轮', filename)
                            if round_match:
                                round_num = round_match.group(1)
                            else:
                                round_num = "未知"
                            display_name = filename.replace("model_log_", "").replace(".md", "")
                        
                        # 统计当前文件的工具使用情况
                        tool_count = tool_stats['tool_count']
                        command_count = tool_stats['command_count']
                        
                        file_stat = f"第{round_num}轮对话工具使用统计:\n"
                        
                        if tool_count:
                            for tool_name, count in sorted(tool_count.items(), key=lambda x: x[1], reverse=True):
                                file_stat += f"  • {tool_name}: {count}次\n"
                                # 累加到总统计
                                if tool_name in all_tool_counts:
                                    all_tool_counts[tool_name] += count
                                else:
                                    all_tool_counts[tool_name] = count
                        else:
                            file_stat += "  无工具调用记录\n"
                        
                        file_tool_stats.append(file_stat)
                        
                        # 统计当前文件的命令使用情况
                        command_stat = f"第{round_num}轮对话命令使用统计:\n"
                        
                        if command_count:
                            for command, count in sorted(command_count.items(), key=lambda x: x[1], reverse=True):
                                # 简化命令显示，避免过长
                                short_command = command[:50] + "..." if len(command) > 50 else command
                                command_stat += f"  • {short_command}: {count}次\n"
                                # 累加到总统计
                                if command in all_command_counts:
                                    all_command_counts[command] += count
                                else:
                                    all_command_counts[command] = count
                        else:
                            command_stat += "  无命令调用记录\n"
                        
                        file_command_stats.append(command_stat)
                
                # 添加统计信息到基础内容
                if file_tool_stats:
                    stats_info += "\n"
                    stats_info += "各轮次工具使用情况:\n"
                    for stat in file_tool_stats:
                        stats_info += stat + "\n"

                # 显示各轮次命令使用统计
                if file_command_stats:
                    stats_info += "\n各轮次命令使用情况:\n"
                    for stat in file_command_stats:
                        stats_info += stat + "\n"
                    
                stats_info += "\n"
            
            content_text.insert("1.0", stats_info)
        except AttributeError:
            pass

    def auto_analyze_opened_windows(self):
        """自动获取并分析已打开的窗口目录"""
        try:
            # 获取已打开的窗口文件夹
            folders = read_opened_windows_folders_from_trae_storage()
            
            if not folders:
                # 没有找到已打开的窗口目录，保持显示示例内容
                self.update_status("未找到已打开的窗口目录，请手动选择目录")
                return
            
            # 更新下拉选择框的值
            current_values = list(self.folder_combo['values'])
            for folder in folders:
                if folder not in current_values:
                    current_values.append(folder)
            self.folder_combo['values'] = current_values
            
            # 默认选择第一个目录并自动开始分析
            if folders:
                selected_folder = folders[0]
                self.folder_var.set(selected_folder)
                
                # 立即开始分析目录
                self.process_selected_folder(selected_folder)
                
                # 更新状态栏
                self.update_status(f"✓ 已自动分析目录: {selected_folder}")
            
        except Exception as e:
            print(f"自动分析已打开目录时出错: {e}")
            # 出错时不显示错误对话框，避免干扰用户体验
            
    def auto_select_folder(self):
        """自动获取已打开的窗口目录并填充下拉选择框"""
        try:
            # 获取已打开的窗口文件夹
            folders = read_opened_windows_folders_from_trae_storage()
            
            if not folders:
                messagebox.showinfo("提示", "未找到任何已打开的窗口目录")
                return
            
            # 更新下拉选择框的值
            self.folder_combo['values'] = folders
            
            # 如果有多个目录，默认选择第一个
            if folders:
                self.folder_var.set(folders[0])
                
            # 更新状态栏
            self.update_status(f"成功获取 {len(folders)} 个已打开的窗口目录")
            
        except Exception as e:
            messagebox.showerror("错误", f"获取已打开目录时出错: {e}")
            self.update_status("获取已打开目录失败")

    def on_folder_selected(self, event):
        """当下拉选择框选择目录时自动解析"""
        selected_folder = self.folder_var.get()
        
        if not selected_folder:
            return
            
        # 自动执行目录解析
        self.process_selected_folder(selected_folder)
        
        # 更新状态栏
        self.update_status(f"✓ 文件分析完成 + {selected_folder}")

    def process_selected_folder(self, folder_path):
        """处理选择的文件夹，检查log文件并更新界面"""
        if not os.path.exists(folder_path):
            messagebox.showerror("错误", f"目录不存在: {folder_path}")
            return
            
        # 检查目录下是否存在log文件
        log_patterns = [
            "*model_log*轮对话*.md",
            "*model_log*.md",
            "*log*.md",
            "*对话*.md",
            "*round*.md",
            "*dialogue*.md"
        ]
        
        found_log_files = []
        for pattern in log_patterns:
            files = glob.glob(os.path.join(folder_path, pattern))
            found_log_files.extend(files)
        
        # 去重
        found_log_files = list(set(found_log_files))
        
        # 如果没有找到文件，尝试搜索所有.md文件
        if not found_log_files:
            all_md_files = glob.glob(os.path.join(folder_path, "*.md"))
            # 过滤掉README.md等非log文件
            found_log_files = [f for f in all_md_files if "readme" not in f.lower() and "readme" not in os.path.basename(f).lower()]
        
        if not found_log_files:
            messagebox.showerror(
                "错误",
                f"在目录 {folder_path} 中未找到log文件！\n\n"
                "请确保目录包含类似以下格式的文件：\n"
                "• 1_model_log_第一轮对话.md\n"
                "• 2_model_log_第二轮对话.md\n"
                "• 3_model_log_第三轮对话.md"
            )
            return
            
        # 更新所有标签页的内容
        self.update_all_tabs_content(folder_path, found_log_files)
        
        # 更新状态栏
        self.update_status(f"成功解析目录: {folder_path}")

    def count_tool_stats_in_files(self, log_files):
        """统计多个文件中的工具调用数据"""
        if not log_files:
            return {'file_stats': [], 'total_rounds': 0}
        
        file_stats = []
        total_rounds = 0
        
        for log_file in sorted(log_files):
            # 统计每个文件的对话轮次
            try:
                with open(log_file, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # 使用正则表达式统计对话轮次
                round_pattern = r'第.*?轮对话'
                rounds = len(re.findall(round_pattern, content))
                total_rounds += rounds
                
                filename = os.path.basename(log_file)
                file_stats.append(f"{filename}: {rounds}轮")
                
            except Exception as e:
                print(f"错误: 读取文件 {log_file} 时发生异常 - {e}")
        
        return {'file_stats': file_stats, 'total_rounds': total_rounds}

    def update_all_tabs_content(self, path, log_files):
        """更新所有标签页的内容"""
        # 统计工具使用情况
        tool_stats = self.count_tool_stats_in_files(log_files)
        
        # 更新任务完成轮次标签页
        self.update_label_content(path, log_files, tool_stats.get('file_stats', []), tool_stats.get('total_rounds', 0))
        
        # 更新工具调用标签页
        self.update_tool_stats_content(path, log_files)
        
        # 更新上下文理解标签页
        self.update_context_content(path, log_files)
        
        # 更新成功交付成果标签页
        self.update_delivery_content(path, log_files)
        
        # 更新重复动作标签页
        self.update_repetition_content(path, log_files)

    def create_git_push_tab_content(self, parent):
        """创建git push标签页的内容，位置1显示命令，位置2显示带下拉功能的分支输入框"""
        # 创建内容框架
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill="both", expand=True)
        
        # 位置1：命令显示区
        command_text = tk.Text(content_frame, wrap="word", font=('Arial', 10))
        command_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 存储文本组件引用
        if not hasattr(self, 'text_widgets'):
            self.text_widgets = {}
        self.text_widgets["git push"] = command_text
        
        # 默认命令内容
        default_branch = "seed_01"
        git_commands = self.generate_git_commands(default_branch)
        command_text.insert("1.0", git_commands)
        command_text.config(state="normal")
        
        # 位置2：分支输入框区域 - 与复制按钮在同一水平位置
        bottom_frame = ttk.Frame(content_frame)
        bottom_frame.pack(fill="x", padx=10, pady=10)
        
        # 左侧：分支标签和输入框
        branch_frame = ttk.Frame(bottom_frame)
        branch_frame.pack(side="left", fill="x", expand=True)
        
        # 分支标签
        branch_label = ttk.Label(branch_frame, text="分支名称:")
        branch_label.pack(side="left", padx=(0, 5))
        
        # 创建Combobox作为下拉输入框
        branch_values = ["seed_01", "seed_02", "seed_03", "main", "master"]  # 预设分支列表
        branch_var = tk.StringVar()
        branch_var.set(default_branch)  # 设置默认值
        
        branch_combo = ttk.Combobox(branch_frame, textvariable=branch_var, values=branch_values, width=20)
        branch_combo.pack(side="left", fill="x", expand=True, padx=(0, 10))
        branch_combo.config(state="normal")  # 允许用户输入
        
        # 右侧：复制按钮
        copy_button = ttk.Button(bottom_frame, text="复制内容", command=lambda: self.copy_text_content("git push"))
        copy_button.pack(side="right", padx=10, pady=5)
        
        # 绑定分支变更事件
        def on_branch_change(event):
            selected_branch = branch_var.get()
            git_commands = self.generate_git_commands(selected_branch)
            command_text.delete("1.0", tk.END)
            command_text.insert("1.0", git_commands)
        
        branch_combo.bind("<<ComboboxSelected>>", on_branch_change)
        branch_combo.bind("<KeyRelease>", lambda event: on_branch_change(event))
    
    def generate_git_commands(self, branch_name):
        """根据分支名称生成Git命令序列"""
        commands = f"# 切换到main分支并拉取最新代码\ngit checkout main\ngit pull origin main\n\n# 创建新分支\ngit checkout -b {branch_name}\n\n# 进行代码修改后，添加并提交\ngit add .\ngit commit -m \"update {branch_name}\"\n\n# 推送到远程仓库\ngit push origin {branch_name}"
        return commands

def read_opened_windows_folders_from_trae_storage():
    """
    从Trae的storage.json文件中读取windowsState.openedWindows变量获取已打开目录
    
    Returns:
        list: 包含有效文件夹路径的列表
    """
    recent_folders = []
    
    # Trae存储文件路径
    storage_path = r"C:\Users\Administrator\AppData\Roaming\Trae CN\User\globalStorage\storage.json"
    
    if os.path.exists(storage_path):
        try:
            with open(storage_path, 'r', encoding='utf-8') as f:
                storage_data = json.load(f)
            
            # 检查是否存在windowsState字段
            if 'windowsState' in storage_data:
                windows_state = storage_data['windowsState']
                
                # 检查windowsState中是否存在openedWindows字段
                if isinstance(windows_state, dict) and 'openedWindows' in windows_state:
                    opened_windows = windows_state['openedWindows']
                    
                    if isinstance(opened_windows, list):
                        for window_info in opened_windows:
                            if isinstance(window_info, dict) and 'folder' in window_info:
                                folder_uri = window_info['folder']
                                
                                # 解析file:// URI格式
                                if folder_uri.startswith('file:///'):
                                    # 移除file:///前缀并解码URL编码
                                    folder_path = folder_uri[8:]  # 移除file:///
                                    
                                    # URL解码（将%3A转换为:等）
                                    folder_path = urllib.parse.unquote(folder_path)
                                    
                                    # 验证路径是否存在且为目录
                                    if os.path.exists(folder_path) and os.path.isdir(folder_path):
                                        recent_folders.append(folder_path)
                                        
        except Exception as e:
            print(f"读取Trae存储文件时出错: {e}")
    else:
        print(f"Trae存储文件不存在: {storage_path}")
    
    return recent_folders


def main():
    """主函数"""
    root = tk.Tk()
    app = EvaluationInterface(root)
    root.mainloop()

if __name__ == "__main__":
    main()