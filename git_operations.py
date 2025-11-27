#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git操作工具函数
用于执行特定的Git工作流程：切换到main分支，创建新分支，提交并推送
"""

import subprocess
import sys
import os
from typing import Tuple


def execute_git_commands(branch_name: str, directory: str = None) -> Tuple[bool, str]:
    """
    执行Git命令序列
    
    Args:
        branch_name: 分支名称（如seed_01）
        directory: 工作目录路径，如果为None则使用当前目录
    
    Returns:
        Tuple[bool, str]: (是否成功, 输出信息)
    """
    
    # 设置工作目录
    if directory:
        original_cwd = os.getcwd()
        try:
            os.chdir(directory)
        except Exception as e:
            return False, f"无法切换到目录 {directory}: {str(e)}"
    
    try:
        commands = [
            ("git checkout main", "切换到main分支"),
            (f"git checkout -b {branch_name}", f"创建并切换到分支 {branch_name}"),
            ("git add .", "添加所有文件到暂存区"),
            ("git commit -m update", "提交更改"),
            (f"git push -u origin {branch_name}", f"推送分支到远程仓库")
        ]
        
        output_lines = []
        
        for cmd, description in commands:
            output_lines.append(f"执行: {description}")
            output_lines.append(f"命令: {cmd}")
            
            try:
                result = subprocess.run(
                    cmd, 
                    shell=True, 
                    capture_output=True, 
                    text=True,
                    encoding='utf-8'
                )
                
                if result.returncode == 0:
                    output_lines.append(f"成功: {result.stdout.strip()}")
                else:
                    output_lines.append(f"错误: {result.stderr.strip()}")
                    # 如果某个命令失败，停止执行后续命令
                    return False, "\n".join(output_lines)
                    
            except Exception as e:
                output_lines.append(f"异常: {str(e)}")
                return False, "\n".join(output_lines)
            
            output_lines.append("-" * 50)
        
        return True, "\n".join(output_lines)
        
    except Exception as e:
        return False, f"执行过程中发生异常: {str(e)}"
    
    finally:
        # 恢复原始工作目录
        if directory:
            os.chdir(original_cwd)


def main():
    """主函数，用于命令行调用"""
    if len(sys.argv) < 2:
        print("用法: python git_operations.py <branch_name> [directory]")
        print("示例: python git_operations.py seed_01 /path/to/repo")
        sys.exit(1)
    
    branch_name = sys.argv[1]
    directory = sys.argv[2] if len(sys.argv) > 2 else None
    
    success, message = execute_git_commands(branch_name, directory)
    
    print(message)
    
    if success:
        print("\n✅ 所有Git操作执行成功！")
        sys.exit(0)
    else:
        print("\n❌ Git操作执行失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()