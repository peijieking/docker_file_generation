# -*- coding: utf-8 -*-
"""
统计模型日志文件中的toolName和status数量
"""

import re
from collections import defaultdict

def count_tool_stats(file_path):
    """统计文件中的toolName、status和command数量"""
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
        
        return tool_count, status_count, command_count, len(tool_names), len(statuses), len(commands)
        
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return None, None, 0, 0

def print_statistics(tool_count, status_count, command_count, total_tools, total_statuses, total_commands):
    """打印统计结果"""
    # 计算各种状态的数量
    success_count = status_count.get('success', 0)
    running_count = status_count.get('running', 0)
    failed_count = status_count.get('failed', 0) + status_count.get('error', 0)
    
    # 计算失败率
    if total_statuses > 0:
        failure_rate = (failed_count / total_statuses) * 100
    else:
        failure_rate = 0
    
    # 按照要求的格式输出
    print(f"总调用次数{total_tools}次，成功{success_count}次，失败{failed_count}次，正在运行{running_count}次，失败率{failure_rate:.0f}%")
    
    # 显示command统计
    if total_commands > 0:
        print(f"\n命令统计（共{total_commands}个命令）:")
        # 按使用次数降序排列
        sorted_commands = sorted(command_count.items(), key=lambda x: x[1], reverse=True)
        for i, (command, count) in enumerate(sorted_commands[:10], 1):  # 显示前10个
            # 简化命令显示，避免过长
            short_command = command[:50] + "..." if len(command) > 50 else command
            print(f"{i}. {short_command} (使用{count}次)")

def main():
    # 要统计的文件路径
    file_path = r"c:\D\04_trae\第三轮\seed_01\docker_file_generation\3_model_log_第三轮对话 copy.md"
    
    print("开始统计toolName、status和command数量...")
    
    tool_count, status_count, command_count, total_tools, total_statuses, total_commands = count_tool_stats(file_path)
    
    if tool_count is not None:
        print_statistics(tool_count, status_count, command_count, total_tools, total_statuses, total_commands)
    else:
        print("统计失败！")

if __name__ == "__main__":
    main()