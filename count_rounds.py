
# -*- coding: utf-8 -*-
"""
统计模型日志文件中的轮次
根据"我"出现在"toolName:"之前作为轮次的标记
"""

import re

def count_rounds(file_path):
    """统计指定文件中的轮次数量"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 使用正则表达式查找轮次标记
        # 模式："我"后面跟着任意字符，然后是"toolName:"
        pattern = r'我[\s\S]*?toolName:'
        matches = re.findall(pattern, content)
        
        # 统计轮次数量
        round_count = len(matches)
        
        # 输出统计结果
        print(f"文件: {file_path}")
        print(f"轮次数量: {round_count}")
        print("=" * 50)
        
        # 显示每个轮次的标记位置
        if matches:
            print("找到的轮次标记:")
            for i, match in enumerate(matches, 1):
                # 清理匹配内容，只显示前50个字符
                cleaned_match = match.replace('\n', ' ').replace('\r', ' ')
                if len(cleaned_match) > 50:
                    cleaned_match = cleaned_match[:47] + "..."
                print(f"轮次 {i}: {cleaned_match}")
        else:
            print("未找到轮次标记")
        
        return round_count
        
    except FileNotFoundError:
        print(f"错误: 文件 {file_path} 不存在")
        return 0
    except Exception as e:
        print(f"错误: 读取文件时发生异常 - {e}")
        return 0

def main():
    """主函数"""
    file_path = r"c:\D\04_trae\第三轮\seed_01\docker_file_generation\3_model_log_第三轮对话 copy.md"
    
    print("开始统计轮次...")
    print("=" * 50)
    
    round_count = count_rounds(file_path)
    
    print("=" * 50)
    print(f"统计完成！总轮次: {round_count}")

if __name__ == "__main__":
    main()