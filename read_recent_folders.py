
# -*- coding: utf-8 -*-
"""
读取Trae的storage.json文件中已打开的窗口文件夹信息

功能说明：
从Trae的storage.json文件中读取windowsState.openedWindows变量获取已打开目录
"""

import os
import json
import urllib.parse


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


if __name__ == "__main__":
    """测试函数"""
    print("=== 读取Trae已打开的窗口文件夹 ===")
    
    # 获取已打开的窗口文件夹
    folders = read_opened_windows_folders_from_trae_storage()
    
    if folders:
        print(f"找到 {len(folders)} 个已打开的窗口文件夹:")
        for i, folder in enumerate(folders, 1):
            print(f"{i}. {folder}")
        print("✅ 成功读取已打开的窗口文件夹")
    else:
        print("❌ 未找到任何已打开的窗口文件夹")
